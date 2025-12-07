"""Photo service for managing photo uploads and metadata with local storage"""

import os
import uuid
import io
import logging
from pathlib import Path
from typing import List, Optional, Any
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

try:
    from PIL import Image
except ImportError as exc:  # Pillow is a hard requirement for the storage pipeline
    raise ImportError("Pillow must be installed to process image uploads") from exc

from ..database.connection import SessionLocal
from ..models.photo import Photo, PhotoResponse, CreatePhotoRequest, UpdatePhotoRequest, PhotoListResponse
from ..models.user import User
from ..auth_middleware import AuthUser
from ..storage import get_storage_backend
from ..storage.interfaces import StorageException

logger = logging.getLogger(__name__)


ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif"
}

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # Align with image processor defaults


class PhotoService:
    def __init__(self, db: Session = None):
        # Use storage abstraction instead of direct GCS
        self.storage = get_storage_backend()
        self.db = db if db else SessionLocal()
    
    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'db'):
            self.db.close()
    
    async def _generate_photo_urls(self, photo_id: uuid.UUID, firebase_uid: str) -> tuple[str, str]:
        """Generate URLs for photo and thumbnail using storage abstraction
        
        Args:
            photo_id: Photo UUID
            firebase_uid: Firebase UID string
            
        Returns:
            Tuple of (image_url, thumbnail_url)
        """
        from app.utils import validate_id_consistency, log_id_context
        
        try:
            # Validate IDs for consistency
            validated_user_id, validated_photo_id = validate_id_consistency(
                firebase_uid, photo_id, context="URL generation"
            )
            
            # Get URLs from storage backend
            urls = await self.storage.get_image_urls(validated_user_id, validated_photo_id)
            
            if urls:
                # Return original and thumbnail URLs
                return urls.get('original', ''), urls.get('thumb', '')
            else:
                logger.warning(f"No URLs found for photo {validated_photo_id}")
                return '', ''
                
        except Exception as e:
            logger.error(f"Failed to generate URLs for photo {photo_id}: {str(e)}")
            return '', ''

    async def upload_photo(self, 
                          firebase_user: AuthUser, 
                          file_content: bytes, 
                          filename: str, 
                          content_type: str,
                          request: CreatePhotoRequest) -> Photo:
        """Upload a photo file using storage abstraction and create database record"""
        from app.utils import validate_firebase_uid, log_id_context

        # Validate Firebase UID first
        validated_firebase_uid = validate_firebase_uid(firebase_user.uid, context="photo upload")

        normalized_content_type = (content_type or "").lower()
        if normalized_content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
            raise ValueError("Unsupported image content type")

        if not file_content:
            raise ValueError("Uploaded file is empty")

        if len(file_content) > MAX_UPLOAD_BYTES:
            raise ValueError("Uploaded file exceeds the 50MB limit")

        if filename:
            extension = Path(filename).suffix.lower()
            if extension and extension not in ALLOWED_IMAGE_EXTENSIONS:
                raise ValueError("File extension does not match allowed image formats")

        try:
            with Image.open(io.BytesIO(file_content)) as uploaded_image:
                uploaded_image.verify()
        except Exception as exc:  # Pillow raises multiple exception types
            raise ValueError("Uploaded file is not a valid image") from exc

        # Generate unique photo ID
        photo_id = uuid.uuid4()
        
        log_id_context("Photo upload", 
                      firebase_uid=validated_firebase_uid,
                      photo_id=str(photo_id),
                      filename=filename)
        
        try:
            # Store image using storage abstraction
            stored_image = await self.storage.store_image(
                file_content=file_content,
                filename=filename,
                user_id=validated_firebase_uid,
                photo_id=str(photo_id),
                content_type=content_type
            )
            
            logger.info(f"Stored image with variants: {list(stored_image.urls.keys())}")
            
            # Extract URLs from stored_image to save in database
            image_url = stored_image.urls.get('original', '')
            thumbnail_url = stored_image.urls.get('thumb', '')
            
            # Validate that we have at least the main image URL
            if not image_url:
                raise Exception("Failed to generate image URL from storage backend")
            
            # Ensure user exists in PostgreSQL
            user_id = await self.ensure_user_exists(firebase_user)
            
            # Create photo record using SQLAlchemy model
            photo = Photo(
                id=photo_id,
                user_id=user_id,  # This is the validated Firebase UID
                title=request.title or filename,
                description=request.description,
                image_url=image_url,                # Added URL fields
                thumbnail_url=thumbnail_url,         # Added URL fields
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
            
            # Return photo with generated URLs from storage
            return PhotoResponse(
                id=str(photo.id),
                title=photo.title,
                description=photo.description,
                image_url=stored_image.urls.get('original', ''),
                thumbnail_url=stored_image.urls.get('thumb', ''),
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
        except ValueError:
            raise
        except StorageException as e:
            self.db.rollback()
            error_message = str(e)
            logger.error(f"Failed to upload photo: {error_message}")

            # Map storage/image processing issues to user-friendly validation errors
            message_lower = error_message.lower()
            if any(keyword in message_lower for keyword in ("invalid image", "processing failed", "file too large")):
                raise ValueError("Uploaded file could not be processed as an image") from e

            raise Exception(f"Storage failure: {error_message}") from e
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to upload photo: {str(e)}")
            raise Exception(f"Failed to upload photo: {str(e)}")

    async def get_recent_photos(self, page: int = 1, limit: int = 20) -> PhotoListResponse:
        """Get recent photos with dynamic URL generation using storage abstraction"""
        try:
            # Calculate offset from page number
            offset = (page - 1) * limit
            # Get photos from database
            photos = self.db.query(Photo).join(User).filter(Photo.status == 'active').order_by(Photo.upload_date.desc()).offset(offset).limit(limit).all()
            
            photo_responses = []
            for photo in photos:
                # Generate URLs using storage abstraction
                image_url, thumbnail_url = await self._generate_photo_urls(photo.id, photo.user_id)
                
                photo_response = PhotoResponse(
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
                    like_count=0,
                    is_liked=False,
                    is_portfolio=photo.is_portfolio,
                    upload_date=photo.upload_date,
                    camera_data=photo.camera_data
                )
                photo_responses.append(photo_response)
            
            # Count total photos for pagination
            total_count = self.db.query(Photo).filter(Photo.status == 'active').count()
            has_more = (page * limit) < total_count
            
            return PhotoListResponse(
                photos=photo_responses,
                total_count=total_count,
                page=page,
                limit=limit,
                has_more=has_more
            )
        except Exception as e:
            logger.error(f"Failed to get recent photos: {str(e)}")
            raise Exception(f"Failed to get recent photos: {str(e)}")

    async def get_user_photos(self, firebase_uid: str, page: int = 1, limit: int = 20) -> PhotoListResponse:
        """Get photos for a specific user using storage abstraction"""
        from app.utils import validate_firebase_uid
        
        validated_firebase_uid = validate_firebase_uid(firebase_uid, context="get user photos")
        
        try:
            # Calculate offset from page number
            offset = (page - 1) * limit
            photos = self.db.query(Photo).filter(Photo.user_id == validated_firebase_uid, Photo.status == 'active')\
                          .order_by(Photo.upload_date.desc()).offset(offset).limit(limit).all()
            
            photo_responses = []
            for photo in photos:
                # Generate URLs using storage abstraction
                image_url, thumbnail_url = await self._generate_photo_urls(photo.id, photo.user_id)
                
                photo_response = PhotoResponse(
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
                    like_count=0,
                    is_liked=False,
                    is_portfolio=photo.is_portfolio,
                    upload_date=photo.upload_date,
                    camera_data=photo.camera_data
                )
                photo_responses.append(photo_response)
            
            # Count total photos for this user for pagination
            total_count = self.db.query(Photo).filter(Photo.user_id == validated_firebase_uid, Photo.status == 'active').count()
            has_more = (page * limit) < total_count
            
            return PhotoListResponse(
                photos=photo_responses,
                total_count=total_count,
                page=page,
                limit=limit,
                has_more=has_more
            )
        except Exception as e:
            logger.error(f"Failed to get user photos: {str(e)}")
            raise Exception(f"Failed to get user photos: {str(e)}")

    async def update_photo(self, photo_id: str, user_id: str, update_data: dict) -> Optional[PhotoResponse]:
        """Update a photo"""
        from app.utils import validate_firebase_uid, validate_uuid

        validated_user_id = validate_firebase_uid(user_id, context="update photo")
        validated_photo_id = validate_uuid(photo_id, context="update photo")

        try:
            photo = self.db.query(Photo).filter(
                Photo.id == validated_photo_id,
                Photo.user_id == validated_user_id
            ).first()

            if not photo:
                return None

            for key, value in update_data.items():
                setattr(photo, key, value)

            self.db.commit()
            self.db.refresh(photo)

            image_url, thumbnail_url = await self._generate_photo_urls(photo.id, photo.user_id)

            return PhotoResponse(
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
                like_count=0,
                is_liked=False,
                is_portfolio=photo.is_portfolio,
                upload_date=photo.upload_date,
                camera_data=photo.camera_data
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update photo: {str(e)}")
            return None

    async def delete_photo(self, photo_id: str, firebase_uid: str, permanent: bool = False) -> bool:
        """Delete a photo using storage abstraction"""
        from app.utils import validate_firebase_uid, validate_uuid
        
        validated_firebase_uid = validate_firebase_uid(firebase_uid, context="delete photo")
        validated_photo_id = validate_uuid(photo_id, context="delete photo")
        
        try:
            # Get photo from database
            photo = self.db.query(Photo).filter(
                Photo.id == validated_photo_id,
                Photo.user_id == validated_firebase_uid
            ).first()
            
            if not photo:
                return False
            
            if permanent:
                # Delete from storage
                deleted = await self.storage.delete_image(validated_firebase_uid, str(validated_photo_id))
                
                if deleted:
                    # Delete from database
                    self.db.delete(photo)
                    self.db.commit()
                    logger.info(f"Permanently deleted photo {validated_photo_id}")
                    return True
                else:
                    logger.error(f"Failed to delete photo from storage: {validated_photo_id}")
                    return False
            else:
                # Soft delete
                photo.status = 'deleted'
                self.db.commit()
                logger.info(f"Soft deleted photo {validated_photo_id}")
                return True
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete photo: {str(e)}")
            return False

    async def ensure_user_exists(self, firebase_user: AuthUser) -> str:
        """Ensure user exists in PostgreSQL and return user ID"""
        from app.utils import validate_firebase_uid
        import re
        
        validated_uid = validate_firebase_uid(firebase_user.uid, context="ensure user exists")
        
        existing_user = self.db.query(User).filter(User.id == validated_uid).first()
        if existing_user:
            return validated_uid

        # Generate a handle from display name or email
        raw_source = firebase_user.name or (firebase_user.email.split('@')[0] if firebase_user.email else "")
        base_handle = re.sub(r'[^a-zA-Z0-9_]', '', raw_source.lower().replace(' ', '_'))

        if len(base_handle) < 3:
            base_handle = f"user_{validated_uid[:8]}"

        suffix = 0

        while suffix < 25:  # Hard cap to avoid infinite loops
            if suffix == 0:
                candidate_handle = base_handle[:47]
            else:
                candidate_handle = f"{base_handle[:44]}_{suffix}"

            try:
                user = User(
                    id=validated_uid,
                    email=firebase_user.email,
                    handle=candidate_handle,
                    display_name=firebase_user.name or firebase_user.email or candidate_handle,
                    primary_user_type=None,
                    city_id=None
                )
                self.db.add(user)
                self.db.commit()
                logger.info(f"Created new user: {validated_uid} with handle: {candidate_handle}")
                return validated_uid
            except IntegrityError as exc:
                self.db.rollback()

                # If the user now exists (race condition on id), return immediately
                if self.db.query(User).filter(User.id == validated_uid).first():
                    return validated_uid

                # Handle collision on the candidate handle and retry with suffix incremented
                suffix += 1
                logger.warning(
                    "Handle collision while creating user %s (attempt %s): %s",
                    validated_uid,
                    suffix,
                    exc
                )
                continue

        raise RuntimeError("Unable to allocate a unique handle after multiple attempts")
