# Database Architecture Decision

## Problem Identified (2025-08-04)

Critical architectural mismatch discovered during upload functionality implementation:

1. **PostgreSQL Models** (`/models/photo.py`): SQLAlchemy with `CreatePhotoRequest` requiring `image_url: str`
2. **Firestore Service** (`/services/photo_service.py`): Using `firestore.client()` with file upload handling
3. **API Endpoint** (`/api/endpoints/photos.py`): Expects file upload but validates with PostgreSQL model

**Upload Failure:** `1 validation error for CreatePhotoRequest image_url Field required`

## Decision: PostgreSQL Architecture

**Chosen:** PostgreSQL (Cloud SQL) over Firestore

**Technical Reasons:**
1. Database connection already configured (`/database/connection.py`)
2. Complete SQLAlchemy models already implemented
3. Better support for complex photography metadata queries
4. ACID transactions for data integrity
5. Standard SQL for easier development and maintenance

**Implementation Changes Required:**
1. Replace `PhotoService` Firestore implementation with PostgreSQL
2. Update service to use SQLAlchemy sessions
3. Maintain file upload handling to Cloud Storage
4. Fix API endpoint validation flow

**Files to Update:**
- `/services/photo_service.py` - Replace Firestore with PostgreSQL
- `/api/endpoints/photos.py` - Fix upload validation
- Test upload workflow end-to-end

**Cost Impact:** +$8.50/month vs Firestore (acceptable for better architecture)

**Status:** Implementation in progress
**Date:** 2025-08-04