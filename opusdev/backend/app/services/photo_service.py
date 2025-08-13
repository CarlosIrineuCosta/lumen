"""Photo service for managing photo uploads and metadata in PostgreSQL"""

import os
import uuid
import io
import logging
from typing import List, Optional, Any
from datetime import datetime
from PIL import Image
from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload
from google.cloud import storage

from ..database.connection import SessionLocal
from ..models.photo import Photo, PhotoResponse, CreatePhotoRequest, UpdatePhotoRequest, PhotoListResponse
from ..models.user import User
from ..auth_middleware import AuthUser

logger = logging.getLogger(__name__)


class PhotoService:
    def __init__(self, db: Session = None):
        self.storage_client = storage.Client()
        
        # CRITICAL WARNING: This bucket name MUST match actual GCS bucket!
        # Actual bucket: 'lumen-photos-20250731' 
        # Wrong bucket breaks ALL image loading with placeholder URLs!
        # See CLAUDE.md "CRITICAL SYSTEM DEPENDENCIES" section before changing!
        self.bucket_name = os.getenv('GOOGLE_CLOUD_STORAGE_BUCKET', 'lumen-photos-20250731')
        
        self.bucket = self.storage_client.bucket(self.bucket_name)
        self.db = db if db else SessionLocal()
    
    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'db'):
            self.db.close()
    
    def _generate_photo_urls(self, photo_id: uuid.UUID, firebase_uid: str) -> tuple[str, str]:
        """Generate signed URLs for photo and thumbnail dynamically
        
        This function constructs GCS file paths using validated ID formats.
        
        FIXED: Now uses ID validation utilities to ensure consistent string formatting
        and proper error handling for ID format mismatches.
        
        Args:
            photo_id: Photo UUID (will be converted to string)
            firebase_uid: Firebase UID string (will be validated)
            
        Returns:
            Tuple of (image_url, thumbnail_url)
            
        Raises:
            IDValidationError: If ID formats are invalid
        """
        from app.utils import validate_id_consistency, format_gcs_path, log_id_context
        
        try:
            # Validate and convert IDs to consistent string format
            validated_user_id, validated_photo_id = validate_id_consistency(
                firebase_uid, photo_id, context="URL generation"
            )
            
            # Construct file paths using validated, string-formatted IDs
            image_path = format_gcs_path("photos", validated_user_id, f"{validated_photo_id}.jpg", 
                                       context="image path")
            thumb_path = format_gcs_path("thumbnails", validated_user_id, f"{validated_photo_id}_thumb.jpg",
                                       context="thumbnail path")
            
            # Log for debugging
            log_id_context("Generating signed URLs", 
                          photo_id=validated_photo_id, 
                          firebase_uid=validated_user_id,
                          image_path=image_path,
                          thumb_path=thumb_path)
            
            # Generate signed URLs with 1-hour expiration (shorter for security)
            from datetime import timedelta
            
            image_blob = self.bucket.blob(image_path)
            thumb_blob = self.bucket.blob(thumb_path)
            
            image_url = image_blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=1),
                method="GET"
            )
            
            thumbnail_url = thumb_blob.generate_signed_url(
                version="v4", 
                expiration=timedelta(hours=1),
                method="GET"
            )
            
            return image_url, thumbnail_url
            
        except Exception as e:
            # Enhanced error logging with ID context
            logger.error(f"Failed to generate signed URLs for photo {photo_id} (user: {firebase_uid}): {e}")
            logger.error(f"Expected paths - Image: {image_path if 'image_path' in locals() else 'unknown'}, "
                        f"Thumbnail: {thumb_path if 'thumb_path' in locals() else 'unknown'}")
            logger.error(f"Debug command: gsutil ls gs://{self.bucket_name}/photos/{firebase_uid}/")
            
            # Return placeholder URLs with more specific error context
            return (
                f"https://via.placeholder.com/800x600?text=Image+Error+{type(e).__name__}",
                f"https://via.placeholder.com/200x200?text=Thumb+Error+{type(e).__name__}"
            )
    
    async def ensure_user_exists(self, firebase_user: AuthUser) -> str:
        """Ensure user exists in PostgreSQL, create if not"""
        from app.utils import validate_firebase_uid, log_id_context
        
        # Validate Firebase UID format first
        validated_uid = validate_firebase_uid(firebase_user.uid, context="user existence check")
        
        log_id_context("Checking user existence", firebase_uid=validated_uid)
        
        # Check if user already exists (Firebase UID is now the primary key)
        result = self.db.execute(
            text("SELECT id FROM users WHERE id = :firebase_uid"),
            {"firebase_uid": validated_uid}
        ).fetchone()
        
        if result:
            logger.debug(f"User exists: {validated_uid}")
            return validated_uid  # User exists, return Firebase UID
        
        # User doesn't exist - create minimal user record
        logger.info(f"Creating new user record for Firebase UID: {validated_uid}")
        
        # Generate unique handle from email or name
        base_handle = firebase_user.email.split('@')[0] if firebase_user.email else 'user'
        base_handle = ''.join(c for c in base_handle if c.isalnum())[:20]  # Clean handle
        
        # Find unique handle
        handle = base_handle
        counter = 1
        while True:
            existing = self.db.execute(
                text("SELECT id FROM users WHERE handle = :handle"),
                {"handle": handle}
            ).fetchone()
            if not existing:
                break
            handle = f"{base_handle}{counter}"
            counter += 1
        
        # Create new user with Firebase UID as primary key
        self.db.execute(text('''
            INSERT INTO users (
                id, email, handle, display_name, 
                city_id, primary_user_type, created_at, updated_at, last_active
            ) VALUES (
                :id, :email, :handle, :display_name,
                4, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
        '''), {
            "id": validated_uid,  # Validated Firebase UID as primary key
            "email": firebase_user.email or f"{handle}@unknown.com",
            "handle": handle,
            "display_name": firebase_user.name or firebase_user.email or handle
        })
        
        self.db.commit()
        logger.info(f"Created user record: {validated_uid} (handle: {handle})")
        return validated_uid
    
    async def upload_photo(self, 
                          firebase_user: AuthUser, 
                          file_content: bytes, 
                          filename: str, 
                          content_type: str,
                          request: CreatePhotoRequest) -> Photo:
        """Upload a photo file to Google Cloud Storage and create database record"""
        from app.utils import validate_firebase_uid, format_gcs_path, log_id_context
        
        # Validate Firebase UID first
        validated_firebase_uid = validate_firebase_uid(firebase_user.uid, context="photo upload")
        
        # Generate unique photo ID
        photo_id = uuid.uuid4()
        file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
        
        # Generate storage paths using validated ID utilities
        storage_filename = format_gcs_path("photos", validated_firebase_uid, f"{photo_id}.{file_extension}",
                                         context="photo upload")
        thumbnail_filename = format_gcs_path("thumbnails", validated_firebase_uid, f"{photo_id}_thumb.{file_extension}",
                                           context="thumbnail upload")
        
        log_id_context("Photo upload", 
                      firebase_uid=validated_firebase_uid,
                      photo_id=str(photo_id),
                      storage_path=storage_filename,
                      thumbnail_path=thumbnail_filename)
        
        try:
            # Upload original image
            blob = self.bucket.blob(storage_filename)
            blob.upload_from_string(file_content, content_type=content_type)
            logger.info(f"Uploaded original image: {storage_filename}")
            
            # Create and upload thumbnail
            thumbnail_content = self._create_thumbnail(file_content)
            thumbnail_blob = self.bucket.blob(thumbnail_filename)
            thumbnail_blob.upload_from_string(thumbnail_content, content_type='image/jpeg')
            logger.info(f"Uploaded thumbnail: {thumbnail_filename}")
            
            # Ensure user exists in PostgreSQL
            user_id = await self.ensure_user_exists(firebase_user)
            
            # Create photo record using SQLAlchemy model
            photo = Photo(
                id=photo_id,
                user_id=user_id,  # This is the validated Firebase UID
                title=request.title or filename,
                description=request.description,
                user_tags=request.user_tags or [],
                is_collaborative=request.is_collaborative,
                model_release_status=request.model_release_status,
                content_rating=request.content_rating,
                is_public=request.is_public,
                is_portfolio=request.is_portfolio,
                camera_data=request.camera_data or {},
                city_id=request.city_id,
                location_name=request.location_name
            )
            
            self.db.add(photo)
            self.db.commit()
            self.db.refresh(photo)
            logger.info(f"Created photo record: {photo.id}")
            
            # Generate dynamic URLs with validated IDs
            image_url, thumbnail_url = self._generate_photo_urls(photo.id, validated_firebase_uid)
            
            # Return photo with generated URLs
            return PhotoResponse(
                id=str(photo.id),
                title=photo.title,
                description=photo.description,
                image_url=image_url,
                thumbnail_url=thumbnail_url,
                photographer_name=firebase_user.name or firebase_user.email,
                location_display=photo.location_display if hasattr(photo, 'location_display') else '',
                user_tags=photo.user_tags or [],
                ai_tags=photo.ai_tags or [],
                collaborators=[],
                like_count=0,
                is_liked=False,
                is_portfolio=photo.is_portfolio,
                upload_date=photo.upload_date,
                camera_data=photo.camera_data
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to upload photo: {str(e)}")
            raise Exception(f"Failed to upload photo: {str(e)}")
    
    def _create_thumbnail(self, file_content: bytes, max_size: tuple = (400, 400)) -> bytes:
        """Create a thumbnail from the uploaded image"""
        try:
            image = Image.open(io.BytesIO(file_content))
            
            # Convert RGBA to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Create thumbnail
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            logger.warning(f"Failed to create thumbnail: {e}")
            # Return original if thumbnail creation fails
            return file_content
    
    async def get_recent_photos(self, page: int = 1, limit: int = 20) -> PhotoListResponse:
        """Get recent photos from all users"""
        try:
            # Query recent photos with user information
            offset = (page - 1) * limit
            photos = self.db.query(Photo).join(User).filter(
                Photo.is_public == True
            ).order_by(Photo.upload_date.desc()).offset(offset).limit(limit).all()
            
            # Get total count
            total_count = self.db.query(Photo).filter(Photo.is_public == True).count()
            
            # Convert to response format
            photo_responses = []
            for photo in photos:
                # Generate URLs dynamically with validated IDs
                image_url, thumbnail_url = self._generate_photo_urls(photo.id, photo.user.id)
                
                photo_responses.append(PhotoResponse(
                    id=str(photo.id),
                    title=photo.title,
                    description=photo.description,
                    image_url=image_url,
                    thumbnail_url=thumbnail_url,
                    photographer_name=photo.user.display_name if photo.user else "Unknown",
                    location_display=photo.location_display if hasattr(photo, 'location_display') else '',
                    user_tags=photo.user_tags or [],
                    ai_tags=photo.ai_tags or [],
                    collaborators=[],
                    like_count=photo.like_count if hasattr(photo, 'like_count') else 0,
                    is_liked=False,
                    is_portfolio=photo.is_portfolio,
                    upload_date=photo.upload_date,
                    camera_data=photo.camera_data
                ))
            
            return PhotoListResponse(
                photos=photo_responses,
                total_count=total_count,
                page=page,
                limit=limit,
                has_more=(page * limit) < total_count
            )
        except Exception as e:
            logger.error(f"Error getting recent photos: {e}")
            return PhotoListResponse(
                photos=[],
                total_count=0,
                page=page,
                limit=limit,
                has_more=False
            )
    
    async def get_user_photos(self, 
                             user_id: str,
                             viewer_user_id: Optional[str] = None,
                             portfolio_only: bool = False,
                             page: int = 1, 
                             limit: int = 20) -> PhotoListResponse:
        """Get photos for a specific user"""
        from app.utils import validate_firebase_uid
        
        try:
            # Validate user_id format
            validated_user_id = validate_firebase_uid(user_id, context="get user photos")
            
            # Build query
            query = self.db.query(Photo).filter(Photo.user_id == validated_user_id)            
            # Filter to portfolio photos if requested
            if portfolio_only:
                query = query.filter(Photo.is_portfolio == True)
            
            # Only show public photos unless viewing own photos
            if viewer_user_id != validated_user_id:
                query = query.filter(Photo.is_public == True)
            
            # Paginate
            offset = (page - 1) * limit
            photos = query.order_by(Photo.upload_date.desc()).offset(offset).limit(limit).all()
            
            # Get total count
            total_count = query.count()
            
            # Get user info for photographer name
            user = self.db.query(User).filter(User.id == validated_user_id).first()
            photographer_name = user.display_name if user else "Unknown"
            
            # Convert to response format
            photo_responses = []
            for photo in photos:
                # Generate URLs dynamically with validated IDs
                image_url, thumbnail_url = self._generate_photo_urls(photo.id, validated_user_id)
                
                photo_responses.append(PhotoResponse(
                    id=str(photo.id),
                    title=photo.title,
                    description=photo.description,
                    image_url=image_url,
                    thumbnail_url=thumbnail_url,
                    photographer_name=photographer_name,
                    location_display=photo.location_display if hasattr(photo, 'location_display') else '',
                    user_tags=photo.user_tags or [],
                    ai_tags=photo.ai_tags or [],
                    collaborators=[],
                    like_count=photo.like_count if hasattr(photo, 'like_count') else 0,
                    is_liked=False,
                    is_portfolio=photo.is_portfolio,
                    upload_date=photo.upload_date,
                    camera_data=photo.camera_data
                ))
            
            return PhotoListResponse(
                photos=photo_responses,
                total_count=total_count,
                page=page,
                limit=limit,
                has_more=(page * limit) < total_count
            )
        except Exception as e:
            logger.error(f"Error getting user photos: {e}")
            return PhotoListResponse(
                photos=[],
                total_count=0,
                page=page,
                limit=limit,
                has_more=False
            )
    
    async def get_photo_by_id(self, photo_id: str, viewer_user_id: Optional[str] = None) -> Optional[PhotoResponse]:
        """Get a single photo by ID"""
        from app.utils import validate_uuid
        
        try:
            # Validate photo_id format
            validated_photo_uuid = validate_uuid(photo_id, context="get photo by id")
            
            photo = self.db.query(Photo).filter(Photo.id == validated_photo_uuid).first()
            
            if not photo:
                return None
            
            # Check access permissions
            if not photo.is_public and photo.user_id != viewer_user_id:
                return None
            
            # Get user info
            user = self.db.query(User).filter(User.id == photo.user_id).first()
            
            # Generate URLs dynamically with validated IDs
            image_url, thumbnail_url = self._generate_photo_urls(photo.id, photo.user_id)
            
            return PhotoResponse(
                id=str(photo.id),
                title=photo.title,
                description=photo.description,
                image_url=image_url,
                thumbnail_url=thumbnail_url,
                photographer_name=user.display_name if user else "Unknown",
                location_display=photo.location_display if hasattr(photo, 'location_display') else '',
                user_tags=photo.user_tags or [],
                ai_tags=photo.ai_tags or [],
                collaborators=[],
                like_count=photo.like_count if hasattr(photo, 'like_count') else 0,
                is_liked=False,
                is_portfolio=photo.is_portfolio,
                upload_date=photo.upload_date,
                camera_data=photo.camera_data
            )
        except Exception as e:
            logger.error(f"Error getting photo by ID: {e}")
            return None
    
    async def update_photo(self, 
                          photo_id: str, 
                          user_id: str, 
                          request: UpdatePhotoRequest) -> Optional[PhotoResponse]:
        """Update photo metadata"""
        from app.utils import validate_uuid, validate_firebase_uid
        
        try:
            # Validate both IDs
            validated_photo_uuid = validate_uuid(photo_id, context="update photo")
            validated_user_id = validate_firebase_uid(user_id, context="update photo")
            
            photo = self.db.query(Photo).filter(
                Photo.id == validated_photo_uuid, 
                Photo.user_id == validated_user_id
            ).first()
            
            if not photo:
                return None
            
            # Update fields if provided
            if request.title is not None:
                photo.title = request.title
            if request.description is not None:
                photo.description = request.description
            if request.user_tags is not None:
                photo.user_tags = request.user_tags
            if request.is_public is not None:
                photo.is_public = request.is_public
            if request.is_portfolio is not None:
                photo.is_portfolio = request.is_portfolio
            if request.city_id is not None:
                photo.city_id = request.city_id
            if request.location_name is not None:
                photo.location_name = request.location_name
            if request.content_rating is not None:
                photo.content_rating = request.content_rating
            
            photo.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(photo)
            
            # Return updated photo
            return await self.get_photo_by_id(str(photo.id), validated_user_id)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating photo: {e}")
            return None
    
    async def delete_photo(self, photo_id: str, user_id: str) -> bool:
        """Delete a photo (both database record and files)"""
        from app.utils import validate_uuid, validate_firebase_uid, format_gcs_path
        
        try:
            # Validate both IDs
            validated_photo_uuid = validate_uuid(photo_id, context="delete photo")
            validated_user_id = validate_firebase_uid(user_id, context="delete photo")
            
            photo = self.db.query(Photo).filter(
                Photo.id == validated_photo_uuid,
                Photo.user_id == validated_user_id
            ).first()
            
            if not photo:
                return False
            
            # Delete files from storage using validated paths
            try:
                # Construct paths using validation utilities
                validated_photo_id_str = str(validated_photo_uuid)
                
                # Delete original
                image_path = format_gcs_path("photos", validated_user_id, f"{validated_photo_id_str}.jpg",
                                           context="delete original")
                blob = self.bucket.blob(image_path)
                if blob.exists():
                    blob.delete()
                    logger.info(f"Deleted original image: {image_path}")
                
                # Delete thumbnail
                thumb_path = format_gcs_path("thumbnails", validated_user_id, f"{validated_photo_id_str}_thumb.jpg",
                                           context="delete thumbnail")
                thumb_blob = self.bucket.blob(thumb_path)
                if thumb_blob.exists():
                    thumb_blob.delete()
                    logger.info(f"Deleted thumbnail: {thumb_path}")
                    
            except Exception as e:
                logger.warning(f"Failed to delete files from storage: {e}")
            
            # Delete database record
            self.db.delete(photo)
            self.db.commit()
            logger.info(f"Deleted photo record: {validated_photo_uuid}")
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting photo: {e}")
            return False