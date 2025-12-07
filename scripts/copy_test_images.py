#!/usr/bin/env python3
"""
Copy test images to correct storage structure for existing photo records
"""

import os
import sys
import random
import shutil
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def main():
    # Load environment
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL not found in .env")
        return
    
    # Storage paths
    storage_base = Path(os.getenv('STORAGE_BASE_PATH', '/home/cdc/lumen-dev-storage'))
    images_dir = Path(__file__).parent.parent / 'docs' / 'images-test'
    
    print(f"Storage base: {storage_base}")
    print(f"Test images: {images_dir}")
    
    # Get test images
    test_images = list(images_dir.glob('*.jpg'))
    if not test_images:
        print("No test images found!")
        return
    
    print(f"Found {len(test_images)} test images")
    
    # Connect to database
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        # Get all photo records
        result = conn.execute(text('SELECT id, user_id, title FROM photos'))
        photos = result.fetchall()
        
        print(f"Found {len(photos)} photo records in database")
        
        for i, (photo_id, user_id, title) in enumerate(photos):
            # Pick a random test image
            test_image = random.choice(test_images)
            
            print(f"Processing {i+1}/{len(photos)}: {title}")
            print(f"  Photo ID: {photo_id}")
            print(f"  User ID: {user_id}")
            print(f"  Source: {test_image.name}")
            
            # Create directories and copy to all sizes
            sizes = ['original', 'large', 'medium', 'small', 'thumb']
            
            for size in sizes:
                # Create user directory
                user_dir = storage_base / 'images' / size / user_id
                user_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy image with photo_id as filename
                dest_file = user_dir / f"{photo_id}.jpg"
                shutil.copy2(test_image, dest_file)
                
            print(f"  ✓ Copied to all {len(sizes)} size directories")
    
    print(f"\n✓ Successfully populated {len(photos)} photo records with test images")
    print("Images are now available at the storage paths the system expects!")

if __name__ == '__main__':
    main()