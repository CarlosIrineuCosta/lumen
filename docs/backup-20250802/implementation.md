# Lumen Implementation Details

Complete technical implementation documentation.

## System Architecture

### Backend (FastAPI)
- **Location**: `/home/cdc/projects/wasenet/lumen-gcp/backend`
- **Python**: 3.11.13 with venv (no Conda)
- **Framework**: FastAPI 0.104.1
- **Authentication**: Firebase Admin SDK 6.3.0
- **Storage**: Google Cloud Storage 2.10.0
- **Image Processing**: Pillow 10.1.0

### Frontend (Vanilla JS)
- **Location**: `/home/cdc/projects/wasenet/lumen-gcp/frontend`
- **Main App**: `lumen-app.html`
- **Firebase**: Client SDK 10.7.1
- **Style**: Dark mode, Instagram-like interface
- **Features**: Drag/drop upload, real-time gallery

### Google Cloud Platform
- **Project ID**: lumen-photo-app-20250731
- **Region**: us-central1
- **Services**: Cloud Storage, Firebase, Billing enabled
- **Bucket**: lumen-photos-20250731 (public read access)
- **Budget**: $3-7/day monitoring

### Network Configuration
- **Development**: Tailscale mesh network
- **Backend**: http://100.106.201.33:8080
- **Frontend**: http://100.106.201.33:8000
- **CORS**: Configured for Tailscale IP access

## File Structure
```
lumen-gcp/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── firebase_config.py      # Firebase initialization
│   │   ├── auth_middleware.py      # JWT token validation
│   │   └── api/endpoints/
│   │       ├── auth.py            # Auth routes
│   │       ├── users.py           # User management
│   │       └── photos.py          # Photo upload/management
│   ├── venv/                      # Python virtual environment
│   ├── .env                       # Environment variables
│   ├── requirements.txt           # Dependencies
│   └── firebase_service_account.json # Firebase credentials
├── frontend/
│   ├── lumen-app.html            # Main application
│   └── firebase-test-client.html # Auth testing
└── docs/                         # Documentation
```

## API Endpoints
- `GET /` - API status
- `GET /health` - Health check
- `POST /api/v1/auth/status` - Auth status
- `GET /api/v1/auth/profile` - User profile (protected)
- `GET /api/v1/users/me` - Current user info
- `POST /api/v1/photos/upload` - Photo upload
- `GET /api/v1/photos/my-photos` - User's photos
- `POST /api/v1/photos/{id}/like` - Like photo

## Development Commands

### Start Development Environment
```bash
# Backend
cd lumen-gcp/backend
source venv/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS=firebase_service_account.json
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8080 > server.log 2>&1 &

# Frontend
cd lumen-gcp/frontend  
python3 -m http.server 8000
```

### Environment Variables (.env)
```
GCP_PROJECT_ID=lumen-photo-app-20250731
STORAGE_BUCKET_NAME=lumen-photos-20250731
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:19006,http://100.106.201.33:8000
```

### Firebase Configuration
- **Project**: lumen-photo-app-20250731
- **Authentication**: Email/Password enabled
- **Service Account**: Admin permissions for backend
- **Client Config**: Web app configuration in frontend

## Photo Upload Workflow
1. User selects file in web interface
2. Frontend creates FormData with file + metadata
3. Backend validates JWT token
4. File uploaded to Cloud Storage with unique filename
5. Thumbnail generated using Pillow
6. Photo metadata stored in in-memory storage
7. Public URLs returned to frontend
8. Gallery refreshed with new photo

## Security
- Firebase JWT token validation on protected routes
- CORS configured for development origins
- Service account keys in .gitignore
- Environment variables for sensitive data
- Cloud Storage with public read access

## Current Limitations
- Database: In-memory storage (photos lost on server restart)
- Deployment: Local development only
- Mobile: Web app only, no native apps
- Moderation: No AI content filtering
- Payments: Not implemented

## Platform Philosophy & Vision

### Core Principles
- **NO ADS EVER** - Clean, distraction-free experience focused on photography
- **NO ALGORITHMIC PLACEMENT** - Chronological, user-controlled content discovery
- **PHOTOGRAPHER-FIRST** - Built for serious photographers, not influencers
- **MEANINGFUL CONNECTIONS** - GPS integration for real-world photographer/model networking
- **INTELLIGENT BUT NOT OVERWHELMING** - AI assists but never dominates the experience

### AI Integration Strategy
- **Smart Tagging**: AI suggests meaningful tags based on image content, not engagement metrics
- **Categorization**: Automatic photo organization by style, lighting, composition
- **Location Intelligence**: GPS-based networking without privacy invasion
- **Content Curation**: Quality-focused, not engagement-focused algorithms
- **Portfolio Generation**: Automatic creation of professional portfolios from user photos

### Instagram Integration Vision
- **Photo Import**: Clean import of existing IG photos without ads/spam
- **Content Liberation**: Rescue quality photography from IG's commercial noise
- **Portfolio Creation**: Instant professional portfolios from imported content
- **Network Migration**: Help photographers transition their following to Lumen

### User Experience Goals
- **Simplicity Over Features**: Every feature must enhance photography, not complicate it
- **Professional Tools**: Advanced image handling, format support, color accuracy
- **Real Connections**: Location-based networking for shoots, collaborations
- **Portfolio Focus**: Every photo should contribute to a professional body of work

## Next Implementation Steps
1. **Database**: Replace in-memory with Cloud SQL PostgreSQL
2. **Deployment**: Containerize and deploy to Cloud Run
3. **Mobile**: Build React Native/Expo apps
4. **AI**: Add Vertex AI for smart tagging and categorization (not moderation)
5. **Instagram Import**: Build photo import and portfolio generation pipeline
6. **GPS Integration**: Location-based photographer networking
7. **Portfolio System**: Enhanced automatic portfolio generation