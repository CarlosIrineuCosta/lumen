"""
Unit tests for enhanced user profile functionality.

Tests the new user profile fields including artistic statement,
availability data, location preferences, and profile image handling.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from app.models.user import (
    UpdateUserRequest, UserProfileFull, UserProfilePublic,
    ProfileImageData, AvailabilityData, ContactPreferences,
    UserType, PhotographyStyle, ExperienceLevel, LocationPreference, ProfileImageSource
)


@pytest.mark.unit
class TestEnhancedUserModels:
    """Test enhanced user profile models and validation."""

    def test_update_user_request_with_artistic_statement(self):
        """Test UpdateUserRequest with artistic statement fields."""
        update_request = UpdateUserRequest(
            display_name="Jane Photographer",
            artistic_statement="I believe photography is about capturing authentic human connections through natural light and genuine emotions.",
            tagline="Natural Light Portraits • NYC Based • Available for Travel",
            mission_statement="Creating timeless portraits that tell each person's unique story",
            bio="Professional portrait photographer specializing in natural light",
            experience_level=ExperienceLevel.PROFESSIONAL,
            experience_years=8,
            photography_styles=[PhotographyStyle.PORTRAIT, PhotographyStyle.LIFESTYLE],
            website="https://janephotography.com",
            social_links={
                "instagram": "@jane_photography",
                "website": "https://janephotography.com"
            }
        )
        
        assert update_request.artistic_statement.startswith("I believe photography")
        assert update_request.tagline == "Natural Light Portraits • NYC Based • Available for Travel"
        assert update_request.experience_level == ExperienceLevel.PROFESSIONAL
        assert update_request.experience_years == 8
        assert len(update_request.photography_styles) == 2

    def test_update_user_request_photographer_specific(self):
        """Test photographer-specific fields in UpdateUserRequest."""
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
        
        assert len(update_request.camera_gear) == 4
        assert "Canon EOS R5" in update_request.camera_gear
        assert update_request.studio_access is True
        assert update_request.rates["hourly_rate"] == 150
        assert update_request.rates["rate_negotiable"] is True

    def test_update_user_request_model_specific(self):
        """Test model-specific fields in UpdateUserRequest."""
        update_request = UpdateUserRequest(
            gender="Female",
            age=25,
            height_cm=175,
            weight_kg=60,
            modeling_types=["fashion", "commercial", "artistic"],
            comfortable_with=["lingerie", "swimwear", "fashion"],
            special_skills=["dance", "yoga", "acting"],
            rates={
                "minimum_rate": 100,
                "currency": "USD"
            }
        )
        
        assert update_request.gender == "Female"
        assert update_request.age == 25
        assert len(update_request.modeling_types) == 3
        assert "dance" in update_request.special_skills
        assert update_request.rates["minimum_rate"] == 100

    def test_update_user_request_studio_specific(self):
        """Test studio-specific fields in UpdateUserRequest."""
        update_request = UpdateUserRequest(
            studio_size_sqft=1200,
            included_equipment=["lighting_kit", "backdrops", "props", "changing_room"],
            hourly_rate=75.0,
            rates={
                "hourly_rate": 75,
                "minimum_booking_hours": 2,
                "deposit_required": True
            }
        )
        
        assert update_request.studio_size_sqft == 1200
        assert len(update_request.included_equipment) == 4
        assert update_request.hourly_rate == 75.0
        assert update_request.rates["minimum_booking_hours"] == 2

    def test_availability_data_validation(self):
        """Test AvailabilityData model validation."""
        availability = AvailabilityData(
            open_for_work=True,
            available_for_travel=True,
            travel_range_km=200,
            travel_internationally=False,
            travel_notes="Available for weekend shoots outside the city",
            location_preferences=[LocationPreference.STUDIO, LocationPreference.OUTDOOR],
            available_days=["monday", "tuesday", "weekend"],
            available_times=["morning", "afternoon"],
            timezone="America/New_York"
        )
        
        assert availability.open_for_work is True
        assert availability.travel_range_km == 200
        assert availability.travel_notes.startswith("Available for weekend")
        assert LocationPreference.STUDIO in availability.location_preferences
        assert "morning" in availability.available_times

    def test_availability_data_travel_range_validation(self):
        """Test travel range validation in AvailabilityData."""
        # Valid range
        availability = AvailabilityData(travel_range_km=500)
        assert availability.travel_range_km == 500
        
        # Test that very high ranges would be caught by validation
        with pytest.raises(ValueError):
            AvailabilityData(travel_range_km=10000)  # Too high

    def test_contact_preferences_validation(self):
        """Test ContactPreferences model validation."""
        preferences = ContactPreferences(
            preferred_contact="email",
            response_time="within_24h",
            booking_lead_time="1_week",
            allow_direct_booking=True,
            require_references=False
        )
        
        assert preferences.preferred_contact == "email"
        assert preferences.response_time == "within_24h"
        assert preferences.allow_direct_booking is True
        assert preferences.require_references is False

    def test_profile_image_data_validation(self):
        """Test ProfileImageData model validation."""
        profile_image = ProfileImageData(
            current_source=ProfileImageSource.UPLOADED,
            uploaded_image_url="https://storage.googleapis.com/bucket/users/uuid/profile.jpg",
            gmail_image_url="https://lh3.googleusercontent.com/example",
            upload_date=datetime.now(),
            image_verified=True
        )
        
        assert profile_image.current_source == ProfileImageSource.UPLOADED
        assert profile_image.uploaded_image_url.startswith("https://storage.googleapis.com")
        assert profile_image.image_verified is True
        assert profile_image.upload_date is not None

    def test_profile_image_data_defaults(self):
        """Test ProfileImageData default values."""
        profile_image = ProfileImageData()
        
        assert profile_image.current_source == ProfileImageSource.GMAIL
        assert profile_image.uploaded_image_url is None
        assert profile_image.image_verified is False

    def test_enhanced_user_profile_public(self):
        """Test enhanced UserProfilePublic with new fields."""
        profile = UserProfilePublic(
            id="user-123",
            handle="jane_photographer",
            display_name="Jane Smith",
            bio="Professional portrait photographer",
            user_type="photographer",
            artistic_statement="I capture authentic human connections through natural light",
            tagline="Natural Light Portraits • NYC Based",
            experience_level="professional",
            experience_years=8,
            specializes_in=["portraits", "lifestyle"],
            open_for_work=True,
            available_for_travel=True,
            location_preferences=["studio", "outdoor"],
            website="https://janephotography.com"
        )
        
        assert profile.id == "user-123"
        assert profile.artistic_statement.startswith("I capture authentic")
        assert profile.tagline.endswith("NYC Based")
        assert profile.experience_level == "professional"
        assert profile.open_for_work is True
        assert len(profile.specializes_in) == 2
        assert "studio" in profile.location_preferences

    def test_enhanced_user_profile_full(self):
        """Test enhanced UserProfileFull with private fields."""
        profile = UserProfileFull(
            id="user-123",
            handle="jane_photographer",
            display_name="Jane Smith",
            email="jane@example.com",
            firebase_uid="firebase-uid-123",
            user_type="photographer",
            city_id=1,
            profile_completion=85,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            mission_statement="Creating timeless portraits that tell stories",
            camera_gear=["Canon EOS R5", "50mm f/1.4"],
            rates={"hourly_rate": 150, "day_rate": 800},
            social_links={"instagram": "@jane_photography"},
            availability_data={
                "open_for_work": True,
                "travel_range_km": 200
            },
            contact_preferences={
                "preferred_contact": "email",
                "response_time": "within_24h"
            }
        )
        
        assert profile.mission_statement.startswith("Creating timeless")
        assert len(profile.camera_gear) == 2
        assert profile.rates["hourly_rate"] == 150
        assert profile.availability_data["travel_range_km"] == 200
        assert profile.contact_preferences["preferred_contact"] == "email"

    def test_artistic_statement_max_length_validation(self):
        """Test artistic statement maximum length validation."""
        # Valid length
        short_statement = "I love photography."
        update_request = UpdateUserRequest(artistic_statement=short_statement)
        assert update_request.artistic_statement == short_statement
        
        # Test very long statement would be caught
        long_statement = "x" * 2001  # Over the 2000 character limit
        with pytest.raises(ValueError):
            UpdateUserRequest(artistic_statement=long_statement)

    def test_tagline_max_length_validation(self):
        """Test tagline maximum length validation."""
        # Valid tagline
        tagline = "Natural Light Portraits • NYC Based • Available for Travel"
        update_request = UpdateUserRequest(tagline=tagline)
        assert update_request.tagline == tagline
        
        # Test very long tagline would be caught
        long_tagline = "x" * 201  # Over the 200 character limit
        with pytest.raises(ValueError):
            UpdateUserRequest(tagline=long_tagline)

    def test_new_user_types_enum(self):
        """Test new user types in UserType enum."""
        assert UserType.PHOTOGRAPHER == "photographer"
        assert UserType.MODEL == "model"
        assert UserType.STUDIO == "studio"
        assert UserType.MAKEUP_ARTIST == "makeup_artist"
        assert UserType.STYLIST == "stylist"

    def test_expanded_photography_styles_enum(self):
        """Test expanded PhotographyStyle enum."""
        # Original styles
        assert PhotographyStyle.PORTRAIT == "portrait"
        assert PhotographyStyle.FASHION == "fashion"
        
        # New styles
        assert PhotographyStyle.BOUDOIR == "boudoir"
        assert PhotographyStyle.STREET == "street"
        assert PhotographyStyle.WEDDING == "wedding"
        assert PhotographyStyle.CORPORATE == "corporate"
        assert PhotographyStyle.DOCUMENTARY == "documentary"

    def test_experience_level_enum(self):
        """Test ExperienceLevel enum values."""
        assert ExperienceLevel.BEGINNER == "beginner"
        assert ExperienceLevel.AMATEUR == "amateur"
        assert ExperienceLevel.SEMI_PRO == "semi_pro"
        assert ExperienceLevel.PROFESSIONAL == "professional"
        assert ExperienceLevel.EXPERT == "expert"

    def test_location_preference_enum(self):
        """Test LocationPreference enum values."""
        assert LocationPreference.STUDIO == "studio"
        assert LocationPreference.OUTDOOR == "outdoor"
        assert LocationPreference.URBAN == "urban"
        assert LocationPreference.NATURE == "nature"
        assert LocationPreference.HOME == "home"

    def test_profile_image_source_enum(self):
        """Test ProfileImageSource enum values."""
        assert ProfileImageSource.GMAIL == "gmail"
        assert ProfileImageSource.UPLOADED == "uploaded"
        assert ProfileImageSource.NONE == "none"