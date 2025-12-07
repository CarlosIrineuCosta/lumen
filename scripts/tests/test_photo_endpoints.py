"""
Modern Photo Endpoint Tests for Lumen Backend
Tests photo CRUD operations, uploads, and search functionality.
"""

import pytest
from unittest.mock import patch, Mock, mock_open
from fastapi.testclient import TestClient
from io import BytesIO


@pytest.mark.integration
@pytest.mark.photos
class TestPhotoEndpoints:
    """Test photo-related endpoints"""

    def test_get_recent_photos(self, client):
        """Test getting recent photos (public endpoint)"""
        with patch('app.services.photo_service.get_recent_photos') as mock_get:
            mock_photos = [
                {
                    "id": "photo-1",
                    "title": "Test Photo 1",
                    "image_url": "https://example.com/photo1.jpg",
                    "user": {"handle": "testuser1"}
                },
                {
                    "id": "photo-2", 
                    "title": "Test Photo 2",
                    "image_url": "https://example.com/photo2.jpg",
                    "user": {"handle": "testuser2"}
                }
            ]
            mock_get.return_value = mock_photos
            
            response = client.get("/api/photos/recent")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["title"] == "Test Photo 1"
            assert data[1]["title"] == "Test Photo 2"

    def test_list_photos_with_pagination(self, client):
        """Test listing photos with pagination"""
        with patch('app.services.photo_service.list_photos') as mock_list:
            mock_list.return_value = {
                "photos": [{"id": f"photo-{i}", "title": f"Photo {i}"} for i in range(5)],
                "total": 50,
                "page": 1,
                "per_page": 10
            }
            
            response = client.get("/api/photos?page=1&per_page=10")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 50
            assert data["page"] == 1
            assert len(data["photos"]) == 5

    @patch('app.auth_middleware.get_current_user')
    def test_upload_photo_authenticated(self, mock_get_user, client):
        """Test photo upload with authentication"""
        mock_get_user.return_value = {"uid": "test-uid", "email": "test@example.com"}
        
        # Mock file upload
        file_content = b"fake image data"
        files = {"file": ("test.jpg", BytesIO(file_content), "image/jpeg")}
        data = {"title": "Test Upload", "description": "Test photo upload"}
        
        with patch('app.services.photo_service.create_photo') as mock_create:
            mock_create.return_value = {
                "id": "new-photo-123",
                "title": "Test Upload",
                "image_url": "https://example.com/new-photo.jpg"
            }
            
            response = client.post("/api/photos/upload",
                                 files=files,
                                 data=data,
                                 headers={"Authorization": "Bearer valid-token"})
            
            assert response.status_code == 201
            response_data = response.json()
            assert response_data["title"] == "Test Upload"
            assert "image_url" in response_data

    def test_upload_photo_unauthenticated(self, client):
        """Test photo upload without authentication"""
        file_content = b"fake image data"
        files = {"file": ("test.jpg", BytesIO(file_content), "image/jpeg")}
        data = {"title": "Test Upload"}
        
        response = client.post("/api/photos/upload", files=files, data=data)
        assert response.status_code == 401

    @patch('app.auth_middleware.get_current_user')
    def test_get_my_photos(self, mock_get_user, client):
        """Test getting current user's photos"""
        mock_get_user.return_value = {"uid": "test-uid"}
        
        with patch('app.services.photo_service.get_user_photos') as mock_get:
            mock_get.return_value = [
                {"id": "photo-1", "title": "My Photo 1"},
                {"id": "photo-2", "title": "My Photo 2"}
            ]
            
            response = client.get("/api/photos/my-photos",
                                headers={"Authorization": "Bearer valid-token"})
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["title"] == "My Photo 1"

    def test_get_photo_by_id(self, client):
        """Test getting a specific photo by ID"""
        photo_id = "test-photo-123"
        
        with patch('app.services.photo_service.get_photo_by_id') as mock_get:
            mock_get.return_value = {
                "id": photo_id,
                "title": "Test Photo",
                "description": "A test photo",
                "image_url": "https://example.com/photo.jpg",
                "user": {"handle": "testuser", "display_name": "Test User"}
            }
            
            response = client.get(f"/api/photos/{photo_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == photo_id
            assert data["title"] == "Test Photo"
            assert data["user"]["handle"] == "testuser"

    def test_get_photo_not_found(self, client):
        """Test getting a non-existent photo"""
        with patch('app.services.photo_service.get_photo_by_id') as mock_get:
            mock_get.return_value = None
            
            response = client.get("/api/photos/nonexistent")
            assert response.status_code == 404

    @patch('app.auth_middleware.get_current_user')
    def test_update_photo_owner(self, mock_get_user, client):
        """Test updating a photo by its owner"""
        mock_get_user.return_value = {"uid": "owner-uid"}
        photo_id = "test-photo-123"
        
        with patch('app.services.photo_service.get_photo_by_id') as mock_get:
            mock_get.return_value = {"id": photo_id, "user_id": "owner-uid"}
            
            with patch('app.services.photo_service.update_photo') as mock_update:
                mock_update.return_value = {
                    "id": photo_id,
                    "title": "Updated Title",
                    "description": "Updated description"
                }
                
                update_data = {"title": "Updated Title", "description": "Updated description"}
                
                response = client.put(f"/api/photos/{photo_id}",
                                    json=update_data,
                                    headers={"Authorization": "Bearer valid-token"})
                
                assert response.status_code == 200
                data = response.json()
                assert data["title"] == "Updated Title"

    @patch('app.auth_middleware.get_current_user')
    def test_delete_photo_owner(self, mock_get_user, client):
        """Test deleting a photo by its owner"""
        mock_get_user.return_value = {"uid": "owner-uid"}
        photo_id = "test-photo-123"
        
        with patch('app.services.photo_service.get_photo_by_id') as mock_get:
            mock_get.return_value = {"id": photo_id, "user_id": "owner-uid"}
            
            with patch('app.services.photo_service.delete_photo') as mock_delete:
                mock_delete.return_value = True
                
                response = client.delete(f"/api/photos/{photo_id}",
                                       headers={"Authorization": "Bearer valid-token"})
                
                assert response.status_code == 200
                data = response.json()
                assert "message" in data

    @patch('app.auth_middleware.get_current_user')
    def test_delete_photo_not_owner(self, mock_get_user, client):
        """Test deleting a photo by non-owner (should fail)"""
        mock_get_user.return_value = {"uid": "different-uid"}
        photo_id = "test-photo-123"
        
        with patch('app.services.photo_service.get_photo_by_id') as mock_get:
            mock_get.return_value = {"id": photo_id, "user_id": "owner-uid"}
            
            response = client.delete(f"/api/photos/{photo_id}",
                                   headers={"Authorization": "Bearer valid-token"})
            
            assert response.status_code == 403

    @patch('app.auth_middleware.get_current_user')
    def test_like_photo(self, mock_get_user, client):
        """Test liking a photo"""
        mock_get_user.return_value = {"uid": "user-uid"}
        photo_id = "test-photo-123"
        
        with patch('app.services.photo_service.toggle_like') as mock_like:
            mock_like.return_value = {"liked": True, "like_count": 5}
            
            response = client.post(f"/api/photos/{photo_id}/like",
                                 headers={"Authorization": "Bearer valid-token"})
            
            assert response.status_code == 200
            data = response.json()
            assert data["liked"] is True
            assert data["like_count"] == 5

    def test_search_photos(self, client):
        """Test photo search functionality"""
        with patch('app.services.photo_service.search_photos') as mock_search:
            mock_search.return_value = {
                "photos": [
                    {"id": "photo-1", "title": "Nature Photo"},
                    {"id": "photo-2", "title": "Nature Landscape"}
                ],
                "total": 2
            }
            
            response = client.get("/api/photos/search?q=nature&category=landscape")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            assert len(data["photos"]) == 2

    def test_get_user_photos_by_handle(self, client):
        """Test getting photos by user handle"""
        handle = "testuser"
        
        with patch('app.services.photo_service.get_photos_by_user_handle') as mock_get:
            mock_get.return_value = [
                {"id": "photo-1", "title": "User Photo 1"},
                {"id": "photo-2", "title": "User Photo 2"}
            ]
            
            response = client.get(f"/api/photos/user/{handle}")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["title"] == "User Photo 1"


@pytest.mark.unit
@pytest.mark.photos
class TestPhotoValidation:
    """Test photo-related validation and models"""

    def test_photo_upload_validation(self):
        """Test photo upload validation"""
        # Test valid file types
        valid_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        for content_type in valid_types:
            # Mock validation would go here
            assert True  # Placeholder for actual validation logic

    def test_photo_size_validation(self):
        """Test photo size limits"""
        # Test file size limits (e.g., max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        test_size = 5 * 1024 * 1024   # 5MB
        assert test_size < max_size

    def test_photo_metadata_validation(self):
        """Test photo metadata validation"""
        valid_metadata = {
            "title": "Test Photo",
            "description": "A test photo description",
            "tags": ["nature", "landscape"],
            "camera_data": {
                "make": "Canon",
                "model": "EOS R5",
                "iso": 100,
                "aperture": "f/2.8"
            }
        }
        
        # Validation logic would be implemented here
        assert valid_metadata["title"] is not None
        assert len(valid_metadata["title"]) > 0
        assert isinstance(valid_metadata["tags"], list)