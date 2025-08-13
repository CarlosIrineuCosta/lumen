#!/usr/bin/env python3
"""
Quick system health check for Lumen platform

This script performs a rapid health check to identify obvious issues
with the system without running the full diagnostic suite.

Usage:
    python tests/tools/system_health_check.py
"""

import os
import sys
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

# Load environment variables from .env file
env_file = backend_path / '.env'
load_dotenv(env_file)

def check_servers():
    """Check if backend and frontend servers are running"""
    print("🔍 Checking server accessibility...")
    
    backend_url = "http://100.106.201.33:8080"
    frontend_url = "http://100.106.201.33:8000"
    
    # Check backend
    try:
        response = requests.get(f"{backend_url}/api/v1/photos/recent", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server: Running and responding")
            data = response.json()
            photo_count = len(data.get('photos', []))
            print(f"   Photos returned: {photo_count}")
        elif response.status_code == 500:
            print("⚠️ Backend server: Running but has internal errors (likely database)")
        else:
            print(f"⚠️ Backend server: Responding with status {response.status_code}")
    except requests.ConnectionError:
        print("❌ Backend server: Not accessible")
        return False
    except Exception as e:
        print(f"⚠️ Backend server: Error - {e}")
    
    # Check frontend
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend server: Running and accessible")
        else:
            print(f"⚠️ Frontend server: Status {response.status_code}")
    except requests.ConnectionError:
        print("❌ Frontend server: Not accessible")
    except Exception as e:
        print(f"⚠️ Frontend server: Error - {e}")
    
    return True

def check_database_connection():
    """Quick database connection check"""
    print("\n🔍 Checking database connectivity...")
    
    try:
        from app.database.connection import SessionLocal
        
        db = SessionLocal()
        result = db.execute("SELECT 1").scalar()
        db.close()
        
        if result == 1:
            print("✅ Database: Connected successfully")
            return True
        else:
            print("⚠️ Database: Connection established but query failed")
            
    except Exception as e:
        print(f"❌ Database: Connection failed - {str(e)[:100]}...")
        if "password authentication failed" in str(e):
            print("   💡 Hint: This is likely a GCP authentication issue")
            print("   Try: gcloud auth login carlos.irineu@gmail.com")
        return False
    
    return False

def check_photo_data():
    """Check if photos exist in database"""
    print("\n🔍 Checking photo data availability...")
    
    try:
        from app.database.connection import SessionLocal
        from app.models.photo import Photo
        from app.models.user import User
        
        db = SessionLocal()
        
        user_count = db.query(User).count()
        photo_count = db.query(Photo).count()
        
        print(f"✅ Data check: {user_count} users, {photo_count} photos in database")
        
        if photo_count == 0:
            print("⚠️ No photos in database - this explains empty galleries")
            print("   💡 Hint: Upload some test photos or run data creation scripts")
        
        db.close()
        return photo_count > 0
        
    except Exception as e:
        print(f"❌ Data check failed: {str(e)[:100]}...")
        return False

def check_gcs_access():
    """Check Google Cloud Storage access"""
    print("\n🔍 Checking Google Cloud Storage access...")
    
    try:
        from google.cloud import storage
        
        client = storage.Client()
        bucket_name = 'lumen-photos-20250731'
        bucket = client.bucket(bucket_name)
        
        # Test bucket access
        exists = bucket.exists()
        if exists:
            print(f"✅ GCS bucket: {bucket_name} accessible")
            
            # Check for photos
            blobs = list(bucket.list_blobs(prefix='photos/', max_results=5))
            print(f"   Sample files found: {len(blobs)}")
            
            if len(blobs) == 0:
                print("⚠️ No photos found in GCS bucket")
            
            return True
        else:
            print(f"❌ GCS bucket: {bucket_name} not found or not accessible")
            
    except Exception as e:
        print(f"❌ GCS access failed: {str(e)[:100]}...")
        if "could not automatically determine credentials" in str(e):
            print("   💡 Hint: GCP authentication issue")
            print("   Try: gcloud auth application-default login")
            
    return False

def check_environment():
    """Check environment configuration"""
    print("\n🔍 Checking environment configuration...")
    
    required_vars = [
        'DB_USER',
        'DB_PASSWORD', 
        'DB_NAME',
        'INSTANCE_CONNECTION_NAME'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        return False
    else:
        print("✅ Required environment variables are set")
        return True

def main():
    print("🏥 LUMEN SYSTEM HEALTH CHECK")
    print("=" * 50)
    print("Quick diagnostic to identify obvious system issues\n")
    
    checks = [
        ("Server Accessibility", check_servers),
        ("Environment Config", check_environment), 
        ("Database Connection", check_database_connection),
        ("Photo Data", check_photo_data),
        ("GCS Access", check_gcs_access),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name}: Unexpected error - {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("HEALTH CHECK SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ System appears healthy!")
        print("If photos still aren't displaying, run full diagnostics:")
        print("   python tests/tools/run_diagnostics.py")
    else:
        print(f"❌ System has {total - passed} issue(s)")
        print("\nNext steps:")
        
        # Provide specific guidance based on failures
        failed_checks = [name for name, result in results if not result]
        
        if "Database Connection" in failed_checks:
            print("1. 🔧 Fix database authentication:")
            print("   gcloud auth login carlos.irineu@gmail.com")
            print("   unset GOOGLE_APPLICATION_CREDENTIALS")
            
        if "GCS Access" in failed_checks:
            print("2. 🔧 Fix GCS access:")
            print("   gcloud auth application-default login")
            
        if "Photo Data" in failed_checks:
            print("3. 📸 Add test photos:")
            print("   Run: python tests/diagnostics/legacy_scripts/create_dummy_simple.py")
            
        print(f"\n4. 🔍 Run detailed diagnostics:")
        print("   python tests/tools/run_diagnostics.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)