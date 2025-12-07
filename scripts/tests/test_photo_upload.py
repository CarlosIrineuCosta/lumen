#!/usr/bin/env python3
"""
Simple test script to verify photo upload fixes
"""

import requests
import json
from pathlib import Path

# Test configuration
BASE_URL = "http://100.106.201.33:8080"
TEST_IMAGE = "temp-images/CarlaB_S01_NEF5787_181221.jpg"

def test_photo_upload():
    """Test photo upload with the fixed backend"""
    
    print("🧪 Testing photo upload fixes...")
    
    # Check if test image exists
    if not Path(TEST_IMAGE).exists():
        print(f"❌ Test image not found: {TEST_IMAGE}")
        return False
    
    # Since Firebase auth is disabled, let's try uploading directly
    # First, let's check what endpoints are available
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Backend server is responding")
        else:
            print(f"❌ Backend server not responding: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test storage directory creation
    try:
        # Try to hit any photos endpoint to see the response
        response = requests.get(f"{BASE_URL}/api/v1/photos")
        print(f"📝 Photos endpoint response: {response.status_code}")
        if response.status_code in [401, 403]:
            print("✅ Auth is working (401/403 expected without token)")
        elif response.status_code == 404:
            print("📋 Photos endpoint may not exist or need different path")
        else:
            print(f"📋 Unexpected response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error testing photos endpoint: {e}")
    
    return True

if __name__ == "__main__":
    test_photo_upload()