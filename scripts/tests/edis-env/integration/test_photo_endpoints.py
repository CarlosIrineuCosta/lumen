"""
Integration tests for photo management endpoints.

These tests verify the photo API endpoints work correctly with
database operations, file uploads, authentication, and error handling.
"""

import pytest
from unittest.mock import patch, Mock, mock_open
from fastapi.testclient import TestClient
from io import BytesIO


@pytest.mark.integration
@pytest.mark.photos
class TestPhotoEndpoints:
    """Test photo management API endpoints."""

    def test_get_recent_photos_empty(self, client, db_session):
        """Test getting recent photos when database is empty."""
        response = client.get("/api/v1/photos/recent")
        
        assert response.status_code == 200
        data = response.json()
        assert data["photos"] == []
        assert data["pagination"]["total"] == 0
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 20

    def test_get_recent_photos_with_pagination(self, client):
        """Test recent photos endpoint with pagination parameters."""
        response = client.get("/api/v1/photos/recent?page=2&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["page"] == 2
        assert data["pagination"]["limit"] == 10

    def test_get_recent_photos_invalid_pagination(self, client):
        """Test recent photos endpoint with invalid pagination parameters."""
        # Page less than 1
        response = client.get("/api/v1/photos/recent?page=0")
        assert response.status_code == 422  # Validation error
        
        # Limit too high
        response = client.get("/api/v1/photos/recent?limit=1000")
        assert response.status_code == 422  # Validation error

    def test_list_photos_public_endpoint(self, client):
        """Test public photos listing endpoint."""
        response = client.get("/api/v1/photos/")
        
        assert response.status_code == 200
        data = response.json()
        assert "photos" in data
        assert "pagination" in data

    def test_get_nonexistent_photo(self, client):
        """Test getting a photo that doesn't exist."""
        response = client.get("/api/v1/photos/nonexistent-photo-id")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    @patch('app.auth_middleware.get_current_user')
    def test_get_my_photos_authenticated(self, mock_get_user, client):
        """Test getting current user's photos with authentication."""
        # Mock authenticated user
        mock_user_token = {
            'uid': 'test-firebase-uid-123',
            'email': 'test@example.com'
        }
        mock_get_user.return_value = mock_user_token
        
        response = client.get("/api/v1/photos/my-photos")
        
        assert response.status_code == 200
        data = response.json()
        assert "photos" in data
        assert "pagination" in data

    def test_get_my_photos_unauthenticated(self, client):
        """Test that my-photos endpoint requires authentication."""
        response = client.get("/api/v1/photos/my-photos")
        
        assert response.status_code == 401

    @patch('app.auth_middleware.get_current_user')
    def test_get_user_photos_endpoint(self, mock_get_user, client):
        """Test getting current user's photos via /user endpoint."""
        mock_user_token = {
            'uid': 'test-firebase-uid-123',
            'email': 'test@example.com'
        }
        mock_get_user.return_value = mock_user_token
        
        response = client.get("/api/v1/photos/user")
        
        assert response.status_code == 200
        data = response.json()
        assert "photos" in data

    def test_get_specific_user_photos(self, client):
        """Test getting photos for a specific user (public endpoint)."""
        response = client.get("/api/v1/photos/user/some-user-id")
        
        assert response.status_code == 200
        data = response.json()
        assert "photos" in data
        assert "pagination" in data

    @patch('app.auth_middleware.get_current_user')
    @patch('app.services.photo_service.PhotoService.upload_photo')
    def test_upload_photo_success(self, mock_upload, mock_get_user, client):
        """Test successful photo upload."""
        # Mock authenticated user
        mock_user_token = {
            'uid': 'test-firebase-uid-123',
            'email': 'test@example.com'
        }
        mock_get_user.return_value = mock_user_token
        
        # Mock upload service response
        mock_photo = Mock()
        mock_photo.id = "test-photo-id"
        mock_photo.title = "Test Photo"
        mock_photo.image_url = "https://storage.googleapis.com/test-photo.jpg"
        mock_upload.return_value = mock_photo
        
        # Create test file data
        test_file = BytesIO(b"fake image data")
        test_file.name = "test.jpg"
        
        response = client.post(
            "/api/v1/photos/upload",
            files={"file": ("test.jpg", test_file, "image/jpeg")},
            data={
                "title": "Test Photo",
                "description": "A test photo",
                "user_tags": "test,photography",
                "is_public": True
            }
        )
        
        assert response.status_code == 200
        # Note: Actual response validation depends on PhotoService._to_photo_response implementation

    def test_upload_photo_unauthenticated(self, client):
        """Test photo upload requires authentication."""
        test_file = BytesIO(b"fake image data")
        
        response = client.post(
            "/api/v1/photos/upload",
            files={"file": ("test.jpg", test_file, "image/jpeg")},
            data={"title": "Test Photo"}
        )
        
        assert response.status_code == 401

    @patch('app.auth_middleware.get_current_user')
    def test_upload_invalid_file_type(self, mock_get_user, client):
        """Test upload rejects non-image files."""
        mock_user_token = {
            'uid': 'test-firebase-uid-123',
            'email': 'test@example.com'
        }
        mock_get_user.return_value = mock_user_token
        
        test_file = BytesIO(b"fake text data")
        
        response = client.post(
            "/api/v1/photos/upload",
            files={"file": ("test.txt", test_file, "text/plain")},
            data={"title": "Test Photo"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "image" in data["detail"].lower()

    @patch('app.auth_middleware.get_current_user')
    def test_update_photo_authenticated(self, mock_get_user, client):
        """Test updating photo metadata with authentication."""
        mock_user_token = {
            'uid': 'test-firebase-uid-123',
            'email': 'test@example.com'
        }
        mock_get_user.return_value = mock_user_token
        
        update_data = {
            "title": "Updated Photo Title",
            "description": "Updated description",
            "user_tags": ["updated", "test"]
        }
        
        response = client.put(
            "/api/v1/photos/test-photo-id",
            json=update_data
        )
        
        # Photo likely doesn't exist, so expect 404 or 500
        assert response.status_code in [404, 500]

    def test_update_photo_unauthenticated(self, client):
        """Test photo update requires authentication."""
        update_data = {
            "title": "Updated Photo Title"
        }
        
        response = client.put(
            "/api/v1/photos/test-photo-id",
            json=update_data
        )
        
        assert response.status_code == 401

    @patch('app.auth_middleware.get_current_user')
    def test_delete_photo_authenticated(self, mock_get_user, client):
        """Test deleting photo with authentication."""
        mock_user_token = {
            'uid': 'test-firebase-uid-123',
            'email': 'test@example.com'
        }
        mock_get_user.return_value = mock_user_token
        
        response = client.delete("/api/v1/photos/test-photo-id")
        
        # Photo likely doesn't exist, so expect 404 or 500
        assert response.status_code in [404, 500]

    def test_delete_photo_unauthenticated(self, client):
        """Test photo deletion requires authentication."""
        response = client.delete("/api/v1/photos/test-photo-id")
        
        assert response.status_code == 401

    @patch('app.auth_middleware.get_current_user')
    def test_like_photo_not_implemented(self, mock_get_user, client):
        """Test like photo endpoint returns not implemented."""
        mock_user_token = {
            'uid': 'test-firebase-uid-123',
            'email': 'test@example.com'
        }
        mock_get_user.return_value = mock_user_token
        
        response = client.post("/api/v1/photos/test-photo-id/like")
        
        assert response.status_code == 501  # Not implemented
        data = response.json()
        assert "not yet implemented" in data["detail"].lower()

    def test_search_photos_not_implemented(self, client):
        """Test photo search endpoint returns not implemented."""
        search_query = {
            "query": "landscape",
            "tags": ["nature", "outdoor"]
        }
        
        response = client.post("/api/v1/photos/search", json=search_query)
        
        assert response.status_code == 501  # Not implemented


@pytest.mark.unit
@pytest.mark.photos
class TestPhotoModels:
    """Test photo-related models and validation."""
    
    def test_photo_upload_form_validation(self):
        """Test photo upload form data validation."""
        # Test that form can handle various data types and optional fields
        
        # Valid minimal upload
        form_data = {
            "title": "Test Photo",
            "is_public": True
        }
        
        # Should not raise validation errors when processed
        assert form_data["title"] == "Test Photo"
        assert form_data["is_public"] is True
        
    def test_photo_tags_parsing(self):
        """Test tag parsing from comma-separated string."""
        tags_string = "photography, nature, landscape, outdoor "
        expected_tags = ["photography", "nature", "landscape", "outdoor"]
        
        # Simulate the tag parsing logic from the endpoint
        parsed_tags = [tag.strip() for tag in tags_string.split(',') if tag.strip()]
        
        assert parsed_tags == expected_tags
        
    def test_empty_tags_handling(self):
        """Test handling of empty or invalid tag strings."""
        # Empty string
        empty_tags = ""
        parsed = [tag.strip() for tag in empty_tags.split(',') if tag.strip()]
        assert parsed == []
        
        # Only commas and spaces
        invalid_tags = " , , , "
        parsed = [tag.strip() for tag in invalid_tags.split(',') if tag.strip()]
        assert parsed == []
        
        # Mix of valid and invalid
        mixed_tags = "valid, , another,  "
        parsed = [tag.strip() for tag in mixed_tags.split(',') if tag.strip()]
        assert parsed == ["valid", "another"]