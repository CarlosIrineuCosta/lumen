#!/usr/bin/env python3
"""
Distribute test images from docs/images-test/ among existing users
and update the photos table with proper image references
"""

import os
import sys
import random
import shutil
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from uuid import uuid4
from datetime import datetime

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def main():
    # Load environment
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL not found in .env")
        return
    
    engine = create_engine(db_url)
    
    # Get current users
    with engine.connect() as conn:
        result = conn.execute(text('SELECT id, display_name FROM users'))
        users = result.fetchall()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  {user[1]} ({user[0]})")
    
    # Get image files
    images_dir = Path(__file__).parent.parent / 'docs' / 'images-test'
    image_files = list(images_dir.glob('*.jpg'))
    print(f"\nFound {len(image_files)} images in {images_dir}")
    
    if not image_files:
        print("No images found!")
        return
    
    # Create uploads directory structure if it doesn't exist
    uploads_dir = Path(__file__).parent.parent / 'backend' / 'uploads'
    uploads_dir.mkdir(exist_ok=True)
    
    # Clear existing photos first
    with engine.connect() as conn:
        conn.execute(text('DELETE FROM photos'))
        conn.commit()
        print("Cleared existing photos")
    
    # Distribute images among users
    photos_to_insert = []
    
    for i, image_file in enumerate(image_files):
        # Pick random user
        user = random.choice(users)
        user_id = user[0]
        
        # Generate new photo ID
        photo_id = str(uuid4())
        
        # Create unique filename 
        filename = f"{photo_id}_{image_file.name}"
        
        # Copy image to uploads directory
        dest_path = uploads_dir / filename
        shutil.copy2(image_file, dest_path)
        
        # Create photo record
        photo_data = {
            'id': photo_id,
            'user_id': user_id,
            'title': f'Photo {i+1} by {user[1]}',
            'description': f'Test photo from {image_file.stem}',
            'image_url': f'/uploads/{filename}',
            'thumbnail_url': f'/uploads/{filename}',  # Same for now
            'city_id': 1,  # Default city
            'location_name': 'Test Location',
            'is_public': True,
            'is_portfolio': random.choice([True, False]),
            'status': 'published',
            'upload_date': datetime.now(),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        photos_to_insert.append(photo_data)
        print(f"  {image_file.name} -> {user[1]} ({user_id[:8]}...)")
    
    # Insert all photos
    with engine.connect() as conn:
        for photo in photos_to_insert:
            conn.execute(text('''
                INSERT INTO photos (
                    id, user_id, title, description, image_url, thumbnail_url,
                    city_id, location_name, is_public, is_portfolio, status,
                    upload_date, created_at, updated_at
                ) VALUES (
                    :id, :user_id, :title, :description, :image_url, :thumbnail_url,
                    :city_id, :location_name, :is_public, :is_portfolio, :status,
                    :upload_date, :created_at, :updated_at
                )
            '''), photo)
        
        conn.commit()
        print(f"\nInserted {len(photos_to_insert)} photos into database")
    
    print(f"\nImages copied to: {uploads_dir}")
    print("Distribution complete!")

if __name__ == '__main__':
    main()