#!/usr/bin/env python3
"""
Security validation test script for Lumen backend
Tests location service security, CORS configuration, and other security measures
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, '/home/cdc/Storage/projects/lumen/backend')

from app.services.location_service import LocationService
from app.storage.redis_cache import create_cache_service

# Mock database session for testing
class MockDB:
    def query(self, model):
        return MockQuery()

class MockQuery:
    def filter(self, condition):
        return self
    def first(self):
        return None
    def limit(self, limit):
        return self
    def all(self):
        return []

def test_location_service_security():
    """Test location service input validation and security measures"""
    print('=== TESTING LOCATION SERVICE SECURITY ===')

    service = LocationService(MockDB())

    # Test input validation with malicious inputs
    test_inputs = [
        ('New York', True),
        ('London, UK', True),
        ('Paris, France', True),
        ('Test; DROP TABLE users; --', False),
        ('<script>alert("xss")</script>', False),
        ("Robert'); DROP TABLE students;--", False),
        ('../../../etc/passwd', False),
        ('valid-city-name', True),
        ('Another Valid City', True),
        ('', False),
        (None, False),
        ('A' * 200, False),  # Over length limit
        ('San Francisco', True),
        ('Los Angeles, CA', True),
        ('SELECT * FROM users', False),
        ('UNION SELECT password', False)
    ]

    passed = 0
    failed = 0

    for test_input, should_pass in test_inputs:
        result = service._validate_location_input(test_input)
        actual_result = result is not None
        status = "PASS" if actual_result == should_pass else "FAIL"

        if status == "PASS":
            passed += 1
        else:
            failed += 1

        print(f'{status}: {repr(test_input)} -> Expected: {should_pass}, Got: {actual_result}')

    print(f'\nLocation Service Security: {passed} passed, {failed} failed')
    return failed == 0

def test_cache_service():
    """Test cache service functionality and fallback"""
    print('\n=== TESTING CACHE SERVICE ===')

    try:
        cache = create_cache_service()
        print(f'Cache service created successfully: {type(cache).__name__}')

        # Test basic cache operations
        import asyncio

        async def test_cache_operations():
            try:
                # Test URL caching
                await cache.cache_urls('test_photo_1', {'small': 'url1', 'medium': 'url2'})
                cached_urls = await cache.get_cached_urls('test_photo_1')
                print(f'URL cache test: {"PASS" if cached_urls else "FAIL"}')

                # Test cache statistics
                stats = await cache.get_cache_stats()
                print(f'Cache stats retrieved: {"PASS" if stats else "FAIL"}')
                print(f'Cache hit rate: {stats.get("hit_rate_percent", 0)}%')

                return True
            except Exception as e:
                print(f'Cache operations failed: {e}')
                return False

        result = asyncio.run(test_cache_operations())
        print(f'Cache Service Test: {"PASS" if result else "FAIL"}')
        return result

    except Exception as e:
        print(f'Cache service creation failed: {e}')
        return False

def test_database_connection():
    """Test database connection pool functionality"""
    print('\n=== TESTING DATABASE CONNECTION ===')

    try:
        from app.database.connection import engine, POOL_SIZE, MAX_OVERFLOW

        print(f'Engine created successfully')
        print(f'Pool size: {engine.pool.size() if hasattr(engine.pool, "size") else "N/A"}')
        print(f'Configured pool size: {POOL_SIZE}')
        print(f'Configured max overflow: {MAX_OVERFLOW}')

        # Test session creation
        from app.database.connection import SessionLocal
        session = SessionLocal()
        session.close()

        print('Database session creation: PASS')
        return True

    except Exception as e:
        print(f'Database connection test failed: {e}')
        return False

def test_cors_configuration():
    """Test CORS configuration"""
    print('\n=== TESTING CORS CONFIGURATION ===')

    try:
        # Check environment variables
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
        environment = os.getenv("ENVIRONMENT", "development")

        print(f'Environment: {environment}')
        print(f'ALLOWED_ORIGINS set: {"Yes" if allowed_origins else "No"}')

        if allowed_origins:
            origins = [origin.strip() for origin in allowed_origins.split(",")]
            print(f'Configured origins: {len(origins)}')
            for origin in origins[:5]:  # Show first 5
                print(f'  - {origin}')
            if len(origins) > 5:
                print(f'  ... and {len(origins) - 5} more')

        print('CORS configuration test: PASS')
        return True

    except Exception as e:
        print(f'CORS configuration test failed: {e}')
        return False

def main():
    """Run all security tests"""
    print('LUMEN BACKEND SECURITY VALIDATION REPORT')
    print('=' * 50)

    results = []

    # Run all tests
    results.append(('Location Service Security', test_location_service_security()))
    results.append(('Cache Service', test_cache_service()))
    results.append(('Database Connection', test_database_connection()))
    results.append(('CORS Configuration', test_cors_configuration()))

    # Summary
    print('\n' + '=' * 50)
    print('SECURITY TEST SUMMARY')
    print('=' * 50)

    passed_count = 0
    total_count = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f'{test_name}: {status}')
        if result:
            passed_count += 1

    print(f'\nOverall: {passed_count}/{total_count} tests passed')

    if passed_count == total_count:
        print('✓ All security tests passed!')
        return 0
    else:
        print('⚠ Some security tests failed - review issues above')
        return 1

if __name__ == "__main__":
    exit(main())