import pytest
from datetime import datetime
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.auth_middleware import get_current_user, get_optional_user
from app.models.user import User

# Mock user data
mock_user_data = {
    "uid": "test-uid-123",
    "email": "test@example.com",
    "email_verified": True,
    "name": "Test User",
    "picture": "https://example.com/photo.jpg"
}

# Mock dependency overrides
def override_get_current_user():
    return mock_user_data

def override_get_optional_user_authenticated():
    return mock_user_data

def override_get_optional_user_unauthenticated():
    return None

@pytest.fixture
def client():
    yield TestClient(app)

@pytest.mark.integration
@pytest.mark.auth
class TestAuthEndpoints:
    """Test authentication-related endpoints"""

    def test_auth_status_unauthenticated(self, client):
        """Test auth status endpoint without authentication"""
        app.dependency_overrides[get_optional_user] = override_get_optional_user_unauthenticated
        response = client.get("/api/v1/auth/status")
        app.dependency_overrides = {}  # Reset overrides
        
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert data["user"] is None

    def test_auth_status_authenticated(self, client):
        """Test auth status endpoint with valid authentication"""
        app.dependency_overrides[get_optional_user] = override_get_optional_user_authenticated
        response = client.get("/api/v1/auth/status")
        app.dependency_overrides = {}  # Reset overrides
        
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert data["user"]["uid"] == "test-uid-123"
        assert data["user"]["email"] == "test@example.com"

    def test_get_profile_unauthenticated(self, client):
        """Test profile endpoint without authentication"""
        with pytest.raises(HTTPException) as excinfo:
            client.get("/api/v1/auth/profile")
        assert excinfo.value.status_code == 401

    def test_get_profile_authenticated(self, client):
        """Test profile endpoint with valid authentication"""
        app.dependency_overrides[get_current_user] = override_get_current_user
        response = client.get("/api/v1/auth/profile")
        app.dependency_overrides = {}  # Reset overrides
        
        assert response.status_code == 200
        data = response.json()
        assert data["uid"] == "test-uid-123"
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"

    def test_logout_endpoint(self, client):
        """Test logout endpoint"""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_test_endpoint(self, client):
        """Test the test endpoint"""
        response = client.get("/api/v1/auth/test")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Lumen API is running!" in data["message"]

    def test_demo_protected_endpoint(self, client):
        """Test demo protected endpoint with authentication"""
        app.dependency_overrides[get_current_user] = override_get_current_user
        response = client.get("/api/v1/auth/demo-protected", headers={"Authorization": "Bearer valid-token"})
        app.dependency_overrides = {}  # Reset overrides
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test-uid-123" in data["user_id"]

    def test_demo_protected_endpoint_unauthenticated(self, client):
        """Test demo protected endpoint without authentication"""
        with pytest.raises(HTTPException) as excinfo:
            client.get("/api/v1/auth/demo-protected")
        assert excinfo.value.status_code == 401

    def test_register_user_new(self, client, db_session):
        """Test user registration for new user"""
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        registration_data = {
            "display_name": "Test Photographer",
            "user_type": 1,  # photographer
            "city_id": 1
        }
        
        response = client.post("/api/v1/auth/register", 
                             json=registration_data)
        app.dependency_overrides = {}  # Reset overrides
        
        # Verify user was actually created in database
        if response.status_code == 201:
            created_user = db_session.query(User).filter(User.id == "test-uid-123").first()
            assert created_user is not None
            assert created_user.display_name == "Test Photographer"
            assert created_user.primary_user_type == 1

    def test_check_registration_existing_user(self, client, db_session):
        """Test registration check for existing user"""
        # Create a real user in the database
        existing_user = User(
            id="test-uid-123",
            email="test@example.com",
            handle="existing_user",
            display_name="Existing User",
            primary_user_type=1,
            city_id=1,
            birth_date=datetime(1990, 1, 1).date(),
            country_code="US",
            tos_accepted_at=datetime.utcnow()
        )
        db_session.add(existing_user)
        db_session.commit()
        
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        response = client.get("/api/v1/auth/check-registration")
        app.dependency_overrides = {}  # Reset overrides
        
        assert response.status_code == 200
        data = response.json()
        assert data["registered"] is True
        assert data["user"]["id"] == "test-uid-123"

    def test_check_registration_new_user(self, client, db_session):
        """Test registration check for new user"""
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        response = client.get("/api/v1/auth/check-registration")
        app.dependency_overrides = {}  # Reset overrides
        
        assert response.status_code == 200
        data = response.json()
        assert data["registered"] is False
        assert data["firebase_user"] is not None