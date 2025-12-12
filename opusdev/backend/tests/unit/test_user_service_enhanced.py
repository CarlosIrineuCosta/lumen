"""
Unit tests for enhanced user service functionality.

Tests the new user service methods including profile image upload,
enhanced profile updates, and artistic statement handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.services.user_service import UserService
from app.models.user import (
    UpdateUserRequest, ExperienceLevel, PhotographyStyle, 
    ProfileImageSource, AvailabilityData, ContactPreferences
)
from app.auth_middleware import AuthUser


@pytest.mark.unit
class TestEnhancedUserService:
    """Test enhanced user service methods."""

    def setup_method(self):
        """Setup test environment"""
        self.user_service = UserService()
        self.mock_user_data = {
            "id": "user-123",
            "firebase_uid": "firebase-uid-123",
            "email": "test@example.com",
            "handle": "test_photographer",
            "display_name": "Test Photographer",
            "bio": "Professional photographer",
            "profile_data": {
                "photography_styles": ["portrait", "fashion"],
                "experience_level": "professional",
                "camera_gear": ["Canon EOS R5", "24-70mm f/2.8"]
            },
            "availability_data": {
                "open_for_work": True,
                "travel_range_km": 200
            }
        }

    @pytest.mark.asyncio
    @patch('app.services.user_service.SessionLocal')
    async def test_update_user_profile_with_artistic_statement(self, mock_session_local):
        """Test updating user profile with artistic statement fields."""
        # Setup mock
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        mock_user = Mock()
        mock_user.firebase_uid = "firebase-uid-123"
        mock_user.profile_data = {}
        mock_user.availability_data = {}
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Create update request
        update_request = UpdateUserRequest(
            artistic_statement="I capture the essence of human emotion through natural light photography.",
            tagline="Natural Light Portrait Specialist • NYC Based",
            mission_statement="Creating timeless portraits that tell each person's unique story",
            experience_level=ExperienceLevel.PROFESSIONAL,
            experience_years=8,
            photography_styles=[PhotographyStyle.PORTRAIT, PhotographyStyle.LIFESTYLE]
        )
        
        # Mock the get_user_profile method to return something
        with patch.object(self.user_service, 'get_user_profile') as mock_get_profile:
            mock_profile = Mock()
            mock_profile.id = "user-123"
            mock_profile.artistic_statement = update_request.artistic_statement
            mock_get_profile.return_value = mock_profile
            
            # Execute update
            result = await self.user_service.update_user_profile("firebase-uid-123", update_request)
            
            # Verify profile_data was updated
            assert mock_user.profile_data["artistic_statement"] == update_request.artistic_statement
            assert mock_user.profile_data["tagline"] == update_request.tagline
            assert mock_user.profile_data["mission_statement"] == update_request.mission_statement
            assert mock_user.profile_data["experience_level"] == ExperienceLevel.PROFESSIONAL.value
            assert mock_user.profile_data["experience_years"] == 8
            assert len(mock_user.profile_data["photography_styles"]) == 2
            
            # Verify database commit was called
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.user_service.SessionLocal')
    async def test_update_user_profile_photographer_specific_fields(self, mock_session_local):
        """Test updating photographer-specific fields."""
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        mock_user = Mock()
        mock_user.firebase_uid = "firebase-uid-123"
        mock_user.profile_data = {}
        mock_user.availability_data = {}
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        update_request = UpdateUserRequest(
            camera_gear=["Canon EOS R5", "24-70mm f/2.8", "50mm f/1.4", "Godox lighting kit"],
            specializes_in=["portraits", "fashion", "commercial"],
            studio_access=True,
            rates={
                "hourly_rate": 150,
                "day_rate": 800,
                "currency": "USD",
                "rate_negotiable": True
            }
        )
        
        with patch.object(self.user_service, 'get_user_profile') as mock_get_profile:
            mock_get_profile.return_value = Mock()
            
            result = await self.user_service.update_user_profile("firebase-uid-123", update_request)
            
            # Verify photographer fields were updated
            assert len(mock_user.profile_data["camera_gear"]) == 4
            assert "Canon EOS R5" in mock_user.profile_data["camera_gear"]
            assert mock_user.profile_data["studio_access"] is True
            assert mock_user.profile_data["rates"]["hourly_rate"] == 150
            assert mock_user.profile_data["rates"]["rate_negotiable"] is True

    @pytest.mark.asyncio
    @patch('app.services.user_service.SessionLocal')
    async def test_update_user_profile_model_specific_fields(self, mock_session_local):
        """Test updating model-specific fields."""
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        mock_user = Mock()
        mock_user.firebase_uid = "firebase-uid-123"
        mock_user.profile_data = {}
        mock_user.availability_data = {}
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        update_request = UpdateUserRequest(
            gender="Female",
            age=25,
            height_cm=175,
            weight_kg=60,
            modeling_types=["fashion", "commercial", "artistic"],
            comfortable_with=["lingerie", "swimwear", "fashion"],
            special_skills=["dance", "yoga", "acting"]
        )
        
        with patch.object(self.user_service, 'get_user_profile') as mock_get_profile:
            mock_get_profile.return_value = Mock()
            
            result = await self.user_service.update_user_profile("firebase-uid-123", update_request)
            
            # Verify model fields were updated
            assert mock_user.gender == "Female"
            assert mock_user.age == 25
            assert mock_user.height_cm == 175
            assert mock_user.weight_kg == 60
            assert len(mock_user.profile_data["modeling_types"]) == 3
            assert "dance" in mock_user.profile_data["special_skills"]

    @pytest.mark.asyncio
    @patch('app.services.user_service.SessionLocal')
    async def test_update_user_profile_availability_data(self, mock_session_local):
        """Test updating availability data."""
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        mock_user = Mock()
        mock_user.firebase_uid = "firebase-uid-123"
        mock_user.profile_data = {}
        mock_user.availability_data = {"existing_field": "value"}
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        availability_data = AvailabilityData(
            open_for_work=True,
            available_for_travel=True,
            travel_range_km=300,
            travel_notes="Available for weekend shoots outside the city",
            available_days=["monday", "tuesday", "weekend"],
            timezone="America/New_York"
        )
        
        update_request = UpdateUserRequest(
            availability_data=availability_data
        )
        
        with patch.object(self.user_service, 'get_user_profile') as mock_get_profile:
            mock_get_profile.return_value = Mock()
            
            result = await self.user_service.update_user_profile("firebase-uid-123", update_request)
            
            # Verify availability data was merged (not replaced)
            assert "existing_field" in mock_user.availability_data
            assert mock_user.availability_data["open_for_work"] is True
            assert mock_user.availability_data["travel_range_km"] == 300

    @pytest.mark.asyncio
    @patch('google.cloud.storage.Client')
    async def test_upload_profile_image_success(self, mock_storage_client):
        """Test successful profile image upload."""
        # Setup mocks
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.public_url = "https://storage.googleapis.com/bucket/users/uid123/profile_12345678.jpg"
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        
        # Test data
        uid = "firebase-uid-123"
        file_content = b"fake image data"
        filename = "profile.jpg"
        content_type = "image/jpeg"
        
        # Execute upload
        result = await self.user_service.upload_profile_image(uid, file_content, filename, content_type)
        
        # Verify operations
        mock_blob.upload_from_string.assert_called_once_with(file_content)
        mock_blob.make_public.assert_called_once()
        assert result == mock_blob.public_url
        assert mock_blob.content_type == content_type

    @pytest.mark.asyncio
    @patch('google.cloud.storage.Client')
    async def test_upload_profile_image_failure(self, mock_storage_client):
        """Test profile image upload failure handling."""
        # Setup mock to raise exception
        mock_storage_client.return_value.bucket.side_effect = Exception("Storage error")
        
        # Test data
        uid = "firebase-uid-123"
        file_content = b"fake image data"
        filename = "profile.jpg"
        content_type = "image/jpeg"
        
        # Execute and verify exception
        with pytest.raises(ValueError, match="Failed to upload profile image"):
            await self.user_service.upload_profile_image(uid, file_content, filename, content_type)

    @pytest.mark.asyncio
    @patch('app.services.user_service.SessionLocal')
    async def test_update_profile_image_url(self, mock_session_local):
        """Test updating profile image URL in database."""
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        mock_user = Mock()
        mock_user.profile_data = {}
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        image_url = "https://storage.googleapis.com/bucket/users/uid123/profile.jpg"
        
        # Execute update
        await self.user_service.update_profile_image("firebase-uid-123", image_url)
        
        # Verify updates
        assert mock_user.profile_image_url == image_url
        assert mock_user.profile_data["profile_image"]["source"] == ProfileImageSource.UPLOADED.value
        assert mock_user.profile_data["profile_image"]["url"] == image_url
        assert mock_user.profile_data["profile_image"]["verified"] is True
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.user_service.SessionLocal')
    async def test_remove_profile_image(self, mock_session_local):
        """Test removing custom profile image."""
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        mock_user = Mock()
        mock_user.profile_data = {
            "profile_image": {
                "gmail_url": "https://lh3.googleusercontent.com/example"
            }
        }
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Execute removal
        await self.user_service.remove_profile_image("firebase-uid-123")
        
        # Verify reversion to Gmail image
        assert mock_user.profile_data["profile_image"]["source"] == ProfileImageSource.GMAIL.value
        assert mock_user.profile_data["profile_image"]["verified"] is False
        assert mock_user.profile_data["profile_image"]["upload_date"] is None
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.user_service.SessionLocal')
    async def test_user_exists(self, mock_session_local):
        """Test checking if user exists."""
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        
        # Test existing user
        mock_session.query.return_value.filter.return_value.first.return_value = Mock()
        result = await self.user_service.user_exists("firebase-uid-123")
        assert result is True
        
        # Test non-existing user
        mock_session.query.return_value.filter.return_value.first.return_value = None
        result = await self.user_service.user_exists("nonexistent-uid")
        assert result is False

    @pytest.mark.asyncio
    @patch('app.services.user_service.SessionLocal')
    async def test_get_user_stats(self, mock_session_local):
        """Test getting user statistics."""
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        mock_user = Mock()
        mock_user.photos = [Mock(), Mock()]  # 2 photos
        mock_user.created_at = datetime(2023, 1, 1, 12, 0, 0)
        mock_user.last_active = datetime(2023, 12, 31, 12, 0, 0)
        mock_user.user_type.type_name = "photographer"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = await self.user_service.get_user_stats("firebase-uid-123")
        
        assert result["user_id"] == "firebase-uid-123"
        assert result["total_photos"] == 2
        assert result["user_type"] == "photographer"
        assert "2023-01-01" in result["account_created"]
        assert "2023-12-31" in result["last_active"]