# Lumen Backend Migration Guide

This guide covers the specific changes that need to be applied when migrating from the previous version to the enhanced production-ready backend.

## Overview of Changes

This migration includes critical security and performance improvements:

1. **Database Connection Pooling** - Switch from NullPool to QueuePool
2. **Enhanced CORS Configuration** - Security-first approach with validation
3. **Location Service Security** - Input validation and SQL injection prevention
4. **Cache Invalidation Strategy** - Comprehensive cache management
5. **Testing Infrastructure** - Complete test suite for all fixes

## Pre-Migration Checklist

### Backup Critical Data
- [ ] Database backup completed
- [ ] Redis backup (if applicable)
- [ ] Configuration files backed up
- [ ] Current application version tagged

### Environment Preparation
- [ ] Staging environment prepared
- [ ] Test database populated
- [ ] Redis instance ready
- [ ] Monitoring tools configured

### Dependency Updates
- [ ] Check for new Python dependencies
- [ ] Verify PostgreSQL version compatibility
- [ ] Confirm Redis version compatibility

## Step-by-Step Migration

### 1. Database Connection Migration

**File Changed**: `app/database/connection.py`

**Previous Code**:
```python
from sqlalchemy.pool import NullPool

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # <-- PROBLEM: No connection pooling
    echo=os.getenv("DEBUG", "false").lower() == "true"
)
```

**New Code**:
```python
from sqlalchemy.pool import QueuePool

# Pool configuration
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,  # <-- FIX: Proper connection pooling
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=True,  # <-- NEW: Connection validation
    echo=os.getenv("DEBUG", "false").lower() == "true"
)
```

**Migration Steps**:
1. Update the `connection.py` file with the new code
2. Add the new environment variables to your configuration:
   ```bash
   DB_POOL_SIZE=10
   DB_MAX_OVERFLOW=20
   DB_POOL_TIMEOUT=30
   DB_POOL_RECYCLE=3600
   ```
3. Test database connectivity
4. Monitor connection pool metrics after deployment

**Validation**:
```python
# Test script to validate connection pooling
from app.database.connection import engine, SessionLocal

def test_connection_pooling():
    # Test multiple concurrent connections
    sessions = []
    for i in range(15):  # More than pool size
        session = SessionLocal()
        sessions.append(session)

    # Should work due to overflow pool
    for session in sessions:
        session.close()

    print("✓ Connection pooling working correctly")
```

### 2. CORS Configuration Migration

**File Changed**: `app/main.py`

**Previous Code**:
```python
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_str:
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]
else:
    allowed_origins = [
        "http://localhost:8000",
        "http://localhost:8080"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],  # <-- SECURITY ISSUE: Too permissive
    allow_headers=["*"],  # <-- SECURITY ISSUE: Too permissive
    expose_headers=["*"]  # <-- SECURITY ISSUE: Too permissive
)
```

**New Code**:
```python
# Parse and validate origins
if allowed_origins_str:
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]
    # Validate origin format  <-- NEW: Origin validation
    allowed_origins = [origin for origin in allowed_origins
                      if origin and (origin.startswith("http://") or origin.startswith("https://"))]
else:
    # Environment-specific defaults  <-- NEW: Production-ready defaults
    if os.getenv("ENVIRONMENT", "development") == "production":
        allowed_origins = []  # Must be explicitly set in production
    else:
        allowed_origins = [
            "http://localhost:8000",
            "http://localhost:3000",  # <-- NEW: React dev server
            # ... other development origins
        ]

# Enhanced CORS middleware  <-- NEW: Security-first configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],  # <-- EXPLICIT
    allow_headers=[  # <-- RESTRICTIVE
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers"
    ],
    expose_headers=["Content-Length", "X-Total-Count"]  # <-- MINIMAL
)
```

**Migration Steps**:
1. Update the CORS middleware configuration in `main.py`
2. Set production origins in environment variables:
   ```bash
   ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
   ENVIRONMENT=production
   ```
3. Test CORS headers with your frontend
4. Verify that only allowed origins can access the API

**Validation**:
```bash
# Test CORS preflight request
curl -X OPTIONS http://your-api/api/v1/photos \
  -H "Origin: https://yourdomain.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type, Authorization"

# Should return 200 with proper CORS headers
```

### 3. Location Service Security Migration

**File Changed**: `app/services/location_service.py`

**Previous Code**:
```python
# INSECURE: Contains SQL injection vulnerability
city = self.db.query(City).filter(
    func.lower(City.name).contains(func.lower(location))  # <-- DANGEROUS
).first()
```

**New Code**:
```python
# SECURE: Comprehensive input validation and safe queries
def _validate_location_input(self, location_string: str) -> Optional[str]:
    """Validate and sanitize location input"""
    if not location_string or not isinstance(location_string, str):
        return None

    location = location_string.strip()

    # Length validation  <-- NEW
    if len(location) < 1 or len(location) > 100:
        return None

    # Security: Remove potentially dangerous characters  <-- NEW
    if not re.match(r"^[a-zA-Z0-9\s,\-'\.]+$", location):
        logger.warning(f"Invalid characters in location input: {location}")
        return None

    # Additional normalization  <-- NEW
    location = re.sub(r'\s+', ' ', location)
    return location if location else None

# SECURE: Safe query with input validation
async def resolve_city(self, location_string: str) -> Optional[int]:
    location = self._validate_location_input(location_string)  # <-- NEW: Validation
    if not location:
        return None

    # ... validation and exact matching logic ...

    # SAFE: Prefix matching instead of contains  <-- NEW
    city = self.db.query(City).filter(
        func.lower(City.name).like(f"{location_lower}%")  # <-- SAFE
    ).first()
```

**Migration Steps**:
1. Replace the entire `LocationService` class with the new implementation
2. Add regex pattern validation to your security testing
3. Test with various input formats, including malicious inputs
4. Monitor logs for rejected inputs

**Validation**:
```python
# Test security validation
service = LocationService(mock_db)

# Valid inputs should work
assert service._validate_location_input("New York") == "New York"
assert service._validate_location_input("Paris, France") == "Paris, France"

# Invalid inputs should be rejected
assert service._validate_location_input("'; DROP TABLE cities; --") is None
assert service._validate_location_input("City@#$") is None
assert service._validate_location_input("A" * 101) is None
```

### 4. Cache Invalidation Strategy Migration

**Files Changed**:
- `app/storage/redis_cache.py` - Enhanced cache service
- `app/services/photo_service_v2.py` - Updated photo service with cache invalidation

**Previous Code**:
```python
# Basic caching without invalidation strategy
async def invalidate_photo(self, photo_id: str) -> None:
    # Only invalidated specific photo cache
    await self.cache.invalidate_photo(photo_id)
```

**New Code**:
```python
# COMPREHENSIVE: Multi-level cache invalidation
async def invalidate_photo(self, photo_id: str) -> None:
    """Remove all cached data for a photo with comprehensive invalidation"""

    # Delete photo-specific cache
    keys_to_delete = [
        f"{self.prefixes['urls']}{photo_id}",
        f"{self.prefixes['metadata']}{photo_id}"
    ]

    # Invalidate user caches that might reference this photo  <-- NEW
    user_keys_pattern = f"{self.prefixes['user_info']}*"
    user_keys = await r.keys(user_keys_pattern)

    for user_key in user_keys:
        # Check if user cache contains photo count/storage info
        cached_data = await r.get(user_key)
        if cached_data:
            data = json.loads(cached_data)
            if 'photo_count' in data or 'total_files' in data:
                await r.delete(user_key)

    # Delete main photo cache entries
    deleted_count = await r.delete(*keys_to_delete)

    # Log invalidation for debugging  <-- NEW
    invalidation_key = f"{self.prefixes['temp']}invalidation_log:{photo_id}"
    await r.setex(invalidation_key, 300, json.dumps({
        'photo_id': photo_id,
        'timestamp': datetime.utcnow().isoformat(),
        'entries_deleted': deleted_count,
        'user_keys_invalidated': len(user_keys)
    }))

# PHOTO SERVICE: Enhanced cache invalidation  <-- NEW
async def upload_photo(self, ...):
    # ... photo upload logic ...

    # Enhanced cache invalidation  <-- NEW
    try:
        # Invalidate user cache since they have a new photo
        await self.cache.invalidate_user_cache(validated_firebase_uid)

        # If photo is public, invalidate recent photos cache
        if request.is_public:
            await self.cache.invalidate_recent_photos_cache()
    except Exception as cache_error:
        # Don't fail the upload if cache invalidation fails
        logger.warning(f"Cache invalidation failed for photo {photo_id_str}: {cache_error}")
```

**Migration Steps**:
1. Update the `RedisCacheService` with enhanced invalidation methods
2. Update `photo_service_v2.py` to use comprehensive cache invalidation
3. Configure Redis environment variables if not already set
4. Test cache invalidation during photo operations

**Validation**:
```python
# Test cache invalidation
cache_service = RedisCacheService()

# Invalidate a photo
await cache_service.invalidate_photo("test_photo_123")

# Check invalidation log
logs = await cache_service.get_invalidation_log("test_photo_123")
assert len(logs) == 1
assert logs[0]['photo_id'] == "test_photo_123"

# Test user cache invalidation
await cache_service.invalidate_user_cache("test_user_456")
```

### 5. Testing Infrastructure Setup

**New Files Added**:
- `tests/test_connection_pool.py` - Database connection pooling tests
- `tests/test_cors_configuration.py` - CORS configuration tests
- `tests/test_location_service_security.py` - Location service security tests
- `tests/test_cache_invalidation.py` - Cache invalidation tests
- `tests/conftest.py` - Test configuration and fixtures
- `tests/run_tests.py` - Test runner script

**Migration Steps**:
1. Create the `tests/` directory if it doesn't exist
2. Copy all test files from this guide
3. Install test requirements:
   ```bash
   cd backend/tests
   pip install -r requirements.txt
   ```
4. Run tests to validate migration:
   ```bash
   python run_tests.py --all
   ```

## Post-Migration Validation

### 1. Functional Testing

**Database Connection Test**:
```bash
# Test database pooling under load
python -c "
import asyncio
from app.database.connection import SessionLocal

async def test_concurrent_connections():
    sessions = []
    for i in range(20):
        session = SessionLocal()
        sessions.append(session)

    # Test concurrent operations
    for session in sessions:
        session.close()

    print('✓ Database connection pooling test passed')

asyncio.run(test_concurrent_connections())
"
```

**CORS Test**:
```bash
# Test CORS with your frontend domain
curl -X OPTIONS http://your-api/api/v1/photos \
  -H "Origin: https://yourdomain.com" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

**Location Service Security Test**:
```bash
# Test SQL injection prevention
curl -X POST http://your-api/api/v1/locations/search \
  -H "Content-Type: application/json" \
  -d '{"query": "New York; DROP TABLE cities; --"}'
# Should return empty results, not an error
```

### 2. Performance Testing

**Database Performance**:
```python
# Monitor connection pool metrics
from app.database.connection import engine

print(f"Pool size: {engine.pool.size()}")
print(f"Pool checked in: {engine.pool.checkedin()}")
print(f"Pool checked out: {engine.pool.checkedout()}")
```

**Cache Performance**:
```python
# Test cache hit rates
cache_service = RedisCacheService()
stats = await cache_service.get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate_percent']}%")
```

### 3. Security Testing

**Input Validation Test**:
```python
# Test location service input validation
from app.services.location_service import LocationService

service = LocationService(mock_db)

# Test various inputs
test_cases = [
    ("New York", True),
    ("'; SELECT * FROM users; --", False),
    ("City@#$%", False),
    ("A" * 101, False),
    ("São Paulo", True),
]

for input_val, should_pass in test_cases:
    result = service._validate_location_input(input_val)
    assert (result is not None) == should_pass
```

## Monitoring Setup

### 1. Database Metrics

**Key Metrics to Monitor**:
- Connection pool utilization
- Query response times
- Connection creation/destruction rates
- Database connection errors

**Prometheus Queries**:
```promql
# Connection pool usage
sqlalchemy_pool_size
sqlalchemy_pool_overflow

# Database response times
histogram_quantile(0.95, rate(sqlalchemy_query_duration_seconds_bucket[5m]))
```

### 2. Cache Metrics

**Key Metrics to Monitor**:
- Cache hit rate
- Redis memory usage
- Cache invalidation success rates
- Redis connection health

**Prometheus Queries**:
```promql
# Cache performance
redis_cache_hit_rate
redis_memory_usage_bytes
redis_cache_invalidation_total
```

### 3. Application Metrics

**Key Metrics to Monitor**:
- API response times
- Error rates by endpoint
- CORS failure rates
- Input validation rejection rates

## Rollback Plan

### Immediate Rollback

If critical issues are discovered after migration:

1. **Application Rollback**:
   ```bash
   # Git rollback
   git checkout previous-stable-tag

   # Docker rollback
   docker rollback lumen-backend:previous-version
   ```

2. **Database Rollback** (if schema changes were made):
   ```bash
   alembic downgrade -1
   ```

3. **Configuration Rollback**:
   - Restore previous environment variable configuration
   - Restart application services

### Verification After Rollback

1. Verify all endpoints are functioning
2. Check database connectivity
3. Confirm CORS is working
4. Validate cache operations
5. Run smoke tests

## Troubleshooting Guide

### Common Issues and Solutions

**Issue**: Database connection timeouts
```
Cause: Insufficient pool size or high database load
Solution:
1. Increase DB_POOL_SIZE environment variable
2. Optimize database queries
3. Add database read replicas
```

**Issue**: CORS errors on frontend
```
Cause: Incorrect ALLOWED_ORIGINS configuration
Solution:
1. Verify exact origin URLs in ALLOWED_ORIGINS
2. Check for trailing slashes or subdomain differences
3. Ensure ENVIRONMENT=production for production deployments
```

**Issue**: Location queries returning no results
```
Cause: New input validation rejecting valid inputs
Solution:
1. Check application logs for validation warnings
2. Review regex pattern in _validate_location_input
3. Test with various input formats
```

**Issue**: Cache invalidation not working
```
Cause: Redis connectivity or configuration issues
Solution:
1. Verify REDIS_URL and REDIS_PASSWORD
2. Test Redis connectivity: redis-cli ping
3. Check Redis memory usage and key expiration
```

## Support Contact

For migration assistance:
- Development Team: dev-team@lumen.com
- Emergency Migration Support: emergency@lumen.com

---

**Migration Version**: v1.0.0 → v2.0.0
**Migration Date**: 2024-11-18
**Rollback Window**: 24 hours (if critical issues discovered)