"""
Global pytest configuration and fixtures for Lumen backend tests.

This file provides shared fixtures and configuration for all tests.
Fixtures defined here are available to all test modules automatically.
"""

import os
import sys
import pytest
import asyncio
from typing import AsyncGenerator, Generator

# Add the backend directory to the sys.path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

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


# Test Database Configuration - Uses same database as main app (single database approach)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://lumen_dev:LumenDev2025!@localhost:5432/lumen_development")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=False  # Set to True for SQL debugging
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
    # Note: Tables are already created from production schema
    # No need to create/drop tables as they already exist with proper constraints
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        # Clean up any existing test data before test runs
        cleanup_test_data(session)
        yield session
    finally:
        # Clean up test data after each test
        cleanup_test_data(session)
        session.close()


def cleanup_test_data(session):
    """Clean up ONLY test data while preserving all real development data."""
    try:
        # Only delete records that are explicitly marked as test data
        # Use ONLY the test- prefix pattern to avoid affecting real data
        session.execute("DELETE FROM photo_interactions WHERE user_id LIKE 'test-%' OR photo_id IN (SELECT id FROM photos WHERE user_id LIKE 'test-%')")
        session.execute("DELETE FROM photo_collaborators WHERE photo_id IN (SELECT id FROM photos WHERE user_id LIKE 'test-%')")
        session.execute("DELETE FROM user_connections WHERE requester_id LIKE 'test-%' OR target_id LIKE 'test-%'")
        session.execute("DELETE FROM user_specialties WHERE user_id LIKE 'test-%'")
        session.execute("DELETE FROM photos WHERE user_id LIKE 'test-%'")
        session.execute("DELETE FROM users WHERE id LIKE 'test-%'")
        session.commit()
    except Exception as e:
        # If anything fails, rollback to avoid partial cleanup
        session.rollback()


@pytest.fixture
def client(db_session):
    """Create a test client with database session override."""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client - this should work with compatible httpx version
    test_client = TestClient(app)
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
    
    # Use transport parameter instead of app parameter for newer httpx
    from starlette.testclient import TestClient
    transport = httpx.ASGITransport(app=app)
    
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_test_client:
        yield async_test_client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def firebase_emulator():
    """Ensure Firebase emulator is configured for tests."""
    # The TESTING environment variable is already set in setup_test_environment
    # This will trigger emulator mode in firebase_config.py
    return {
        'auth_url': 'http://localhost:9099',
        'storage_url': 'http://localhost:9199',
        'project_id': 'demo-lumen-project'
    }


@pytest.fixture
def test_auth_token():
    """Create a test Firebase auth token using emulator."""
    # In real Firebase emulator, we would create actual test tokens
    # For now, return a test token structure that works with our auth system
    return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJ0ZXN0LWZpcmViYXNlLXVpZC0xMjMiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZX0.test"


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    from datetime import datetime, date
    return {
        "id": "test-firebase-uid-123456789",
        "email": "test@example.com",
        "handle": "testuser",
        "display_name": "Test User",
        "city_id": 1,
        "primary_user_type": 1,
        "birth_date": date(1990, 1, 1),
        "country_code": "US",
        "tos_accepted_at": datetime.now(),
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
def test_image_file(tmp_path):
    """Create a real test image file for upload testing."""
    import tempfile
    from io import BytesIO
    
    # Create a simple test image (1x1 pixel PNG)
    test_image_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00'
        b'\x00\x04\x00\x01\xdd\xb6\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    
    # Create temporary file
    test_file = tmp_path / "test-photo.png"
    test_file.write_bytes(test_image_data)
    
    return {
        'path': str(test_file),
        'filename': 'test-photo.png',
        'content_type': 'image/png',
        'data': test_image_data
    }


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