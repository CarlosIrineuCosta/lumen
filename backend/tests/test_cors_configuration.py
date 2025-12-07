"""
Test suite for CORS configuration fixes.

This test suite validates that the CORS middleware is properly
configured for security and functionality.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware

from app.main import app, allowed_origins


class TestCORSConfiguration:
    """Test CORS configuration implementation"""

    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Setup test environment variables"""
        # Save original environment variables
        self.original_env = {}
        env_vars = ['ALLOWED_ORIGINS', 'ENVIRONMENT']

        for var in env_vars:
            self.original_env[var] = os.getenv(var)

        yield

        # Restore original environment variables
        for var, value in self.original_env.items():
            if value is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = value

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_default_development_origins(self):
        """Test that default development origins are configured correctly"""
        # Remove ALLOWED_ORIGINS to test defaults
        os.environ.pop('ALLOWED_ORIGINS', None)
        os.environ['ENVIRONMENT'] = 'development'

        # Re-import the module to pick up new values
        import importlib
        import app.main
        importlib.reload(app.main)

        from app.main import allowed_origins

        expected_origins = [
            "http://localhost:8000",
            "http://localhost:3000",  # React dev server
            "http://localhost:8080",
            "http://100.106.201.33:8000",
            "http://100.106.201.33:8080",
            "http://127.0.0.1:8000",
            "http://127.0.0.1:8080",
            "http://127.0.0.1:3000"
        ]

        assert set(allowed_origins) == set(expected_origins)

    def test_production_restrictive_origins(self):
        """Test that production uses restrictive origins"""
        os.environ.pop('ALLOWED_ORIGINS', None)
        os.environ['ENVIRONMENT'] = 'production'

        # Re-import the module to pick up new values
        import importlib
        import app.main
        importlib.reload(app.main)

        from app.main import allowed_origins

        # Production should have empty default origins
        assert allowed_origins == []

    def test_custom_origins_from_environment(self):
        """Test that custom origins are loaded from environment"""
        custom_origins = "https://example.com,https://app.example.com"
        os.environ['ALLOWED_ORIGINS'] = custom_origins

        # Re-import the module to pick up new values
        import importlib
        import app.main
        importlib.reload(app.main)

        from app.main import allowed_origins

        expected = [
            "https://example.com",
            "https://app.example.com"
        ]

        assert allowed_origins == expected

    def test_invalid_origins_filtered(self):
        """Test that invalid origins are filtered out"""
        invalid_origins = "https://example.com,invalid-origin,ftp://invalid.com,http://valid.com"
        os.environ['ALLOWED_ORIGINS'] = invalid_origins

        # Re-import the module to pick up new values
        import importlib
        import app.main
        importlib.reload(app.main)

        from app.main import allowed_origins

        # Should only include valid HTTP/HTTPS origins
        expected = [
            "https://example.com",
            "http://valid.com"
        ]

        assert set(allowed_origins) == set(expected)

    def test_cors_middleware_configuration(self, client):
        """Test that CORS middleware is properly configured"""
        # Find the CORS middleware
        cors_middleware = None
        for middleware in app.user_middleware:
            if middleware.cls == CORSMiddleware:
                cors_middleware = middleware
                break

        assert cors_middleware is not None, "CORS middleware not found"

        # Check middleware options
        options = cors_middleware.options
        assert options['allow_credentials'] is True
        assert options['allow_methods'] == ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

        expected_headers = [
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers"
        ]
        assert set(options['allow_headers']) == set(expected_headers)

        expected_exposed_headers = ["Content-Length", "X-Total-Count"]
        assert set(options['expose_headers']) == set(expected_exposed_headers)

    def test_preflight_request_handling(self, client):
        """Test OPTIONS preflight request handling"""
        origin = "http://localhost:3000"
        headers = {
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type, Authorization"
        }

        response = client.options("/api/v1/photos", headers=headers)

        # Check CORS headers in response
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] in [origin, "*"]

    def test_actual_request_cors_headers(self, client):
        """Test CORS headers on actual requests"""
        origin = "http://localhost:3000"
        headers = {"Origin": origin}

        response = client.get("/", headers=headers)

        # Check CORS headers
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-credentials"] == "true"

    def test_invalid_origin_blocked(self, client):
        """Test that invalid origins are blocked"""
        headers = {"Origin": "http://malicious-site.com"}

        response = client.get("/", headers=headers)

        # Should not have CORS headers for invalid origin
        assert response.headers.get("access-control-allow-origin") is None or \
               response.headers.get("access-control-allow-origin") == "null"

    def test_credentials_enabled(self):
        """Test that credentials are properly enabled"""
        # Check that the CORS middleware allows credentials
        cors_middleware = None
        for middleware in app.user_middleware:
            if middleware.cls == CORSMiddleware:
                cors_middleware = middleware
                break

        assert cors_middleware.options['allow_credentials'] is True

    def test_security_headers_configuration(self, client):
        """Test that security headers are properly configured"""
        response = client.get("/")

        # Check for security-related headers
        # Note: These might be added by other middleware, not CORS directly
        response_headers = dict(response.headers)

        # Verify that sensitive headers are not exposed
        cors_exposed = response_headers.get("access-control-expose-headers", "")
        assert "server" not in cors_exposed.lower()
        assert "x-powered-by" not in cors_exposed.lower()

    def test_origin_whitespace_handling(self):
        """Test that origins with whitespace are properly handled"""
        origins_with_whitespace = " https://example.com , https://app.example.com "
        os.environ['ALLOWED_ORIGINS'] = origins_with_whitespace

        # Re-import the module to pick up new values
        import importlib
        import app.main
        importlib.reload(app.main)

        from app.main import allowed_origins

        expected = [
            "https://example.com",
            "https://app.example.com"
        ]

        assert allowed_origins == expected

    def test_duplicate_origins_deduplication(self):
        """Test that duplicate origins are properly handled"""
        duplicate_origins = "https://example.com,https://example.com,https://app.example.com"
        os.environ['ALLOWED_ORIGINS'] = duplicate_origins

        # Re-import the module to pick up new values
        import importlib
        import app.main
        importlib.reload(app.main)

        from app.main import allowed_origins

        # Should not have duplicates
        assert len(allowed_origins) == len(set(allowed_origins))

    def test_empty_origins_handling(self):
        """Test handling of empty ALLOWED_ORIGINS"""
        os.environ['ALLOWED_ORIGINS'] = ""

        # Re-import the module to pick up new values
        import importlib
        import app.main
        importlib.reload(app.main)

        from app.main import allowed_origins

        # Should fall back to default origins for development
        assert len(allowed_origins) > 0

    @patch('app.main.logger')
    def test_cors_logging(self, mock_logger):
        """Test that CORS configuration is properly logged"""
        # Re-import to trigger logging
        import importlib
        import app.main
        importlib.reload(app.main)

        # Check that origins were logged
        mock_logger.info.assert_any_call("CORS Enabled: True")
        # Should also log the origins (implementation dependent)

    def test_api_endpoints_accessible_with_cors(self, client):
        """Test that API endpoints are accessible with proper CORS headers"""
        origin = "http://localhost:3000"
        headers = {"Origin": origin}

        # Test various endpoints
        endpoints = [
            "/",
            "/health",
            "/api/v1/photos",
            "/api/v1/users/profile"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint, headers=headers)

            # Should have CORS headers
            assert response.status_code in [200, 401, 404]  # Various expected statuses
            assert "access-control-allow-origin" in response.headers

    def test_method_specific_cors(self, client):
        """Test CORS for different HTTP methods"""
        origin = "http://localhost:3000"
        headers = {"Origin": origin}

        methods = [
            ("GET", "/"),
            ("POST", "/api/v1/photos"),
            ("PUT", "/api/v1/users/profile"),
            ("DELETE", "/api/v1/photos/test-id"),
            ("PATCH", "/api/v1/photos/test-id")
        ]

        for method, endpoint in methods:
            if method == "GET":
                response = client.get(endpoint, headers=headers)
            elif method == "POST":
                response = client.post(endpoint, headers=headers, json={})
            elif method == "PUT":
                response = client.put(endpoint, headers=headers, json={})
            elif method == "DELETE":
                response = client.delete(endpoint, headers=headers)
            elif method == "PATCH":
                response = client.patch(endpoint, headers=headers, json={})

            # Should have CORS headers
            assert "access-control-allow-origin" in response.headers
            assert response.headers["access-control-allow-credentials"] == "true"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])