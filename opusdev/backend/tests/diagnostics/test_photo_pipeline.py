"""
Photo Display Pipeline Diagnostic Tests

This module contains end-to-end tests for the complete photo display pipeline
to diagnose why photos aren't appearing despite successful authentication.

The pipeline tested includes:
1. Frontend authentication (Firebase OAuth)
2. Backend token validation  
3. Database photo retrieval
4. GCS signed URL generation
5. ID validation throughout the process
6. Photo service operations

This addresses the user's issue: authenticated but can't see photos.
"""

import pytest
import uuid
import json
from unittest.mock import patch, Mock, MagicMock
from fastapi.testclient import TestClient
from io import BytesIO
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
backend_path = Path(__file__).parent.parent.parent
env_file = backend_path / '.env'
load_dotenv(env_file)

from app.main import app
from app.auth_middleware import AuthUser
from app.services.photo_service import PhotoService
from app.models.photo import Photo, PhotoResponse
from app.models.user import User
from app.database.connection import SessionLocal
from app.utils import validate_firebase_uid, validate_uuid


@pytest.mark.diagnostics
@pytest.mark.photos
@pytest.mark.integration
class TestPhotoDisplayPipeline:
    """Test complete photo display pipeline from authentication to display"""
    
    def setup_method(self):
        """Setup test client and mock data"""
        self.client = TestClient(app)
        self.db = SessionLocal()
        
        # Sample Firebase user for testing
        self.test_firebase_uid = "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2"
        self.test_user_email = "testuser@example.com"
        
    def teardown_method(self):
        """Cleanup after tests"""
        if hasattr(self, 'db'):
            self.db.close()
    
    def test_database_has_photos(self):
        """Check if database contains any photos for testing"""
        try:
            photo_count = self.db.query(Photo).count()
            user_count = self.db.query(User).count()
            
            print(f"Database status:")
            print(f"  Total users: {user_count}")
            print(f"  Total photos: {photo_count}")
            
            if photo_count == 0:
                pytest.skip("No photos in database for testing")
                
            # Get sample photo for testing
            sample_photo = self.db.query(Photo).first()
            print(f"  Sample photo: {sample_photo.title} (ID: {sample_photo.id})")
            print(f"  Photo user_id: {sample_photo.user_id}")
            
        except Exception as e:
            pytest.fail(f"Database photo query failed: {e}")
    
    def test_photo_service_initialization(self):
        """Test PhotoService can be initialized and basic operations work"""
        try:
            photo_service = PhotoService(self.db)
            assert photo_service is not None
            assert photo_service.bucket_name == 'lumen-photos-20250731'
            print(f"✅ PhotoService initialized with bucket: {photo_service.bucket_name}")
            
        except Exception as e:
            pytest.fail(f"PhotoService initialization failed: {e}")
    
    @patch('app.services.photo_service.storage.Client')
    def test_signed_url_generation(self, mock_storage_client):
        """Test GCS signed URL generation with ID validation"""
        # Setup mocks
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.generate_signed_url.return_value = "https://signed-url.example.com/photo.jpg"
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        
        photo_service = PhotoService(self.db)
        
        # Test with valid IDs
        test_photo_id = uuid.uuid4()
        test_firebase_uid = "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2"
        
        try:
            image_url, thumbnail_url = photo_service._generate_photo_urls(
                test_photo_id, test_firebase_uid
            )
            
            assert image_url.startswith("https://"), "Should return valid URL"
            assert thumbnail_url.startswith("https://"), "Should return valid thumbnail URL"
            print(f"✅ Signed URL generation successful")
            print(f"  Image URL: {image_url[:50]}...")
            print(f"  Thumbnail URL: {thumbnail_url[:50]}...")
            
        except Exception as e:
            pytest.fail(f"Signed URL generation failed: {e}")
    
    def test_recent_photos_endpoint_unauthenticated(self):
        """Test /photos/recent endpoint without authentication"""
        try:
            response = self.client.get("/api/v1/photos/recent")
            print(f"Recent photos response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Recent photos endpoint working")
                print(f"  Photos returned: {len(data.get('photos', []))}")
                print(f"  Total count: {data.get('total_count', 0)}")
                
                if data.get('photos'):
                    sample_photo = data['photos'][0]
                    print(f"  Sample photo: {sample_photo.get('title', 'No title')}")
                    print(f"  Image URL: {sample_photo.get('image_url', 'No URL')[:50]}...")
                    
            else:
                print(f"❌ Recent photos endpoint failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            pytest.fail(f"Recent photos endpoint test failed: {e}")
    
    @patch('app.auth_middleware.get_current_user')
    def test_my_photos_endpoint_authenticated(self, mock_auth):
        """Test /photos/my-photos endpoint with mocked authentication"""
        # Mock authentication
        mock_auth.return_value = {
            'uid': self.test_firebase_uid,
            'email': self.test_user_email
        }
        
        try:
            response = self.client.get(
                "/api/v1/photos/my-photos",
                headers={'Authorization': 'Bearer fake-token'}
            )
            
            print(f"My photos response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ My photos endpoint working")
                print(f"  Photos returned: {len(data.get('photos', []))}")
                
            elif response.status_code == 500:
                print(f"⚠️ My photos endpoint failed (likely database issue): {response.status_code}")
                print(f"Response: {response.text}")
                
            else:
                print(f"❌ My photos endpoint failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            pytest.fail(f"My photos endpoint test failed: {e}")
    
    def test_photo_service_recent_photos(self):
        """Test PhotoService.get_recent_photos directly"""
        try:
            photo_service = PhotoService(self.db)
            
            # Mock GCS operations to avoid network calls
            with patch.object(photo_service, '_generate_photo_urls') as mock_urls:
                mock_urls.return_value = (
                    "https://test-image.jpg",
                    "https://test-thumbnail.jpg"
                )
                
                result = photo_service.get_recent_photos(page=1, limit=5)
                
                print(f"✅ PhotoService.get_recent_photos working")
                print(f"  Photos returned: {len(result.photos)}")
                print(f"  Total count: {result.total_count}")
                print(f"  Has more: {result.has_more}")
                
                if result.photos:
                    sample = result.photos[0]
                    print(f"  Sample photo: {sample.title}")
                    print(f"  Photo ID: {sample.id}")
                    print(f"  Image URL: {sample.image_url}")
                
        except Exception as e:
            pytest.fail(f"PhotoService.get_recent_photos failed: {e}")
    
    def test_user_photo_relationship(self):
        """Test that photos are properly linked to users"""
        try:
            # Get a photo with user relationship loaded
            photo_with_user = self.db.query(Photo).join(User).first()
            
            if not photo_with_user:
                pytest.skip("No photos with user relationships found")
            
            assert photo_with_user.user is not None, "Photo should have associated user"
            assert photo_with_user.user_id == photo_with_user.user.id, "User IDs should match"
            
            print(f"✅ Photo-User relationship working")
            print(f"  Photo: {photo_with_user.title}")
            print(f"  User: {photo_with_user.user.display_name}")
            print(f"  User ID: {photo_with_user.user.id}")
            
        except Exception as e:
            pytest.fail(f"Photo-User relationship test failed: {e}")


@pytest.mark.diagnostics
@pytest.mark.photos  
@pytest.mark.auth
class TestAuthenticationFlow:
    """Test the complete authentication flow for photo access"""
    
    def setup_method(self):
        """Setup test data"""
        self.client = TestClient(app)
        self.test_firebase_uid = "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2"
        
    @patch('app.auth_middleware.firebase_admin.auth.verify_id_token')
    def test_firebase_token_validation(self, mock_verify):
        """Test Firebase token validation in auth middleware"""
        # Mock successful token verification
        mock_verify.return_value = {
            'uid': self.test_firebase_uid,
            'email': 'test@example.com'
        }
        
        # Test protected endpoint
        response = self.client.get(
            "/api/v1/photos/my-photos",
            headers={'Authorization': 'Bearer valid-token'}
        )
        
        print(f"Auth validation response: {response.status_code}")
        
        # We expect either success or a controlled error (not auth failure)
        assert response.status_code != 401, "Should not be unauthorized with valid token"
        
    def test_auth_middleware_error_handling(self):
        """Test auth middleware handles missing/invalid tokens"""
        # Test without auth header
        response = self.client.get("/api/v1/photos/my-photos")
        assert response.status_code == 401, "Should require authentication"
        
        # Test with invalid token
        response = self.client.get(
            "/api/v1/photos/my-photos",
            headers={'Authorization': 'Bearer invalid-token'}
        )
        assert response.status_code == 401, "Should reject invalid token"
        
        print("✅ Auth middleware error handling working")


@pytest.mark.diagnostics
@pytest.mark.photos
@pytest.mark.external  
class TestExternalServiceIntegration:
    """Test integration with external services (GCS, Firebase)"""
    
    def test_gcs_bucket_accessibility(self):
        """Test if GCS bucket is accessible"""
        try:
            from google.cloud import storage
            
            client = storage.Client()
            bucket_name = 'lumen-photos-20250731'
            bucket = client.bucket(bucket_name)
            
            # Test bucket exists and is accessible
            assert bucket.exists(), f"Bucket {bucket_name} should exist"
            
            # Test listing files (limit to avoid performance issues)
            blobs = list(bucket.list_blobs(prefix='photos/', max_results=1))
            print(f"✅ GCS bucket accessible: {bucket_name}")
            print(f"  Sample files found: {len(blobs)}")
            
        except Exception as e:
            pytest.fail(f"GCS bucket accessibility test failed: {e}")
    
    def test_firebase_admin_connectivity(self):
        """Test Firebase Admin SDK connectivity"""
        try:
            import firebase_admin
            from firebase_admin import auth
            
            # Test Firebase Admin is initialized
            apps = firebase_admin._apps
            assert len(apps) > 0, "Firebase Admin should be initialized"
            
            print(f"✅ Firebase Admin initialized: {len(apps)} app(s)")
            
        except Exception as e:
            pytest.fail(f"Firebase Admin connectivity test failed: {e}")


if __name__ == "__main__":
    # Allow running diagnostics directly
    pytest.main([__file__, "-v", "-s"])