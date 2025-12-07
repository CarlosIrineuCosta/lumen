#!/usr/bin/env python3
"""
Test data creation tool for Lumen platform

This script creates test users and photos for diagnostic purposes.
Useful when the database is empty and you need sample data to test
the photo display pipeline.

Usage:
    python tests/tools/create_test_data.py [--users-only] [--photos-only]
"""

import os
import sys
import argparse
import uuid
import random
from datetime import datetime
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def create_test_users():
    """Create test users in the database"""
    print("🔧 Creating test users...")
    
    try:
        from app.database.connection import SessionLocal
        from app.models.user import User
        
        # Sample users with Firebase-style UIDs
        test_users = [
            {
                'id': '9pGzwsVBRMaSxMOZ6QNTJJjnl1b2',  # 28-char Firebase UID
                'email': 'testphotographer@example.com',
                'handle': 'testphotographer',
                'display_name': 'Test Photographer',
                'bio': 'Test photographer for diagnostic purposes',
                'user_type': 'photographer'
            },
            {
                'id': 'AbCd1234EfGh5678IjKl9012MnOp',  # 28-char Firebase UID
                'email': 'testmodel@example.com', 
                'handle': 'testmodel',
                'display_name': 'Test Model',
                'bio': 'Test model for diagnostic purposes',
                'user_type': 'model'
            }
        ]
        
        db = SessionLocal()
        created_count = 0
        
        for user_data in test_users:
            # Check if user already exists
            existing = db.query(User).filter(User.id == user_data['id']).first()
            
            if existing:
                print(f"   User {user_data['display_name']} already exists")
                continue
            
            # Create new user
            user = User(
                id=user_data['id'],
                email=user_data['email'],
                handle=user_data['handle'], 
                display_name=user_data['display_name'],
                bio=user_data['bio'],
                profile_data={
                    'user_type': user_data['user_type'],
                    'city': 'Test City',
                    'experience_level': 'intermediate'
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(user)
            created_count += 1
            print(f"   ✅ Created {user_data['display_name']}")
        
        db.commit()
        db.close()
        
        print(f"✅ Created {created_count} test users")
        return created_count
        
    except Exception as e:
        print(f"❌ Failed to create test users: {e}")
        return 0

def create_test_photos():
    """Create test photo records in the database"""
    print("🔧 Creating test photo records...")
    
    try:
        from app.database.connection import SessionLocal
        from app.models.photo import Photo
        from app.models.user import User
        
        db = SessionLocal()
        
        # Get existing users
        users = db.query(User).limit(5).all()
        if not users:
            print("❌ No users found - create users first")
            db.close()
            return 0
        
        created_count = 0
        
        for i, user in enumerate(users):
            # Create 1-2 photos per user
            for j in range(random.randint(1, 2)):
                photo_id = uuid.uuid4()
                
                photo = Photo(
                    id=photo_id,
                    user_id=user.id,  # This is the Firebase UID
                    title=f"Test Photo {i+1}-{j+1}",
                    description=f"Test photo for diagnostic purposes by {user.display_name}",
                    user_tags=['test', 'diagnostic'],
                    is_public=True,
                    is_portfolio=random.choice([True, False]),
                    content_rating='general',
                    model_release_status='none',
                    camera_data={
                        'camera': 'Test Camera',
                        'lens': 'Test Lens 50mm',
                        'settings': 'ISO 400 | f/2.8 | 1/125s'
                    },
                    upload_date=datetime.utcnow()
                )
                
                db.add(photo)
                created_count += 1
                print(f"   ✅ Created photo: {photo.title}")
        
        db.commit()
        db.close()
        
        print(f"✅ Created {created_count} test photos")
        return created_count
        
    except Exception as e:
        print(f"❌ Failed to create test photos: {e}")
        return 0

def create_test_gcs_files():
    """Create placeholder files in GCS for test photos"""
    print("🔧 Creating test files in Google Cloud Storage...")
    
    try:
        from google.cloud import storage
        from app.database.connection import SessionLocal
        from app.models.photo import Photo
        
        # Simple test image content (1x1 pixel PNG)
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xddܦ\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        
        client = storage.Client()
        bucket_name = 'lumen-photos-20250731'
        bucket = client.bucket(bucket_name)
        
        # Get test photos from database
        db = SessionLocal()
        photos = db.query(Photo).limit(10).all()
        db.close()
        
        if not photos:
            print("❌ No photos found in database")
            return 0
        
        created_count = 0
        
        for photo in photos:
            # Create image file
            image_path = f"photos/{photo.user_id}/{photo.id}.jpg"
            image_blob = bucket.blob(image_path)
            
            if not image_blob.exists():
                image_blob.upload_from_string(test_image_data, content_type='image/jpeg')
                print(f"   ✅ Created {image_path}")
                created_count += 1
            else:
                print(f"   File already exists: {image_path}")
            
            # Create thumbnail file
            thumb_path = f"thumbnails/{photo.user_id}/{photo.id}_thumb.jpg"
            thumb_blob = bucket.blob(thumb_path)
            
            if not thumb_blob.exists():
                thumb_blob.upload_from_string(test_image_data, content_type='image/jpeg')
                print(f"   ✅ Created {thumb_path}")
                created_count += 1
            else:
                print(f"   Thumbnail already exists: {thumb_path}")
        
        print(f"✅ Created {created_count} test files in GCS")
        return created_count
        
    except Exception as e:
        print(f"❌ Failed to create GCS files: {e}")
        return 0

def main():
    parser = argparse.ArgumentParser(description="Create test data for Lumen platform")
    parser.add_argument("--users-only", action="store_true", help="Create only test users")
    parser.add_argument("--photos-only", action="store_true", help="Create only test photos")
    parser.add_argument("--no-gcs", action="store_true", help="Skip GCS file creation")
    
    args = parser.parse_args()
    
    print("🏗️ LUMEN TEST DATA CREATION")
    print("=" * 50)
    print("Creating test data for diagnostic purposes\n")
    
    os.chdir(backend_path)
    
    total_created = 0
    
    if not args.photos_only:
        users_created = create_test_users()
        total_created += users_created
        print()
    
    if not args.users_only:
        photos_created = create_test_photos()
        total_created += photos_created
        print()
        
        if not args.no_gcs:
            gcs_files_created = create_test_gcs_files()
            total_created += gcs_files_created
            print()
    
    print("=" * 50)
    print("TEST DATA CREATION SUMMARY")
    print("=" * 50)
    
    if total_created > 0:
        print(f"✅ Successfully created {total_created} items")
        print("\nNext steps:")
        print("1. Refresh your browser to see the new photos")
        print("2. Run system health check:")
        print("   python tests/tools/system_health_check.py")
        print("3. Run full diagnostics if needed:")
        print("   python tests/tools/run_diagnostics.py")
    else:
        print("❌ No items were created")
        print("Check the error messages above for issues")
    
    return total_created > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)