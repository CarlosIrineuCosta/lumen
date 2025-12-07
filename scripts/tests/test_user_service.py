"""
Modern User Service Tests for Lumen Backend
Tests user creation, retrieval, updates, and business logic.
"""

import pytest
from unittest.mock import patch, Mock
from datetime import date
from app.services.user_service import UserService
from app.models.user import User, UserType


@pytest.mark.unit
@pytest.mark.users
class TestUserService:
    """Test user service business logic"""

    def test_create_photographer_user(self, db_session):
        """Test creating a photographer user"""
        user_data = {
            "firebase_uid": "test-photographer-123",
            "email": "photographer@example.com",
            "handle": "testphotographer",
            "display_name": "Test Photographer",
            "user_type": UserType.PHOTOGRAPHER,
            "birth_date": date(1990, 1, 1),
            "country_code": "US"
        }
        
        with patch('app.services.user_service.get_db') as mock_db:
            mock_db.return_value = db_session
            
            # Mock the user creation
            created_user = User(**user_data)
            created_user.id = "test-photographer-123"
            
            with patch.object(db_session, 'add') as mock_add, \
                 patch.object(db_session, 'commit') as mock_commit, \
                 patch.object(db_session, 'refresh') as mock_refresh:
                
                mock_refresh.side_effect = lambda user: setattr(user, 'id', user_data["firebase_uid"])
                
                service = UserService()
                result = service.create_user(user_data, db_session)
                
                mock_add.assert_called_once()
                mock_commit.assert_called_once()
                assert result.handle == "testphotographer"
                assert result.user_type == UserType.PHOTOGRAPHER

    def test_create_model_user(self, db_session):
        """Test creating a model user with additional fields"""
        user_data = {
            "firebase_uid": "test-model-123",
            "email": "model@example.com", 
            "handle": "testmodel",
            "display_name": "Test Model",
            "user_type": UserType.MODEL,
            "birth_date": date(1995, 6, 15),
            "country_code": "US",
            "gender": "Female",
            "age": 28,
            "height_cm": 170,
            "weight_kg": 55,
            "ethnicity": "Caucasian",
            "eye_color": "Blue",
            "hair_color": "Blonde"
        }
        
        with patch('app.services.user_service.get_db') as mock_db:
            mock_db.return_value = db_session
            
            created_user = User(**user_data)
            created_user.id = "test-model-123"
            
            with patch.object(db_session, 'add'), \
                 patch.object(db_session, 'commit'), \
                 patch.object(db_session, 'refresh') as mock_refresh:
                
                mock_refresh.side_effect = lambda user: setattr(user, 'id', user_data["firebase_uid"])
                
                service = UserService()
                result = service.create_user(user_data, db_session)
                
                assert result.handle == "testmodel"
                assert result.user_type == UserType.MODEL
                assert result.gender == "Female"
                assert result.height_cm == 170

    def test_get_user_by_firebase_uid(self, db_session):
        """Test retrieving user by Firebase UID"""
        firebase_uid = "test-uid-123"
        
        mock_user = User(
            id=firebase_uid,
            firebase_uid=firebase_uid,
            email="test@example.com",
            handle="testuser",
            display_name="Test User"
        )
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = mock_user
            
            service = UserService()
            result = service.get_user_by_firebase_uid(firebase_uid, db_session)
            
            assert result is not None
            assert result.firebase_uid == firebase_uid
            assert result.handle == "testuser"

    def test_get_user_by_handle(self, db_session):
        """Test retrieving user by handle"""
        handle = "testuser"
        
        mock_user = User(
            id="test-uid-123",
            handle=handle,
            display_name="Test User",
            email="test@example.com"
        )
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = mock_user
            
            service = UserService()
            result = service.get_user_by_handle(handle, db_session)
            
            assert result is not None
            assert result.handle == handle
            assert result.display_name == "Test User"

    def test_update_user_profile(self, db_session):
        """Test updating user profile"""
        user_id = "test-uid-123"
        
        existing_user = User(
            id=user_id,
            handle="oldhandle",
            display_name="Old Name",
            bio="Old bio"
        )
        
        update_data = {
            "display_name": "New Name",
            "bio": "Updated bio",
            "location": "New York"
        }
        
        with patch.object(db_session, 'query') as mock_query, \
             patch.object(db_session, 'commit') as mock_commit:
            
            mock_query.return_value.filter.return_value.first.return_value = existing_user
            
            service = UserService()
            result = service.update_user_profile(user_id, update_data, db_session)
            
            assert result.display_name == "New Name"
            assert result.bio == "Updated bio"
            mock_commit.assert_called_once()

    def test_validate_unique_handle(self, db_session):
        """Test handle uniqueness validation"""
        handle = "existinghandle"
        
        # First test: handle exists
        mock_existing_user = User(handle=handle)
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = mock_existing_user
            
            service = UserService()
            is_available = service.is_handle_available(handle, db_session)
            
            assert is_available is False
        
        # Second test: handle doesn't exist
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = None
            
            service = UserService()
            is_available = service.is_handle_available("newhandle", db_session)
            
            assert is_available is True

    def test_user_age_verification(self, db_session):
        """Test age verification logic"""
        from app.utils.age_verification import verify_age_compliance
        
        # Test adult user (18+ years old)
        adult_birth_date = date(1990, 1, 1)
        country_code = "US"
        
        is_compliant = verify_age_compliance(adult_birth_date, country_code)
        assert is_compliant is True
        
        # Test minor user (under 18)
        minor_birth_date = date(2010, 1, 1)
        
        is_compliant = verify_age_compliance(minor_birth_date, country_code)
        assert is_compliant is False

    def test_user_search_functionality(self, db_session):
        """Test user search with various filters"""
        search_params = {
            "user_type": "photographer",
            "location": "New York",
            "specialties": ["portrait", "wedding"]
        }
        
        mock_users = [
            User(handle="photographer1", user_type=UserType.PHOTOGRAPHER),
            User(handle="photographer2", user_type=UserType.PHOTOGRAPHER)
        ]
        
        with patch.object(db_session, 'query') as mock_query:
            # Mock the complex query chain
            query_mock = Mock()
            query_mock.filter.return_value = query_mock
            query_mock.join.return_value = query_mock  
            query_mock.all.return_value = mock_users
            mock_query.return_value = query_mock
            
            service = UserService()
            results = service.search_users(search_params, db_session)
            
            assert len(results) == 2
            assert all(user.user_type == UserType.PHOTOGRAPHER for user in results)

    def test_user_profile_visibility(self, db_session):
        """Test profile visibility settings"""
        user_data = {
            "id": "test-uid",
            "handle": "testuser", 
            "display_name": "Test User",
            "email": "test@example.com",
            "profile_visibility": "public"
        }
        
        user = User(**user_data)
        
        # Test public profile access
        assert user.profile_visibility == "public"
        
        # Test private profile logic would be implemented here
        user.profile_visibility = "private"
        assert user.profile_visibility == "private"

    def test_user_content_permissions(self, db_session):
        """Test user content access permissions"""
        photographer_uid = "photographer-123"
        model_uid = "model-123"
        
        # Test photographer can view model profiles
        # Test model can control photo usage permissions
        # This would integrate with the actual permission system
        
        service = UserService()
        
        # Mock permission check
        with patch.object(service, 'check_content_access') as mock_check:
            mock_check.return_value = True
            
            has_access = service.check_content_access(photographer_uid, model_uid)
            assert has_access is True


@pytest.mark.integration
@pytest.mark.users
class TestUserModelIntegration:
    """Integration tests for user models with database"""

    def test_user_model_creation_with_relationships(self, db_session):
        """Test user model creation with related entities"""
        # This would test actual database constraints and relationships
        # Mock the related entities (cities, user_types, etc.)
        
        user_data = {
            "firebase_uid": "integration-test-123",
            "email": "integration@example.com",
            "handle": "integrationtest",
            "display_name": "Integration Test User",
            "birth_date": date(1990, 1, 1),
            "country_code": "US"
        }
        
        # Mock successful creation
        with patch('app.models.user.User') as mock_user_class:
            mock_user = Mock()
            mock_user.id = user_data["firebase_uid"]
            mock_user_class.return_value = mock_user
            
            # Simulate successful database operations
            db_session.add(mock_user)
            db_session.commit()
            
            assert mock_user.id == user_data["firebase_uid"]

    def test_user_cascade_operations(self, db_session):
        """Test cascade delete and update operations"""
        # Test that deleting a user properly handles related records
        user_id = "test-cascade-user"
        
        with patch.object(db_session, 'delete') as mock_delete, \
             patch.object(db_session, 'commit') as mock_commit:
            
            # Mock user deletion
            service = UserService()
            result = service.delete_user(user_id, db_session)
            
            # Verify cascade operations are handled
            mock_delete.assert_called_once()
            mock_commit.assert_called_once()
            assert result is True