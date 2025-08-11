"""
Unit tests for authentication middleware.

Tests Firebase token verification, user authentication,
and authorization middleware functionality.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.auth_middleware import get_current_user, get_optional_user, AuthUser


@pytest.mark.unit
@pytest.mark.auth
class TestAuthMiddleware:
    """Test authentication middleware functions."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        """Test successful user authentication."""
        # Mock credentials
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid-firebase-token"
        )
        
        # Mock Firebase token verification
        mock_decoded_token = {
            'uid': 'test-firebase-uid',
            'email': 'test@example.com',
            'email_verified': True,
            'name': 'Test User',
            'picture': 'https://example.com/avatar.jpg'
        }
        
        with patch('app.auth_middleware.firebase_config') as mock_firebase:
            mock_firebase.verify_token.return_value = mock_decoded_token
            
            result = await get_current_user(mock_credentials)
            
            assert result == mock_decoded_token
            mock_firebase.verify_token.assert_called_once_with("valid-firebase-token")

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test authentication with invalid token."""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid-token"
        )
        
        with patch('app.auth_middleware.firebase_config') as mock_firebase:
            mock_firebase.verify_token.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials)
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid authentication token" in exc_info.value.detail
            assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    @pytest.mark.asyncio
    async def test_get_current_user_firebase_exception(self):
        """Test authentication when Firebase raises exception."""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="problematic-token"
        )
        
        with patch('app.auth_middleware.firebase_config') as mock_firebase:
            mock_firebase.verify_token.side_effect = Exception("Firebase error")
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials)
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid authentication token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_optional_user_success(self):
        """Test optional authentication with valid token."""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid-token"
        )
        
        mock_decoded_token = {
            'uid': 'test-uid',
            'email': 'test@example.com'
        }
        
        with patch('app.auth_middleware.firebase_config') as mock_firebase:
            mock_firebase.verify_token.return_value = mock_decoded_token
            
            result = await get_optional_user(mock_credentials)
            
            assert result == mock_decoded_token

    @pytest.mark.asyncio
    async def test_get_optional_user_no_credentials(self):
        """Test optional authentication with no credentials."""
        result = await get_optional_user(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_optional_user_invalid_token(self):
        """Test optional authentication with invalid token."""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid-token"
        )
        
        with patch('app.auth_middleware.firebase_config') as mock_firebase:
            mock_firebase.verify_token.side_effect = Exception("Firebase error")
            
            result = await get_optional_user(mock_credentials)
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_optional_user_firebase_returns_none(self):
        """Test optional authentication when Firebase returns None."""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="expired-token"
        )
        
        with patch('app.auth_middleware.firebase_config') as mock_firebase:
            mock_firebase.verify_token.return_value = None
            
            result = await get_optional_user(mock_credentials)
            
            assert result is None


@pytest.mark.unit
@pytest.mark.auth
class TestAuthUser:
    """Test AuthUser helper class."""

    def test_auth_user_creation_full_data(self):
        """Test AuthUser creation with full Firebase token data."""
        decoded_token = {
            'uid': 'firebase-uid-123',
            'email': 'user@example.com',
            'email_verified': True,
            'name': 'John Doe',
            'picture': 'https://example.com/photo.jpg',
            'iss': 'https://securetoken.google.com/project-id',
            'exp': 1234567890
        }
        
        auth_user = AuthUser(decoded_token)
        
        assert auth_user.uid == 'firebase-uid-123'
        assert auth_user.email == 'user@example.com'
        assert auth_user.email_verified is True
        assert auth_user.name == 'John Doe'
        assert auth_user.picture == 'https://example.com/photo.jpg'
        assert auth_user.firebase_token == decoded_token

    def test_auth_user_creation_minimal_data(self):
        """Test AuthUser creation with minimal token data."""
        decoded_token = {
            'uid': 'firebase-uid-456'
        }
        
        auth_user = AuthUser(decoded_token)
        
        assert auth_user.uid == 'firebase-uid-456'
        assert auth_user.email is None
        assert auth_user.email_verified is False
        assert auth_user.name is None
        assert auth_user.picture is None
        assert auth_user.firebase_token == decoded_token

    def test_auth_user_creation_empty_token(self):
        """Test AuthUser creation with empty token data."""
        decoded_token = {}
        
        auth_user = AuthUser(decoded_token)
        
        assert auth_user.uid is None
        assert auth_user.email is None
        assert auth_user.email_verified is False
        assert auth_user.name is None
        assert auth_user.picture is None
        assert auth_user.firebase_token == decoded_token

    def test_auth_user_email_verification_false(self):
        """Test AuthUser with explicit email_verified: False."""
        decoded_token = {
            'uid': 'firebase-uid-789',
            'email': 'unverified@example.com',
            'email_verified': False
        }
        
        auth_user = AuthUser(decoded_token)
        
        assert auth_user.uid == 'firebase-uid-789'
        assert auth_user.email == 'unverified@example.com'
        assert auth_user.email_verified is False

    def test_auth_user_preserves_token_data(self):
        """Test that AuthUser preserves original Firebase token data."""
        decoded_token = {
            'uid': 'firebase-uid-000',
            'email': 'preserve@example.com',
            'custom_claims': {'role': 'admin'},
            'provider_data': [{'providerId': 'google.com'}],
            'firebase': {'sign_in_provider': 'google.com'}
        }
        
        auth_user = AuthUser(decoded_token)
        
        # Basic properties extracted
        assert auth_user.uid == 'firebase-uid-000'
        assert auth_user.email == 'preserve@example.com'
        
        # Original token data preserved
        assert auth_user.firebase_token == decoded_token
        assert 'custom_claims' in auth_user.firebase_token
        assert 'provider_data' in auth_user.firebase_token
        assert 'firebase' in auth_user.firebase_token


@pytest.mark.integration
@pytest.mark.auth
class TestAuthMiddlewareIntegration:
    """Integration tests for authentication middleware with FastAPI."""

    @pytest.mark.asyncio
    async def test_middleware_with_fastapi_dependency_injection(self):
        """Test auth middleware works with FastAPI dependency injection."""
        from fastapi import Depends
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        # Create test app
        app = FastAPI()
        
        @app.get("/protected")
        async def protected_endpoint(user_token: dict = Depends(get_current_user)):
            return {"message": "success", "uid": user_token.get("uid")}
        
        @app.get("/optional")
        async def optional_endpoint(user_token: dict = Depends(get_optional_user)):
            if user_token:
                return {"authenticated": True, "uid": user_token.get("uid")}
            return {"authenticated": False}
        
        client = TestClient(app)
        
        # Test protected endpoint without auth (should fail)
        response = client.get("/protected")
        assert response.status_code == 403  # No auth provided
        
        # Test optional endpoint without auth (should succeed)
        response = client.get("/optional")
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False

    def test_http_bearer_security_scheme(self):
        """Test HTTP Bearer security scheme configuration."""
        from app.auth_middleware import security
        from fastapi.security import HTTPBearer
        
        assert isinstance(security, HTTPBearer)

    def test_auth_user_as_data_class(self):
        """Test AuthUser can be used as a data container."""
        token_data = {
            'uid': 'test-uid-integration',
            'email': 'integration@test.com',
            'email_verified': True,
            'name': 'Integration Test User'
        }
        
        auth_user = AuthUser(token_data)
        
        # Test it can be used in string formatting
        user_info = f"User {auth_user.name} ({auth_user.email})"
        assert user_info == "User Integration Test User (integration@test.com)"
        
        # Test boolean evaluation of email_verified
        if auth_user.email_verified:
            verified_status = "verified"
        else:
            verified_status = "unverified"
        
        assert verified_status == "verified"