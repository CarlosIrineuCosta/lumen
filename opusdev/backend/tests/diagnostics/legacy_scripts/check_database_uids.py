#!/usr/bin/env python3
"""
Script to check Firebase UID formats in database vs GCS file paths
WARNING: This script is for diagnostic purposes only - DO NOT modify database!

MOVED FROM: /check_database_uids.py to organized test structure
"""
import os
import sys
sys.path.append('../../..')  # Updated path for new location

from app.database.connection import SessionLocal
from app.models.photo import Photo
from app.models.user import User
from sqlalchemy.orm import joinedload
from google.cloud import storage
import re

def check_database_uids():
    """Check what Firebase UIDs are stored in database"""
    print("=== DATABASE UID ANALYSIS ===")
    
    db = SessionLocal()
    try:
        # Check user UIDs
        users = db.query(User).limit(5).all()
        print(f"\n--- USERS TABLE ({len(users)} samples) ---")
        for user in users:
            uid_str = str(user.id)
            is_uuid = bool(re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', uid_str))
            print(f"ID: {uid_str[:20]}{'...' if len(uid_str) > 20 else ''}")
            print(f"  Length: {len(uid_str)}")
            print(f"  Format: {'UUID' if is_uuid else 'OTHER'}")
            print(f"  Display: {user.display_name}")
            print()
        
        # Check photo user_ids
        photos = db.query(Photo).options(joinedload(Photo.user)).limit(5).all()
        print(f"--- PHOTOS TABLE ({len(photos)} samples) ---")
        for photo in photos:
            uid_str = str(photo.user_id)
            is_uuid = bool(re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', uid_str))
            print(f"Photo ID: {photo.id}")
            print(f"User ID: {uid_str[:20]}{'...' if len(uid_str) > 20 else ''}")
            print(f"  Length: {len(uid_str)}")
            print(f"  Format: {'UUID' if is_uuid else 'OTHER'}")
            print(f"  Title: {photo.title}")
            print(f"  Expected GCS Path: photos/{uid_str}/{photo.id}.jpg")
            print()
            
    finally:
        db.close()

def check_gcs_file_paths():
    """Check what file paths actually exist in Google Cloud Storage"""
    print("=== GOOGLE CLOUD STORAGE ANALYSIS ===")
    
    try:
        client = storage.Client()
        bucket_name = os.getenv('GOOGLE_CLOUD_STORAGE_BUCKET', 'lumen-photos-20250731')  # Updated bucket name
        bucket = client.bucket(bucket_name)
        
        print(f"\nBucket: {bucket_name}")
        
        # List some files in photos/ directory
        photo_blobs = list(bucket.list_blobs(prefix='photos/', max_results=10))
        
        print(f"\n--- ACTUAL GCS FILE PATHS ({len(photo_blobs)} samples) ---")
        for blob in photo_blobs:
            path_parts = blob.name.split('/')
            if len(path_parts) >= 3:
                folder = path_parts[0]  # 'photos'
                uid_part = path_parts[1]  # Firebase UID
                filename = path_parts[2]  # photo file
                
                is_uuid = bool(re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', uid_part))
                
                print(f"Path: {blob.name}")
                print(f"  UID part: {uid_part[:20]}{'...' if len(uid_part) > 20 else ''}")
                print(f"  UID length: {len(uid_part)}")
                print(f"  UID format: {'UUID' if is_uuid else 'OTHER'}")
                print(f"  File: {filename}")
                print()
    
    except Exception as e:
        print(f"GCS Error: {e}")

if __name__ == '__main__':
    check_database_uids()
    check_gcs_file_paths()