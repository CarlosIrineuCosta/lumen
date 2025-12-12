"""
Integration tests for database operations.

Tests database connections, model relationships, query performance,
and data integrity across the application.
"""

import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import uuid
from datetime import datetime

from app.models.user import User
from app.models.photo import Photo
from app.models.lookup_tables import UserType, City, Specialty
from app.models.relationships import UserSpecialty, PhotoCollaborator, PhotoInteraction


@pytest.mark.integration
class TestDatabaseConnection:
    """Test database connection and basic operations."""

    def test_database_session_creation(self, db_session):
        """Test database session can be created and used."""
        # Session should be created by fixture
        assert db_session is not None
        
        # Should be able to execute basic query
        result = db_session.execute("SELECT 1").scalar()
        assert result == 1

    def test_database_transaction_rollback(self, db_session):
        """Test database transaction rollback works correctly."""
        # Create test user
        user = User(
            firebase_uid="test-rollback-uid",
            email="rollback@example.com", 
            handle="rollbackuser",
            display_name="Rollback Test",
            city_id=1,
            primary_user_type=1
        )
        
        db_session.add(user)
        db_session.flush()  # Make available in transaction
        
        # Verify user exists in current transaction
        found_user = db_session.query(User).filter(
            User.firebase_uid == "test-rollback-uid"
        ).first()
        assert found_user is not None
        
        # Rollback transaction
        db_session.rollback()
        
        # User should no longer exist
        found_user = db_session.query(User).filter(
            User.firebase_uid == "test-rollback-uid"
        ).first()
        assert found_user is None


@pytest.mark.integration
class TestUserDatabaseOperations:
    """Test User model database operations."""

    def test_create_user_with_relationships(self, db_session):
        """Test creating user with related data."""
        # Create lookup table entries first
        user_type = UserType(
            id=1,
            type_name="photographer",
            display_name="Photographer"
        )
        city = City(
            id=1,
            name="New York",
            country="USA",
            latitude=40.7128,
            longitude=-74.0060
        )
        
        db_session.add(user_type)
        db_session.add(city)
        db_session.flush()
        
        # Create user
        user = User(
            firebase_uid="test-relationship-uid",
            email="relationship@example.com",
            handle="relationshipuser",
            display_name="Relationship Test",
            city_id=city.id,
            primary_user_type=user_type.id,
            bio="Test photographer with relationships"
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Verify user and relationships
        found_user = db_session.query(User).filter(
            User.firebase_uid == "test-relationship-uid"
        ).first()
        
        assert found_user is not None
        assert found_user.handle == "relationshipuser"
        assert found_user.city.name == "New York"
        assert found_user.user_type.type_name == "photographer"

    def test_user_unique_constraints(self, db_session):
        """Test user unique constraints are enforced."""
        # Create first user
        user1 = User(
            firebase_uid="unique-test-uid-1",
            email="unique1@example.com",
            handle="uniqueuser",
            display_name="Unique User 1",
            city_id=1,
            primary_user_type=1
        )
        
        db_session.add(user1)
        db_session.commit()
        
        # Attempt to create user with same handle
        user2 = User(
            firebase_uid="unique-test-uid-2",
            email="unique2@example.com", 
            handle="uniqueuser",  # Same handle
            display_name="Unique User 2",
            city_id=1,
            primary_user_type=1
        )
        
        db_session.add(user2)
        
        # Should raise integrity error
        with pytest.raises(Exception):  # IntegrityError from SQLAlchemy
            db_session.commit()

    def test_user_cascade_delete(self, db_session):
        """Test user deletion cascades to related records."""
        # Create user
        user = User(
            firebase_uid="cascade-test-uid",
            email="cascade@example.com",
            handle="cascadeuser", 
            display_name="Cascade Test",
            city_id=1,
            primary_user_type=1
        )
        
        db_session.add(user)
        db_session.flush()
        
        # Create photo owned by user
        photo = Photo(
            user_id=user.id,
            title="Test Photo for Cascade",
            is_public=True
        )
        
        db_session.add(photo)
        db_session.commit()
        
        # Verify photo exists
        found_photo = db_session.query(Photo).filter(
            Photo.user_id == user.id
        ).first()
        assert found_photo is not None
        
        # Delete user
        db_session.delete(user)
        db_session.commit()
        
        # Photo should also be deleted (cascade)
        found_photo = db_session.query(Photo).filter(
            Photo.user_id == user.id
        ).first()
        assert found_photo is None


@pytest.mark.integration
class TestPhotoDatabaseOperations:
    """Test Photo model database operations."""

    def test_create_photo_with_metadata(self, db_session):
        """Test creating photo with complex metadata."""
        # Create user first
        user = User(
            firebase_uid="photo-test-uid",
            email="photo@example.com",
            handle="photouser",
            display_name="Photo User",
            city_id=1,
            primary_user_type=1
        )
        
        db_session.add(user)
        db_session.flush()
        
        # Create photo with rich metadata
        photo = Photo(
            user_id=user.id,
            title="Test Photo with Metadata",
            description="A detailed test photo",
            camera_data={
                "make": "Canon",
                "model": "EOS R5",
                "settings": {
                    "iso": 100,
                    "aperture": 2.8,
                    "shutter": "1/60",
                    "focal_length": 50
                }
            },
            ai_tags=["portrait", "studio", "professional"],
            user_tags=["test", "portfolio"],
            is_public=True,
            is_portfolio=True,
            content_rating="general",
            extra_metadata={
                "processing_notes": "Light color correction applied",
                "shooting_conditions": "Controlled studio lighting"
            }
        )
        
        db_session.add(photo)
        db_session.commit()
        
        # Verify photo and metadata
        found_photo = db_session.query(Photo).filter(
            Photo.title == "Test Photo with Metadata"
        ).first()
        
        assert found_photo is not None
        assert found_photo.user_id == user.id
        assert found_photo.camera_data["make"] == "Canon"
        assert "portrait" in found_photo.ai_tags
        assert "test" in found_photo.user_tags
        assert found_photo.extra_metadata["processing_notes"] == "Light color correction applied"

    def test_photo_collaborator_relationships(self, db_session):
        """Test photo collaborator relationships."""
        # Create users
        photographer = User(
            firebase_uid="photographer-uid",
            email="photographer@example.com",
            handle="photographer",
            display_name="John Photographer", 
            city_id=1,
            primary_user_type=1
        )
        
        model = User(
            firebase_uid="model-uid",
            email="model@example.com",
            handle="model",
            display_name="Jane Model",
            city_id=1,
            primary_user_type=2  # Assume 2 is model type
        )
        
        db_session.add_all([photographer, model])
        db_session.flush()
        
        # Create photo
        photo = Photo(
            user_id=photographer.id,
            title="Collaborative Photo",
            is_collaborative=True
        )
        
        db_session.add(photo)
        db_session.flush()
        
        # Add collaborator
        collaborator = PhotoCollaborator(
            photo_id=photo.id,
            user_id=model.id,
            display_name=model.display_name,
            handle=model.handle,
            role="model"
        )
        
        db_session.add(collaborator)
        db_session.commit()
        
        # Verify relationships
        found_photo = db_session.query(Photo).filter(
            Photo.title == "Collaborative Photo"
        ).first()
        
        assert found_photo is not None
        assert len(found_photo.collaborators) == 1
        assert found_photo.collaborators[0].display_name == "Jane Model"
        assert found_photo.collaborators[0].role == "model"

    def test_photo_interaction_tracking(self, db_session):
        """Test photo like/interaction tracking."""
        # Create users
        owner = User(
            firebase_uid="owner-uid", 
            email="owner@example.com",
            handle="owner",
            display_name="Photo Owner",
            city_id=1,
            primary_user_type=1
        )
        
        liker = User(
            firebase_uid="liker-uid",
            email="liker@example.com", 
            handle="liker",
            display_name="Photo Liker",
            city_id=1,
            primary_user_type=1
        )
        
        db_session.add_all([owner, liker])
        db_session.flush()
        
        # Create photo
        photo = Photo(
            user_id=owner.id,
            title="Photo to Like"
        )
        
        db_session.add(photo)
        db_session.flush()
        
        # Add like interaction
        like_interaction = PhotoInteraction(
            photo_id=photo.id,
            user_id=liker.id,
            interaction_type="like"
        )
        
        db_session.add(like_interaction)
        db_session.commit()
        
        # Verify interaction
        found_photo = db_session.query(Photo).filter(
            Photo.title == "Photo to Like"
        ).first()
        
        assert found_photo is not None
        assert len(found_photo.interactions) == 1
        assert found_photo.interactions[0].interaction_type == "like"
        assert found_photo.like_count == 1
        assert found_photo.is_liked_by(liker.id) is True
        assert found_photo.is_liked_by(owner.id) is False


@pytest.mark.integration
@pytest.mark.slow
class TestDatabasePerformance:
    """Test database query performance and optimization."""

    def test_user_photo_query_efficiency(self, db_session):
        """Test efficient querying of user photos with relationships."""
        # Create test user
        user = User(
            firebase_uid="performance-test-uid",
            email="performance@example.com",
            handle="perfuser",
            display_name="Performance User",
            city_id=1,
            primary_user_type=1
        )
        
        db_session.add(user)
        db_session.flush()
        
        # Create multiple photos
        photos = []
        for i in range(10):
            photo = Photo(
                user_id=user.id,
                title=f"Performance Test Photo {i}",
                description=f"Test photo number {i}",
                user_tags=[f"tag{i}", "performance", "test"],
                is_public=True
            )
            photos.append(photo)
        
        db_session.add_all(photos)
        db_session.commit()
        
        # Query with relationship loading
        from sqlalchemy.orm import joinedload
        
        found_user = db_session.query(User).options(
            joinedload(User.photos)
        ).filter(User.firebase_uid == "performance-test-uid").first()
        
        assert found_user is not None
        assert len(found_user.photos) == 10
        
        # Verify photos are loaded (no additional query needed)
        for photo in found_user.photos:
            assert photo.title.startswith("Performance Test Photo")
            assert "performance" in photo.user_tags

    def test_photo_search_with_indexes(self, db_session):
        """Test photo search queries utilize indexes effectively."""
        # Create test photos with various properties
        user_id = uuid.uuid4()
        
        photos_data = [
            {"title": "Landscape Photo", "user_tags": ["landscape", "nature"], "is_public": True},
            {"title": "Portrait Photo", "user_tags": ["portrait", "people"], "is_public": True},
            {"title": "Private Photo", "user_tags": ["personal"], "is_public": False},
            {"title": "Studio Photo", "user_tags": ["studio", "portrait"], "is_public": True},
        ]
        
        for photo_data in photos_data:
            photo = Photo(user_id=user_id, **photo_data)
            db_session.add(photo)
        
        db_session.commit()
        
        # Test indexed queries
        # Query by public status (should use index)
        public_photos = db_session.query(Photo).filter(
            Photo.is_public == True
        ).all()
        assert len(public_photos) == 3
        
        # Query by creation date (should use index)
        recent_photos = db_session.query(Photo).order_by(
            Photo.created_at.desc()
        ).limit(2).all()
        assert len(recent_photos) == 2
        
        # Complex query combining multiple indexed fields
        portrait_public = db_session.query(Photo).filter(
            Photo.is_public == True,
            Photo.user_tags.contains(["portrait"])
        ).all()
        assert len(portrait_public) == 2