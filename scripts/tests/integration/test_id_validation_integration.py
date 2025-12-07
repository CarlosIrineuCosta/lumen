"""
Integration tests for ID validation throughout the photo upload/retrieval pipeline.

These tests verify that our ID validation system works correctly across all layers:
- Firebase Authentication 
- Database operations
- Google Cloud Storage path generation
- Photo service operations

The tests simulate real-world scenarios with various ID formats and edge cases
to ensure the robustness of our ID validation fixes.
"""

import pytest
import uuid
from unittest.mock import patch, Mock, MagicMock
from fastapi.testclient import TestClient
from io import BytesIO

from app.utils import IDValidationError, validate_firebase_uid, validate_uuid
from app.services import PhotoService, IDManagementService
from app.models.photo import Photo, CreatePhotoRequest
from app.auth_middleware import AuthUser


@pytest.mark.integration
@pytest.mark.id_validation
class TestIDValidationIntegration:
    """Test end-to-end ID validation in photo operations"""
    
    def test_valid_firebase_uid_formats(self):
        """Test that valid Firebase UID formats are accepted"""
        valid_uids = [
            "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2",  # Typical Firebase UID
            "abcd1234efgh5678ijkl9012mnop3456",  # All lowercase
            "ABCD1234EFGH5678IJKL9012MNOP3456",  # All uppercase  
            "AbCd1234EfGh5678IjKl9012MnOp3456",  # Mixed case
        ]
        
        for uid in valid_uids:
            # Should not raise exception
            validated = validate_firebase_uid(uid, f"test valid UID: {uid}")
            assert validated == uid
    
    def test_invalid_firebase_uid_formats(self):
        """Test that invalid Firebase UID formats are rejected"""
        invalid_uids = [
            "short",  # Too short
            "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2extra",  # Too long
            "9pGzwsVBRMaSxMOZ6QNTJJjnl1b!",  # Invalid character
            "",  # Empty string
            None,  # None value
            123456789012345678901234567890,  # Number instead of string
        ]
        
        for uid in invalid_uids:
            with pytest.raises(IDValidationError):
                validate_firebase_uid(uid, f"test invalid UID: {uid}")
    
    def test_valid_uuid_formats(self):
        """Test that valid UUID formats are accepted"""
        valid_uuids = [
            uuid.uuid4(),  # UUID object
            "550e8400-e29b-41d4-a716-446655440000",  # UUID string
            str(uuid.uuid4()),  # UUID converted to string
        ]
        
        for test_uuid in valid_uuids:
            # Should not raise exception
            validated = validate_uuid(test_uuid, f"test valid UUID: {test_uuid}")
            assert isinstance(validated, uuid.UUID)
    
    def test_invalid_uuid_formats(self):
        """Test that invalid UUID formats are rejected"""
        invalid_uuids = [
            "not-a-uuid",  # Invalid format
            "550e8400-e29b-41d4-a716",  # Too short
            "",  # Empty string
            None,  # None value
            123,  # Number instead of string/UUID
            "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2",  # Firebase UID (wrong type)
        ]
        
        for test_uuid in invalid_uuids:
            with pytest.raises(IDValidationError):
                validate_uuid(test_uuid, f"test invalid UUID: {test_uuid}")


@pytest.mark.integration
@pytest.mark.photo_service
class TestPhotoServiceIDValidation:
    """Test PhotoService with ID validation enabled"""
    
    @pytest.fixture
    def mock_firebase_user(self):
        """Create a mock Firebase user with valid UID"""
        user = Mock(spec=AuthUser)
        user.uid = "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2"  # Valid Firebase UID
        user.email = "test@example.com"
        user.name = "Test User"
        return user
    
    @pytest.fixture
    def mock_invalid_firebase_user(self):
        """Create a mock Firebase user with invalid UID"""
        user = Mock(spec=AuthUser)
        user.uid = "invalid-uid-format!"  # Invalid Firebase UID
        user.email = "test@example.com"
        user.name = "Test User"
        return user
    
    @pytest.fixture
    def sample_photo_request(self):
        """Create a sample photo upload request"""
        return CreatePhotoRequest(
            title="Test Photo",
            description="A test photo for ID validation",
            user_tags=["test", "validation"],
            is_public=True,
            is_portfolio=False
        )
    
    @patch('app.services.photo_service.storage.Client')
    def test_photo_service_with_valid_ids(self, mock_storage_client, db_session, mock_firebase_user, sample_photo_request):
        """Test PhotoService operations with valid IDs"""
        # Mock storage operations
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        # Create PhotoService instance
        photo_service = PhotoService(db=db_session)
        
        # Test URL generation with valid IDs
        test_photo_id = uuid.uuid4()
        test_firebase_uid = "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2"
        
        # Should not raise exception
        image_url, thumbnail_url = photo_service._generate_photo_urls(test_photo_id, test_firebase_uid)
        
        # Verify URLs were generated (will be placeholders due to mock, but that's OK)
        assert image_url is not None
        assert thumbnail_url is not None
        assert "placeholder" in image_url  # Mock returns placeholder
        assert "placeholder" in thumbnail_url
    
    @patch('app.services.photo_service.storage.Client')
    def test_photo_service_with_invalid_firebase_uid(self, mock_storage_client, db_session, sample_photo_request):
        """Test PhotoService rejects invalid Firebase UID"""
        photo_service = PhotoService(db=db_session)
        
        test_photo_id = uuid.uuid4()
        invalid_firebase_uid = "invalid-uid!"
        
        # Should raise IDValidationError
        with pytest.raises(IDValidationError):
            photo_service._generate_photo_urls(test_photo_id, invalid_firebase_uid)
    
    @patch('app.services.photo_service.storage.Client')
    def test_photo_service_with_invalid_photo_id(self, mock_storage_client, db_session, mock_firebase_user):
        """Test PhotoService rejects invalid photo ID"""
        photo_service = PhotoService(db=db_session)
        
        invalid_photo_id = "not-a-uuid"
        valid_firebase_uid = "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2"
        
        # Should raise IDValidationError
        with pytest.raises(IDValidationError):
            photo_service._generate_photo_urls(invalid_photo_id, valid_firebase_uid)
    
    @patch('app.services.photo_service.storage.Client')
    def test_ensure_user_exists_with_valid_uid(self, mock_storage_client, db_session, mock_firebase_user):
        """Test that ensure_user_exists works with valid Firebase UID"""
        photo_service = PhotoService(db=db_session)
        
        # Should create user and return Firebase UID
        import asyncio
        result = asyncio.run(photo_service.ensure_user_exists(mock_firebase_user))
        
        assert result == mock_firebase_user.uid
        
        # Verify user was created in database
        from sqlalchemy import text
        user_record = db_session.execute(
            text("SELECT id, email FROM users WHERE id = :uid"),
            {"uid": mock_firebase_user.uid}
        ).fetchone()
        
        assert user_record is not None
        assert user_record[0] == mock_firebase_user.uid  # id column
        assert user_record[1] == mock_firebase_user.email  # email column
    
    @patch('app.services.photo_service.storage.Client')
    def test_ensure_user_exists_with_invalid_uid(self, mock_storage_client, db_session, mock_invalid_firebase_user):
        """Test that ensure_user_exists rejects invalid Firebase UID"""
        photo_service = PhotoService(db=db_session)
        
        # Should raise IDValidationError
        import asyncio
        with pytest.raises(IDValidationError):
            asyncio.run(photo_service.ensure_user_exists(mock_invalid_firebase_user))


@pytest.mark.integration
@pytest.mark.id_management
class TestIDManagementServiceIntegration:
    """Test IDManagementService integration functionality"""
    
    def test_normalize_user_id_integration(self, db_session):
        """Test user ID normalization"""
        id_service = IDManagementService(db=db_session)
        
        valid_uid = "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2"
        normalized = id_service.normalize_user_id(valid_uid, "integration test")
        
        assert normalized == valid_uid
    
    def test_normalize_photo_id_integration(self, db_session):
        """Test photo ID normalization"""
        id_service = IDManagementService(db=db_session)
        
        test_uuid = uuid.uuid4()
        
        # Test returning string
        normalized_str = id_service.normalize_photo_id(test_uuid, "integration test", return_uuid=False)
        assert normalized_str == str(test_uuid)
        assert isinstance(normalized_str, str)
        
        # Test returning UUID object
        normalized_uuid = id_service.normalize_photo_id(test_uuid, "integration test", return_uuid=True)
        assert normalized_uuid == test_uuid
        assert isinstance(normalized_uuid, uuid.UUID)
    
    def test_generate_storage_paths_integration(self, db_session):
        """Test storage path generation"""
        id_service = IDManagementService(db=db_session)
        
        user_id = "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2"
        photo_id = uuid.uuid4()
        
        photo_path, thumbnail_path = id_service.generate_storage_paths(user_id, photo_id)
        
        # Verify path format
        expected_photo_path = f"photos/{user_id}/{photo_id}.jpg"
        expected_thumbnail_path = f"thumbnails/{user_id}/{photo_id}_thumb.jpg"
        
        assert photo_path == expected_photo_path
        assert thumbnail_path == expected_thumbnail_path
    
    def test_parse_storage_path_integration(self, db_session):
        """Test storage path parsing"""
        id_service = IDManagementService(db=db_session)
        
        user_id = "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2"
        photo_id = str(uuid.uuid4())
        
        # Test photo path
        photo_path = f"photos/{user_id}/{photo_id}.jpg"
        parsed = id_service.parse_storage_path(photo_path)
        
        assert parsed["type"] == "photos"
        assert parsed["user_id"] == user_id
        assert parsed["photo_id"] == photo_id
        assert parsed["file_extension"] == "jpg"
        
        # Test thumbnail path
        thumbnail_path = f"thumbnails/{user_id}/{photo_id}_thumb.png"
        parsed_thumb = id_service.parse_storage_path(thumbnail_path)
        
        assert parsed_thumb["type"] == "thumbnails"
        assert parsed_thumb["user_id"] == user_id
        assert parsed_thumb["photo_id"] == photo_id
        assert parsed_thumb["file_extension"] == "png"
    
    def test_prepare_ids_for_operation_integration(self, db_session):
        """Test ID preparation for operations"""
        id_service = IDManagementService(db=db_session)
        
        user_id = "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2"
        photo_id = uuid.uuid4()
        
        firebase_uid, photo_id_str, photo_uuid = id_service.prepare_ids_for_operation(
            user_id, photo_id, "integration test"
        )
        
        assert firebase_uid == user_id
        assert photo_id_str == str(photo_id)
        assert photo_uuid == photo_id
        assert isinstance(firebase_uid, str)
        assert isinstance(photo_id_str, str)
        assert isinstance(photo_uuid, uuid.UUID)


@pytest.mark.integration
@pytest.mark.end_to_end
class TestEndToEndPhotoFlow:
    """Test complete photo upload/retrieval flow with ID validation"""
    
    @pytest.fixture
    def mock_complete_firebase_user(self):
        """Create a complete mock Firebase user"""
        user = Mock(spec=AuthUser)
        user.uid = "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2"
        user.email = "integration@test.com"
        user.name = "Integration Test User"
        return user
    
    @patch('app.services.photo_service.storage.Client')
    @patch('app.auth_middleware.get_current_user')
    def test_complete_photo_upload_flow(self, mock_get_user, mock_storage_client, 
                                       client, db_session, mock_complete_firebase_user):
        """Test complete photo upload flow with ID validation"""
        # Setup mocks
        mock_get_user.return_value = {
            'uid': mock_complete_firebase_user.uid,
            'email': mock_complete_firebase_user.email,
            'name': mock_complete_firebase_user.name
        }
        
        # Mock storage operations
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.generate_signed_url.return_value = "https://storage.googleapis.com/test-url"
        
        # Create test file data
        test_file = BytesIO(b"fake image data for testing")
        test_file.name = "test.jpg"
        
        # Test photo upload
        response = client.post(
            "/api/v1/photos/upload",
            files={"file": ("test.jpg", test_file, "image/jpeg")},
            data={
                "title": "Integration Test Photo",
                "description": "Testing ID validation in upload flow",
                "user_tags": "integration,test,validation",
                "is_public": True
            }
        )
        
        # Verify upload succeeded
        assert response.status_code == 200
        response_data = response.json()
        
        # Verify response contains valid IDs
        assert "id" in response_data
        assert "image_url" in response_data
        assert "thumbnail_url" in response_data
        
        # Verify photo ID is valid UUID format
        photo_id = response_data["id"]
        photo_uuid = uuid.UUID(photo_id)  # Should not raise exception
        
        # Verify photo was created in database with correct ID formats
        from sqlalchemy import text
        photo_record = db_session.execute(
            text("SELECT id, user_id, title FROM photos WHERE id = :photo_id"),
            {"photo_id": photo_uuid}
        ).fetchone()
        
        assert photo_record is not None
        assert str(photo_record[0]) == photo_id  # Photo ID matches
        assert photo_record[1] == mock_complete_firebase_user.uid  # User ID is Firebase UID
        assert photo_record[2] == "Integration Test Photo"  # Title matches
    
    @patch('app.services.photo_service.storage.Client')
    def test_photo_retrieval_with_id_validation(self, mock_storage_client, db_session):
        """Test photo retrieval with validated IDs"""
        # Setup storage mock
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.generate_signed_url.return_value = "https://storage.googleapis.com/test-url"
        
        # Create test data directly in database
        from app.models.photo import Photo
        from app.models.user import User
        
        # Create user
        test_user_id = "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2"
        test_user = User(
            id=test_user_id,
            email="retrieval@test.com",
            handle="retrievaltest",
            display_name="Retrieval Test User",
            city_id=1,
            primary_user_type=1
        )
        db_session.add(test_user)
        
        # Create photo
        test_photo_id = uuid.uuid4()
        test_photo = Photo(
            id=test_photo_id,
            user_id=test_user_id,
            title="Retrieval Test Photo",
            description="Testing ID validation in retrieval",
            is_public=True
        )
        db_session.add(test_photo)
        db_session.commit()
        
        # Test photo retrieval via PhotoService
        photo_service = PhotoService(db=db_session)
        
        import asyncio
        retrieved_photo = asyncio.run(
            photo_service.get_photo_by_id(str(test_photo_id), test_user_id)
        )
        
        # Verify retrieval succeeded
        assert retrieved_photo is not None
        assert retrieved_photo.id == str(test_photo_id)
        assert retrieved_photo.title == "Retrieval Test Photo"
        assert retrieved_photo.image_url is not None
        assert retrieved_photo.thumbnail_url is not None
    
    def test_invalid_id_formats_rejected_in_flow(self, db_session):
        """Test that invalid ID formats are rejected throughout the flow"""
        photo_service = PhotoService(db=db_session)
        id_service = IDManagementService(db=db_session)
        
        # Test invalid Firebase UID in user operations
        with pytest.raises(IDValidationError):
            id_service.normalize_user_id("invalid-uid-format!", "flow test")
        
        # Test invalid photo ID in photo operations
        with pytest.raises(IDValidationError):
            id_service.normalize_photo_id("not-a-uuid", "flow test")
        
        # Test invalid IDs in PhotoService operations
        import asyncio
        with pytest.raises(IDValidationError):
            asyncio.run(photo_service.get_photo_by_id("invalid-photo-id", "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2"))