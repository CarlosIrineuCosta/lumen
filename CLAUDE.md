# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Critical Rules
- **NEVER USE EMOJIS** - Never add emojis to any files, responses, or UI elements
- **NEVER GET STUCK IN LOOPS** - Always use `nohup` with `&` for servers, never wait for output
- **DAILY SERVER CLEANUP** - Always run `./scripts/server-manager.sh clean` before starting work to prevent port conflicts
- **USE SERENA EXTENSIVELY** - Leverage semantic analysis, memory system, and symbol-level code understanding instead of basic file operations
- **NO MOCKS** - Never use mock data or temporary workarounds, always implement real functionality
- **READ ALL MD FILES ON START** - Always check project_status.md, CLAUDE.md, and README.md first
- **ALWAYS USE ID VALIDATION** - Use `app.utils` validation functions for all Firebase UIDs and UUIDs to prevent image loading issues

## ID Management (CRITICAL)

**NEVER bypass ID validation** - All Firebase UIDs and UUIDs MUST be validated using the centralized system:

```python
# Always validate IDs in your code
from app.utils import validate_firebase_uid, validate_uuid, validate_id_consistency
from app.services import IDManagementService

# Validate Firebase UID (28-char alphanumeric)
user_id = validate_firebase_uid(firebase_user.uid, "operation context")

# Validate UUID format
photo_uuid = validate_uuid(photo_id, "operation context")

# Use ID Management Service for complex operations
id_service = IDManagementService()
photo_path, thumb_path = id_service.generate_storage_paths(user_id, photo_id)
```

**Key Points:**
- Firebase UIDs = 28-char strings (NOT UUIDs) - used for users and GCS paths
- Photo IDs = UUID4 format - used for photos and database references
- NEVER mix up these formats or images will show as placeholders
- Use audit scripts to check consistency: `python scripts/audit_gcs_files.py` and `python scripts/check_db_consistency.py`

## Project Overview
Lumen - Professional photography platform with real photo uploads, Firebase auth, and Google Cloud Storage. Instagram-like interface focused on professional photography networking and people-first discovery.

## Core Business Principles
- **NO ADS EVER** - Clean, distraction-free photography experience
- **NO ALGORITHMIC PLACEMENT** - Chronological, user-controlled content discovery
- **PEOPLE-FIRST DISCOVERY** - Find photographers/models, not just browse images
- **PROFESSIONAL NETWORKING** - Real-world connections via GPS proximity
- **SUBSCRIPTION MODEL** - $5-150/year, no data exploitation or engagement manipulation

## Architecture Overview

The application follows a microservices architecture with clear separation of concerns:

### Backend (`lumen-gcp/backend/`)
- **Framework**: FastAPI 0.104.1 with Python 3.11.x
- **Database**: PostgreSQL via Cloud SQL with SQLAlchemy 2.0.23 ORM
- **Authentication**: Dual-layer system (Firebase Admin SDK + gcloud auth)
- **Storage**: Google Cloud Storage for photos
- **API Structure**: Modular endpoints in `app/api/endpoints/`
  - `auth.py` - Authentication and user registration
  - `photos.py` - Photo upload, retrieval, and management
  - `users.py` - User profile management

### Frontend (`lumen-gcp/frontend/`)
- **Tech Stack**: Expo ~49.0.0 with React Native for cross-platform support
- **Web Interface**: `lumen-app.html` - main application entry point
- **Styling**: `css/lumen.css` - custom styling
- **JavaScript**: `js/lumen-gallery.js` - photo gallery functionality
- **Gallery System**: Professional Masonry.js grid layout

### Database Schema
- **Users**: Flexible schema with photographer/model types, specialties, locations
- **Photos**: Rich metadata including camera data, location, tags, collaborators
- **Relationships**: User connections, photo interactions, specialties mapping
- **Geographic**: Cities table for location-based discovery

## Development Commands

### Server Management (Primary Method)
```bash
# Clean startup - ALWAYS USE THIS
./scripts/server-manager.sh start

# Check server status
./scripts/server-manager.sh status

# Stop all servers
./scripts/server-manager.sh stop

# Restart servers
./scripts/server-manager.sh restart

# Clean processes without starting
./scripts/server-manager.sh clean
```

### Manual Server Commands (Fallback Only)
```bash
# Backend (port 8080)
cd lumen-gcp/backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 &

# Frontend (port 8000)
cd lumen-gcp/frontend
python3 -m http.server 8000
```

### Database Operations
```bash
# Initialize database with schema and seed data
cd lumen-gcp/backend
source venv/bin/activate
python init_db.py

# Connect to PostgreSQL (requires gcloud auth)
gcloud sql connect [INSTANCE_NAME] --user=postgres --database=lumen
```

### Development Setup
```bash
# Backend setup
cd lumen-gcp/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd lumen-gcp/frontend
npm install
```

### Testing Commands
```bash
# Run all tests
cd lumen-gcp/backend && source venv/bin/activate && pytest

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run only unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run specific test categories
pytest -m auth          # Authentication tests
pytest -m photos        # Photo management tests

# Run tests in parallel
pytest -n auto

# Debug failing test
pytest -vvv -s tests/unit/test_user_model.py::TestUserModel::test_method
```

### Testing and Deployment
```bash
# Deploy backend to Cloud Run
./lumen-gcp/deploy/deploy.sh [PROJECT_ID]

# Expo development commands
cd lumen-gcp/frontend
npm start          # Start Expo development server
npm run web        # Run web version
npm run build:web  # Build for web deployment
npm run deploy:web # Deploy to Firebase hosting

# Infrastructure management
cd lumen-gcp/infrastructure/terraform
terraform init
terraform plan
terraform apply

# Cost monitoring
python lumen-gcp/infrastructure/scripts/monitor_costs.py
```

## Authentication Architecture (Critical)

Lumen uses a **dual-layer authentication system**:

### Layer 1: Personal Authentication (Primary)
- **Method**: `gcloud auth login carlos.irineu@gmail.com`
- **Purpose**: Direct access to GCP services (Cloud SQL, Storage)
- **Priority**: ALWAYS try this first for development

### Layer 2: Service Account (Secondary)
- **File**: `firebase_service_account.json`
- **Purpose**: Firebase Admin SDK operations, background tasks
- **Scope**: Limited application-level permissions

### Environment Configuration
```bash
# Development (use personal auth)
unset GOOGLE_APPLICATION_CREDENTIALS

# Production (use service account)
export GOOGLE_APPLICATION_CREDENTIALS=firebase_service_account.json
```

### Authentication Troubleshooting
- **409 Conflict errors**: Service account lacks permissions - switch to personal auth
- **Missing photos**: Verify correct auth method for database queries
- **Upload failures**: Ensure `gcloud auth` is active

## Network Access

All development accessible via Tailscale network (100.106.201.33):

- **Backend API**: http://100.106.201.33:8080
- **API Documentation**: http://100.106.201.33:8080/docs
- **Frontend App**: http://100.106.201.33:8000/lumen-app.html
- **Never use localhost** - always use Tailscale IP

## Key File Locations

### Core Application Files
- **Main App**: `lumen-gcp/frontend/lumen-app.html`
- **Backend Entry**: `lumen-gcp/backend/app/main.py`
- **CSS**: `lumen-gcp/frontend/css/lumen.css`
- **JavaScript**: `lumen-gcp/frontend/js/lumen-gallery.js`

### Configuration Files
- **Requirements**: `lumen-gcp/backend/requirements.txt`
- **Package Config**: `lumen-gcp/frontend/package.json`
- **Database Schema**: `lumen-gcp/backend/database/schema.sql`
- **Seed Data**: `lumen-gcp/backend/database/seed_data.sql`

### Infrastructure
- **Terraform**: `lumen-gcp/infrastructure/terraform/`
- **Deployment**: `lumen-gcp/deploy/deploy.sh`
- **Server Manager**: `scripts/server-manager.sh`

## Dependencies

### Backend Key Libraries
- **FastAPI 0.104.1** - Web framework
- **SQLAlchemy 2.0.23** - Database ORM
- **firebase-admin 6.3.0** - Authentication
- **google-cloud-storage 2.10.0** - File storage
- **uvicorn[standard] 0.24.0** - ASGI server
- **psycopg2-binary 2.9.9** - PostgreSQL adapter

### Frontend Key Libraries
- **Expo ~49.0.0** - React Native framework
- **Firebase 10.5.0** - Authentication client
- **React Navigation 6.x** - Navigation

## Development Philosophy
- **NO MOCKS**: Always implement real functionality with actual services
- **QUALITY OVER SCALE**: Professional photography focus, not viral growth
- **USER EMPOWERMENT**: Users own their data, complete export capabilities
- **DIRECT FIXES**: Address issues directly rather than working around them

## Multi-AI Coordination System

### Roles
- **Claude Code**: Head developer (technical implementation lead)
- **Claude Desktop**: Systems architect and business planner
- **Gemini CLI**: GCP and Firebase specialist

### Gemini CLI Specific Responsibilities
When working with Gemini CLI, focus on:
- **Firebase Authentication**: Token validation, user management, security rules
- **Google Cloud Storage**: Bucket management, permissions, image upload flows
- **Cloud SQL**: Database connections, query optimization, backup strategies
- **Infrastructure**: GCP service configuration, monitoring, cost optimization
- **API Integration**: Firebase Admin SDK, Cloud SDK troubleshooting

### Documentation Structure
- **CODE-** prefix: Technical implementation documents (Claude Code territory)
- **STRATEGY-** prefix: Business strategy documents (Claude Desktop territory)
- **SHARED-STATUS.md**: Coordination file - ALWAYS CHECK AND UPDATE

### Firebase & GCP Commands Reference
```bash
# Firebase CLI
firebase projects:list
firebase auth:export
firebase storage:rules:get
firebase hosting:sites:list

# Google Cloud SDK
gcloud auth list
gcloud projects list
gcloud sql instances list
gcloud storage buckets list

# Testing connectivity
firebase functions:config:get
gsutil ls gs://bucket-name
gcloud sql connect instance-name --user=username
```

## Current Development Status

### Completed Features
- Firebase authentication with Google OAuth
- PostgreSQL database schema and models
- Photo upload pipeline with Cloud Storage
- Backend API endpoints for auth, users, photos
- Frontend gallery with Masonry.js layout
- Server management automation

### Known Issues
- **Performance**: Google Cloud Storage signed URL generation slow (11+ seconds for 2 photos)
- **Testing**: No test files currently exist - needs pytest implementation
- **CORS**: Currently allows all origins - needs production configuration

### MVP Requirements
- User profile management (edit display name, bio, city, specialties)
- Model-specific fields (gender, age, height, weight)
- Photo stream with infinite scroll
- Real-time gallery updates after uploads
- User connection/networking system

## Testing Framework

### Test Structure
- **Unit Tests**: Fast, isolated tests in `tests/unit/` (models, utilities, business logic)
- **Integration Tests**: API endpoints, database operations in `tests/integration/`
- **Coverage Target**: 70%+ code coverage with `pytest --cov=app`
- **Test Categories**: Use markers (`@pytest.mark.unit`, `@pytest.mark.auth`, `@pytest.mark.photos`)

### Test Database
- SQLite in-memory database for tests
- Each test gets fresh database session (automatic cleanup)
- Mock Firebase authentication and Google Cloud Storage
- Test fixtures available for common data (`sample_user_data`, `sample_photo_data`)

### Running Tests Efficiently
1. **Development**: `pytest -m unit` (fast unit tests only)
2. **Pre-commit**: `pytest --cov=app --cov-fail-under=70` (full suite with coverage)
3. **Debugging**: `pytest -vvv -s path/to/test.py::TestClass::test_method`
4. **CI/CD**: `pytest -n auto` (parallel execution)

## Development Policies

### Bash Command Execution Guidelines
**Run bash commands directly for normal troubleshooting.** Only ask user for help with:
- Process management and server operations that might hang
- Permission or access issues (sudo, file permissions)
- Long-running operations or system-level changes
- Directory navigation issues with path resolution failures

### Daily Project Management
- Document session start time in daily .md files
- Use TodoWrite for complex multi-step tasks  
- Clean up server processes daily to prevent conflicts
- Always check and update SHARED-STATUS.md for coordination

### Multi-AI Coordination
- **Claude Code**: Technical implementation lead
- **Gemini CLI**: GCP and Firebase specialist
- Reference SHARED-STATUS.md for real-time coordination between AI assistants

## CRITICAL SYSTEM DEPENDENCIES (READ BEFORE ANY CHANGES!)

### Firebase UID vs Database vs Google Cloud Storage Consistency
**THIS IS THE MOST FRAGILE PART OF THE SYSTEM - BREAKING THIS BREAKS IMAGE LOADING**

1. **Firebase Authentication**: Creates UIDs like `9pGzwsVBRMaSxMOZ6QNTJJjnl1b2` (28-char strings)
2. **Database Storage**: Uses UUID format in `users.id` and `photos.user_id` columns
3. **Google Cloud Storage**: Photos stored at `gs://lumen-photos-20250731/photos/{firebase_uid}/{photo_id}.jpg`

**CRITICAL PATH CONSISTENCY REQUIREMENTS:**
- **Bucket Name**: Code MUST use `lumen-photos-20250731` (NOT `lumen-photo-app-20250731.appspot.com`)
- **UID Format**: Database UUIDs must map to GCS Firebase UID strings for signed URL generation
- **File Paths**: Any change to UID format requires migrating ALL existing files in GCS

**WARNING LOCATIONS IN CODE:**
- `opusdev/backend/app/services/photo_service.py` - bucket_name and _generate_photo_urls()
- `opusdev/backend/app/models/user.py` - User.id column definition
- `opusdev/backend/app/models/photo.py` - Photo.user_id column definition

**IF IMAGES STOP LOADING:**
1. Check bucket name in PhotoService.__init__()
2. Verify Firebase UID format matches between database and GCS paths
3. Test: `gsutil ls gs://lumen-photos-20250731/photos/` to see actual file paths

## Important Notes
- Development environment accessible from any OS via Tailscale network
- Daily budget monitoring implemented (target: $3-7/day)
- Comprehensive test suite with 70%+ coverage target
- Project uses Google Cloud services extensively