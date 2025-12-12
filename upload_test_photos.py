#!/usr/bin/env python3
"""
Upload test photos for Karl Tester user
"""

import requests
import os
from pathlib import Path

# Configuration
API_BASE_URL = "http://100.106.201.33:8080/api/v1"
TEMP_IMAGES_DIR = "/home/cdc/Storage/NVMe/projects/wasenet/temp-images"

# You'll need to get the actual auth token from the browser
# This is a placeholder - you'll need to provide the real token
AUTH_TOKEN = "REPLACE_WITH_ACTUAL_TOKEN"

def upload_photo(file_path, title, description, camera="", lens="", is_portfolio=False):
    """Upload a single photo to the Lumen API"""
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"📸 Uploading: {os.path.basename(file_path)}")
    
    # Prepare the multipart form data
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'image/jpeg')}
        
        data = {
            'title': title,
            'description': description,
            'is_portfolio': str(is_portfolio).lower(),
            'is_public': 'true',
        }
        
        if camera:
            data['camera'] = camera
        if lens:
            data['lens'] = lens
        
        headers = {
            'Authorization': f'Bearer {AUTH_TOKEN}'
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/photos/upload",
                files=files,
                data=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload successful! Photo ID: {result.get('id', 'unknown')}")
                return True
            else:
                print(f"❌ Upload failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Upload error: {str(e)}")
            return False

def main():
    """Upload 3 test photos for Karl Tester"""
    
    if AUTH_TOKEN == "REPLACE_WITH_ACTUAL_TOKEN":
        print("❌ Please replace AUTH_TOKEN with the actual token from Karl Tester's session")
        print("   You can get this from the browser's localStorage or developer tools")
        return
    
    # Define the photos to upload
    photos_to_upload = [
        {
            'file': 'CarlaB_S01_NEF5787_181221.jpg',
            'title': 'Portrait Session with Carla B',
            'description': 'Professional portrait session featuring natural lighting and elegant composition. Part of Series 01 from December 2021.',
            'camera': 'Nikon D850',
            'lens': 'Nikkor 85mm f/1.4',
            'is_portfolio': True
        },
        {
            'file': 'CharlesK_Barb_S01_DIL3894-5.jpg', 
            'title': 'Creative Portrait - Barb',
            'description': 'Artistic portrait session with dramatic lighting. Captured during Series 01 collaboration with Charles K.',
            'camera': 'Canon EOS R5',
            'lens': 'Canon RF 70-200mm f/2.8',
            'is_portfolio': True
        },
        {
            'file': 'CharlesK_Mari_S07_G0030017.jpg',
            'title': 'Studio Session with Mari',
            'description': 'Professional studio portrait from Series 07. Clean, minimalist styling with expert lighting setup.',
            'camera': 'Sony A7R IV', 
            'lens': 'Sony FE 85mm f/1.4 GM',
            'is_portfolio': False
        }
    ]
    
    print(f"🚀 Starting upload of {len(photos_to_upload)} photos for Karl Tester")
    print(f"📁 Source directory: {TEMP_IMAGES_DIR}")
    print()
    
    successful_uploads = 0
    
    for i, photo in enumerate(photos_to_upload, 1):
        file_path = os.path.join(TEMP_IMAGES_DIR, photo['file'])
        
        print(f"[{i}/{len(photos_to_upload)}] {photo['title']}")
        
        success = upload_photo(
            file_path=file_path,
            title=photo['title'],
            description=photo['description'],
            camera=photo['camera'],
            lens=photo['lens'],
            is_portfolio=photo['is_portfolio']
        )
        
        if success:
            successful_uploads += 1
        
        print()
    
    print(f"📊 Upload Summary:")
    print(f"   ✅ Successful: {successful_uploads}")
    print(f"   ❌ Failed: {len(photos_to_upload) - successful_uploads}")
    print(f"   📈 Success Rate: {(successful_uploads/len(photos_to_upload)*100):.1f}%")

if __name__ == "__main__":
    main()