# Major Decisions - 2025-08-04 Session

## Architecture Decisions Made

### Image Upload Architecture (CRITICAL)
**Decision**: Option A - Backend Handles Storage Upload
**Flow**: Frontend → Backend API (with file) → Backend uploads to Firebase Storage → Database
**Reasoning**: 
- Better security (backend controls Firebase Storage access)
- Consistent with existing backend API design
- Centralized error handling
- Backend expects multipart file uploads, not JSON metadata

**Implementation Details**:
- Frontend sends multipart FormData with file + metadata to `/api/v1/photos/upload`
- Backend handles Firebase Storage upload internally
- Data still ends up in Firebase Storage bucket: `gs://lumen-photos-20250731/`
- CORS configuration applied for web uploads

### Server Management Solution
**Problem**: Daily port conflicts and stale processes
**Solution**: Automated server management script at `./scripts/server-manager.sh`
**Usage**: 
- `./scripts/server-manager.sh clean` - Kill all processes
- `./scripts/server-manager.sh start` - Clean startup
- `./scripts/server-manager.sh status` - Check status

### Google Cloud Storage Configuration
**Bucket**: `gs://lumen-photos-20250731/` (US-CENTRAL1 region)
**CRITICAL**: Always use US regions for free tier compatibility, never South America
**CORS**: Applied for web upload compatibility
**Access**: Public read (`allUsers` have `objectViewer` role)

### Development Environment
**Backend**: Port 8080 (FastAPI with PostgreSQL)
**Frontend**: Port 8001 (Python HTTP server)
**Access**: All via Tailscale network (100.106.201.33)
**Database**: PostgreSQL with schema and seed data (completed by Gemini)

## Implementation Completed

### Frontend Features
1. **Complete Upload Workflow**: Drag & drop with real backend integration
2. **User Photo Management**: Personal uploads view with delete functionality
3. **Notification System**: Toast notifications for user feedback
4. **Professional UI**: 500px-style gallery with responsive design
5. **Authentication Integration**: Firebase Auth tokens for all APIs

### Backend Integration
1. **Real API Calls**: No more mock data fallbacks needed
2. **Multipart Upload**: Backend receives files directly
3. **Firebase Storage**: Backend handles upload to Google Cloud Storage
4. **Database**: Metadata saved to PostgreSQL

## Coordination with Gemini
**Gemini Responsibilities**: GCP/Firebase backend configuration, database setup
**Claude Code Responsibilities**: Frontend interface development, user experience
**Shared Status**: Updated in `SHARED-STATUS.md` for coordination

## Development Policies Established
1. **Bash Commands**: Run directly, only ask user for help with environmental issues
2. **Architecture Communication**: Always explain options and trade-offs upfront
3. **Daily Documentation**: Record session start times and key decisions
4. **Serena Usage**: Leverage semantic analysis and memory system extensively

## Technical Notes for Tomorrow
- Upload functionality implemented and should be working
- All servers clean and properly configured
- CORS applied to storage bucket
- Frontend uses correct bucket name and API endpoints
- Server management script prevents daily port conflicts