"""
Unit tests for User model and related functionality.

Tests the User SQLAlchemy model, Pydantic validation models,
and user-specific business logic.
"""

import pytest
from unittest.mock import Mock
from datetime import datetime, date
import uuid

from app.models.user import (
    User, UserType, PhotographyStyle,
    UserProfilePublic, UserProfilePrivate, UserProfileFull,
    CreateUserRequest, UpdateUserRequest, UserSearchQuery
)


@pytest.mark.unit
class TestUserModel:
    """Test User SQLAlchemy model."""

    def test_user_model_creation(self, db_session, sample_user_data):
        """Test creating a User model instance."""
        user = User(
            id=sample_user_data["id"],
            email=sample_user_data["email"],
            handle=sample_user_data["handle"],
            display_name=sample_user_data["display_name"],
            city_id=sample_user_data["city_id"],
            primary_user_type=sample_user_data["primary_user_type"],
            birth_date=sample_user_data["birth_date"],
            country_code=sample_user_data["country_code"],
            tos_accepted_at=sample_user_data["tos_accepted_at"],
            bio=sample_user_data["bio"],
            profile_data=sample_user_data["profile_data"]
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.id == sample_user_data["id"]
        assert user.email == sample_user_data["email"]
        assert user.handle == sample_user_data["handle"]
        assert user.display_name == sample_user_data["display_name"]
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_default_values(self, db_session):
        """Test User model default values."""
        user = User(
            id="test-uid-defaults-12345678",
            email="defaults@example.com",
            handle="defaultuser",
            display_name="Default User",
            city_id=1,
            primary_user_type=1,
            birth_date=datetime(1990, 1, 1).date(),
            country_code="US",
            tos_accepted_at=datetime.now()
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Check default values
        assert user.has_tattoos is False
        assert user.has_piercings is False
        assert user.profile_data == {}
        assert user.availability_data == {}
        assert user.privacy_settings == {
            "show_city": False,
            "show_country": True,
            "show_age": True
        }

    def test_user_repr(self, db_session, sample_user_data):
        """Test User __repr__ method."""
        user = User(**sample_user_data)
        
        repr_str = str(user)
        
        assert sample_user_data["handle"] in repr_str
        assert sample_user_data["display_name"] in repr_str
        assert "User" in repr_str

    def test_user_type_properties(self):
        """Test user type checking properties."""
        # Mock user type relationships
        photographer_type = Mock()
        photographer_type.type_name = "photographer"
        
        model_type = Mock()
        model_type.type_name = "model"
        
        # Test photographer
        user = User(
            id="test-photographer-123456789",
            email="photo@example.com",
            handle="photographer",
            display_name="Test Photographer",
            city_id=1,
            primary_user_type=1,
            birth_date=datetime(1985, 1, 1).date(),
            country_code="US",
            tos_accepted_at=datetime.now()
        )
        user.user_type = photographer_type
        
        assert user.is_photographer is True
        assert user.is_model is False
        
        # Test model
        user.user_type = model_type
        
        assert user.is_photographer is False
        assert user.is_model is True

    def test_location_display_with_privacy(self):
        """Test location display respects privacy settings."""
        # Mock city relationship
        mock_city = Mock()
        mock_city.name = "New York"
        mock_city.country = "USA"
        
        user = User(
            id="test-location-1234567890",
            email="location@example.com",
            handle="locationuser",
            display_name="Location User",
            city_id=1,
            primary_user_type=1,
            birth_date=datetime(1990, 1, 1).date(),
            country_code="US",
            tos_accepted_at=datetime.now()
        )
        user.city = mock_city
        
        # Test showing country only (default)
        user.privacy_settings = {"show_city": False, "show_country": True}
        assert user.location_display == "USA"
        
        # Test showing city and country
        user.privacy_settings = {"show_city": True, "show_country": True}
        assert user.location_display == "New York, USA"
        
        # Test no city data
        user.city = None
        assert user.location_display == "Unknown"

    def test_model_validation_requirements(self):
        """Test model-specific field validation."""
        # Mock model type
        model_type = Mock()
        model_type.type_name = "model"
        
        user = User(
            id="test-model-12345678901234",
            email="model@example.com",
            handle="testmodel",
            display_name="Test Model",
            city_id=1,
            primary_user_type=1,
            birth_date=datetime(1995, 1, 1).date(),
            country_code="US",
            tos_accepted_at=datetime.now()
        )
        user.user_type = model_type
        
        # Test incomplete model data
        user.gender = "Female"
        user.age = 25
        user.height_cm = None  # Missing
        user.weight_kg = None  # Missing
        
        mandatory_fields = user.get_mandatory_model_fields()
        assert mandatory_fields["gender"] == "Female"
        assert mandatory_fields["age"] == 25
        assert mandatory_fields["height_cm"] is None
        assert mandatory_fields["weight_kg"] is None
        
        # Should fail validation
        assert user.validate_model_requirements() is False
        
        # Complete model data
        user.height_cm = 175
        user.weight_kg = 60
        
        # Should pass validation
        assert user.validate_model_requirements() is True

    def test_photographer_validation_requirements(self):
        """Test photographer doesn't need model-specific fields."""
        # Mock photographer type
        photographer_type = Mock()
        photographer_type.type_name = "photographer"
        
        user = User(
            id="test-photographer-validation",
            email="photovalidation@example.com",
            handle="photouser",
            display_name="Photo User",
            city_id=1,
            primary_user_type=1,
            birth_date=datetime(1988, 1, 1).date(),
            country_code="US",
            tos_accepted_at=datetime.now()
        )
        user.user_type = photographer_type
        
        # Photographer should always pass validation
        assert user.validate_model_requirements() is True
        
        # Even with no model-specific data
        assert user.get_mandatory_model_fields() == {}


@pytest.mark.unit
class TestUserPydanticModels:
    """Test User Pydantic models for API serialization."""

    def test_create_user_request_validation(self):
        """Test CreateUserRequest validation."""
        # Valid photographer request
        photographer_request = CreateUserRequest(
            handle="photographer_jane",
            display_name="Jane Smith",
            bio="Professional portrait photographer",
            city_id=1,
            user_type=UserType.PHOTOGRAPHER,
            photography_styles=[PhotographyStyle.PORTRAIT, PhotographyStyle.FASHION]
        )
        
        assert photographer_request.handle == "photographer_jane"
        assert photographer_request.user_type == UserType.PHOTOGRAPHER
        assert len(photographer_request.photography_styles) == 2

        # Valid model request
        model_request = CreateUserRequest(
            handle="model_sarah",
            display_name="Sarah Johnson",
            bio="Fashion and artistic model",
            city_id=2,
            user_type=UserType.MODEL,
            gender="Female",
            age=24,
            height_cm=175,
            weight_kg=58
        )
        
        assert model_request.user_type == UserType.MODEL
        assert model_request.gender == "Female"
        assert model_request.age == 24

    def test_create_user_request_validation_errors(self):
        """Test CreateUserRequest validation errors."""
        # Handle too short
        with pytest.raises(ValueError):
            CreateUserRequest(
                handle="ab",  # Too short
                display_name="Test User",
                city_id=1,
                user_type=UserType.PHOTOGRAPHER
            )
        
        # Age out of range
        with pytest.raises(ValueError):
            CreateUserRequest(
                handle="testuser",
                display_name="Test User",
                city_id=1,
                user_type=UserType.MODEL,
                age=17  # Too young
            )
        
        # Height out of range
        with pytest.raises(ValueError):
            CreateUserRequest(
                handle="testuser",
                display_name="Test User",
                city_id=1,
                user_type=UserType.MODEL,
                height_cm=300  # Too tall
            )

    def test_update_user_request_validation(self):
        """Test UpdateUserRequest validation."""
        # Valid update
        update_request = UpdateUserRequest(
            display_name="Updated Name",
            bio="Updated bio",
            age=26,
            privacy_settings={"show_city": True}
        )
        
        assert update_request.display_name == "Updated Name"
        assert update_request.bio == "Updated bio"
        assert update_request.age == 26
        assert update_request.privacy_settings["show_city"] is True

    def test_user_profile_models(self):
        """Test user profile response models."""
        # Public profile
        public_profile = UserProfilePublic(
            id="test-user-id",
            handle="testuser",
            display_name="Test User",
            bio="Test bio",
            city_name="New York",
            user_type="photographer",
            photography_styles=["portrait", "fashion"],
            portfolio_count=15,
            is_verified=True
        )
        
        assert public_profile.id == "test-user-id"
        assert public_profile.handle == "testuser"
        assert public_profile.portfolio_count == 15
        
        # Private profile extends public
        private_profile = UserProfilePrivate(
            id="test-user-id",
            handle="testuser",
            display_name="Test User",
            user_type="photographer",
            email="test@example.com",
            firebase_uid="firebase-uid-123",
            privacy_settings={"show_city": False}
        )
        
        assert private_profile.email == "test@example.com"
        assert private_profile.firebase_uid == "firebase-uid-123"

    def test_user_search_query_validation(self):
        """Test UserSearchQuery validation."""
        # Valid search query
        search_query = UserSearchQuery(
            query="fashion photographer",
            user_type=UserType.PHOTOGRAPHER,
            city_id=1,
            photography_styles=[PhotographyStyle.FASHION, PhotographyStyle.PORTRAIT],
            max_distance_km=50,
            page=2,
            limit=10
        )
        
        assert search_query.query == "fashion photographer"
        assert search_query.user_type == UserType.PHOTOGRAPHER
        assert search_query.max_distance_km == 50
        assert search_query.page == 2
        assert search_query.limit == 10

    def test_user_search_query_defaults(self):
        """Test UserSearchQuery default values."""
        # Minimal search query
        search_query = UserSearchQuery()
        
        assert search_query.query is None
        assert search_query.user_type is None
        assert search_query.page == 1
        assert search_query.limit == 20

    def test_photography_style_enum(self):
        """Test PhotographyStyle enum values."""
        assert PhotographyStyle.PORTRAIT == "portrait"
        assert PhotographyStyle.FASHION == "fashion"
        assert PhotographyStyle.ARTISTIC_NUDE == "artistic_nude"
        assert PhotographyStyle.COMMERCIAL == "commercial"
        assert PhotographyStyle.LIFESTYLE == "lifestyle"
        assert PhotographyStyle.FITNESS == "fitness"
        assert PhotographyStyle.POLE_DANCE == "pole_dance"
        assert PhotographyStyle.BIKINI == "bikini"

    def test_user_type_enum(self):
        """Test UserType enum values."""
        assert UserType.PHOTOGRAPHER == "photographer"
        assert UserType.MODEL == "model"