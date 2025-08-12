"""Photo service for managing photo uploads and metadata in PostgreSQL"""

import os
import uuid
import io
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


class PhotoService:
    def __init__(self, db: Session = None):
        self.storage_client = storage.Client()
        
        # ⚠️ CRITICAL WARNING: This bucket name MUST match actual GCS bucket!
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
        
        ⚠️⚠️⚠️ CRITICAL WARNING: UID FORMAT MAPPING ISSUE ⚠️⚠️⚠️
        
        This function is the MOST FRAGILE part of the system!
        
        CURRENT PROBLEM (Aug 12, 2025):
        - Database has UUID format (after schema changes)
        - GCS files stored with Firebase UID strings (28-char alphanumeric)
        - This mismatch causes ALL images to show as placeholders!
        
        REQUIRED PATH FORMAT: photos/{firebase_uid}/{photo_id}.jpg
        Example: photos/9pGzwsVBRMaSxMOZ6QNTJJjnl1b2/c711a9ab-4689-4576-a511-7ce60cc214f3.jpg
        
        See CLAUDE.md "CRITICAL SYSTEM DEPENDENCIES" before modifying!
        """
        try:
            # Construct file paths using Firebase UID (matches upload path)
            image_path = f"photos/{firebase_uid}/{photo_id}.jpg"
            thumb_path = f"thumbnails/{firebase_uid}/{photo_id}_thumb.jpg"
            
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
            # FALLBACK: Return placeholder URLs if GCS fails
            print(f"⚠️ Failed to generate signed URLs for photo {photo_id}: {e}")
            print(f"⚠️ Expected path: {image_path}")
            print(f"⚠️ Check if file exists: gsutil ls gs://{self.bucket_name}/photos/{firebase_uid}/")
            return (
                f"https://via.placeholder.com/800x600?text=Image+Not+Available",
                f"https://via.placeholder.com/200x200?text=Thumb+Not+Available"
            )
    
    async def ensure_user_exists(self, firebase_user: AuthUser) -> str:
        """Ensure user exists in PostgreSQL, create if not"""
        
        # Check if user already exists (Firebase UID is now the primary key)
        result = self.db.execute(
            text("SELECT id FROM users WHERE id = :firebase_uid"),
            {"firebase_uid": firebase_user.uid}
        ).fetchone()
        
        if result:
            return firebase_user.uid  # User exists, return Firebase UID
        
        # User doesn't exist - create minimal user record
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
            "id": firebase_user.uid,  # Firebase UID as primary key
            "email": firebase_user.email or f"{handle}@unknown.com",
            "handle": handle,
            "display_name": firebase_user.name or firebase_user.email or handle
        })
        
        self.db.commit()
        return firebase_user.uid
    
    async def upload_photo(self, 
                          firebase_user: AuthUser, 
                          file_content: bytes, 
                          filename: str, 
                          content_type: str,
                          request: CreatePhotoRequest) -> Photo:
        """Upload a photo file to Google Cloud Storage and create database record"""
        
        # Generate unique photo ID
        photo_id = uuid.uuid4()
        file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
                
        # Generate storage paths
        storage_filename = f"photos/{firebase_user.uid}/{photo_id}.{file_extension}"
        thumbnail_filename = f"thumbnails/{firebase_user.uid}/{photo_id}_thumb.{file_extension}"
        
        try:
            # Upload original image
            blob = self.bucket.blob(storage_filename)
            blob.upload_from_string(file_content, content_type=content_type)
            
            # Create and upload thumbnail
            thumbnail_content = self._create_thumbnail(file_content)
            thumbnail_blob = self.bucket.blob(thumbnail_filename)
            thumbnail_blob.upload_from_string(thumbnail_content, content_type='image/jpeg')
            
            # Ensure user exists in PostgreSQL
            user_id = await self.ensure_user_exists(firebase_user)
            
            # Create photo record using SQLAlchemy model
            photo = Photo(
                id=photo_id,
                user_id=user_id,  # This is the Firebase UID
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
            
            # Generate dynamic URLs
            image_url, thumbnail_url = self._generate_photo_urls(photo.id, firebase_user.uid)
            
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
            print(f"Warning: Failed to create thumbnail: {e}")
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
                # Generate URLs dynamically
                image_url, thumbnail_url = self._generate_photo_urls(photo.id, photo.user_id)
                
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
            print(f"Error getting recent photos: {e}")
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
        try:
            # Build query
            query = self.db.query(Photo).filter(Photo.user_id == user_id)            
            # Filter to portfolio photos if requested
            if portfolio_only:
                query = query.filter(Photo.is_portfolio == True)
            
            # Only show public photos unless viewing own photos
            if viewer_user_id != user_id:
                query = query.filter(Photo.is_public == True)
            
            # Paginate
            offset = (page - 1) * limit
            photos = query.order_by(Photo.upload_date.desc()).offset(offset).limit(limit).all()
            
            # Get total count
            total_count = query.count()
            
            # Get user info for photographer name
            user = self.db.query(User).filter(User.id == user_id).first()
            photographer_name = user.display_name if user else "Unknown"
            
            # Convert to response format
            photo_responses = []
            for photo in photos:
                # Generate URLs dynamically
                image_url, thumbnail_url = self._generate_photo_urls(photo.id, user_id)
                
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
            print(f"Error getting user photos: {e}")
            return PhotoListResponse(
                photos=[],
                total_count=0,
                page=page,
                limit=limit,
                has_more=False
            )
    
    async def get_photo_by_id(self, photo_id: str, viewer_user_id: Optional[str] = None) -> Optional[PhotoResponse]:
        """Get a single photo by ID"""
        try:
            photo = self.db.query(Photo).filter(Photo.id == photo_id).first()
            
            if not photo:
                return None
            
            # Check access permissions
            if not photo.is_public and photo.user_id != viewer_user_id:
                return None
            
            # Get user info
            user = self.db.query(User).filter(User.id == photo.user_id).first()
            
            # Generate URLs dynamically
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
            print(f"Error getting photo by ID: {e}")
            return None
    
    async def update_photo(self, 
                          photo_id: str, 
                          user_id: str, 
                          request: UpdatePhotoRequest) -> Optional[PhotoResponse]:
        """Update photo metadata"""
        try:
            photo = self.db.query(Photo).filter(
                Photo.id == photo_id, 
                Photo.user_id == user_id
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
            return await self.get_photo_by_id(str(photo.id), user_id)
            
        except Exception as e:
            self.db.rollback()
            print(f"Error updating photo: {e}")
            return None
    
    async def delete_photo(self, photo_id: str, user_id: str) -> bool:
        """Delete a photo (both database record and files)"""
        try:
            photo = self.db.query(Photo).filter(
                Photo.id == photo_id,
                Photo.user_id == user_id
            ).first()
            
            if not photo:
                return False
            
            # Delete files from storage
            try:
                # Delete original
                blob = self.bucket.blob(f"photos/{user_id}/{photo.id}.jpg")
                if blob.exists():
                    blob.delete()
                
                # Delete thumbnail
                thumb_blob = self.bucket.blob(f"thumbnails/{user_id}/{photo.id}_thumb.jpg")
                if thumb_blob.exists():
                    thumb_blob.delete()
            except Exception as e:
                print(f"Warning: Failed to delete files from storage: {e}")
            
            # Delete database record
            self.db.delete(photo)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Error deleting photo: {e}")
            return False