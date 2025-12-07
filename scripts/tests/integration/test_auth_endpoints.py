"""
Integration tests for authentication endpoints.

These tests verify the authentication API endpoints work correctly
with proper request/response handling, authentication middleware,
and error conditions.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient


@pytest.mark.integration
@pytest.mark.auth
class TestAuthEndpoints:
    """Test authentication API endpoints."""

    def test_auth_status_unauthenticated(self, client):
        """Test auth status endpoint returns correct response for unauthenticated user."""
        response = client.get("/api/v1/auth/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert data["user"] is None
        assert data["message"] == "User is not authenticated"

    @patch('app.auth_middleware.get_optional_user')
    def test_auth_status_authenticated(self, mock_get_user, client):
        """Test auth status endpoint returns user info when authenticated."""
        # Mock authenticated user
        mock_user_token = {
            'uid': 'test-firebase-uid-123',
            'email': 'test@example.com',
            'email_verified': True,
            'name': 'Test User',
            'picture': 'https://example.com/avatar.jpg'
        }
        mock_get_user.return_value = mock_user_token
        
        response = client.get("/api/v1/auth/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert data["user"]["uid"] == 'test-firebase-uid-123'
        assert data["user"]["email"] == 'test@example.com'
        assert data["user"]["email_verified"] is True
        assert data["message"] == "User is authenticated"

    def test_get_profile_unauthenticated(self, client):
        """Test protected profile endpoint rejects unauthenticated requests."""
        response = client.get("/api/v1/auth/profile")
        
        # Should return 401 Unauthorized (handled by auth middleware)
        assert response.status_code == 401

    @patch('app.auth_middleware.get_current_user')
    def test_get_profile_authenticated(self, mock_get_user, client):
        """Test profile endpoint returns user data when authenticated."""
        # Mock authenticated user
        mock_user_token = {
            'uid': 'test-firebase-uid-123',
            'email': 'test@example.com',
            'email_verified': True,
            'name': 'Test User',
            'picture': 'https://example.com/avatar.jpg'
        }
        mock_get_user.return_value = mock_user_token
        
        response = client.get("/api/v1/auth/profile")
        
        assert response.status_code == 200
        data = response.json()
        assert data["uid"] == 'test-firebase-uid-123'
        assert data["email"] == 'test@example.com'
        assert data["name"] == 'Test User'

    def test_logout_endpoint(self, client):
        """Test logout endpoint (client-side token removal)."""
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logged out successfully"

    def test_test_endpoint(self, client):
        """Test the basic API health endpoint."""
        response = client.get("/api/v1/auth/test")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Lumen API is running!"
        assert data["status"] == "healthy"
        assert data["firebase_enabled"] is True

    @patch('app.auth_middleware.get_current_user')
    def test_demo_protected_endpoint(self, mock_get_user, client):
        """Test demo protected endpoint with authentication."""
        # Mock authenticated user
        mock_user_token = {
            'uid': 'test-firebase-uid-123',
            'email': 'test@example.com',
            'email_verified': True,
            'name': 'Test User'
        }
        mock_get_user.return_value = mock_user_token
        
        response = client.get("/api/v1/auth/demo-protected")
        
        assert response.status_code == 200
        data = response.json()
        assert "This is a protected endpoint" in data["message"]
        assert data["user_id"] == 'test-firebase-uid-123'
        assert data["email"] == 'test@example.com'
        assert "timestamp" in data

    def test_demo_protected_endpoint_unauthenticated(self, client):
        """Test demo protected endpoint rejects unauthenticated requests."""
        response = client.get("/api/v1/auth/demo-protected")
        
        # Should return 401 Unauthorized
        assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.auth 
class TestAuthModels:
    """Test authentication-related models and data structures."""
    
    def test_user_profile_model_validation(self):
        """Test UserProfile model validates correctly."""
        from app.api.endpoints.auth import UserProfile
        
        # Valid profile
        profile = UserProfile(
            uid="test-uid",
            email="test@example.com",
            email_verified=True,
            name="Test User",
            picture="https://example.com/pic.jpg"
        )
        
        assert profile.uid == "test-uid"
        assert profile.email == "test@example.com"
        assert profile.email_verified is True
        
        # Profile with minimal data
        minimal_profile = UserProfile(uid="test-uid-2")
        assert minimal_profile.uid == "test-uid-2"
        assert minimal_profile.email is None
        assert minimal_profile.email_verified is False

    def test_auth_status_model_validation(self):
        """Test AuthStatus model validates correctly."""
        from app.api.endpoints.auth import AuthStatus, UserProfile
        
        # Authenticated status
        profile = UserProfile(uid="test-uid")
        auth_status = AuthStatus(
            authenticated=True,
            user=profile,
            message="User is authenticated"
        )
        
        assert auth_status.authenticated is True
        assert auth_status.user.uid == "test-uid"
        assert auth_status.message == "User is authenticated"
        
        # Unauthenticated status  
        unauth_status = AuthStatus(
            authenticated=False,
            message="User is not authenticated"
        )
        
        assert unauth_status.authenticated is False
        assert unauth_status.user is None