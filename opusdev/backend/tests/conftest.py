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


# Test Database Configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
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
def mock_cloud_storage():
    """Mock Google Cloud Storage for testing."""
    mock_storage = Mock()
    mock_bucket = Mock()
    mock_blob = Mock()
    
    # Configure mock behavior
    mock_storage.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.upload_from_file.return_value = None
    mock_blob.generate_signed_url.return_value = "https://mock-signed-url.com/test-photo.jpg"
    mock_blob.public_url = "https://mock-public-url.com/test-photo.jpg"
    
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
    yield
    # Cleanup
    if "TESTING" in os.environ:
        del os.environ["TESTING"]


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