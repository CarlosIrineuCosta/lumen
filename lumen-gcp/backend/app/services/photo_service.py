"""Photo service for managing photos in PostgreSQL"""

import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from google.cloud import storage
from PIL import Image
import io

from ..models.photo import (
    Photo, PhotoResponse, PhotoListResponse, CreatePhotoRequest, 
    UpdatePhotoRequest, PhotoSearchQuery, PhotoMetadata
)
from ..models.user import User, UserType
from ..database.connection import get_db
from ..auth_middleware import AuthUser
from .user_service import UserService
from sqlalchemy import text


class PhotoService:
    def __init__(self, db: Session = None):
        self.db = db
        self.storage_client = storage.Client()
        self.bucket_name = os.getenv('STORAGE_BUCKET_NAME', 'lumen-photos-20250731')
        self.bucket = self.storage_client.bucket(self.bucket_name)
        self.user_service = UserService()
    
    def _generate_photo_urls(self, photo_id: uuid.UUID, firebase_uid: str) -> tuple[str, str]:
        """Generate signed URLs for photo and thumbnail dynamically"""
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
            return (
                f"https://via.placeholder.com/800x600?text=Image+Not+Available",
                f"https://via.placeholder.com/200x200?text=Thumb+Not+Available"
            )
    
    async def get_or_create_user_uuid(self, firebase_user: AuthUser) -> uuid.UUID:
        """Get existing PostgreSQL user UUID or create new user from Firebase data"""
        
        # Check if user already exists in PostgreSQL
        result = self.db.execute(
            text("SELECT id FROM users WHERE firebase_uid = :firebase_uid"),
            {"firebase_uid": firebase_user.uid}
        ).fetchone()
        
        if result:
            return result[0]  # Return existing UUID
        
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
        
        # Create new user with minimal required data
        user_id = uuid.uuid4()
        self.db.execute(text('''
            INSERT INTO users (
                id, firebase_uid, email, handle, display_name, 
                city_id, primary_user_type, created_at, updated_at, last_active
            ) VALUES (
                :id, :firebase_uid, :email, :handle, :display_name,
                4, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
        '''), {
            "id": user_id,
            "firebase_uid": firebase_user.uid,
            "email": firebase_user.email or f"{handle}@unknown.com",
            "handle": handle,
            "display_name": firebase_user.name or firebase_user.email or handle
        })
        
        self.db.commit()
        return user_id
    
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
            
            # URLs will be generated dynamically - no storage needed
            
            # Get or create PostgreSQL user for this Firebase user
            user_uuid = await self.get_or_create_user_uuid(firebase_user)
            
            # Create photo record using SQLAlchemy model
            photo = Photo(
                id=photo_id,
                user_id=user_uuid,
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
            
            # Save to PostgreSQL
            self.db.add(photo)
            self.db.commit()
            self.db.refresh(photo)
            
            return photo
            
        except Exception as e:
            # Clean up uploaded files if database save fails
            try:
                blob.delete()
                thumbnail_blob.delete()
            except:
                pass
            self.db.rollback()
            raise e
    
    async def get_photo(self, photo_id: str, viewer_user_id: Optional[str] = None) -> Optional[Photo]:
        """Get a photo by ID"""
        try:
            photo_uuid = uuid.UUID(photo_id)
        except ValueError:
            return None
            
        photo = self.db.query(Photo).filter(Photo.id == photo_uuid).first()
        
        if not photo:
            return None
        
        # Check visibility permissions
        if not self._can_view_photo(photo, viewer_user_id):
            return None
        
        return photo
    
    async def get_user_photos(self, user_id: str, viewer_user_id: Optional[str] = None, 
                             page: int = 1, limit: int = 20) -> PhotoListResponse:
        """Get photos for a specific user"""
        
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return PhotoListResponse(photos=[], total_count=0, page=page, limit=limit, has_more=False)
        
        # Base query for user's photos with eager loading
        query = self.db.query(Photo).options(
            joinedload(Photo.user).joinedload(User.user_type),
            joinedload(Photo.interactions)
        ).filter(Photo.user_id == user_uuid)
        
        # If viewer is not the owner, only show public photos
        if viewer_user_id != user_id:
            query = query.filter(Photo.is_public == True)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and ordering
        photos = query.order_by(desc(Photo.created_at)).offset((page - 1) * limit).limit(limit).all()
        
        # Convert to response format
        photo_responses = [self._to_photo_response(photo) for photo in photos]
        
        has_more = (page * limit) < total_count
        
        return PhotoListResponse(
            photos=photo_responses,
            total_count=total_count,
            page=page,
            limit=limit,
            has_more=has_more
        )
    
    async def get_public_photos(self, page: int = 1, limit: int = 20) -> PhotoListResponse:
        """Get public photos for the main feed"""
        
        # Query for public photos with eager loading to prevent N+1 queries
        query = self.db.query(Photo).options(
            joinedload(Photo.user).joinedload(User.user_type),
            joinedload(Photo.interactions)
        ).filter(Photo.is_public == True, Photo.status == 'active')
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and ordering
        photos = query.order_by(desc(Photo.created_at)).offset((page - 1) * limit).limit(limit).all()
        
        # Convert to response format
        photo_responses = [self._to_photo_response(photo) for photo in photos]
        
        has_more = (page * limit) < total_count
        
        return PhotoListResponse(
            photos=photo_responses,
            total_count=total_count,
            page=page,
            limit=limit,
            has_more=has_more
        )
    
    async def update_photo(self, photo_id: str, user_id: str, request: UpdatePhotoRequest) -> Optional[Photo]:
        """Update photo metadata"""
        try:
            photo_uuid = uuid.UUID(photo_id)
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return None
            
        photo = self.db.query(Photo).filter(Photo.id == photo_uuid).first()
        
        if not photo or photo.user_id != user_uuid:
            return None
        
        # Update fields if provided
        if request.title is not None:
            photo.title = request.title
        if request.description is not None:
            photo.description = request.description
        if request.city_id is not None:
            photo.city_id = request.city_id
        if request.location_name is not None:
            photo.location_name = request.location_name
        if request.user_tags is not None:
            photo.user_tags = request.user_tags
        if request.content_rating is not None:
            photo.content_rating = request.content_rating
        if request.is_public is not None:
            photo.is_public = request.is_public
        if request.is_portfolio is not None:
            photo.is_portfolio = request.is_portfolio
        
        photo.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(photo)
        
        return photo
    
    async def delete_photo(self, photo_id: str, user_id: str) -> bool:
        """Delete a photo"""
        try:
            photo_uuid = uuid.UUID(photo_id)
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return False
            
        photo = self.db.query(Photo).filter(Photo.id == photo_uuid).first()
        
        if not photo or photo.user_id != user_uuid:
            return False
        
        try:
            # Delete from storage
            storage_filename = f"photos/{user_id}/{photo_id}"
            thumbnail_filename = f"thumbnails/{user_id}/{photo_id}_thumb"
            
            try:
                original_blob = self.bucket.blob(storage_filename)
                original_blob.delete()
            except:
                pass  # Continue even if file doesn't exist
            
            try:
                thumbnail_blob = self.bucket.blob(thumbnail_filename)
                thumbnail_blob.delete()
            except:
                pass  # Continue even if file doesn't exist
            
            # Delete from database
            self.db.delete(photo)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Error deleting photo {photo_id}: {str(e)}")
            return False
    
    def _create_thumbnail(self, image_data: bytes, size: tuple = (200, 200)) -> bytes:
        """Create a thumbnail from image data"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Invalid image file: {str(e)}")
    
    def _can_view_photo(self, photo: Photo, viewer_user_id: Optional[str]) -> bool:
        """Check if user can view this photo"""
        if photo.is_public:
            return True
        
        if not viewer_user_id:
            return False
        
        try:
            viewer_uuid = uuid.UUID(viewer_user_id)
            return photo.user_id == viewer_uuid
        except ValueError:
            return False
    
    def _to_photo_response(self, photo: Photo) -> PhotoResponse:
        """Convert Photo to PhotoResponse with dynamic URLs"""
        # Generate URLs dynamically using Firebase UID from user relationship
        image_url, thumbnail_url = self._generate_photo_urls(photo.id, photo.user.firebase_uid)
        
        return PhotoResponse(
            id=str(photo.id),
            title=photo.title,
            description=photo.description,
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            photographer_name=photo.photographer_name,
            location_display=photo.location_display,
            user_tags=photo.user_tags or [],
            ai_tags=photo.ai_tags or [],
            collaborators=[],  # TODO: Implement collaborators
            like_count=photo.like_count,
            is_liked=False,  # TODO: Implement user-specific likes
            upload_date=photo.upload_date,
            camera_data=photo.camera_data
        )