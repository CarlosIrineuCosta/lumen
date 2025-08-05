# Backend/Frontend Integration Issues - Analysis

## Current Architecture Status

### Backend (FastAPI)
- **Authentication**: Firebase Auth for Google OAuth ✓
- **Database**: PostgreSQL with JSONB fields ✓
- **Storage**: Google Cloud Storage for images ✓
- **Photo Model**: Has `extra_data` JSONB column defined
- **API Endpoints**: Expect multipart form data for photo uploads

### Frontend (JavaScript)
- **Authentication**: Firebase client SDK integration ✓
- **Gallery**: Justified Gallery implementation ✓
- **API Calls**: Currently using mock data
- **Upload**: Not yet connected to backend API

## Key Issues Identified

### 1. Database Schema Mismatch
**Problem**: Photo model defines `extra_data` column that doesn't exist in PostgreSQL
**Location**: `backend/app/models/photo.py` line 42
**Solution**: Either:
  - Add column to database: `ALTER TABLE photos ADD COLUMN extra_data JSONB DEFAULT '{}';`
  - Remove from model (if not needed)

### 2. Frontend-Backend Disconnect
**Problem**: Frontend not making real API calls
**Issues**:
  - Mock photo data still in use
  - Upload form not connected to `/api/v1/photos/upload`
  - Photo feed not calling `/api/v1/photos/`
  
### 3. API Contract Mismatch
**Upload Endpoint Expects**:
- Multipart form data with file + metadata fields
- Bearer token authentication

**Frontend Needs**:
- Form data construction for uploads
- Proper headers with auth token
- Error handling for API responses

## Fix Priority

1. **Database Schema**: Add missing `extra_data` column
2. **API Integration**: Replace mock data with real API calls
3. **Upload Flow**: Connect drag-drop to backend upload
4. **Error Handling**: Add proper error states and messages

## Code Locations

- **Photo Model**: `backend/app/models/photo.py`
- **Photo Service**: `backend/app/services/photo_service.py`
- **Photo API**: `backend/app/api/endpoints/photos.py`
- **Frontend Gallery**: `frontend/js/lumen-gallery.js`
- **Frontend App**: `frontend/lumen-app.html`