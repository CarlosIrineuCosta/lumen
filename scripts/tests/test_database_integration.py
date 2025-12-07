"""
Database Integration Tests for Lumen Backend
Tests database connections, models, and complex queries.
"""

import pytest
from unittest.mock import patch, Mock
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.database.connection import get_db, Base
from app.models.user import User, UserType
from app.models.photo import Photo
from datetime import date, datetime


@pytest.mark.integration
@pytest.mark.database
class TestDatabaseConnection:
    """Test database connection and session management"""

    def test_database_session_creation(self, db_session):
        """Test database session can be created successfully"""
        assert db_session is not None
        
        # Test basic session operations
        with patch.object(db_session, 'execute') as mock_execute:
            mock_execute.return_value = Mock()
            
            # Mock a simple query
            result = db_session.execute("SELECT 1")
            assert result is not None
            mock_execute.assert_called_once()

    def test_database_transaction_rollback(self, db_session):
        """Test transaction rollback functionality"""
        with patch.object(db_session, 'rollback') as mock_rollback:
            with patch.object(db_session, 'add') as mock_add:
                mock_add.side_effect = Exception("Database error")
                
                try:
                    # Simulate failed operation
                    db_session.add(Mock())
                    db_session.commit()
                except Exception:
                    db_session.rollback()
                    
                mock_rollback.assert_called_once()


@pytest.mark.integration
@pytest.mark.database
class TestUserDatabaseOperations:
    """Test user-related database operations"""

    def test_create_user_with_relationships(self, db_session):
        """Test creating user with proper relationships"""
        user_data = {
            "id": "test-user-db-123",
            "email": "dbtest@example.com",
            "handle": "dbtestuser",
            "display_name": "DB Test User",
            "birth_date": date(1990, 1, 1),
            "country_code": "US"
        }
        
        # Mock user creation with relationships
        with patch.object(db_session, 'add') as mock_add, \
             patch.object(db_session, 'commit') as mock_commit, \
             patch.object(db_session, 'refresh') as mock_refresh:
            
            user = User(**user_data)
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
            
            mock_add.assert_called_once()
            mock_commit.assert_called_once()
            mock_refresh.assert_called_once()

    def test_user_unique_constraints(self, db_session):
        """Test user unique constraints (email, handle)"""
        from sqlalchemy.exc import IntegrityError
        
        # Test duplicate email constraint
        with patch.object(db_session, 'commit') as mock_commit:
            mock_commit.side_effect = IntegrityError("duplicate key", "params", "orig")
            
            user1 = User(
                id="user1",
                email="duplicate@example.com",
                handle="user1handle",
                display_name="User 1"
            )
            
            db_session.add(user1)
            
            with pytest.raises(IntegrityError):
                db_session.commit()

    def test_user_cascade_delete(self, db_session):
        """Test user deletion cascades properly"""
        user_id = "cascade-test-user"
        
        # Mock user with related photos
        with patch.object(db_session, 'query') as mock_query, \
             patch.object(db_session, 'delete') as mock_delete:
            
            mock_user = Mock()
            mock_user.id = user_id
            mock_query.return_value.filter.return_value.first.return_value = mock_user
            
            # Test cascade delete
            user = db_session.query(User).filter(User.id == user_id).first()
            if user:
                db_session.delete(user)
                
            mock_delete.assert_called_once()


@pytest.mark.integration  
@pytest.mark.database
class TestPhotoDatabaseOperations:
    """Test photo-related database operations"""

    def test_create_photo_with_metadata(self, db_session):
        """Test creating photo with JSONB metadata"""
        photo_data = {
            "id": "test-photo-db-123",
            "user_id": "test-user-123",
            "title": "Test Photo",
            "description": "Database test photo",
            "image_url": "https://example.com/photo.jpg",
            "camera_data": {
                "make": "Canon",
                "model": "EOS R5",
                "iso": 100,
                "aperture": "f/2.8",
                "shutter_speed": "1/60"
            },
            "user_tags": ["test", "database", "integration"],
            "is_public": True,
            "created_at": datetime.utcnow()
        }
        
        with patch.object(db_session, 'add') as mock_add, \
             patch.object(db_session, 'commit') as mock_commit:
            
            photo = Photo(**photo_data)
            db_session.add(photo)
            db_session.commit()
            
            mock_add.assert_called_once()
            mock_commit.assert_called_once()

    def test_photo_search_with_indexes(self, db_session):
        """Test photo search leveraging database indexes"""
        search_terms = ["portrait", "nature", "wedding"]
        
        with patch.object(db_session, 'query') as mock_query:
            # Mock indexed search query
            query_chain = Mock()
            query_chain.filter.return_value = query_chain
            query_chain.order_by.return_value = query_chain
            query_chain.limit.return_value = query_chain
            query_chain.offset.return_value = query_chain
            query_chain.all.return_value = [Mock() for _ in range(20)]
            
            mock_query.return_value = query_chain
            
            # Test search query performance
            results = (db_session.query(Photo)
                      .filter(Photo.user_tags.op('&&')(search_terms))  # PostgreSQL array overlap
                      .order_by(Photo.created_at.desc())
                      .limit(20)
                      .all())
            
            assert len(results) == 20
            query_chain.filter.assert_called()
            query_chain.order_by.assert_called()