"""
Local filesystem storage implementation for EDIS server.

This module implements the IStorageService interface using the local filesystem
with optimizations for performance, caching, and storage efficiency.
"""

import asyncio
import hashlib
import json
import logging
import os
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union
import uuid

import aiofiles
import aiofiles.os

from .interfaces import (
    IStorageService, ImageMetadata, ImageVariant, StoredImage, 
    StorageMetrics, StorageException, StorageQuotaException
)
from .image_processor import ImageProcessor, ProcessingConfig

logger = logging.getLogger(__name__)


class LocalStorageService(IStorageService):
    """
    Local filesystem storage service optimized for the EDIS server.
    
    Features:
    - Multi-tier storage (cache, main storage)
    - Automatic cleanup of old cache files
    - Efficient directory structure
    - Async file operations
    - Storage quota management
    """

    def __init__(self, 
                 base_path: str = "/opt/lumen/storage",
                 cache_ttl_days: int = 7,
                 max_storage_gb: float = 40.0,
                 enable_cache: bool = True):
        """
        Initialize local storage service.
        
        Args:
            base_path: Base directory for all storage
            cache_ttl_days: Days to keep files in hot cache
            max_storage_gb: Maximum storage quota in GB
            enable_cache: Whether to use hot cache tier
        """
        self.base_path = Path(base_path)
        self.cache_ttl_days = cache_ttl_days
        self.max_storage_bytes = int(max_storage_gb * 1024 * 1024 * 1024)
        self.enable_cache = enable_cache
        
        # Directory structure
        self.dirs = {
            'images': self.base_path / 'images',
            'cache': self.base_path / 'cache',
            'temp': self.base_path / 'temp',
            'metadata': self.base_path / 'metadata',
            'backups': self.base_path / 'backups'
        }
        
        # Size-specific directories under images/
        self.size_dirs = ['thumb', 'small', 'medium', 'large', 'original']
        
        # Initialize image processor
        self.processor = ImageProcessor(ProcessingConfig(
            enable_webp=True,
            enable_progressive_jpeg=True,
            thread_pool_size=2  # Conservative for VPS
        ))
        
        # Metrics tracking
        self.metrics = StorageMetrics()
        self._last_cleanup = datetime.utcnow()
        
        # Ensure directories exist
        asyncio.create_task(self._initialize_directories())

    async def _initialize_directories(self):
        """Create necessary directory structure"""
        try:
            for dir_path in self.dirs.values():
                await aiofiles.os.makedirs(dir_path, exist_ok=True)
            
            # Create size-specific directories
            for size in self.size_dirs:
                for base_dir in ['images', 'cache']:
                    size_dir = self.dirs[base_dir] / size
                    await aiofiles.os.makedirs(size_dir, exist_ok=True)
            
            logger.info(f"Storage directories initialized at {self.base_path}")
            
            # Start background cleanup task
            asyncio.create_task(self._periodic_cleanup())
            
        except Exception as e:
            logger.error(f"Failed to initialize storage directories: {e}")
            raise StorageException(f"Storage initialization failed: {e}")

    async def store_image(self, 
                         file_content: bytes, 
                         filename: str, 
                         user_id: str, 
                         photo_id: str,
                         content_type: str) -> StoredImage:
        """Store image with all variants and metadata"""
        start_time = time.time()
        
        try:
            # Check storage quota
            await self._check_storage_quota(len(file_content))
            
            # Process image into variants
            processing_start = time.time()
            metadata, variants, processed_images = await self.processor.process_image(
                file_content, filename, user_id, photo_id
            )
            processing_time = time.time() - processing_start
            self.metrics.processing_time = processing_time
            
            # Store all variants
            urls = {}
            stored_variants = []
            
            for variant in variants:
                if variant.size_name in processed_images:
                    variant_bytes = processed_images[variant.size_name]
                    
                    # Store in main storage
                    file_path = await self._store_variant_file(
                        variant_bytes, user_id, photo_id, variant.size_name, variant.format
                    )
                    
                    # Store in hot cache if enabled and file is small enough
                    if (self.enable_cache and 
                        variant.size_name in ['thumb', 'small'] and 
                        len(variant_bytes) < 1024 * 1024):  # 1MB limit for cache
                        
                        await self._store_in_cache(
                            variant_bytes, user_id, photo_id, variant.size_name, variant.format
                        )
                    
                    # Generate URL
                    url = f"/images/{variant.size_name}/{user_id}/{photo_id}.{variant.format}"
                    urls[variant.size_name] = url
                    
                    # Update variant with actual file path info
                    variant.url = url
                    stored_variants.append(variant)

            # Store metadata
            await self._store_metadata(metadata)
            
            # Update metrics
            upload_time = time.time() - start_time
            self.metrics.upload_time = upload_time
            self.metrics.storage_used += sum(len(img) for img in processed_images.values())
            
            logger.info(f"Stored image {photo_id} with {len(stored_variants)} variants "
                       f"(processing: {processing_time:.2f}s, total: {upload_time:.2f}s)")
            
            return StoredImage(
                photo_id=photo_id,
                user_id=user_id,
                metadata=metadata,
                variants=stored_variants,
                urls=urls
            )
            
        except Exception as e:
            logger.error(f"Failed to store image {photo_id}: {e}")
            # Cleanup partial files
            await self._cleanup_failed_upload(user_id, photo_id)
            raise StorageException(f"Image storage failed: {str(e)}")

    async def _store_variant_file(self, 
                                 content: bytes, 
                                 user_id: str, 
                                 photo_id: str, 
                                 size: str, 
                                 format: str) -> Path:
        """Store a single image variant to filesystem"""
        
        # Create user directory structure
        user_dir = self.dirs['images'] / size / user_id
        await aiofiles.os.makedirs(user_dir, exist_ok=True)
        
        # Write file
        file_path = user_dir / f"{photo_id}.{format}"
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        return file_path

    async def _store_in_cache(self, 
                             content: bytes, 
                             user_id: str, 
                             photo_id: str, 
                             size: str, 
                             format: str) -> Path:
        """Store image variant in hot cache"""
        
        # Create cache directory structure
        cache_dir = self.dirs['cache'] / size / user_id
        await aiofiles.os.makedirs(cache_dir, exist_ok=True)
        
        # Write to cache
        cache_path = cache_dir / f"{photo_id}.{format}"
        async with aiofiles.open(cache_path, 'wb') as f:
            await f.write(content)
        
        return cache_path

    async def _store_metadata(self, metadata: ImageMetadata):
        """Store image metadata as JSON"""
        
        # Create metadata directory structure
        user_meta_dir = self.dirs['metadata'] / metadata.user_id
        await aiofiles.os.makedirs(user_meta_dir, exist_ok=True)
        
        # Convert metadata to dict
        meta_dict = {
            'filename': metadata.filename,
            'original_filename': metadata.original_filename,
            'file_size': metadata.file_size,
            'width': metadata.width,
            'height': metadata.height,
            'content_type': metadata.content_type,
            'created_at': metadata.created_at.isoformat(),
            'user_id': metadata.user_id,
            'photo_id': metadata.photo_id,
            'checksum': metadata.checksum
        }
        
        # Write metadata
        meta_path = user_meta_dir / f"{metadata.photo_id}.json"
        async with aiofiles.open(meta_path, 'w') as f:
            await f.write(json.dumps(meta_dict, indent=2))

    async def retrieve_image(self, 
                           user_id: str, 
                           photo_id: str, 
                           size: str = 'original') -> Optional[bytes]:
        """Retrieve image content with cache-first strategy"""
        
        # Try cache first for small images
        if (self.enable_cache and 
            size in ['thumb', 'small']):
            
            cache_file = await self._find_image_file(user_id, photo_id, size, cache=True)
            if cache_file and await aiofiles.os.path.exists(cache_file):
                async with aiofiles.open(cache_file, 'rb') as f:
                    content = await f.read()
                    self.metrics.cache_hit_rate += 1
                    return content
        
        # Try main storage
        main_file = await self._find_image_file(user_id, photo_id, size, cache=False)
        if main_file and await aiofiles.os.path.exists(main_file):
            async with aiofiles.open(main_file, 'rb') as f:
                content = await f.read()
                
                # Store in cache if small enough
                if (self.enable_cache and 
                    size in ['thumb', 'small'] and 
                    len(content) < 1024 * 1024):
                    await self._store_in_cache(content, user_id, photo_id, size, 
                                             main_file.suffix.lstrip('.'))
                
                return content
        
        return None

    async def _find_image_file(self, 
                              user_id: str, 
                              photo_id: str, 
                              size: str, 
                              cache: bool = False) -> Optional[Path]:
        """Find image file with format detection"""
        
        base_dir = self.dirs['cache' if cache else 'images']
        user_dir = base_dir / size / user_id
        
        if not await aiofiles.os.path.exists(user_dir):
            return None
        
        # Try common formats
        for ext in ['webp', 'jpeg', 'jpg', 'png']:
            file_path = user_dir / f"{photo_id}.{ext}"
            if await aiofiles.os.path.exists(file_path):
                return file_path
        
        return None

    async def get_image_urls(self, 
                           user_id: str, 
                           photo_id: str) -> Optional[Dict[str, str]]:
        """Get URLs for all available variants"""
        
        # Get base URL from environment or use default
        base_url = os.getenv('STORAGE_BASE_URL', 'https://lumen.photo/storage')
        
        urls = {}
        
        for size in self.size_dirs:
            file_path = await self._find_image_file(user_id, photo_id, size)
            if file_path:
                format_ext = file_path.suffix.lstrip('.')
                # Return full URLs with base URL
                urls[size] = f"{base_url}/images/{size}/{user_id}/{photo_id}.{format_ext}"
        
        return urls if urls else None

    async def delete_image(self, user_id: str, photo_id: str) -> bool:
        """Delete all variants and metadata for an image"""
        
        success = True
        
        try:
            # Delete from main storage and cache
            for base_dir in ['images', 'cache']:
                for size in self.size_dirs:
                    file_path = await self._find_image_file(user_id, photo_id, size, 
                                                          cache=(base_dir == 'cache'))
                    if file_path and await aiofiles.os.path.exists(file_path):
                        await aiofiles.os.remove(file_path)
                        logger.debug(f"Deleted {base_dir}/{size} variant: {file_path}")
            
            # Delete metadata
            meta_path = self.dirs['metadata'] / user_id / f"{photo_id}.json"
            if await aiofiles.os.path.exists(meta_path):
                await aiofiles.os.remove(meta_path)
                logger.debug(f"Deleted metadata: {meta_path}")
            
            logger.info(f"Successfully deleted image {photo_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete image {photo_id}: {e}")
            success = False
        
        return success

    async def get_storage_info(self, user_id: str) -> Dict[str, Union[int, float]]:
        """Get storage usage information for a user"""
        
        total_size = 0
        image_count = 0
        
        try:
            # Check main storage
            for size in self.size_dirs:
                user_dir = self.dirs['images'] / size / user_id
                if await aiofiles.os.path.exists(user_dir):
                    async for entry in aiofiles.os.scandir(user_dir):
                        if entry.is_file():
                            stat = await aiofiles.os.stat(entry.path)
                            total_size += stat.st_size
                            if size == 'original':  # Count each image once
                                image_count += 1
            
            return {
                'used_bytes': total_size,
                'image_count': image_count,
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage info for {user_id}: {e}")
            return {'used_bytes': 0, 'image_count': 0, 'user_id': user_id}

    async def health_check(self) -> Dict[str, Union[bool, str, float]]:
        """Check storage service health"""
        
        health = {
            'healthy': True,
            'message': 'OK',
            'storage_available': True,
            'write_test_passed': False,
            'read_test_passed': False,
            'disk_usage_percent': 0.0,
            'cache_enabled': self.enable_cache
        }
        
        try:
            # Check disk space
            shutil.disk_usage(self.base_path)
            total, used, free = shutil.disk_usage(self.base_path)
            disk_usage_percent = (used / total) * 100
            health['disk_usage_percent'] = disk_usage_percent
            
            if disk_usage_percent > 90:
                health['healthy'] = False
                health['message'] = f"Low disk space: {disk_usage_percent:.1f}% used"
            
            # Test write
            test_file = self.dirs['temp'] / f"health_test_{uuid.uuid4().hex[:8]}.tmp"
            test_data = b"health_check_test"
            
            async with aiofiles.open(test_file, 'wb') as f:
                await f.write(test_data)
            health['write_test_passed'] = True
            
            # Test read
            async with aiofiles.open(test_file, 'rb') as f:
                read_data = await f.read()
                if read_data == test_data:
                    health['read_test_passed'] = True
            
            # Cleanup test file
            await aiofiles.os.remove(test_file)
            
        except Exception as e:
            health['healthy'] = False
            health['message'] = f"Health check failed: {str(e)}"
            logger.error(f"Storage health check failed: {e}")
        
        return health

    def get_metrics(self) -> StorageMetrics:
        """Get current storage performance metrics"""
        return self.metrics

    async def _calculate_directory_size(self, directory: Path) -> int:
        """Calculate total size of files in directory recursively"""
        total_size = 0
        try:
            async for root, dirs, files in aiofiles.os.walk(directory):
                for file in files:
                    file_path = Path(root) / file
                    if await aiofiles.os.path.exists(file_path):
                        stat = await aiofiles.os.stat(file_path)
                        total_size += stat.st_size
        except Exception as e:
            logger.warning(f"Failed to calculate size for {directory}: {e}")
        return total_size

    async def _check_storage_quota(self, additional_bytes: int):
        """Check if adding more data would exceed quota"""
        
        # Calculate actual storage directory usage instead of system disk usage
        storage_used = 0
        try:
            for dir_name in ['images', 'cache', 'metadata']:
                dir_path = self.dirs[dir_name]
                if await aiofiles.os.path.exists(dir_path):
                    storage_used += await self._calculate_directory_size(dir_path)
        except Exception as e:
            logger.warning(f"Failed to calculate storage usage: {e}")
            # Fallback to disk usage check if directory calculation fails
            total, used, free = shutil.disk_usage(self.base_path)
            storage_used = used
        
        if storage_used + additional_bytes > self.max_storage_bytes:
            raise StorageQuotaException(
                f"Storage quota exceeded. Used: {storage_used}, "
                f"Available: {self.max_storage_bytes}, "
                f"Requested: {additional_bytes}"
            )

    async def _cleanup_failed_upload(self, user_id: str, photo_id: str):
        """Clean up partially uploaded files"""
        
        try:
            for base_dir in ['images', 'cache']:
                for size in self.size_dirs:
                    file_path = await self._find_image_file(user_id, photo_id, size, 
                                                          cache=(base_dir == 'cache'))
                    if file_path and await aiofiles.os.path.exists(file_path):
                        await aiofiles.os.remove(file_path)
            
            # Clean up metadata
            meta_path = self.dirs['metadata'] / user_id / f"{photo_id}.json"
            if await aiofiles.os.path.exists(meta_path):
                await aiofiles.os.remove(meta_path)
                
        except Exception as e:
            logger.warning(f"Failed to cleanup failed upload {photo_id}: {e}")

    async def _periodic_cleanup(self):
        """Background task for periodic cache cleanup"""
        
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                if datetime.utcnow() - self._last_cleanup > timedelta(hours=6):
                    await self._cleanup_old_cache_files()
                    self._last_cleanup = datetime.utcnow()
                    
            except Exception as e:
                logger.error(f"Periodic cleanup failed: {e}")

    async def _cleanup_old_cache_files(self):
        """Remove cache files older than TTL"""
        
        if not self.enable_cache:
            return
        
        cutoff_time = datetime.utcnow() - timedelta(days=self.cache_ttl_days)
        cleaned_count = 0
        cleaned_size = 0
        
        try:
            for size in self.size_dirs:
                cache_size_dir = self.dirs['cache'] / size
                
                if not await aiofiles.os.path.exists(cache_size_dir):
                    continue
                
                async for user_dir_entry in aiofiles.os.scandir(cache_size_dir):
                    if user_dir_entry.is_dir():
                        user_cache_dir = Path(user_dir_entry.path)
                        
                        async for file_entry in aiofiles.os.scandir(user_cache_dir):
                            if file_entry.is_file():
                                file_path = Path(file_entry.path)
                                stat = await aiofiles.os.stat(file_path)
                                file_time = datetime.fromtimestamp(stat.st_mtime)
                                
                                if file_time < cutoff_time:
                                    cleaned_size += stat.st_size
                                    await aiofiles.os.remove(file_path)
                                    cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info(f"Cache cleanup: removed {cleaned_count} files, "
                           f"freed {cleaned_size / (1024*1024):.1f} MB")
                
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")