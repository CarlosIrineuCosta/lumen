# Lumen Codebase Structure & Architecture

## Project Root Structure
```
wasenet/                           # Main project directory
├── CLAUDE.md                     # Claude Code instructions
├── README.md                     # Project documentation overview
├── lumen-gcp/                    # Main application directory
├── docs/                         # Documentation (CODE- and STRATEGY- prefixed)
└── screenshots/                  # Development screenshots
```

## Core Application Structure (lumen-gcp/)

### Backend Architecture
```
backend/
├── app/                          # Main application package
│   ├── main.py                   # FastAPI application entry point
│   ├── api/                      # API layer
│   │   ├── endpoints/            # Route handlers by domain
│   │   │   ├── auth.py           # Authentication endpoints
│   │   │   ├── users.py          # User management endpoints
│   │   │   └── photos.py         # Photo management endpoints
│   │   └── deps/                 # Dependency injection modules
│   ├── models/                   # Data models
│   │   ├── user.py               # User SQLAlchemy + Pydantic models
│   │   ├── photo.py              # Photo SQLAlchemy + Pydantic models
│   │   ├── lookup_tables.py      # Cities, specialties, user types
│   │   └── relationships.py      # Association tables and connections
│   ├── services/                 # Business logic layer
│   │   ├── user_service.py       # User operations and validation
│   │   └── photo_service.py      # Photo processing and storage
│   ├── database/                 # Database utilities
│   │   ├── connection.py         # Database connection management
│   │   └── __init__.py
│   ├── firebase_config.py        # Firebase Admin SDK configuration
│   └── auth_middleware.py        # Authentication middleware
├── database/                     # Database schema and data
│   ├── schema.sql                # PostgreSQL database schema
│   └── seed_data.sql             # Sample data for development
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container configuration
├── .env.example                  # Environment variables template
└── server.log                    # Server logs (runtime generated)
```

### Frontend Architecture (Current Web Interface)
```
frontend/
├── lumen-app.html                # Main application interface
├── css/
│   └── lumen.css                 # Main stylesheet with CSS variables
├── js/
│   └── lumen-gallery.js          # Gallery functionality and Firebase integration
├── assets/                       # Images and static resources
├── public/                       # Public assets
├── firebase-test-client.html     # Firebase authentication testing
├── simple-test-client.html       # API endpoint testing
├── auth-debug.html               # Authentication debugging
├── user-registration.html        # User registration interface
├── portfolio-generator.html      # Portfolio generation tool
├── package.json                  # Node.js dependencies (Expo/React Native)
└── README.md                     # Frontend documentation
```

### Infrastructure & Deployment
```
infrastructure/
├── terraform/                    # Infrastructure as Code
│   ├── main.tf                   # Main Terraform configuration
│   ├── variables.tf              # Variable definitions
│   ├── modules/                  # Reusable Terraform modules
│   └── environments/             # Environment-specific configs
├── scripts/                      # Monitoring and utility scripts
│   ├── monitor_costs.py          # Daily cost monitoring
│   └── simple_cost_monitor.py    # Basic cost checking
└── monitoring/                   # Monitoring configuration

deploy/
├── deploy.sh                     # Deployment script for Cloud Run
├── production/                   # Production deployment configs
└── staging/                      # Staging deployment configs

config/
├── development/                  # Development environment config
├── production/                   # Production environment config
└── staging/                      # Staging environment config
```

## Data Model Architecture

### Database Schema Overview
```sql
-- Core entities
users                    # User profiles with JSONB flexibility
photos                   # Photo metadata and storage references
cities                   # Geographic data for user locations
user_types              # Photographer/Model classification
specialties             # Photography style categories

-- Relationship tables
user_specialties        # Many-to-many user-specialty mapping
photo_collaborators     # Photo collaboration tracking
user_connections        # Professional networking relationships
photo_interactions      # Likes, comments, shares
```

### Key Model Patterns

#### SQLAlchemy Models
- **Base Class**: Inherits from declarative_base()
- **UUID Primary Keys**: `gen_random_uuid()` for distributed uniqueness
- **JSONB Fields**: Flexible schema expansion (`profile_data`, `camera_data`)
- **Relationships**: Proper back_populates and cascade configurations
- **Timestamps**: Automatic `created_at`, `updated_at` with timezone

#### Pydantic Models
- **Request Models**: Input validation with Field constraints
- **Response Models**: Output serialization with `from_attributes=True`
- **Nested Models**: Complex structures with proper type hints
- **Enums**: String enums for controlled vocabularies

## API Architecture

### Endpoint Organization
```
/api/v1/
├── auth/                         # Authentication & authorization
│   ├── test                      # Public endpoint for testing
│   ├── status                    # Authentication status check
│   ├── profile                   # Current user profile
│   └── logout                    # Logout endpoint
├── users/                        # User management
│   ├── profile                   # User profile CRUD
│   ├── search                    # User discovery
│   └── {user_id}                 # Public user profile
└── photos/                       # Photo management
    ├── upload                    # Photo upload and processing
    ├── stream                    # Photo feed with pagination
    ├── {photo_id}                # Individual photo operations
    └── user/{user_id}            # User's photo gallery
```

### Authentication Flow
1. **Client**: Firebase authentication (Google OAuth)
2. **Token**: Firebase ID token sent to backend
3. **Validation**: Firebase Admin SDK validates token
4. **Middleware**: Custom auth middleware extracts user data
5. **Authorization**: Endpoint-level protection via FastAPI dependencies

## Frontend Architecture Patterns

### Current Web Interface (Transitional)
- **Vanilla JavaScript**: Direct DOM manipulation for MVP speed
- **Firebase Web SDK**: Client-side authentication
- **Justified Gallery**: 500px-style photo layout library
- **CSS Custom Properties**: Consistent theming system
- **Responsive Design**: Mobile-first CSS approach

### Future React Native (Planned)
- **Expo Framework**: Cross-platform development
- **React Navigation**: Stack-based navigation
- **Firebase SDK**: Authentication and storage
- **TypeScript**: Type safety and development experience

## Storage Architecture

### Google Cloud Storage
```
lumen-photos-bucket/
├── originals/                    # Full-resolution images
│   └── {user_id}/
│       └── {photo_id}.{ext}
├── thumbnails/                   # Auto-generated thumbnails
│   └── {user_id}/
│       └── {photo_id}_thumb.{ext}
└── temp/                         # Temporary upload processing
```

### Database Storage Patterns
- **File References**: URLs stored in database, files in Cloud Storage
- **Metadata**: EXIF, camera data, and AI tags in JSONB fields
- **Flexible Schemas**: JSONB for evolving data structures
- **Indexing**: Optimized queries for user searches and photo feeds

## Service Layer Architecture

### Business Logic Organization
```python
# Service layer pattern
class UserService:
    def create_user(self, request: CreateUserRequest) -> UserProfileFull
    def update_profile(self, user_id: str, request: UpdateUserRequest) -> UserProfileFull
    def search_users(self, query: UserSearchQuery) -> List[UserProfilePublic]

class PhotoService:
    def upload_photo(self, user_id: str, file: bytes, request: CreatePhotoRequest) -> PhotoResponse
    def get_photo_stream(self, query: PhotoSearchQuery) -> PhotoListResponse
    def update_photo(self, photo_id: str, request: UpdatePhotoRequest) -> PhotoResponse
```

### Dependency Injection Pattern
```python
# FastAPI dependency injection
async def get_current_user(token: str = Depends(auth_middleware)) -> AuthUser:
    return AuthUser(token)

@router.get("/profile")
async def get_profile(user: AuthUser = Depends(get_current_user)):
    return user_service.get_profile(user.uid)
```

## Configuration Management

### Environment Variables
```bash
# Core services
PROJECT_ID=lumen-photography-platform
GCS_BUCKET_NAME=lumen-photos-bucket
FIREBASE_PROJECT_ID=lumen-photo-app-20250731

# Database
DATABASE_URL=postgresql://[user]:[pass]@[host]/[db]
CLOUD_SQL_CONNECTION_NAME=project:region:instance

# Authentication
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
FIREBASE_SERVICE_ACCOUNT_KEY=/path/to/firebase-key.json

# API configuration
ALLOWED_ORIGINS=http://100.106.201.33:8000,http://localhost:3000
```

### Firebase Configuration
- **Admin SDK**: Server-side token validation and user management
- **Web SDK**: Client-side authentication and file uploads
- **Security Rules**: Proper access control for user data

## Development Workflow Integration

### Hot Reload Development
- **Backend**: `uvicorn --reload` for automatic code reloading
- **Frontend**: Static file serving with manual refresh
- **Database**: Schema changes require manual migration

### Testing Architecture
- **Manual Testing**: HTML test clients for API validation
- **Integration Testing**: Full user flow through web interface
- **Service Testing**: Individual component validation scripts

## Key Architectural Decisions

### Flexibility First
- **JSONB Fields**: Allow schema evolution without migrations
- **Modular Services**: Business logic separated from API layer
- **Pluggable Authentication**: Firebase can be replaced if needed

### Performance Considerations
- **UUID Primary Keys**: Distributed database compatibility
- **Image Processing**: Automatic thumbnail generation
- **Database Indexing**: Optimized for common query patterns
- **CDN Ready**: Cloud Storage URLs for global content delivery

### Security by Design
- **Token-based Auth**: Stateless authentication with Firebase
- **Input Validation**: Pydantic models for all API inputs
- **CORS Configuration**: Controlled cross-origin access
- **Environment Isolation**: Separate configs for dev/staging/production

This architecture supports the MVP development while providing flexibility for future growth and feature additions.