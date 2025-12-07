"""
Global pytest configuration and fixtures for Lumen backend tests.

This file provides shared fixtures and configuration for all tests.
Fixtures defined here are available to all test modules automatically.
"""

import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, MagicMock

import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import your app components
from app.main import app
from app.database.connection import get_db
from app.models.user import Base as UserBase
from app.models.photo import Base as PhotoBase


# PostgreSQL Test Database Configuration
# Use PostgreSQL for tests to match production environment
TEST_DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
TEST_DB_PORT = os.getenv("TEST_DB_PORT", "5432")
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "lumen_test")
TEST_DB_USER = os.getenv("TEST_DB_USER", "postgres")
TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "")

SQLALCHEMY_DATABASE_URL = f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    # Create all tables
    UserBase.metadata.create_all(bind=engine)
    PhotoBase.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        UserBase.metadata.drop_all(bind=engine)
        PhotoBase.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client with database session override."""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(db_session):
    """Create an async test client for async endpoint testing."""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with httpx.AsyncClient(app=app, base_url="http://test") as async_test_client:
        yield async_test_client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def mock_firebase_auth():
    """Mock Firebase authentication for testing."""
    mock_auth = Mock()
    mock_auth.verify_id_token.return_value = {
        'uid': 'test-firebase-uid-123',
        'email': 'test@example.com',
        'email_verified': True
    }
    return mock_auth


@pytest.fixture
def mock_storage_service():
    """Mock local storage service for testing."""
    from app.storage.interfaces import IStorageService, StoredImage
    
    mock_storage = Mock(spec=IStorageService)
    
    # Configure mock behavior for local storage
    mock_storage.store_image.return_value = StoredImage(
        original_path="/mock/path/original.jpg",
        urls={
            "original": "https://lumenphotos.com/storage/photos/test-user/test-photo.jpg",
            "thumb": "https://lumenphotos.com/storage/photos/test-user/test-photo_thumb.jpg",
            "small": "https://lumenphotos.com/storage/photos/test-user/test-photo_small.jpg",
            "medium": "https://lumenphotos.com/storage/photos/test-user/test-photo_medium.jpg",
            "large": "https://lumenphotos.com/storage/photos/test-user/test-photo_large.jpg"
        }
    )
    
    mock_storage.get_image_urls.return_value = {
        "original": "https://lumenphotos.com/storage/photos/test-user/test-photo.jpg",
        "thumb": "https://lumenphotos.com/storage/photos/test-user/test-photo_thumb.jpg"
    }
    
    mock_storage.delete_image.return_value = True
    
    return mock_storage


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "firebase_uid": "test-firebase-uid-123",
        "email": "test@example.com",
        "handle": "testuser",
        "display_name": "Test User",
        "city_id": 1,
        "primary_user_type": 1,
        "bio": "Test photographer",
        "profile_data": {"portfolio_url": "https://example.com"}
    }


@pytest.fixture
def sample_photo_data():
    """Sample photo data for testing."""
    return {
        "title": "Test Photo",
        "description": "A test photo for unit testing",
        "image_url": "https://example.com/test-photo.jpg",
        "thumbnail_url": "https://example.com/test-photo-thumb.jpg",
        "camera_data": {
            "make": "Canon",
            "model": "EOS R5",
            "settings": {
                "iso": 100,
                "aperture": 2.8,
                "shutter": "1/60",
                "focal_length": 50
            }
        },
        "user_tags": ["portrait", "studio"],
        "is_public": True
    }


@pytest.fixture
def auth_headers():
    """Create authorization headers for testing protected endpoints."""
    return {
        "Authorization": "Bearer test-firebase-token-123"
    }


@pytest.fixture
def mock_file_upload():
    """Mock file upload for photo testing."""
    mock_file = Mock()
    mock_file.filename = "test-photo.jpg"
    mock_file.content_type = "image/jpeg"
    mock_file.size = 1024 * 1024  # 1MB
    mock_file.file = Mock()
    mock_file.file.read.return_value = b"fake image data"
    return mock_file


# Environment setup for tests
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = SQLALCHEMY_DATABASE_URL
    os.environ["STORAGE_MODE"] = "local"
    os.environ["STORAGE_BASE_PATH"] = "/tmp/test_storage"
    os.environ["STORAGE_BASE_URL"] = "https://lumenphotos.com/storage"
    os.environ["ENABLE_REDIS_CACHE"] = "false"
    yield
    # Cleanup
    test_env_vars = ["TESTING", "STORAGE_MODE", "STORAGE_BASE_PATH", "STORAGE_BASE_URL", "ENABLE_REDIS_CACHE"]
    for var in test_env_vars:
        if var in os.environ:
            del os.environ[var]


# Pytest hooks for custom behavior
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as authentication-related"
    )
    config.addinivalue_line(
        "markers", "photos: mark test as photo-related"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "external: mark test as requiring external services"
    )