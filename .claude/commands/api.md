---
description: Backend API development and integration with FastAPI
---

# Backend API Development & Integration

Develop backend functionality for $ARGUMENTS:

## 1. Design Phase

### API Endpoint Analysis
```bash
echo "=== API DESIGN ANALYSIS ==="

# Analyze current API structure
echo "Current API endpoints:"
find opusdev/backend/app -name "*.py" -path "*/routers/*" -exec grep -l "router\|APIRouter" {} \;

# Check existing models and schemas
echo ""
echo "Current data models:"
find opusdev/backend/app -name "*.py" -path "*/models/*" | head -5

echo ""
echo "Pydantic schemas:"
find opusdev/backend/app -name "*.py" -path "*/schemas/*" | head -5
```

### Database Schema Planning
```bash
echo "=== DATABASE SCHEMA PLANNING ==="

# Check current Alembic migrations
echo "Current migrations:"
ls -la opusdev/backend/alembic/versions/ | tail -5

# Check SQLAlchemy models
echo ""
echo "Database models:"
grep -r "class.*Base\|Table" opusdev/backend/app/models/ | head -5

# Plan new tables if needed
FEATURE_TYPE="$ARGUMENTS"
case $FEATURE_TYPE in
    *user*|*profile*)
        echo "Planning user/profile related tables"
        ;;
    *photo*|*image*)
        echo "Planning photo/image related tables"
        ;;
    *auth*)
        echo "Planning authentication related tables"
        ;;
    *)
        echo "Planning general feature tables"
        ;;
esac
```

## 2. FastAPI Implementation

### API Router Development
```bash
echo "=== FASTAPI ROUTER IMPLEMENTATION ==="

# Create router based on feature type
FEATURE_TYPE="$ARGUMENTS"
ROUTER_FILE="opusdev/backend/app/routers/${FEATURE_TYPE// /_}.py"

echo "Implementing router: $ROUTER_FILE"
echo "Router structure:"
echo "- GET endpoints for data retrieval"
echo "- POST endpoints for data creation"  
echo "- PUT/PATCH endpoints for updates"
echo "- DELETE endpoints for removal"
echo "- Proper HTTP status codes"
echo "- Error handling and validation"
```

### Pydantic Model Development
```bash
echo "=== PYDANTIC SCHEMAS ==="

# Define request/response models
echo "Schema Requirements:"
echo "- [ ] Request models with validation"
echo "- [ ] Response models with proper typing"
echo "- [ ] Error response schemas"
echo "- [ ] Nested model relationships"
echo "- [ ] Optional field handling"

# Lumen-specific schemas
echo ""
echo "Lumen Photography Schemas:"
echo "- User profiles (photographer/model types)"
echo "- Photo metadata and EXIF data"
echo "- Geolocation for nearby features"
echo "- Privacy settings and visibility"
```

### Database Models (SQLAlchemy)
```bash
echo "=== SQLALCHEMY MODELS ==="

# Database model requirements
echo "Model Implementation:"
echo "- [ ] Proper table relationships (ForeignKey, backref)"
echo "- [ ] Flexible JSONB fields for extensibility" 
echo "- [ ] Indexed columns for performance"
echo "- [ ] Validation constraints"
echo "- [ ] Audit fields (created_at, updated_at)"

echo ""
echo "Lumen-specific Models:"
echo "- Users table with flexible profiles"
echo "- Photos table with metadata and tagging"
echo "- Cities table for geolocation"
echo "- Specialties for photographer/model types"
```

## 3. Authentication Integration

### Firebase Authentication
```bash
echo "=== FIREBASE AUTHENTICATION ==="

# Check Firebase integration
echo "Firebase Auth Status:"
cd opusdev/backend
python -c "
try:
    from app.firebase_config import firebase_config
    print('✅ Firebase config loaded')
    print('App name:', firebase_config.app.name if firebase_config.app else 'None')
except Exception as e:
    print('❌ Firebase config error:', str(e))
"

# Authentication middleware
echo ""
echo "Auth Middleware Requirements:"
echo "- [ ] JWT token validation"
echo "- [ ] User role/permission checking"
echo "- [ ] Protected endpoint decoration"
echo "- [ ] Token refresh handling"
echo "- [ ] Error responses for auth failures"
```

### Permission System
```bash
echo "=== PERMISSION SYSTEM ==="

# Role-based access control
echo "RBAC Implementation:"
echo "- [ ] User roles (photographer, model, admin)"
echo "- [ ] Resource-level permissions"
echo "- [ ] Privacy settings enforcement"
echo "- [ ] Profile visibility controls"

# Lumen-specific permissions
echo ""
echo "Lumen Permission Model:"
echo "- Public profiles vs private profiles"
echo "- Photo visibility (public, followers, private)"
echo "- Model/photographer specific permissions"
echo "- Geographic privacy (location sharing)"
```

## 4. Data Processing

### Image Processing Pipeline
```bash
echo "=== IMAGE PROCESSING ==="

# Pillow integration for image processing
echo "Image Processing Features:"
echo "- [ ] HEIF/HEIC format support (pillow-heif)"
echo "- [ ] Image compression and optimization"
echo "- [ ] Thumbnail generation (multiple sizes)"
echo "- [ ] EXIF metadata extraction"
echo "- [ ] Image format conversion (WebP, JPEG)"

echo ""
echo "Performance Considerations:"
echo "- [ ] Async file processing with aiofiles"
echo "- [ ] Background task queuing"
echo "- [ ] Progressive image loading"
echo "- [ ] CDN integration for image serving"
```

### Data Validation
```bash
echo "=== DATA VALIDATION ==="

# Input validation and sanitization
echo "Validation Requirements:"
echo "- [ ] Email format validation"
echo "- [ ] Password strength requirements"
echo "- [ ] Image file type validation"
echo "- [ ] Geographic coordinate validation"
echo "- [ ] Profile data completeness checks"

# Business logic validation
echo ""
echo "Business Logic Validation:"
echo "- [ ] Age verification for models"
echo "- [ ] Professional portfolio requirements"
echo "- [ ] Photo content moderation"
echo "- [ ] Profile information accuracy"
```

## 5. Database Operations

### Query Optimization
```bash
echo "=== DATABASE OPTIMIZATION ==="

# SQLAlchemy query performance
echo "Query Performance:"
echo "- [ ] Proper indexing strategy"
echo "- [ ] N+1 query prevention"
echo "- [ ] Eager loading for relationships"
echo "- [ ] Pagination for large datasets"
echo "- [ ] Query result caching"

# Database monitoring
echo ""
echo "Database Monitoring:"
echo "- [ ] Slow query identification"
echo "- [ ] Connection pool monitoring"
echo "- [ ] Database size tracking"
echo "- [ ] Performance metrics collection"
```

### Migration Management
```bash
echo "=== ALEMBIC MIGRATIONS ==="

# Database migration strategy
echo "Migration Planning:"
echo "- [ ] Schema change versioning"
echo "- [ ] Data migration scripts"
echo "- [ ] Rollback procedures"
echo "- [ ] Testing migration procedures"

echo ""
echo "Migration Commands:"
echo "# Create new migration"
echo "alembic revision --autogenerate -m 'description'"
echo ""
echo "# Apply migrations"
echo "alembic upgrade head"
echo ""
echo "# Rollback migration"
echo "alembic downgrade -1"
```

## 6. API Testing

### Unit Testing
```bash
echo "=== API TESTING ==="

# Test implementation with pytest
echo "Testing Strategy:"
echo "- [ ] Unit tests for individual functions"
echo "- [ ] Integration tests for API endpoints" 
echo "- [ ] Authentication flow testing"
echo "- [ ] Database operation testing"
echo "- [ ] Error handling validation"

echo ""
echo "Test Structure:"
echo "- tests/test_api/ - API endpoint tests"
echo "- tests/test_models/ - Database model tests"
echo "- tests/test_auth/ - Authentication tests"
echo "- tests/fixtures/ - Test data fixtures"
```

### API Documentation Testing
```bash
echo "=== API DOCUMENTATION ==="

# FastAPI automatic documentation
echo "Documentation Validation:"
echo "- [ ] OpenAPI schema generation"
echo "- [ ] Interactive docs (/docs endpoint)"
echo "- [ ] ReDoc alternative docs (/redoc)"
echo "- [ ] Example request/response data"
echo "- [ ] Error response documentation"

echo ""
echo "Documentation URLs:"
echo "- API Docs: http://100.106.201.33:8080/docs"
echo "- ReDoc: http://100.106.201.33:8080/redoc"
echo "- OpenAPI JSON: http://100.106.201.33:8080/openapi.json"
```

## 7. Performance and Monitoring

### API Performance
```bash
echo "=== PERFORMANCE OPTIMIZATION ==="

# FastAPI performance tuning
echo "Performance Features:"
echo "- [ ] Async endpoint implementation"
echo "- [ ] Connection pooling configuration"
echo "- [ ] Response caching with Redis"
echo "- [ ] Database query optimization"
echo "- [ ] File upload streaming"

echo ""
echo "Monitoring Integration:"
echo "- [ ] Prometheus metrics collection"
echo "- [ ] Request/response time tracking"
echo "- [ ] Error rate monitoring"
echo "- [ ] Database performance metrics"
```

### Error Handling
```bash
echo "=== ERROR HANDLING ==="

# Comprehensive error management
echo "Error Handling Strategy:"
echo "- [ ] Custom exception classes"
echo "- [ ] HTTP status code mapping"
echo "- [ ] User-friendly error messages"
echo "- [ ] Detailed logging for debugging"
echo "- [ ] Error response standardization"

echo ""
echo "Lumen-specific Errors:"
echo "- Authentication failures"
echo "- Image processing errors"
echo "- Database constraint violations"
echo "- File upload failures"
echo "- Geographic service errors"
```

## 8. Integration Points

### Frontend API Integration
```bash
echo "=== FRONTEND INTEGRATION ==="

# API endpoints for frontend consumption
echo "Frontend Integration Points:"
echo "- [ ] User authentication endpoints"
echo "- [ ] Profile management APIs"
echo "- [ ] Photo upload/retrieval APIs"
echo "- [ ] Search and discovery APIs"
echo "- [ ] Real-time notification APIs"

echo ""
echo "CORS Configuration:"
echo "- [ ] Proper CORS headers for development"
echo "- [ ] Production domain whitelisting"
echo "- [ ] Preflight request handling"
```

### External Service Integration
```bash
echo "=== EXTERNAL SERVICES ==="

# Third-party service integration
echo "External APIs:"
echo "- [ ] Firebase Authentication"
echo "- [ ] Google Cloud Storage for images"
echo "- [ ] Geocoding for location services"
echo "- [ ] Email service for notifications"

echo ""
echo "Service Health Checks:"
echo "- [ ] Firebase connectivity"
echo "- [ ] Database connectivity"
echo "- [ ] Storage service availability"
echo "- [ ] External API rate limits"
```

## 9. Security Implementation

### API Security
```bash
echo "=== API SECURITY ==="

# Security best practices
echo "Security Checklist:"
echo "- [ ] Input sanitization and validation"
echo "- [ ] SQL injection prevention"
echo "- [ ] XSS protection"
echo "- [ ] Rate limiting implementation"
echo "- [ ] HTTPS enforcement"
echo "- [ ] Sensitive data encryption"

echo ""
echo "Lumen-specific Security:"
echo "- Profile privacy controls"
echo "- Image metadata scrubbing"
echo "- Location data protection"
echo "- Age verification compliance"
```

## 10. Deployment Preparation

### Production Readiness
```bash
echo "=== PRODUCTION READINESS ==="

# Pre-deployment checklist
echo "Deployment Checklist:"
echo "- [ ] Environment variable configuration"
echo "- [ ] Database migration scripts"
echo "- [ ] Static file serving setup"
echo "- [ ] Health check endpoints"
echo "- [ ] Logging configuration"
echo "- [ ] Monitoring integration"

echo ""
echo "Performance Validation:"
echo "- [ ] Load testing completed"
echo "- [ ] Memory usage optimized"
echo "- [ ] Database queries optimized"
echo "- [ ] Error handling tested"
```

## Implementation Notes

- **Architecture**: Follow FastAPI best practices with clean separation
- **Database**: Use PostgreSQL with flexible JSONB for extensibility
- **Authentication**: Integrate with Firebase for consistent auth
- **Performance**: Implement async operations and caching
- **Testing**: Comprehensive test coverage for all endpoints

This command integrates with:
- `/check` for API testing validation
- `/dev` for local API development
- `/deploy` for production API deployment
- Frontend `/ui` command for full-stack integration