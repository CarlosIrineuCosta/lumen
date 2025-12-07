"""
Test configuration and fixtures for Lumen backend tests.

This module provides common test fixtures and configuration
for all backend test suites.
"""

import os
import sys
import pytest
from unittest.mock import Mock, MagicMock

# Add the backend directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_test_environment():
    """Set up mock environment variables for testing"""
    test_env_vars = {
        'DATABASE_URL': 'sqlite:///:memory:',
        'DB_POOL_SIZE': '5',
        'DB_MAX_OVERFLOW': '10',
        'DB_POOL_TIMEOUT': '15',
        'DB_POOL_RECYCLE': '1800',
        'REDIS_URL': 'redis://localhost:6379',
        'STORAGE_PATH': '/tmp/lumen-test-storage',
        'ENVIRONMENT': 'test',
        'DEBUG': 'false'
    }

    # Set environment variables
    original_env = {}
    for key, value in test_env_vars.items():
        original_env[key] = os.getenv(key)
        os.environ[key] = value

    yield

    # Restore original environment variables
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def mock_firebase_user():
    """Create a mock Firebase user for testing"""
    return Mock(
        uid="test_firebase_uid_123",
        email="test@example.com",
        name="Test User",
        picture="https://example.com/avatar.jpg"
    )


@pytest.fixture
def mock_auth_user():
    """Create a mock authenticated user"""
    from app.auth_middleware import AuthUser
    return AuthUser(
        uid="test_uid_123",
        email="test@example.com",
        name="Test User",
        verified=True
    )


@pytest.fixture
def sample_photo_data():
    """Create sample photo data for testing"""
    return {
        'id': 'test_photo_id',
        'title': 'Test Photo',
        'description': 'A test photo',
        'image_url': 'https://example.com/photo.jpg',
        'thumbnail_url': 'https://example.com/thumb.jpg',
        'user_id': 'test_user_id',
        'user_tags': ['test', 'sample'],
        'ai_tags': ['outdoor', 'nature'],
        'camera_data': {
            'make': 'Canon',
            'model': 'EOS 5D',
            'exposure_time': '1/125',
            'aperture': 'f/2.8'
        },
        'is_public': True,
        'is_portfolio': False,
        'location_name': 'Test City',
        'city_id': 1
    }


@pytest.fixture
def mock_create_photo_request():
    """Create a mock CreatePhotoRequest for testing"""
    from app.models.photo import CreatePhotoRequest
    return CreatePhotoRequest(
        title="Test Photo Upload",
        description="A test photo upload",
        user_tags=["test", "upload"],
        is_collaborative=False,
        model_release_status="not_required",
        content_rating="general",
        is_public=True,
        is_portfolio=False,
        camera_data={
            "make": "Test Camera",
            "model": "Test Model"
        },
        city_id=1,
        location_name="Test Location"
    )


@pytest.fixture
def mock_storage_backend():
    """Create a mock storage backend for testing"""
    storage = Mock()
    storage.store_image = Mock(return_value=Mock(
        urls={
            'original': 'https://example.com/original.jpg',
            'thumb': 'https://example.com/thumb.jpg',
            'large': 'https://example.com/large.jpg'
        },
        metadata=Mock(
            filename='stored_image.jpg',
            file_size=1024000,
            width=1920,
            height=1080
        )
    ))
    storage.get_image_urls = Mock(return_value={
        'original': 'https://example.com/original.jpg',
        'thumb': 'https://example.com/thumb.jpg',
        'large': 'https://example.com/large.jpg'
    })
    storage.delete_image = Mock(return_value=True)
    storage.health_check = Mock(return_value={'healthy': True})
    storage.get_metrics = Mock(return_value=Mock(upload_time=0.1, processing_time=0.5))
    return storage


# Test database setup
@pytest.fixture(scope="session")
def test_db():
    """Create test database session"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create all tables
    from app.database.connection import Base
    Base.metadata.create_all(bind=engine)

    yield TestingSessionLocal()

    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Create database session for testing"""
    session = test_db()
    try:
        yield session
    finally:
        session.close()


# Mock Redis for testing
@pytest.fixture
def mock_redis_client():
    """Create a mock Redis client for testing"""
    redis_mock = Mock()
    redis_mock.ping = Mock(return_value=True)
    redis_mock.get = Mock(return_value=None)
    redis_mock.set = Mock(return_value=True)
    redis_mock.setex = Mock(return_value=True)
    redis_mock.delete = Mock(return_value=1)
    redis_mock.exists = Mock(return_value=False)
    redis_mock.keys = Mock(return_value=[])
    redis_mock.info = Mock(return_value={
        'used_memory': 1024000,
        'uptime_in_seconds': 3600
    })
    return redis_mock


# Logging configuration for tests
@pytest.fixture(autouse=True)
def configure_test_logging():
    """Configure logging for tests"""
    import logging
    # Set logging level to INFO for tests
    logging.getLogger().setLevel(logging.INFO)


# Disable actual network requests during testing
@pytest.fixture(autouse=True)
def disable_network_requests(monkeypatch):
    """Disable actual network requests during testing"""
    def mock_request(*args, **kwargs):
        raise Exception("Network requests disabled in tests")

    # Mock common HTTP clients
    monkeypatch.setattr("requests.get", mock_request)
    monkeypatch.setattr("requests.post", mock_request)
    monkeypatch.setattr("requests.put", mock_request)
    monkeypatch.setattr("requests.delete", mock_request)


# Custom markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "database: mark test as database dependent"
    )


# Helper functions for tests
def create_mock_city(city_id=1, name="Test City", country="Test Country"):
    """Create a mock City object"""
    city = Mock()
    city.id = city_id
    city.name = name
    city.country = country
    return city


def create_mock_user(user_id="test_user", email="test@example.com", name="Test User"):
    """Create a mock User object"""
    user = Mock()
    user.id = user_id
    user.email = email
    user.name = name
    user.display_name = name
    user.handle = "test_user"
    return user


def create_mock_photo(photo_id="test_photo", user_id="test_user", title="Test Photo"):
    """Create a mock Photo object"""
    photo = Mock()
    photo.id = photo_id
    photo.user_id = user_id
    photo.title = title
    photo.description = "Test description"
    photo.is_public = True
    photo.is_portfolio = False
    photo.user_tags = ["test"]
    photo.ai_tags = ["outdoor"]
    photo.upload_date = "2024-01-01T00:00:00Z"
    photo.camera_data = {"make": "Test", "model": "Camera"}
    photo.location_name = "Test Location"
    return photo