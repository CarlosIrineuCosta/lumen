#!/usr/bin/env python3
"""
Simple test to check if we can generate working signed URLs for actual files
"""
from google.cloud import storage
from datetime import timedelta

# Known facts from our investigation:
# - Bucket: lumen-photos-20250731
# - Firebase UID: 9pGzwsVBRMaSxMOZ6QNTJJjnl1b2 (from gsutil ls)
# - Photo ID: c711a9ab-4689-4576-a511-7ce60cc214f3 (from API response)

def test_signed_url():
    print("=== TESTING SIGNED URL GENERATION ===")
    
    bucket_name = 'lumen-photos-20250731'
    firebase_uid = '9pGzwsVBRMaSxMOZ6QNTJJjnl1b2'
    photo_id = 'c711a9ab-4689-4576-a511-7ce60cc214f3'
    
    print(f"Bucket: {bucket_name}")
    print(f"Firebase UID: {firebase_uid}")
    print(f"Photo ID: {photo_id}")
    
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        
        # Test the exact path we know exists
        image_path = f"photos/{firebase_uid}/{photo_id}.jpg"
        print(f"Testing path: {image_path}")
        
        # Check if file exists
        blob = bucket.blob(image_path)
        exists = blob.exists()
        print(f"File exists: {exists}")
        
        if exists:
            # Generate signed URL
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=1),
                method="GET"
            )
            print(f"SUCCESS! Signed URL generated:")
            print(f"{signed_url}")
            return signed_url
        else:
            print("ERROR: File does not exist at expected path")
            return None
            
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def test_direct_public_url():
    """Test if we can access the file with a public URL (might not work due to permissions)"""
    bucket_name = 'lumen-photos-20250731'
    firebase_uid = '9pGzwsVBRMaSxMOZ6QNTJJjnl1b2'
    photo_id = 'c711a9ab-4689-4576-a511-7ce60cc214f3'
    
    public_url = f"https://storage.googleapis.com/{bucket_name}/photos/{firebase_uid}/{photo_id}.jpg"
    print(f"\nPublic URL (might be blocked by permissions):")
    print(f"{public_url}")
    return public_url

if __name__ == '__main__':
    signed_url = test_signed_url()
    public_url = test_direct_public_url()
    
    if signed_url:
        print(f"\n✅ SUCCESS: We can generate working signed URLs!")
        print(f"The issue is in how PhotoService passes Firebase UID vs database UUID")
    else:
        print(f"\n❌ FAILED: Either auth issue or path mismatch")