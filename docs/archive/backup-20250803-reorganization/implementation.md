# Lumen Implementation Details

Complete technical implementation for professional photography platform.

## Business-Driven Architecture

### Platform Vision
Professional photography alternative to Instagram with:
- **Uncensored artistic expression** - No arbitrary content restrictions
- **People-first networking** - GPS-based photographer/model connections
- **Quality-focused discovery** - No engagement manipulation algorithms
- **Subscription revenue** - User empowerment over data exploitation

### Current Technical Stack
- **Backend**: FastAPI 0.104.1 (Python 3.11.13) with Firebase Admin SDK
- **Database**: PostgreSQL (Cloud SQL) - migrating from in-memory
- **Storage**: Google Cloud Storage with multi-format compression
- **Authentication**: Firebase JWT with proper state management (needs fixing)
- **Frontend**: Migrating to claudesk-code/lumen-prototype (Justified Gallery)

## Infrastructure (Google Cloud Platform)
- **Project**: lumen-photo-app-20250731
- **Region**: us-central1  
- **Services**: Cloud Storage, Firebase, Cloud SQL, Vertex AI
- **Bucket**: lumen-photos-20250731 (public read access)
- **Network**: Tailscale mesh (100.106.201.33)
- **Budget**: $3-7/day monitoring with cost optimization

## Frontend Architecture (New Direction)

### Justified Gallery Implementation
**Location**: `/home/cdc/projects/wasenet/claudesk-code/lumen-prototype`
- **Mosaic Layout**: Variable-sized grid respecting image proportions
- **Library**: Justified Gallery (same as 500px)
- **Performance**: Lazy loading, infinite scroll, optimized for high-res photography
- **Discovery Modes**: Latest Work, Photographers, Models, Nearby (30km), Open for Work

### People-First Design Philosophy  
- **Photographer Focus**: Every image shows WHO took it, not just the image
- **Model Recognition**: Equal discovery for photographers AND models
- **Professional Networking**: Geographic collaboration tools
- **Portfolio System**: Toggle between feed and curated professional work

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

## API Endpoints (Current + Planned)

### Authentication (Needs Fixes)
- `POST /api/v1/auth/status` - Auth status (fix state management)
- `GET /api/v1/auth/profile` - User profile (protected)
- `POST /api/v1/auth/register` - User registration (fix completion flow)

### Photo Management
- `POST /api/v1/photos/upload` - Upload with compression pipeline
- `GET /api/v1/photos/recent` - Recent photos feed (for Latest Work mode)
- `GET /api/v1/photos/my-photos` - User's photos
- `GET /api/v1/photos/{id}` - Single photo details for lightbox

### Discovery (New - Based on Business Strategy)
- `GET /api/v1/discovery/photographers` - Photographers mode
- `GET /api/v1/discovery/models` - Models mode  
- `GET /api/v1/discovery/nearby` - Geographic discovery (30km radius)
- `GET /api/v1/discovery/collaborations` - Open for work
- `POST /api/v1/networking/connect` - Professional connection requests

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

## Implementation Priorities

### Phase 1: Foundation (This Weekend)
1. **Fix Authentication**: State management and registration completion
2. **Frontend Migration**: Move to claudesk-code/lumen-prototype 
3. **Database Migration**: Complete Cloud SQL PostgreSQL setup
4. **Image Compression**: MozJPEG pipeline for web delivery

### Phase 2: Business Features (Next Sprint)
1. **Discovery Modes**: Implement people-first navigation
2. **Geographic Networking**: GPS-based photographer/model connections  
3. **Professional Profiles**: Portfolio vs feed content separation
4. **Smart Tagging**: Vertex AI for categorization (not moderation)

### Phase 3: Advanced Features
1. **TV Integration**: 4K display mode for professional presentation
2. **Contract System**: Digital model releases and agreements  
3. **Portfolio Tools**: Automated professional portfolio generation
4. **Magazine Integration**: Content curation and quality awards

## Current Limitations to Address
- **Authentication**: Token persistence and state management issues
- **Database**: Still using in-memory storage (photos lost on restart)
- **Content Discovery**: No geographic or professional networking features
- **Image Processing**: Basic compression, needs multi-format pipeline
- **Mobile**: Web-only, needs responsive optimization for prototype