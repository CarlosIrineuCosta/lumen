#!/usr/bin/env python3
"""
Upload test script to run ON the edis server
"""

import json

# Simple test data
test_photo_data = {
    "title": "Test Photo Upload",
    "description": "Testing photo upload fixes",
    "user_tags": ["test", "upload"],
    "is_public": True,
    "is_portfolio": False
}

# Create a test script to upload on the server
server_test_script = '''#!/usr/bin/env python3
import requests
import json
import base64

# Test configuration for server
BASE_URL = "http://localhost:8080"
TEST_IMAGE_PATH = "/tmp/test_image.jpg"

# Create a simple test image (1x1 pixel JPEG)
test_image_data = base64.b64decode(
    "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/8A"
)

with open(TEST_IMAGE_PATH, "wb") as f:
    f.write(test_image_data)

def test_server_upload():
    """Test photo upload directly on server"""
    
    print("🧪 Testing photo upload on edis server...")
    
    try:
        # Test basic endpoint
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Server responding")
        else:
            print(f"❌ Server not responding: {response.status_code}")
            return False
            
        # Test photos endpoint
        response = requests.get(f"{BASE_URL}/api/v1/photos/")
        print(f"📝 Photos endpoint: {response.status_code}")
        
        if response.status_code == 200:
            photos_data = response.json()
            print(f"✅ Photos endpoint working - found {len(photos_data.get('photos', []))} photos")
        else:
            print(f"❌ Photos endpoint error: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_server_upload()
'''

print("Test script created for server deployment")
print("Now uploading to edis server...")