#!/usr/bin/env python3
"""Test script to verify GCP setup for Lumen project"""

import os
from google.cloud import storage
from google.oauth2 import service_account
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_cloud_storage():
    """Test Cloud Storage access"""
    project_id = os.getenv("PROJECT_ID")
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    
    print(f"\n📸 Testing Cloud Storage access...")
    print(f"📦 Bucket: {bucket_name}")
    
    try:
        cred_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
        credentials = service_account.Credentials.from_service_account_file(cred_path)
        client = storage.Client(project=project_id, credentials=credentials)
        bucket = client.bucket(bucket_name)
        
        if bucket.exists():
            print(f"✅ Bucket '{bucket_name}' exists and is accessible")
            
            # Try to upload a test file
            blob = bucket.blob("test/setup_verification.txt")
            blob.upload_from_string("Lumen GCP setup verified!")
            print("✅ Successfully uploaded test file")
            
            # Clean up
            blob.delete()
            print("✅ Successfully deleted test file")
            return True
        else:
            print(f"❌ Bucket '{bucket_name}' not found")
            return False
            
    except Exception as e:
        print(f"❌ Cloud Storage Error: {e}")
        return False

def test_firebase():
    """Test Firebase configuration"""
    print(f"\n🔥 Testing Firebase configuration...")
    
    try:
        from app.firebase_config import firebase_config
        
        if firebase_config.app:
            print("✅ Firebase Admin SDK initialized successfully")
            
            # Test project ID
            project_id = os.getenv("FIREBASE_PROJECT_ID")
            print(f"✅ Firebase project ID: {project_id}")
            return True
        else:
            print("❌ Firebase not initialized")
            return False
            
    except Exception as e:
        print(f"❌ Firebase Error: {e}")
        print("💡 Make sure firebase_service_account.json exists")
        return False

def test_environment_variables():
    """Test environment variables"""
    print(f"\n⚙️  Testing environment variables...")
    
    required_vars = [
        "PROJECT_ID",
        "GCS_BUCKET_NAME", 
        "FIREBASE_PROJECT_ID",
        "GOOGLE_APPLICATION_CREDENTIALS"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Missing")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def test_gcp_setup():
    """Test complete GCP setup for Lumen project"""
    
    project_id = os.getenv("PROJECT_ID")
    print(f"🔍 Testing GCP Setup for Lumen Project")
    print(f"📋 Project ID: {project_id}")
    print("="*50)
    
    # Test environment variables
    env_ok = test_environment_variables()
    
    # Test Cloud Storage
    storage_ok = test_cloud_storage()
    
    # Test Firebase
    firebase_ok = test_firebase()
    
    # Summary
    print("\n" + "="*50)
    print("📊 SETUP SUMMARY:")
    print(f"⚙️  Environment Variables: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"📸 Cloud Storage: {'✅ PASS' if storage_ok else '❌ FAIL'}")
    print(f"🔥 Firebase: {'✅ PASS' if firebase_ok else '❌ FAIL'}")
    
    if env_ok and storage_ok and firebase_ok:
        print("\n🎉 All tests passed! Your Lumen GCP setup is ready!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure you're authenticated: gcloud auth application-default login")
        print("2. Verify all environment variables in .env file")
        print("3. Check if all APIs are enabled")
        print("4. Ensure firebase_service_account.json exists")

if __name__ == "__main__":
    test_gcp_setup()