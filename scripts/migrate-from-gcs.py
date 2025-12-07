#!/usr/bin/env python3
"""
Migration script to transfer images from Google Cloud Storage to EDIS local storage.

This script downloads all existing images from GCS and processes them through
the new optimized storage system to create all required variants.
"""

import asyncio
import argparse
import json
import logging
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import uuid

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

try:
    from google.cloud import storage as gcs
    HAS_GCS = True
except ImportError:
    HAS_GCS = False
    print("Warning: google-cloud-storage not available. Run: pip install google-cloud-storage")

import psycopg2
from psycopg2.extras import RealDictCursor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GCSMigrator:
    """Handles migration from Google Cloud Storage to local storage"""
    
    def __init__(self, 
                 gcs_bucket_name: str,
                 local_storage_path: str,
                 db_config: Dict[str, str],
                 batch_size: int = 50):
        """
        Initialize migrator.
        
        Args:
            gcs_bucket_name: GCS bucket name
            local_storage_path: Local storage base path
            db_config: Database connection configuration
            batch_size: Number of images to process in parallel
        """
        self.gcs_bucket_name = gcs_bucket_name
        self.local_storage_path = Path(local_storage_path)
        self.db_config = db_config
        self.batch_size = batch_size
        
        # Statistics
        self.stats = {
            'total_images': 0,
            'processed': 0,
            'errors': 0,
            'skipped': 0,
            'bytes_transferred': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Initialize GCS client
        if HAS_GCS:
            self.gcs_client = gcs.Client()
            self.bucket = self.gcs_client.bucket(gcs_bucket_name)
        else:
            logger.error("Google Cloud Storage client not available")
            raise ImportError("google-cloud-storage package required")

    async def migrate_all_images(self, dry_run: bool = False) -> Dict:
        """
        Migrate all images from GCS to local storage.
        
        Args:
            dry_run: If True, only scan and report what would be migrated
            
        Returns:
            Migration statistics
        """
        logger.info(f"Starting GCS to local storage migration (dry_run={dry_run})")
        self.stats['start_time'] = datetime.utcnow()
        
        try:
            # Get list of photos from database
            photos = await self._get_photos_from_db()
            self.stats['total_images'] = len(photos)
            
            logger.info(f"Found {len(photos)} photos in database")
            
            if dry_run:
                return await self._dry_run_analysis(photos)
            
            # Process photos in batches
            for i in range(0, len(photos), self.batch_size):
                batch = photos[i:i + self.batch_size]
                logger.info(f"Processing batch {i//self.batch_size + 1}: photos {i+1}-{min(i+self.batch_size, len(photos))}")
                
                await self._process_batch(batch)
                
                # Progress report
                progress = (i + len(batch)) / len(photos) * 100
                logger.info(f"Progress: {progress:.1f}% ({i + len(batch)}/{len(photos)} photos)")
            
            self.stats['end_time'] = datetime.utcnow()
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            
            logger.info("Migration completed!")
            logger.info(f"Total time: {duration:.1f} seconds")
            logger.info(f"Processed: {self.stats['processed']}")
            logger.info(f"Errors: {self.stats['errors']}")
            logger.info(f"Skipped: {self.stats['skipped']}")
            logger.info(f"Data transferred: {self.stats['bytes_transferred'] / 1024 / 1024:.1f} MB")
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise

    async def _get_photos_from_db(self) -> List[Dict]:
        """Get all photos from database"""
        
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("""
                SELECT p.id, p.user_id, p.title, p.upload_date,
                       u.display_name
                FROM photos p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.upload_date DESC
            """)
            
            photos = []
            for row in cursor.fetchall():
                photos.append(dict(row))
            
            return photos
            
        finally:
            cursor.close()
            conn.close()

    async def _dry_run_analysis(self, photos: List[Dict]) -> Dict:
        """Analyze what would be migrated without actually doing it"""
        
        logger.info("Running dry-run analysis...")
        
        analysis = {
            'photos_to_migrate': 0,
            'photos_already_exist': 0,
            'photos_missing_in_gcs': 0,
            'estimated_storage_needed': 0,
            'gcs_files_found': 0,
            'file_size_distribution': {},
            'user_distribution': {}
        }
        
        for photo in photos:
            user_id = photo['user_id']
            photo_id = str(photo['id'])
            
            # Check if files exist in GCS
            original_exists, original_size = await self._check_gcs_file_exists(user_id, photo_id, 'original')
            thumb_exists, thumb_size = await self._check_gcs_file_exists(user_id, photo_id, 'thumbnail')
            
            if original_exists:
                analysis['gcs_files_found'] += 1
                analysis['estimated_storage_needed'] += original_size
                
                # Check if already exists locally
                local_exists = await self._check_local_file_exists(user_id, photo_id)
                
                if local_exists:
                    analysis['photos_already_exist'] += 1
                else:
                    analysis['photos_to_migrate'] += 1
                
                # Size distribution
                size_category = self._get_size_category(original_size)
                analysis['file_size_distribution'][size_category] = analysis['file_size_distribution'].get(size_category, 0) + 1
                
                # User distribution
                analysis['user_distribution'][user_id] = analysis['user_distribution'].get(user_id, 0) + 1
                
            else:
                analysis['photos_missing_in_gcs'] += 1
        
        # Log analysis results
        logger.info("=== DRY RUN ANALYSIS ===")
        logger.info(f"Photos to migrate: {analysis['photos_to_migrate']}")
        logger.info(f"Photos already exist locally: {analysis['photos_already_exist']}")
        logger.info(f"Photos missing in GCS: {analysis['photos_missing_in_gcs']}")
        logger.info(f"Estimated storage needed: {analysis['estimated_storage_needed'] / 1024 / 1024:.1f} MB")
        logger.info(f"File size distribution: {analysis['file_size_distribution']}")
        logger.info(f"Users with photos: {len(analysis['user_distribution'])}")
        
        return analysis

    async def _process_batch(self, photos: List[Dict]):
        """Process a batch of photos"""
        
        tasks = []
        for photo in photos:
            task = asyncio.create_task(self._migrate_single_photo(photo))
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing photo {photos[i]['id']}: {result}")
                self.stats['errors'] += 1
            elif result:
                self.stats['processed'] += 1
            else:
                self.stats['skipped'] += 1

    async def _migrate_single_photo(self, photo: Dict) -> bool:
        """
        Migrate a single photo from GCS to local storage.
        
        Returns:
            True if successfully migrated, False if skipped
        """
        user_id = photo['user_id']
        photo_id = str(photo['id'])
        
        try:
            # Check if already exists locally
            if await self._check_local_file_exists(user_id, photo_id):
                logger.debug(f"Photo {photo_id} already exists locally, skipping")
                return False
            
            # Download original image from GCS
            original_blob_name = f"photos/{user_id}/{photo_id}.jpg"
            original_data = await self._download_from_gcs(original_blob_name)
            
            if not original_data:
                # Try different extensions
                for ext in ['jpeg', 'png', 'webp']:
                    original_blob_name = f"photos/{user_id}/{photo_id}.{ext}"
                    original_data = await self._download_from_gcs(original_blob_name)
                    if original_data:
                        break
            
            if not original_data:
                logger.warning(f"Original image not found in GCS for photo {photo_id}")
                return False
            
            # Process through local storage system
            await self._process_with_local_storage(
                original_data, 
                user_id, 
                photo_id, 
                f"{photo_id}.jpg"
            )
            
            self.stats['bytes_transferred'] += len(original_data)
            logger.info(f"Migrated photo {photo_id} ({len(original_data)} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate photo {photo_id}: {e}")
            raise

    async def _check_gcs_file_exists(self, user_id: str, photo_id: str, file_type: str) -> Tuple[bool, int]:
        """Check if file exists in GCS and return size"""
        
        if file_type == 'original':
            blob_name = f"photos/{user_id}/{photo_id}.jpg"
        else:  # thumbnail
            blob_name = f"thumbnails/{user_id}/{photo_id}_thumb.jpg"
        
        try:
            blob = self.bucket.blob(blob_name)
            if blob.exists():
                blob.reload()  # Load metadata
                return True, blob.size
            return False, 0
        except Exception:
            return False, 0

    async def _check_local_file_exists(self, user_id: str, photo_id: str) -> bool:
        """Check if photo exists in local storage"""
        
        # Check if any variant exists
        for size in ['thumb', 'small', 'medium', 'large', 'original']:
            size_dir = self.local_storage_path / 'images' / size / user_id
            for ext in ['jpg', 'jpeg', 'webp', 'png']:
                file_path = size_dir / f"{photo_id}.{ext}"
                if file_path.exists():
                    return True
        
        return False

    async def _download_from_gcs(self, blob_name: str) -> Optional[bytes]:
        """Download file from GCS"""
        
        try:
            blob = self.bucket.blob(blob_name)
            if not blob.exists():
                return None
            
            # Download in memory
            data = blob.download_as_bytes()
            return data
            
        except Exception as e:
            logger.warning(f"Failed to download {blob_name}: {e}")
            return None

    async def _process_with_local_storage(self, 
                                        image_data: bytes, 
                                        user_id: str, 
                                        photo_id: str, 
                                        filename: str):
        """Process image through local storage system"""
        
        # Import storage classes
        from app.storage.local_storage import LocalStorageService
        from app.storage.image_processor import ProcessingConfig
        
        # Initialize storage service
        storage = LocalStorageService(
            base_path=str(self.local_storage_path),
            cache_ttl_days=7,
            max_storage_gb=40.0
        )
        
        try:
            # Store the image (this will create all variants)
            stored_image = await storage.store_image(
                file_content=image_data,
                filename=filename,
                user_id=user_id,
                photo_id=photo_id,
                content_type='image/jpeg'  # Default to JPEG
            )
            
            logger.debug(f"Created {len(stored_image.variants)} variants for {photo_id}")
            
        except Exception as e:
            logger.error(f"Failed to process {photo_id} with local storage: {e}")
            raise

    def _get_size_category(self, size_bytes: int) -> str:
        """Categorize file size"""
        
        mb = size_bytes / 1024 / 1024
        
        if mb < 1:
            return "< 1MB"
        elif mb < 5:
            return "1-5MB"
        elif mb < 10:
            return "5-10MB"
        elif mb < 20:
            return "10-20MB"
        else:
            return "> 20MB"


async def main():
    """Main migration function"""
    
    parser = argparse.ArgumentParser(description='Migrate images from GCS to local storage')
    parser.add_argument('--gcs-bucket', required=True, help='GCS bucket name')
    parser.add_argument('--local-path', default='/opt/lumen/storage', help='Local storage path')
    parser.add_argument('--db-host', default='localhost', help='Database host')
    parser.add_argument('--db-port', default='5432', help='Database port')
    parser.add_argument('--db-name', required=True, help='Database name')
    parser.add_argument('--db-user', required=True, help='Database user')
    parser.add_argument('--db-password', required=True, help='Database password')
    parser.add_argument('--batch-size', type=int, default=50, help='Batch size for parallel processing')
    parser.add_argument('--dry-run', action='store_true', help='Only analyze what would be migrated')
    
    args = parser.parse_args()
    
    # Database configuration
    db_config = {
        'host': args.db_host,
        'port': args.db_port,
        'database': args.db_name,
        'user': args.db_user,
        'password': args.db_password
    }
    
    # Initialize migrator
    migrator = GCSMigrator(
        gcs_bucket_name=args.gcs_bucket,
        local_storage_path=args.local_path,
        db_config=db_config,
        batch_size=args.batch_size
    )
    
    # Run migration
    try:
        stats = await migrator.migrate_all_images(dry_run=args.dry_run)
        
        # Save stats to file
        stats_file = f"migration_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, 'w') as f:
            # Convert datetime objects to strings for JSON serialization
            json_stats = dict(stats)
            if json_stats.get('start_time'):
                json_stats['start_time'] = json_stats['start_time'].isoformat()
            if json_stats.get('end_time'):
                json_stats['end_time'] = json_stats['end_time'].isoformat()
            
            json.dump(json_stats, f, indent=2)
        
        logger.info(f"Migration statistics saved to {stats_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)