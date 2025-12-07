"""
Storage interface abstractions for Lumen image storage.

This module defines the abstract base classes for storage services,
allowing for different storage implementations (local filesystem, S3, etc.)
while maintaining a consistent API.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import uuid


@dataclass
class ImageMetadata:
    """Metadata for a stored image"""
    filename: str
    original_filename: str
    file_size: int
    width: int
    height: int
    content_type: str
    created_at: datetime
    user_id: str
    photo_id: str
    checksum: str


@dataclass
class ImageVariant:
    """Represents different size variants of an image"""
    size_name: str  # 'thumb', 'small', 'medium', 'large', 'original'
    width: int
    height: int
    file_size: int
    url: str
    format: str  # 'webp', 'jpeg', 'png'


@dataclass
class StoredImage:
    """Complete information about a stored image"""
    photo_id: str
    user_id: str
    metadata: ImageMetadata
    variants: List[ImageVariant]
    urls: Dict[str, str]  # size_name -> url mapping
    
    
class StorageMetrics:
    """Storage performance and usage metrics"""
    def __init__(self):
        self.upload_time: float = 0
        self.processing_time: float = 0
        self.cache_hit_rate: float = 0
        self.storage_used: int = 0
        self.bandwidth_used: int = 0


class IStorageService(ABC):
    """
    Abstract interface for image storage services.
    
    This interface defines the contract that all storage implementations must follow,
    enabling easy switching between local filesystem, cloud storage, or hybrid solutions.
    """

    @abstractmethod
    async def store_image(self, 
                         file_content: bytes, 
                         filename: str, 
                         user_id: str, 
                         photo_id: str,
                         content_type: str) -> StoredImage:
        """
        Store an image and generate all required variants.
        
        Args:
            file_content: Raw image data
            filename: Original filename
            user_id: Firebase UID of the user
            photo_id: UUID of the photo
            content_type: MIME type of the image
            
        Returns:
            StoredImage with metadata and URLs for all variants
            
        Raises:
            StorageException: If storage operation fails
        """
        pass

    @abstractmethod
    async def retrieve_image(self, 
                           user_id: str, 
                           photo_id: str, 
                           size: str = 'original') -> Optional[bytes]:
        """
        Retrieve image content for a specific size.
        
        Args:
            user_id: Firebase UID of the user
            photo_id: UUID of the photo
            size: Size variant to retrieve
            
        Returns:
            Image bytes or None if not found
        """
        pass

    @abstractmethod
    async def get_image_urls(self, 
                           user_id: str, 
                           photo_id: str) -> Optional[Dict[str, str]]:
        """
        Get URLs for all variants of an image.
        
        Args:
            user_id: Firebase UID of the user
            photo_id: UUID of the photo
            
        Returns:
            Dictionary mapping size names to URLs
        """
        pass

    @abstractmethod
    async def delete_image(self, user_id: str, photo_id: str) -> bool:
        """
        Delete all variants of an image.
        
        Args:
            user_id: Firebase UID of the user
            photo_id: UUID of the photo
            
        Returns:
            True if deletion was successful
        """
        pass

    @abstractmethod
    async def get_storage_info(self, user_id: str) -> Dict[str, Union[int, float]]:
        """
        Get storage usage information for a user.
        
        Args:
            user_id: Firebase UID of the user
            
        Returns:
            Dictionary with storage metrics (used_bytes, image_count, etc.)
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Union[bool, str, float]]:
        """
        Check the health of the storage service.
        
        Returns:
            Dictionary with health status and performance metrics
        """
        pass

    @abstractmethod
    def get_metrics(self) -> StorageMetrics:
        """
        Get current storage performance metrics.
        
        Returns:
            StorageMetrics object with current performance data
        """
        pass


class ICacheService(ABC):
    """
    Abstract interface for caching services.
    
    Used to cache image metadata, frequently accessed images, and URLs
    to improve response times.
    """

    @abstractmethod
    async def get_cached_urls(self, photo_id: str) -> Optional[Dict[str, str]]:
        """Get cached image URLs for a photo"""
        pass

    @abstractmethod
    async def cache_urls(self, 
                        photo_id: str, 
                        urls: Dict[str, str], 
                        ttl: int = 3600) -> None:
        """Cache image URLs for a photo"""
        pass

    @abstractmethod
    async def get_cached_metadata(self, photo_id: str) -> Optional[ImageMetadata]:
        """Get cached image metadata"""
        pass

    @abstractmethod
    async def cache_metadata(self, 
                           photo_id: str, 
                           metadata: ImageMetadata, 
                           ttl: int = 3600) -> None:
        """Cache image metadata"""
        pass

    @abstractmethod
    async def invalidate_photo(self, photo_id: str) -> None:
        """Remove all cached data for a photo"""
        pass

    @abstractmethod
    async def get_cache_stats(self) -> Dict[str, Union[int, float]]:
        """Get cache performance statistics"""
        pass


class StorageException(Exception):
    """Base exception for storage operations"""
    pass


class ImageProcessingException(StorageException):
    """Exception raised during image processing"""
    pass


class StorageQuotaException(StorageException):
    """Exception raised when storage quota is exceeded"""
    pass


class StorageUnavailableException(StorageException):
    """Exception raised when storage service is unavailable"""
    pass