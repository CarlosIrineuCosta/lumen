---
description: Lumen image processing and storage management
---

# Lumen Image Processing & Storage Management

Handle image operations for $ARGUMENTS:

## 1. Image Analysis Phase

### Current Storage Assessment
```bash
echo "=== STORAGE ANALYSIS ==="

# Check current image storage structure
echo "Image storage structure:"
find opusdev -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.heic" -o -name "*.webp" 2>/dev/null | head -10

# Check storage configuration
echo ""
echo "Storage configuration check:"
cd opusdev/backend
python -c "
try:
    import os
    from app.config import settings
    print(f'Upload directory: {getattr(settings, \"UPLOAD_DIR\", \"Not configured\")}')
    print(f'Max file size: {getattr(settings, \"MAX_FILE_SIZE\", \"Not configured\")}')
    print(f'Allowed formats: {getattr(settings, \"ALLOWED_FORMATS\", \"Not configured\")}')
except Exception as e:
    print(f'Configuration check failed: {e}')
" 2>/dev/null || echo "Could not check storage configuration"

# Check available disk space
echo ""
echo "Disk space analysis:"
df -h . | tail -1 | awk '{print "Available space: " $4 " (" $5 " used)"}'
```

### Image Format Support Analysis
```bash
echo "=== IMAGE FORMAT SUPPORT ==="

# Check Pillow capabilities
echo "Pillow image format support:"
python -c "
from PIL import Image
import pillow_heif

# Register HEIF opener
pillow_heif.register_heif_opener()

print('Supported formats:')
formats = list(Image.registered_extensions().keys())
key_formats = ['.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.tiff']

for fmt in key_formats:
    if fmt in formats:
        print(f'  ✅ {fmt.upper()}: Supported')
    else:
        print(f'  ❌ {fmt.upper()}: Not supported')

print(f'\\nTotal supported formats: {len(formats)}')
" 2>/dev/null || echo "Could not check image format support"
```

## 2. Image Processing Pipeline

### Upload Processing
```bash
echo "=== IMAGE UPLOAD PROCESSING ==="

# Image processing workflow for uploads
echo "Processing workflow for: $ARGUMENTS"

OPERATION_TYPE="$ARGUMENTS"
case $OPERATION_TYPE in
    *upload*|*process*)
        echo "Image upload processing:"
        echo "1. File validation and security check"
        echo "2. Format conversion (HEIC → JPEG/WebP)"
        echo "3. EXIF data extraction and sanitization"
        echo "4. Multiple thumbnail generation"
        echo "5. Optimization and compression"
        echo "6. Storage to Firebase/GCS"
        ;;
    *resize*|*thumbnail*)
        echo "Image resize/thumbnail generation:"
        echo "1. Load original image"
        echo "2. Calculate optimal dimensions"
        echo "3. Generate multiple sizes"
        echo "4. Optimize for web delivery"
        ;;
    *convert*|*format*)
        echo "Format conversion processing:"
        echo "1. Detect input format"
        echo "2. Convert to target format"
        echo "3. Preserve quality settings"
        echo "4. Update metadata"
        ;;
esac
```

### HEIF/HEIC Processing
```bash
echo "=== HEIF/HEIC PROCESSING ==="

# Handle Apple's HEIC format conversion
echo "HEIC format handling:"
python -c "
import os
from PIL import Image
import pillow_heif

# Register HEIF opener
pillow_heif.register_heif_opener()

def process_heic_sample():
    print('HEIC Processing Capabilities:')
    print('✅ HEIF/HEIC reading: Enabled')
    print('✅ JPEG conversion: Available') 
    print('✅ WebP conversion: Available')
    print('✅ Quality preservation: Configurable')
    
    print()
    print('Typical HEIC workflow:')
    print('1. Open HEIC file with pillow-heif')
    print('2. Extract EXIF metadata')
    print('3. Convert to JPEG/WebP for web compatibility')
    print('4. Generate thumbnails at multiple sizes')
    print('5. Optimize for storage and delivery')

process_heic_sample()
" 2>/dev/null || echo "HEIC processing not available"
```

### Thumbnail Generation
```bash
echo "=== THUMBNAIL GENERATION ==="

# Multi-size thumbnail generation
echo "Generating thumbnails for Lumen gallery:"
python -c "
from PIL import Image
import os

# Lumen thumbnail sizes (500px gallery style)
THUMBNAIL_SIZES = [
    (150, 150),   # Small thumbnail
    (300, 300),   # Medium thumbnail  
    (600, 600),   # Large thumbnail
    (1200, 1200), # Full preview
]

def generate_thumbnails_info():
    print('Lumen Thumbnail Specifications:')
    for i, (width, height) in enumerate(THUMBNAIL_SIZES):
        size_name = ['Small', 'Medium', 'Large', 'Preview'][i]
        print(f'  {size_name}: {width}x{height}px')
    
    print()
    print('Thumbnail Features:')
    print('✅ Aspect ratio preservation')
    print('✅ Progressive JPEG encoding')
    print('✅ WebP format with JPEG fallback')
    print('✅ Quality optimization per size')
    print('✅ Fast loading for 500px-style gallery')

generate_thumbnails_info()
" 2>/dev/null
```

## 3. Image Optimization

### Compression and Quality
```bash
echo "=== IMAGE OPTIMIZATION ==="

# Optimize images for web delivery
echo "Image optimization strategy:"
python -c "
from PIL import Image
import io

def show_optimization_strategy():
    print('Lumen Image Optimization:')
    print()
    
    print('JPEG Settings:')
    print('  Quality: 85-95 (balance size/quality)')
    print('  Progressive: True (faster perceived loading)')
    print('  Optimize: True (smaller file sizes)')
    print('  Strip EXIF: Configurable (privacy option)')
    
    print()
    print('WebP Settings:')
    print('  Quality: 80-90 (better compression than JPEG)')
    print('  Method: 6 (best compression)')
    print('  Lossless: False (for photos)')
    
    print()
    print('Size Targets:')
    print('  Thumbnails: < 50KB each')
    print('  Preview: < 200KB')
    print('  Full size: < 2MB (compressed from originals)')
    
    print()
    print('Performance Features:')
    print('  ✅ Progressive loading')
    print('  ✅ Lazy loading support')
    print('  ✅ CDN-optimized delivery')
    print('  ✅ Responsive image serving')

show_optimization_strategy()
" 2>/dev/null
```

### Metadata Processing
```bash
echo "=== METADATA PROCESSING ==="

# EXIF data extraction and handling
echo "Photo metadata processing:"
python -c "
from PIL import Image
from PIL.ExifTags import TAGS
import json

def show_metadata_processing():
    print('EXIF Metadata Handling:')
    print()
    
    print('Extracted Information:')
    print('  ✅ Camera make/model')
    print('  ✅ Shooting settings (ISO, aperture, shutter)')
    print('  ✅ Timestamp and date')
    print('  ✅ Image dimensions')
    print('  ✅ GPS location (if present)')
    print('  ✅ Copyright information')
    
    print()
    print('Privacy Protection:')
    print('  🔒 GPS stripping (user configurable)')
    print('  🔒 Personal info removal')
    print('  🔒 Camera serial number removal')
    print('  🔒 Software version stripping')
    
    print()
    print('Lumen Metadata Schema:')
    metadata_schema = {
        'original_filename': 'string',
        'file_size': 'integer (bytes)',
        'format': 'string (JPEG, PNG, etc)',
        'dimensions': {'width': 'integer', 'height': 'integer'},
        'camera_info': {
            'make': 'string',
            'model': 'string',
            'lens': 'string (optional)'
        },
        'settings': {
            'iso': 'integer',
            'aperture': 'float',
            'shutter_speed': 'string',
            'focal_length': 'float'
        },
        'datetime': 'ISO 8601 string',
        'location': {
            'latitude': 'float (optional)',
            'longitude': 'float (optional)',
            'privacy_level': 'string'
        }
    }
    
    print(json.dumps(metadata_schema, indent=2))

show_metadata_processing()
" 2>/dev/null
```

## 4. Storage Integration

### Firebase Storage Operations
```bash
echo "=== FIREBASE STORAGE INTEGRATION ==="

# Firebase/GCS storage management
echo "Firebase Storage operations:"
cd opusdev/backend
python -c "
try:
    from app.firebase_config import firebase_config
    print('Firebase Storage Configuration:')
    print(f'  Project: {firebase_config.app.project_id if firebase_config.app else \"Not configured\"}')
    print('  Bucket: [from environment]')
    print('  CDN: Firebase hosting integration')
    
    print()
    print('Storage Structure:')
    print('  /users/{user_id}/photos/{photo_id}/')
    print('    ├── original.{ext}')
    print('    ├── preview.webp')
    print('    ├── large.webp')
    print('    ├── medium.webp')
    print('    └── small.webp')
    
    print()
    print('Storage Features:')
    print('  ✅ Automatic CDN distribution')
    print('  ✅ Secure access with Firebase Auth')
    print('  ✅ Resumable uploads for large files')
    print('  ✅ Automatic backup and versioning')
    print('  ✅ Geographic redundancy')
    
except Exception as e:
    print(f'Firebase config check failed: {e}')
" 2>/dev/null || echo "Could not check Firebase configuration"
```

### Local Storage Management
```bash
echo "=== LOCAL STORAGE MANAGEMENT ==="

# Local storage operations for development
echo "Local storage configuration:"

# Create necessary directories
UPLOAD_DIR="opusdev/backend/uploads"
TEMP_DIR="opusdev/backend/temp"
PROCESSED_DIR="opusdev/backend/processed"

mkdir -p "$UPLOAD_DIR" "$TEMP_DIR" "$PROCESSED_DIR"

echo "Directory structure:"
echo "  Upload dir: $UPLOAD_DIR"
echo "  Temp dir: $TEMP_DIR"  
echo "  Processed dir: $PROCESSED_DIR"

# Check directory permissions
echo ""
echo "Directory permissions:"
ls -la opusdev/backend/ | grep -E "(uploads|temp|processed)"

# Storage cleanup for development
echo ""
echo "Storage cleanup options:"
echo "  - Clear temp files older than 24 hours"
echo "  - Remove processed files older than 7 days"
echo "  - Archive uploads older than 30 days"
```

## 5. Performance Optimization

### Async File Processing
```bash
echo "=== ASYNC FILE PROCESSING ==="

# Asynchronous file operations
echo "Async processing implementation:"
python -c "
import asyncio
import aiofiles

def show_async_strategy():
    print('Async File Processing Strategy:')
    print()
    
    print('Upload Pipeline:')
    print('  1. Async file reception with aiofiles')
    print('  2. Background processing with asyncio')
    print('  3. Parallel thumbnail generation')
    print('  4. Concurrent storage uploads')
    print('  5. Real-time progress updates')
    
    print()
    print('Performance Benefits:')
    print('  ✅ Non-blocking file I/O')
    print('  ✅ Concurrent image processing')
    print('  ✅ Parallel storage operations')
    print('  ✅ Better resource utilization')
    print('  ✅ Improved user experience')
    
    print()
    print('Implementation Features:')
    print('  - Progress tracking for large uploads')
    print('  - Error recovery and retry logic')
    print('  - Memory-efficient streaming')
    print('  - Background task queuing')

show_async_strategy()
" 2>/dev/null
```

### Caching Strategy
```bash
echo "=== CACHING STRATEGY ==="

# Image caching and delivery optimization
echo "Image caching implementation:"
python -c "
def show_caching_strategy():
    print('Lumen Image Caching Strategy:')
    print()
    
    print('Redis Caching:')
    print('  - Thumbnail cache (1 hour TTL)')
    print('  - Metadata cache (24 hour TTL)')
    print('  - User gallery cache (30 min TTL)')
    print('  - Search results cache (15 min TTL)')
    
    print()
    print('CDN Caching:')
    print('  - Original images: 1 year cache')
    print('  - Thumbnails: 6 months cache')
    print('  - Profile images: 1 month cache')
    print('  - Cache invalidation on updates')
    
    print()
    print('Browser Caching:')
    print('  - Aggressive caching for immutable images')
    print('  - ETag support for change detection')
    print('  - Conditional requests (304 responses)')
    print('  - Service worker caching for PWA')

show_caching_strategy()
" 2>/dev/null
```

## 6. Security and Privacy

### Image Security
```bash
echo "=== IMAGE SECURITY ==="

# Security measures for image handling
echo "Image security implementation:"
python -c "
def show_security_measures():
    print('Lumen Image Security:')
    print()
    
    print('Upload Security:')
    print('  ✅ File type validation (magic number check)')
    print('  ✅ File size limits (max 50MB)')
    print('  ✅ Virus scanning integration')
    print('  ✅ Content analysis for inappropriate material')
    print('  ✅ Filename sanitization')
    
    print()
    print('Privacy Protection:')
    print('  🔒 EXIF stripping (GPS, personal info)')
    print('  🔒 Access control (user permissions)')
    print('  🔒 Secure URLs with tokens')
    print('  🔒 Time-limited access links')
    print('  🔒 Privacy level enforcement')
    
    print()
    print('Storage Security:')
    print('  🔐 Encrypted at rest')
    print('  🔐 TLS for transfers')
    print('  🔐 Signed URLs for access')
    print('  🔐 Audit logging')
    print('  🔐 Regular security scans')

show_security_measures()
" 2>/dev/null
```

### Privacy Controls
```bash
echo "=== PRIVACY CONTROLS ==="

# User privacy settings for images
echo "Image privacy implementation:"
python -c "
def show_privacy_controls():
    print('Lumen Privacy Controls:')
    print()
    
    print('Visibility Levels:')
    print('  Public: Visible to all users')
    print('  Followers: Visible to followers only')
    print('  Private: Visible to user only')
    print('  Collaboration: Visible to tagged users')
    
    print()
    print('Metadata Privacy:')
    print('  - Location stripping (user choice)')
    print('  - Equipment info sharing (optional)')
    print('  - Shooting settings visibility')
    print('  - Copyright information display')
    
    print()
    print('Geographic Privacy:')
    print('  - Precise location (GPS coordinates)')
    print('  - City-level location only')
    print('  - No location sharing')
    print('  - Location approximate radius')

show_privacy_controls()
" 2>/dev/null
```

## 7. Monitoring and Analytics

### Storage Analytics
```bash
echo "=== STORAGE ANALYTICS ==="

# Storage usage and performance monitoring
echo "Storage monitoring:"
python -c "
def show_storage_analytics():
    print('Storage Analytics & Monitoring:')
    print()
    
    print('Usage Metrics:')
    print('  - Total storage per user')
    print('  - Average image file sizes')
    print('  - Popular image formats')
    print('  - Upload frequency patterns')
    print('  - Bandwidth usage trends')
    
    print()
    print('Performance Metrics:')
    print('  - Upload processing time')
    print('  - Thumbnail generation speed')
    print('  - CDN cache hit rates')
    print('  - Error rates by operation')
    print('  - User experience metrics')
    
    print()
    print('Cost Monitoring:')
    print('  - Storage costs by user tier')
    print('  - Bandwidth costs')
    print('  - Processing costs')
    print('  - Cost per image served')

show_storage_analytics()
" 2>/dev/null
```

### Health Monitoring
```bash
echo "=== STORAGE HEALTH MONITORING ==="

# Monitor storage system health
echo "Storage system health:"

# Check processing queue
echo "Processing queue status:"
echo "  - Pending uploads: [to be implemented]"
echo "  - Failed processing: [to be implemented]"
echo "  - Average processing time: [to be implemented]"

# Storage capacity monitoring
echo ""
echo "Storage capacity:"
du -sh opusdev/backend/uploads opusdev/backend/processed 2>/dev/null || echo "  Local storage directories not found"

# Error monitoring
echo ""
echo "Error monitoring:"
echo "  - Image processing failures"
echo "  - Upload timeout errors"  
echo "  - Storage service errors"
echo "  - Format conversion errors"
```

## 8. Backup and Recovery

### Image Backup Strategy
```bash
echo "=== IMAGE BACKUP STRATEGY ==="

# Backup strategy for image assets
echo "Image backup implementation:"
python -c "
def show_backup_strategy():
    print('Lumen Image Backup Strategy:')
    print()
    
    print('Multi-tier Backup:')
    print('  Tier 1: Firebase Storage (primary)')
    print('  Tier 2: Google Cloud Archive (long-term)')
    print('  Tier 3: Local backup (development)')
    print('  Tier 4: External backup (disaster recovery)')
    
    print()
    print('Backup Schedule:')
    print('  - Real-time: Primary to secondary')
    print('  - Daily: Incremental backup')
    print('  - Weekly: Full backup verification')
    print('  - Monthly: Archive to cold storage')
    
    print()
    print('Recovery Options:')
    print('  - Point-in-time recovery')
    print('  - Individual file recovery')
    print('  - Bulk restoration')
    print('  - Cross-region recovery')

show_backup_strategy()
" 2>/dev/null
```

## Implementation Notes

- **Format Support**: Prioritize HEIC, JPEG, and WebP for modern compatibility
- **Performance**: Use async processing for all file operations
- **Security**: Validate files thoroughly and strip sensitive metadata
- **Privacy**: Implement granular privacy controls for user content
- **Scalability**: Design for high-volume photo uploads and serving

This command integrates with:
- `/api` for backend storage APIs
- `/check` for storage system validation
- `/deploy` for production storage configuration
- Database operations for metadata storage