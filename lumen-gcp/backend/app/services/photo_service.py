"""Photo service for managing photos in Firestore"""

import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from firebase_admin import firestore
from google.cloud import storage
from PIL import Image
import io

from ..models.photo import (
    Photo, PhotoResponse, PhotoListResponse, CreatePhotoRequest, 
    UpdatePhotoRequest, PhotoSearchQuery, PhotoUrls, PhotoMetadata,
    PhotoEngagement, PhotoVisibility, PhotoStatus
)
from ..auth_middleware import AuthUser
from .user_service import UserService

class PhotoService:
    def __init__(self):
        self.db = firestore.client()
        self.photos_collection = self.db.collection('photos')
        self.storage_client = storage.Client()
        self.bucket_name = os.getenv('STORAGE_BUCKET_NAME', 'lumen-photos-20250731')
        self.bucket = self.storage_client.bucket(self.bucket_name)
        self.user_service = UserService()
    
    async def upload_photo(self, 
                          firebase_user: AuthUser, 
                          file_content: bytes, 
                          filename: str, 
                          content_type: str,
                          request: CreatePhotoRequest) -> Photo:
        """Upload a photo file to Google Cloud Storage and create database record"""
        
        # Generate unique photo ID
        photo_id = str(uuid.uuid4())
        file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
        
        # Generate storage paths
        storage_filename = f"photos/{firebase_user.uid}/{photo_id}.{file_extension}"
        thumbnail_filename = f"thumbnails/{firebase_user.uid}/{photo_id}_thumb.{file_extension}"
        
        try:
            # Process image and extract metadata
            metadata = self._extract_image_metadata(file_content)
            
            # Upload original image
            blob = self.bucket.blob(storage_filename)
            blob.upload_from_string(file_content, content_type=content_type)
            
            # Create and upload thumbnail
            thumbnail_content = self._create_thumbnail(file_content)
            thumbnail_blob = self.bucket.blob(thumbnail_filename)
            thumbnail_blob.upload_from_string(thumbnail_content, content_type='image/jpeg')
            
            # Generate public URLs
            original_url = f"https://storage.googleapis.com/{self.bucket_name}/{storage_filename}"
            thumbnail_url = f"https://storage.googleapis.com/{self.bucket_name}/{thumbnail_filename}"
            
            # Create photo URLs
            urls = PhotoUrls(
                original=original_url,
                thumbnail=thumbnail_url
            )
            
            # Create photo record
            now = datetime.utcnow()
            photo = Photo(
                id=photo_id,
                user_id=firebase_user.uid,
                title=request.title or filename,
                description=request.description,
                alt_text=request.alt_text,
                urls=urls,
                tags=request.tags,
                photography_style=request.photography_style,
                metadata=metadata,
                location=request.location,
                visibility=request.visibility,
                allow_downloads=request.allow_downloads,
                allow_comments=request.allow_comments,
                engagement=PhotoEngagement(),
                status=PhotoStatus.READY,
                created_at=now,
                updated_at=now,
                published_at=now if request.visibility == PhotoVisibility.PUBLIC else None,
                custom_metadata=request.custom_metadata
            )
            
            # Save to Firestore
            doc_ref = self.photos_collection.document(photo_id)
            doc_ref.set(photo.dict())
            
            # Update user's photo count
            await self._update_user_photo_count(firebase_user.uid, 1)
            
            return photo
            
        except Exception as e:
            # Clean up uploaded files if database save fails
            try:
                blob.delete()
                thumbnail_blob.delete()
            except:
                pass
            raise e
    
    async def get_photo(self, photo_id: str, viewer_user_id: Optional[str] = None) -> Optional[Photo]:
        """Get a photo by ID"""
        doc_ref = self.photos_collection.document(photo_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        photo = Photo(**data)
        
        # Check visibility permissions
        if not self._can_view_photo(photo, viewer_user_id):
            return None
        
        # Increment view count if different user
        if viewer_user_id and viewer_user_id != photo.user_id:
            await self._increment_view_count(photo_id)
        
        return photo
    
    async def get_user_photos(self, user_id: str, viewer_user_id: Optional[str] = None, 
                             page: int = 1, per_page: int = 20) -> PhotoListResponse:
        """Get photos for a specific user"""
        
        # Simple query to avoid index issues - get all photos and filter client-side
        query = self.photos_collection.limit(100)  # Limit to prevent huge reads
        
        # Execute query
        results = query.get()
        
        photos = []
        total = 0
        
        for doc in results:
            data = doc.to_dict()
            photo = Photo(**data)
            
            # Filter for this user's photos
            if photo.user_id == user_id:
                # If viewer is not the owner, only show public photos
                if viewer_user_id != user_id and photo.visibility != PhotoVisibility.PUBLIC:
                    continue
                
                total += 1
                photos.append(self._to_photo_response(photo))
        
        # Sort by created_at descending
        photos.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_photos = photos[start_idx:end_idx]
        
        has_more = end_idx < len(photos)
        
        return PhotoListResponse(
            photos=paginated_photos,
            total=total,
            page=page,
            per_page=per_page,
            has_more=has_more
        )
    
    async def get_public_photos(self, page: int = 1, per_page: int = 20) -> PhotoListResponse:
        """Get public photos for the main feed"""
        
        # Very simple query - just get all photos, filter client-side for now
        # This avoids complex index requirements
        query = self.photos_collection.limit(100)  # Limit to prevent huge reads
        
        # Execute query
        results = query.get()
        
        photos = []
        total = 0
        
        for doc in results:
            data = doc.to_dict()
            photo = Photo(**data)
            
            # Filter for public photos
            if photo.visibility == PhotoVisibility.PUBLIC:
                total += 1
                photos.append(self._to_photo_response(photo))
        
        # Sort by created_at descending
        photos.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_photos = photos[start_idx:end_idx]
        
        has_more = end_idx < len(photos)
        
        return PhotoListResponse(
            photos=paginated_photos,
            total=total,
            page=page,
            per_page=per_page,
            has_more=has_more
        )
    
    async def update_photo(self, photo_id: str, user_id: str, request: UpdatePhotoRequest) -> Optional[Photo]:
        """Update photo metadata"""
        doc_ref = self.photos_collection.document(photo_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        photo = Photo(**data)
        
        # Check ownership
        if photo.user_id != user_id:
            return None
        
        # Build updates
        updates = {"updated_at": datetime.utcnow()}
        
        if request.title is not None:
            updates["title"] = request.title
        
        if request.description is not None:
            updates["description"] = request.description
        
        if request.alt_text is not None:
            updates["alt_text"] = request.alt_text
        
        if request.tags is not None:
            updates["tags"] = request.tags
        
        if request.photography_style is not None:
            updates["photography_style"] = request.photography_style
        
        if request.visibility is not None:
            updates["visibility"] = request.visibility.value
            # Update published_at if making public for first time
            if request.visibility == PhotoVisibility.PUBLIC and not photo.published_at:
                updates["published_at"] = datetime.utcnow()
        
        if request.allow_downloads is not None:
            updates["allow_downloads"] = request.allow_downloads
        
        if request.allow_comments is not None:
            updates["allow_comments"] = request.allow_comments
        
        if request.location is not None:
            updates["location"] = request.location.dict()
        
        if request.custom_metadata is not None:
            updates["custom_metadata"] = {**photo.custom_metadata, **request.custom_metadata}
        
        # Apply updates
        doc_ref.update(updates)
        
        # Return updated photo
        return await self.get_photo(photo_id, user_id)
    
    async def delete_photo(self, photo_id: str, user_id: str) -> bool:
        """Delete a photo"""
        doc_ref = self.photos_collection.document(photo_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        data = doc.to_dict()
        photo = Photo(**data)
        
        # Check ownership
        if photo.user_id != user_id:
            return False
        
        try:
            # Delete from storage
            original_blob = self.bucket.blob(f"photos/{user_id}/{photo_id}")
            thumbnail_blob = self.bucket.blob(f"thumbnails/{user_id}/{photo_id}_thumb")
            
            try:
                original_blob.delete()
            except:
                pass  # Continue even if file doesn't exist
            
            try:
                thumbnail_blob.delete()
            except:
                pass  # Continue even if file doesn't exist
            
            # Delete from database
            doc_ref.delete()
            
            # Update user's photo count
            await self._update_user_photo_count(user_id, -1)
            
            return True
            
        except Exception as e:
            print(f"Error deleting photo {photo_id}: {str(e)}")
            return False
    
    async def like_photo(self, photo_id: str, user_id: str) -> bool:
        """Like/unlike a photo"""
        doc_ref = self.photos_collection.document(photo_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        # TODO: Implement proper like tracking with user-specific likes
        # For now, just increment the like count
        doc_ref.update({
            "engagement.likes_count": firestore.Increment(1),
            "updated_at": datetime.utcnow()
        })
        
        return True
    
    def _extract_image_metadata(self, image_data: bytes) -> PhotoMetadata:
        """Extract metadata from image data"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            metadata = PhotoMetadata(
                width=image.width,
                height=image.height,
                file_size=len(image_data),
                mime_type=f"image/{image.format.lower()}" if image.format else None,
                color_space=image.mode,
                orientation=1  # Default orientation
            )
            
            # Extract EXIF data if available
            if hasattr(image, '_getexif') and image._getexif():
                exif = image._getexif()
                # TODO: Extract camera info, GPS, etc. from EXIF
            
            return metadata
            
        except Exception as e:
            print(f"Error extracting image metadata: {str(e)}")
            return PhotoMetadata(file_size=len(image_data))
    
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
        if photo.visibility == PhotoVisibility.PUBLIC:
            return True
        
        if not viewer_user_id:
            return False
        
        if photo.user_id == viewer_user_id:
            return True
        
        # TODO: Implement followers_only check
        if photo.visibility == PhotoVisibility.FOLLOWERS_ONLY:
            return False  # For now, deny access
        
        if photo.visibility == PhotoVisibility.PRIVATE:
            return False
        
        return False
    
    def _to_photo_response(self, photo: Photo) -> PhotoResponse:
        """Convert Photo to PhotoResponse"""
        return PhotoResponse(
            id=photo.id,
            user_id=photo.user_id,
            title=photo.title,
            description=photo.description,
            alt_text=photo.alt_text,
            urls=photo.urls,
            tags=photo.tags,
            photography_style=photo.photography_style,
            visibility=photo.visibility,
            location=photo.location,
            engagement=photo.engagement,
            created_at=photo.created_at,
            updated_at=photo.updated_at,
            published_at=photo.published_at
        )
    
    async def _increment_view_count(self, photo_id: str):
        """Increment view count for a photo"""
        doc_ref = self.photos_collection.document(photo_id)
        doc_ref.update({
            "engagement.views_count": firestore.Increment(1)
        })
    
    async def _update_user_photo_count(self, user_id: str, increment: int):
        """Update user's photo count"""
        try:
            user_doc_ref = self.db.collection('users').document(user_id)
            user_doc_ref.update({
                "public_profile.photo_count": firestore.Increment(increment),
                "updated_at": datetime.utcnow()
            })
        except Exception as e:
            print(f"Error updating user photo count: {str(e)}")
            # Don't fail the photo operation if user update fails