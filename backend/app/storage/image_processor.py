"""
Advanced image processing utilities for Lumen storage.

This module handles image resizing, format conversion, optimization,
and metadata extraction for the storage system.
"""

import asyncio
import hashlib
import io
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path

try:
    from PIL import Image, ImageOps, ExifTags
    from PIL.ExifTags import TAGS
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pillow_heif
    # Register HEIF opener with Pillow
    pillow_heif.register_heif_opener()
    HAS_HEIF = True
except ImportError:
    HAS_HEIF = False

from .interfaces import ImageMetadata, ImageVariant, ImageProcessingException

logger = logging.getLogger(__name__)


@dataclass
class ProcessingConfig:
    """Configuration for image processing operations"""
    sizes: Dict[str, Tuple[int, int]] = None
    formats: Dict[str, str] = None
    quality_settings: Dict[str, int] = None
    enable_webp: bool = True
    enable_progressive_jpeg: bool = True
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    thread_pool_size: int = 4

    def __post_init__(self):
        if self.sizes is None:
            self.sizes = {
                'thumb': (150, 150),
                'small': (400, 400),
                'medium': (800, 800),
                'large': (1600, 1600),
                'original': None  # Keep original size
            }
        
        if self.formats is None:
            self.formats = {
                'thumb': 'webp' if self.enable_webp else 'jpeg',
                'small': 'webp' if self.enable_webp else 'jpeg',
                'medium': 'webp' if self.enable_webp else 'jpeg',
                'large': 'jpeg',  # Keep large images as JPEG for compatibility
                'original': None  # Preserve original format
            }
        
        if self.quality_settings is None:
            self.quality_settings = {
                'webp': 85,
                'jpeg': 88,
                'png': None  # PNG is lossless
            }


class ImageProcessor:
    """
    High-performance image processing engine.
    
    Handles resizing, format conversion, optimization, and metadata extraction
    with async support and thread pooling for CPU-intensive operations.
    """

    def __init__(self, config: Optional[ProcessingConfig] = None):
        if not HAS_PIL:
            raise ImportError("Pillow is required for image processing")
        
        self.config = config or ProcessingConfig()
        self.executor = ThreadPoolExecutor(max_workers=self.config.thread_pool_size)
        
        logger.info(f"ImageProcessor initialized with WebP: {self.config.enable_webp}, "
                   f"HEIF: {HAS_HEIF}, Thread pool: {self.config.thread_pool_size}")

    async def process_image(self, 
                          file_content: bytes, 
                          original_filename: str,
                          user_id: str,
                          photo_id: str) -> Tuple[ImageMetadata, List[ImageVariant], Dict[str, bytes]]:
        """
        Process an uploaded image into multiple variants.
        
        Args:
            file_content: Raw image bytes
            original_filename: Original filename
            user_id: Firebase UID
            photo_id: Photo UUID
            
        Returns:
            Tuple of (metadata, variants_list, processed_images_dict)
            
        Raises:
            ImageProcessingException: If processing fails
        """
        if len(file_content) > self.config.max_file_size:
            raise ImageProcessingException(f"File too large: {len(file_content)} bytes")

        try:
            # Process image in thread pool to avoid blocking
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._process_image_sync, file_content, original_filename, user_id, photo_id
            )
            return result
        except Exception as e:
            logger.error(f"Image processing failed for {photo_id}: {e}")
            raise ImageProcessingException(f"Processing failed: {str(e)}") from e

    def _process_image_sync(self, 
                           file_content: bytes, 
                           original_filename: str,
                           user_id: str,
                           photo_id: str) -> Tuple[ImageMetadata, List[ImageVariant], Dict[str, bytes]]:
        """Synchronous image processing - runs in thread pool"""
        
        # Calculate checksum
        checksum = hashlib.sha256(file_content).hexdigest()
        
        # Open and validate image
        try:
            image = Image.open(io.BytesIO(file_content))
            # Auto-rotate based on EXIF orientation
            image = ImageOps.exif_transpose(image)
        except Exception as e:
            raise ImageProcessingException(f"Invalid image format: {e}")

        # Extract metadata
        original_format = image.format.lower() if image.format else 'jpeg'
        width, height = image.size
        
        metadata = ImageMetadata(
            filename=f"{photo_id}.{original_format}",
            original_filename=original_filename,
            file_size=len(file_content),
            width=width,
            height=height,
            content_type=f"image/{original_format}",
            created_at=datetime.utcnow(),
            user_id=user_id,
            photo_id=photo_id,
            checksum=checksum
        )

        # Process all size variants
        variants = []
        processed_images = {}

        for size_name, dimensions in self.config.sizes.items():
            try:
                if size_name == 'original':
                    # Store original with potential format optimization
                    variant_data = self._optimize_original(image, original_format, file_content)
                else:
                    # Create resized variant
                    variant_data = self._create_variant(image, size_name, dimensions)
                
                if variant_data:
                    variant_image, variant_bytes, variant_format = variant_data
                    
                    variant = ImageVariant(
                        size_name=size_name,
                        width=variant_image.width,
                        height=variant_image.height,
                        file_size=len(variant_bytes),
                        url=f"/images/{size_name}/{user_id}/{photo_id}.{variant_format}",
                        format=variant_format
                    )
                    
                    variants.append(variant)
                    processed_images[size_name] = variant_bytes
                    
            except Exception as e:
                logger.warning(f"Failed to create {size_name} variant for {photo_id}: {e}")
                continue

        if not variants:
            raise ImageProcessingException("No variants could be created")

        logger.info(f"Processed {len(variants)} variants for {photo_id}")
        return metadata, variants, processed_images

    def _optimize_original(self, 
                          image: Image.Image, 
                          original_format: str, 
                          original_bytes: bytes) -> Tuple[Image.Image, bytes, str]:
        """Optimize original image while preserving format"""
        
        # For JPEG, enable progressive encoding
        if original_format.lower() in ['jpeg', 'jpg']:
            output = io.BytesIO()
            image.save(output, 
                      format='JPEG', 
                      quality=self.config.quality_settings['jpeg'],
                      progressive=self.config.enable_progressive_jpeg,
                      optimize=True)
            return image, output.getvalue(), 'jpeg'
        
        # For PNG, optimize without quality loss
        elif original_format.lower() == 'png':
            output = io.BytesIO()
            image.save(output, format='PNG', optimize=True)
            return image, output.getvalue(), 'png'
        
        # For other formats, convert to JPEG
        else:
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            output = io.BytesIO()
            image.save(output, 
                      format='JPEG', 
                      quality=self.config.quality_settings['jpeg'],
                      progressive=self.config.enable_progressive_jpeg,
                      optimize=True)
            return image, output.getvalue(), 'jpeg'

    def _create_variant(self, 
                       image: Image.Image, 
                       size_name: str, 
                       dimensions: Tuple[int, int]) -> Optional[Tuple[Image.Image, bytes, str]]:
        """Create a resized variant of the image"""
        
        # Create resized image
        variant_image = image.copy()
        variant_image.thumbnail(dimensions, Image.Resampling.LANCZOS)
        
        # Convert RGBA/P to RGB if needed for JPEG/WebP
        if variant_image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', variant_image.size, (255, 255, 255))
            if variant_image.mode == 'P':
                variant_image = variant_image.convert('RGBA')
            background.paste(variant_image, mask=variant_image.split()[-1] if variant_image.mode == 'RGBA' else None)
            variant_image = background

        # Determine output format
        target_format = self.config.formats.get(size_name, 'jpeg')
        
        # Save variant
        output = io.BytesIO()
        
        if target_format == 'webp' and self.config.enable_webp:
            variant_image.save(output, 
                             format='WebP', 
                             quality=self.config.quality_settings['webp'],
                             method=6,  # Best compression
                             optimize=True)
            return variant_image, output.getvalue(), 'webp'
        
        elif target_format == 'jpeg':
            variant_image.save(output, 
                             format='JPEG', 
                             quality=self.config.quality_settings['jpeg'],
                             progressive=self.config.enable_progressive_jpeg,
                             optimize=True)
            return variant_image, output.getvalue(), 'jpeg'
        
        else:  # PNG fallback
            variant_image.save(output, format='PNG', optimize=True)
            return variant_image, output.getvalue(), 'png'

    def extract_exif_data(self, image: Image.Image) -> Dict[str, Union[str, int, float]]:
        """Extract EXIF metadata from image"""
        exif_data = {}
        
        try:
            if hasattr(image, '_getexif') and image._getexif() is not None:
                exif = image._getexif()
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    
                    # Convert bytes to string for text fields
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8')
                        except UnicodeDecodeError:
                            continue
                    
                    # Store useful metadata
                    if tag in ['Make', 'Model', 'DateTime', 'DateTimeOriginal', 
                              'ExposureTime', 'FNumber', 'ISO', 'FocalLength']:
                        exif_data[tag] = value
                        
        except Exception as e:
            logger.warning(f"Failed to extract EXIF data: {e}")
            
        return exif_data

    async def get_image_info(self, file_content: bytes) -> Dict[str, Union[str, int]]:
        """Get basic image information without full processing"""
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._get_image_info_sync, file_content
            )
            return result
        except Exception as e:
            logger.error(f"Failed to get image info: {e}")
            return {}

    def _get_image_info_sync(self, file_content: bytes) -> Dict[str, Union[str, int]]:
        """Synchronous version of get_image_info"""
        try:
            with Image.open(io.BytesIO(file_content)) as image:
                return {
                    'width': image.width,
                    'height': image.height,
                    'format': image.format.lower() if image.format else 'unknown',
                    'mode': image.mode,
                    'size_bytes': len(file_content)
                }
        except Exception:
            return {}

    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()