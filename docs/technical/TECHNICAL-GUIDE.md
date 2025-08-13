# Lumen - Technical Implementation Guide

**FOR DEVELOPERS AND CODE IMPLEMENTATION**  
**Last Updated**: August 13, 2025

## System Architecture Overview

### Technology Stack
- **Backend**: FastAPI 0.104.1 (Python 3.11.x)
- **Frontend**: PWA-ready vanilla JavaScript with Instagram-style dark mode
- **Database**: PostgreSQL via Cloud SQL with SQLAlchemy 2.0.23 ORM
- **Authentication**: Dual-layer system (Firebase Admin SDK + gcloud auth)
- **Storage**: Google Cloud Storage (Bucket: lumen-photos-20250731)
- **Image Processing**: PIL for thumbnails, planned MozJPEG/Guetzli pipeline
- **Infrastructure**: Google Cloud Platform (Project: lumen-photo-app-20250731)

### Architecture Decisions
- **PostgreSQL over Firestore**: Better complex queries, ACID transactions, $8.50/month extra acceptable
- **Firebase UIDs as Primary Keys**: Maintain consistency with GCS file paths
- **Dynamic URL Generation**: No redundant URL storage in database (saves 1200+ chars per photo)
- **Microservices Design**: Clear separation between backend API and frontend PWA

## Current Implementation Status

### ✅ Working Features

#### User Management
- **Complete Registration**: Firebase OAuth → PostgreSQL user creation
- **Profile System**: Full CRUD with photographer/model types, experience levels
- **Profile Images**: Upload/update/delete with GCS storage
- **User Discovery**: Search by type, location, experience level

#### Photo Management  
- **Upload Pipeline**: Complete flow to Google Cloud Storage
- **Thumbnail Generation**: Automatic 400x400px with PIL
- **EXIF Extraction**: Camera make, model, settings captured
- **Photo Editing**: Update titles, descriptions, tags
- **Photo Deletion**: Complete removal from storage and database

#### Discovery & Social
- **Recent Photos Feed**: Paginated timeline with infinite scroll
- **User Galleries**: Individual photographer portfolios
- **Portfolio Filter**: Separate portfolio vs all photos views
- **Like System**: Photo engagement tracking
- **Search**: Photos by tags, location, content

#### Infrastructure
- **Server Management**: Automated scripts for process control
- **Tailscale Network**: Development access via 100.106.201.33
- **Database Optimization**: Indexes, no redundant URL storage
- **Error Handling**: Comprehensive fallback mechanisms

### 🚧 In Progress
- Performance optimization (signed URL caching)
- Advanced search with geolocation
- Mobile PWA installation
- Image compression pipeline

### ❌ Not Yet Implemented
- Real-time notifications
- Messaging system
- Payment processing
- TV display feature (4K output)

## ID Management System (CRITICAL)

### Overview
Lumen uses a comprehensive ID validation system to ensure consistency between Firebase Authentication, PostgreSQL database, and Google Cloud Storage paths.

### ID Format Standards
- **Firebase UIDs**: 28-character alphanumeric strings (e.g., `9pGzwsVBRMaSxMOZ6QNTJJjnl1b2`)
- **Photo IDs**: UUID4 format (e.g., `c711a9ab-4689-4576-a511-7ce60cc214f3`)
- **Storage Paths**: `photos/{firebase_uid}/{photo_uuid}.jpg`

### Using ID Validation

```python
from app.utils import validate_firebase_uid, validate_uuid, validate_id_consistency
from app.services import IDManagementService

# Basic validation
user_id = validate_firebase_uid(firebase_user.uid, "photo upload")
photo_uuid = validate_uuid(photo_id, "photo retrieval")

# ID Management Service
id_service = IDManagementService()
photo_path, thumb_path = id_service.generate_storage_paths(user_id, photo_id)
normalized_user_id = id_service.normalize_user_id(user_id)
```

### Audit Tools
```bash
# Check GCS file formats
python scripts/audit_gcs_files.py --limit 1000 --verbose

# Check database consistency
python scripts/check_db_consistency.py --tables users,photos --verbose
```

## Database Schema

### Users Table (Firebase UID Primary Key)
```sql
CREATE TABLE users (
    id VARCHAR(128) PRIMARY KEY,  -- Firebase UID (NOT UUID)
    email VARCHAR(255) UNIQUE NOT NULL,
    handle VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    bio TEXT,
    profile_image_url VARCHAR(500),
    city_id INTEGER REFERENCES cities(id),
    primary_user_type INTEGER REFERENCES user_types(id),
    experience_level INTEGER REFERENCES experience_levels(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Photos Table
```sql
CREATE TABLE photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(128) REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    description TEXT,
    user_tags TEXT[],
    ai_tags JSONB,
    camera_data JSONB,
    is_public BOOLEAN DEFAULT true,
    is_portfolio BOOLEAN DEFAULT false,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Key Design Decisions
- No URL storage in database (generated dynamically)
- CASCADE DELETE for data integrity
- JSONB for flexible metadata storage
- Array fields for tags

## API Endpoints

### Authentication (`/api/v1/auth/`)
- `GET /status` - Check authentication status
- `GET /profile` - Current user auth profile  
- `POST /logout` - User logout

### Users (`/api/v1/users/`)
- `POST /register` - New user registration
- `GET /me` - Full user profile
- `PUT /me` - Update user profile
- `POST /me/profile-image` - Upload profile image
- `DELETE /me/profile-image` - Remove profile image
- `GET /{user_id}/public` - View other user's profile
- `POST /search` - Search users

### Photos (`/api/v1/photos/`)
- `POST /upload` - Upload new photo
- `GET /recent` - Recent photos feed
- `GET /user/{user_id}` - User's photo gallery
- `GET /{photo_id}` - Photo details
- `PUT /{photo_id}` - Update photo metadata
- `DELETE /{photo_id}` - Delete photo
- `POST /{photo_id}/like` - Like/unlike toggle
- `POST /search` - Search photos

## Development Environment

### File Structure
```
wasenet/
├── opusdev/              # PWA frontend
│   ├── backend/          # FastAPI application
│   │   ├── app/
│   │   │   ├── api/endpoints/
│   │   │   ├── models/
│   │   │   ├── services/
│   │   │   └── utils/
│   │   └── tests/
│   ├── css/app.css
│   ├── js/
│   └── index.html
├── scripts/
│   └── server-manager.sh
└── docs/
```

### Development Setup
```bash
# Backend
cd opusdev/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start servers
./scripts/server-manager.sh start
```

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/lumen
DB_HOST=localhost
DB_PORT=5432

# Firebase
FIREBASE_PROJECT_ID=lumen-photo-app-20250731
GOOGLE_APPLICATION_CREDENTIALS=firebase_service_account.json

# Storage
STORAGE_BUCKET_NAME=lumen-photos-20250731

# API
ALLOWED_ORIGINS=http://localhost:8000,http://100.106.201.33:8000
```

## Testing Framework

### Test Structure
- **Unit Tests**: `tests/unit/` - Models, utilities, business logic
- **Integration Tests**: `tests/integration/` - API endpoints, database
- **Coverage Target**: 70%+ with `pytest --cov=app`

### Running Tests
```bash
# All tests
pytest

# Unit tests only (fast)
pytest -m unit

# With coverage
pytest --cov=app --cov-report=term-missing

# Specific test
pytest -vvv tests/unit/test_user_model.py::TestUserModel::test_method
```

### Test Categories
- `@pytest.mark.unit` - Fast, isolated tests
- `@pytest.mark.integration` - Database/API tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.photos` - Photo management tests

## Performance Considerations

### Current Issues
- **Signed URL Generation**: 1-2 seconds for large collections
- **No Caching**: URLs regenerated on every request
- **Database Queries**: May need optimization at scale

### Optimization Strategy
1. **Redis Caching**: For signed URLs (1-hour expiry)
2. **Database Indexes**: On frequently queried columns
3. **CDN Integration**: For image delivery
4. **Query Optimization**: Prevent N+1 problems

### Performance Targets
- API Response: <200ms
- Image Load: <1s for thumbnail
- Page Load: <2s total
- Database Query: <50ms

## Image Processing Pipeline

### Current Implementation
- **Upload**: Direct to GCS with original quality
- **Thumbnails**: 400x400px generated with PIL
- **Formats**: JPEG only currently

### Planned Pipeline
```
Upload → Process → Store:
├── Thumbnail (400x400) → Grid display
├── Web (1200px) → Standard viewing
├── Portfolio (2400px) → Professional display
└── TV (4K) → Large screen viewing
```

### Storage Structure
```
lumen-photos-20250731/
├── photos/{user_id}/{photo_id}.jpg
├── thumbnails/{user_id}/{photo_id}_thumb.jpg
└── profile-images/{user_id}/profile.jpg
```

## Security Considerations

### Authentication
- Firebase JWT validation on all protected endpoints
- Dual-layer auth system for development/production
- Token refresh handling

### Data Protection
- Input validation on all endpoints
- SQL injection prevention via SQLAlchemy
- XSS protection in frontend
- CORS configuration for allowed origins

### Privacy
- User data ownership and export capabilities
- Optional anonymous browsing
- Granular privacy controls

## Deployment

### Development Access
- Backend: http://100.106.201.33:8080
- Frontend: http://100.106.201.33:8000
- API Docs: http://100.106.201.33:8080/docs

### Production Deployment
```bash
# Deploy to Cloud Run
./deploy/deploy.sh [PROJECT_ID]

# Update infrastructure
cd infrastructure/terraform
terraform apply
```

### Monitoring
- Cost tracking: $3-7/day target
- Error logging with structured output
- Performance metrics collection

## Critical System Dependencies

### Firebase UID vs Database Consistency
**WARNING: This is the most fragile part of the system**

1. **Firebase**: Creates UIDs like `9pGzwsVBRMaSxMOZ6QNTJJjnl1b2`
2. **Database**: Stores Firebase UID directly (NOT UUID)
3. **GCS**: Photos at `gs://lumen-photos-20250731/photos/{firebase_uid}/{photo_id}.jpg`

### Critical Code Locations
- `backend/app/services/photo_service.py` - URL generation
- `backend/app/models/user.py` - User ID definition
- `backend/app/models/photo.py` - Photo user_id reference

### If Images Stop Loading
1. Check bucket name in PhotoService
2. Verify Firebase UID format in database
3. Test: `gsutil ls gs://lumen-photos-20250731/photos/`

## Development Guidelines

### Code Standards
- Type hints for all functions
- Docstrings for public methods
- Error handling with proper logging
- Test coverage for new features

### Git Workflow
- Feature branches from main
- PR reviews required
- Run tests before merging
- Update documentation

### Daily Workflow
1. Run `./scripts/server-manager.sh clean`
2. Check SHARED-STATUS.md
3. Update todo list for complex tasks
4. Test changes thoroughly
5. Update documentation

---

*This document provides complete technical implementation guidelines for the Lumen platform. For business strategy and content policies, see the business documentation.*