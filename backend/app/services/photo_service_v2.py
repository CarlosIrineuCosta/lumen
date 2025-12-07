"""
Optimized Photo service for EDIS server deployment.

This service uses the new storage architecture with local filesystem storage,
Redis caching, and optimized image processing for improved performance.
"""

import io
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

try:
    from PIL import Image
except ImportError as exc:
    raise ImportError("Pillow must be installed to process image uploads") from exc

from ..database.connection import SessionLocal
from ..models.photo import Photo, PhotoResponse, CreatePhotoRequest, UpdatePhotoRequest, PhotoListResponse
from ..models.user import User
from ..auth_middleware import AuthUser
from ..storage.local_storage import LocalStorageService
from ..storage.redis_cache import create_cache_service
from ..storage.interfaces import StorageException, ICacheService, IStorageService

logger = logging.getLogger(__name__)


ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif"
}

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
MAX_UPLOAD_BYTES = 50 * 1024 * 1024


class OptimizedPhotoService:
    """
    Next-generation photo service optimized for EDIS server.
    
    Features:
    - Local filesystem storage with multi-tier caching
    - Redis caching for URLs and metadata
    - Async image processing
    - Performance monitoring
    - Graceful fallback when services unavailable
    """

    def __init__(self, 
                 db: Session = None,
                 storage_service: IStorageService = None,
                 cache_service: ICacheService = None):
        """
        Initialize optimized photo service.
        
        Args:
            db: Database session
            storage_service: Storage service implementation
            cache_service: Cache service implementation
        """
        self.db = db if db else SessionLocal()
        
        # Initialize storage service
        if storage_service:
            self.storage = storage_service
        else:
            # Use environment variables for configuration
            storage_path = os.getenv('STORAGE_PATH', '/opt/lumen/storage')
            max_storage_gb = float(os.getenv('MAX_STORAGE_GB', '40'))
            cache_ttl_days = int(os.getenv('CACHE_TTL_DAYS', '7'))
            
            self.storage = LocalStorageService(
                base_path=storage_path,
                max_storage_gb=max_storage_gb,
                cache_ttl_days=cache_ttl_days
            )
        
        # Initialize cache service
        if cache_service:
            self.cache = cache_service
        else:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            redis_password = os.getenv('REDIS_PASSWORD')
            self.cache = create_cache_service(redis_url, redis_password)
        
        # Configuration
        self.image_base_url = os.getenv('IMAGE_BASE_URL', 'http://localhost:8080/images')
        
        logger.info("OptimizedPhotoService initialized with local storage and Redis cache")

    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'db'):
            self.db.close()

    async def upload_photo(self,
                          firebase_user: AuthUser,
                          file_content: bytes,
                          filename: str,
                          content_type: str,
                          request: CreatePhotoRequest) -> PhotoResponse:
        """Upload a photo with optimized processing and enhanced cache management."""

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
        except Exception as exc:
            raise ValueError("Uploaded file is not a valid image") from exc

        try:
            from app.utils import validate_firebase_uid

            validated_firebase_uid = validate_firebase_uid(firebase_user.uid, context="photo upload")
            photo_id = uuid.uuid4()
            photo_id_str = str(photo_id)

            logger.info(f"Starting upload for photo {photo_id_str} by user {validated_firebase_uid}")

            stored_image = await self.storage.store_image(
                file_content=file_content,
                filename=filename,
                user_id=validated_firebase_uid,
                photo_id=photo_id_str,
                content_type=content_type
            )

            user_id = await self.ensure_user_exists(firebase_user)

            photo = Photo(
                id=photo_id,
                user_id=user_id,
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

            # Cache photo data
            await self._cache_photo_data(photo_id_str, stored_image)

            # Enhanced cache invalidation
            try:
                # Invalidate user cache since they have a new photo
                await self.cache.invalidate_user_cache(validated_firebase_uid)

                # If photo is public, invalidate recent photos cache
                if request.is_public:
                    await self.cache.invalidate_recent_photos_cache()

            except Exception as cache_error:
                # Don't fail the upload if cache invalidation fails
                logger.warning(f"Cache invalidation failed for photo {photo_id_str}: {cache_error}")

            response = PhotoResponse(
                id=photo_id_str,
                title=photo.title,
                description=photo.description,
                image_url=stored_image.urls.get('large', stored_image.urls.get('original', '')),
                thumbnail_url=stored_image.urls.get('thumb', ''),
                photographer_name=firebase_user.name or firebase_user.email,
                location_display=photo.location_name or '',
                user_tags=photo.user_tags or [],
                ai_tags=photo.ai_tags or [],
                collaborators=[],
                like_count=0,
                is_liked=False,
                is_portfolio=photo.is_portfolio,
                upload_date=photo.upload_date,
                camera_data=photo.camera_data
            )

            logger.info(f"Successfully uploaded photo {photo_id_str}")
            return response

        except ValueError:
            raise
        except StorageException as e:
            self.db.rollback()
            error_message = str(e)
            logger.error(f"Failed to upload photo {firebase_user.uid}: {error_message}")

            message_lower = error_message.lower()
            if any(keyword in message_lower for keyword in ("invalid image", "processing failed", "file too large")):
                raise ValueError("Uploaded file could not be processed as an image") from e

            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to upload photo: {str(e)}")
            raise StorageException(f"Photo upload failed: {str(e)}") from e

    async def get_recent_photos(self, page: int = 1, limit: int = 20) -> PhotoListResponse:
        """Get recent photos with cached URLs"""
        try:
            # Query recent photos
            offset = (page - 1) * limit
            photos = self.db.query(Photo).join(User).filter(
                Photo.is_public == True
            ).order_by(Photo.upload_date.desc()).offset(offset).limit(limit).all()
            
            total_count = self.db.query(Photo).filter(Photo.is_public == True).count()
            
            # Convert to response format with cached URLs
            photo_responses = []
            for photo in photos:
                photo_response = await self._build_photo_response(photo)
                if photo_response:
                    photo_responses.append(photo_response)
            
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
        """Get user photos with cached URLs"""
        try:
            from app.utils import validate_firebase_uid
            validated_user_id = validate_firebase_uid(user_id, context="get user photos")
            
            # Build query
            query = self.db.query(Photo).filter(Photo.user_id == validated_user_id)
            
            if portfolio_only:
                query = query.filter(Photo.is_portfolio == True)
            
            if viewer_user_id != validated_user_id:
                query = query.filter(Photo.is_public == True)
            
            # Paginate
            offset = (page - 1) * limit
            photos = query.order_by(Photo.upload_date.desc()).offset(offset).limit(limit).all()
            
            total_count = query.count()
            
            # Get user info
            user = self.db.query(User).filter(User.id == validated_user_id).first()
            photographer_name = user.display_name if user else "Unknown"
            
            # Convert to response format
            photo_responses = []
            for photo in photos:
                photo_response = await self._build_photo_response(photo, photographer_name)
                if photo_response:
                    photo_responses.append(photo_response)
            
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

    async def get_photo_by_id(self, 
                             photo_id: str, 
                             viewer_user_id: Optional[str] = None) -> Optional[PhotoResponse]:
        """Get single photo by ID with cached URLs"""
        try:
            from app.utils import validate_uuid
            validated_photo_uuid = validate_uuid(photo_id, context="get photo by id")
            
            photo = self.db.query(Photo).filter(Photo.id == validated_photo_uuid).first()
            
            if not photo:
                return None
            
            # Check permissions
            if not photo.is_public and photo.user_id != viewer_user_id:
                return None
            
            return await self._build_photo_response(photo)
            
        except Exception as e:
            logger.error(f"Error getting photo by ID: {e}")
            return None

    async def delete_photo(self, photo_id: str, user_id: str) -> bool:
        """Delete photo from storage and database with comprehensive cache invalidation"""
        try:
            from app.utils import validate_uuid, validate_firebase_uid

            validated_photo_uuid = validate_uuid(photo_id, context="delete photo")
            validated_user_id = validate_firebase_uid(user_id, context="delete photo")

            # Get photo from database
            photo = self.db.query(Photo).filter(
                Photo.id == validated_photo_uuid,
                Photo.user_id == validated_user_id
            ).first()

            if not photo:
                return False

            # Store photo info for cache invalidation before deletion
            was_public = photo.is_public
            user_id_for_cache = validated_user_id

            # Delete from storage
            storage_deleted = await self.storage.delete_image(validated_user_id, photo_id)

            if not storage_deleted:
                logger.warning(f"Failed to delete storage files for {photo_id}")

            # Enhanced cache invalidation
            try:
                # Invalidate specific photo cache
                await self.cache.invalidate_photo(photo_id)

                # Invalidate user cache (since photo count changes)
                await self.cache.invalidate_user_cache(user_id_for_cache)

                # If photo was public, invalidate global caches
                if was_public:
                    await self.cache.invalidate_recent_photos_cache()

                logger.info(f"Comprehensive cache invalidation completed for photo {photo_id}")

            except Exception as cache_error:
                # Don't fail the deletion if cache invalidation fails
                logger.warning(f"Cache invalidation failed during photo deletion {photo_id}: {cache_error}")

            # Delete from database
            self.db.delete(photo)
            self.db.commit()

            logger.info(f"Successfully deleted photo {photo_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting photo {photo_id}: {e}")
            return False

    async def get_storage_stats(self) -> dict:
        """Get storage service statistics"""
        try:
            storage_health = await self.storage.health_check()
            storage_metrics = self.storage.get_metrics()
            cache_stats = await self.cache.get_cache_stats()
            
            return {
                'storage': {
                    'healthy': storage_health.get('healthy', False),
                    'disk_usage_percent': storage_health.get('disk_usage_percent', 0),
                    'upload_time_avg': storage_metrics.upload_time,
                    'processing_time_avg': storage_metrics.processing_time
                },
                'cache': cache_stats,
                'service': 'OptimizedPhotoService'
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {'error': str(e)}

    async def _build_photo_response(self, 
                                   photo: Photo, 
                                   photographer_name: str = None) -> Optional[PhotoResponse]:
        """Build PhotoResponse with cached URLs"""
        try:
            photo_id_str = str(photo.id)
            
            # Try to get URLs from cache first
            cached_urls = await self.cache.get_cached_urls(photo_id_str)
            
            if not cached_urls:
                # Generate URLs from storage
                urls = await self.storage.get_image_urls(photo.user_id, photo_id_str)
                
                if urls:
                    # Cache the URLs
                    await self.cache.cache_urls(photo_id_str, urls, ttl=3600)
                    cached_urls = {'urls': urls}
            
            if not cached_urls or not cached_urls.get('urls'):
                logger.warning(f"No URLs available for photo {photo_id_str}")
                return None
            
            urls = cached_urls['urls']
            
            # Get photographer name if not provided
            if not photographer_name:
                user = self.db.query(User).filter(User.id == photo.user_id).first()
                photographer_name = user.display_name if user else "Unknown"
            
            return PhotoResponse(
                id=photo_id_str,
                title=photo.title,
                description=photo.description,
                image_url=urls.get('large', urls.get('medium', urls.get('original', ''))),
                thumbnail_url=urls.get('thumb', urls.get('small', '')),
                photographer_name=photographer_name,
                location_display=photo.location_name or '',
                user_tags=photo.user_tags or [],
                ai_tags=photo.ai_tags or [],
                collaborators=[],
                like_count=getattr(photo, 'like_count', 0),
                is_liked=False,
                is_portfolio=photo.is_portfolio,
                upload_date=photo.upload_date,
                camera_data=photo.camera_data or {}
            )
            
        except Exception as e:
            logger.error(f"Failed to build photo response for {photo.id}: {e}")
            return None

    async def _cache_photo_data(self, photo_id: str, stored_image):
        """Cache photo URLs and metadata"""
        try:
            # Cache URLs with longer TTL
            await self.cache.cache_urls(photo_id, stored_image.urls, ttl=7200)
            
            # Cache metadata with shorter TTL
            await self.cache.cache_metadata(photo_id, stored_image.metadata, ttl=3600)
            
        except Exception as e:
            logger.warning(f"Failed to cache data for {photo_id}: {e}")

    async def ensure_user_exists(self, firebase_user: AuthUser) -> str:
        """Ensure user exists in PostgreSQL"""
        from app.utils import validate_firebase_uid, log_id_context
        import re

        validated_uid = validate_firebase_uid(firebase_user.uid, context="user existence check")
        log_id_context("Checking user existence", firebase_uid=validated_uid)

        result = self.db.execute(
            text("SELECT id FROM users WHERE id = :firebase_uid"),
            {"firebase_uid": validated_uid}
        ).fetchone()

        if result:
            return validated_uid

        logger.info(f"Creating new user record for Firebase UID: {validated_uid}")

        raw_source = firebase_user.email.split('@')[0] if firebase_user.email else firebase_user.name or "user"
        base_handle = ''.join(c for c in re.sub(r'\s+', '_', raw_source.lower()) if c.isalnum() or c == '_')

        if len(base_handle) < 3:
            base_handle = f"user_{validated_uid[:8]}"

        suffix = 0

        while suffix < 25:
            candidate_handle = base_handle[:20] if suffix == 0 else f"{base_handle[:17]}{suffix:02d}"

            try:
                self.db.execute(text('''
                    INSERT INTO users (
                        id, email, handle, display_name,
                        city_id, primary_user_type, created_at, updated_at, last_active
                    ) VALUES (
                        :id, :email, :handle, :display_name,
                        4, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                '''), {
                    "id": validated_uid,
                    "email": firebase_user.email or f"{candidate_handle}@unknown.com",
                    "handle": candidate_handle,
                    "display_name": firebase_user.name or firebase_user.email or candidate_handle
                })

                self.db.commit()
                logger.info(f"Created user record: {validated_uid} (handle: {candidate_handle})")
                return validated_uid

            except IntegrityError as exc:
                self.db.rollback()

                # If another process inserted the same user id, we are done
                result = self.db.execute(
                    text("SELECT id FROM users WHERE id = :firebase_uid"),
                    {"firebase_uid": validated_uid}
                ).fetchone()
                if result:
                    return validated_uid

                suffix += 1
                logger.warning(
                    "Handle collision while creating user %s (attempt %s): %s",
                    validated_uid,
                    suffix,
                    exc
                )

        raise RuntimeError("Unable to allocate a unique handle after multiple attempts")
