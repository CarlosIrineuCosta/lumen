# CLAUDE.md

Instructions for Claude Code when working with this repository.

## Critical Rules
- **NEVER USE EMOJIS** - Never add emojis to any files, responses, or UI elements
- **NEVER GET STUCK IN LOOPS** - Always use `nohup` with `&` for servers, never wait for output
- **DAILY SERVER CLEANUP** - Always run `./scripts/server-manager.sh clean` before starting work to prevent port conflicts
- **USE SERENA EXTENSIVELY** - Leverage semantic analysis, memory system, and symbol-level code understanding instead of basic file operations
- **NO MOCKS** - Never use mock data or temporary workarounds, always implement real functionality
- **READ ALL MD FILES ON START** - Always check project_status.md, CLAUDE.md, and README.md first

## Project Overview
Lumen - Professional photography platform with real photo uploads, Firebase auth, and Google Cloud Storage. Instagram-like interface focused on professional photography networking and people-first discovery.

## Core Business Principles
- **NO ADS EVER** - Clean, distraction-free photography experience
- **NO ALGORITHMIC PLACEMENT** - Chronological, user-controlled content discovery
- **PEOPLE-FIRST DISCOVERY** - Find photographers/models, not just browse images
- **PROFESSIONAL NETWORKING** - Real-world connections via GPS proximity
- **SUBSCRIPTION MODEL** - $5-150/year, no data exploitation or engagement manipulation

## Current Status: MVP Development (2025-08-04)
**COMPLETED**: 
- Firebase authentication, user avatars, backend models, 500px-style gallery framework
- PostgreSQL architecture migration (PhotoService, API endpoints)
- Backend/frontend servers running successfully
- API contract fixes for upload functionality

**BLOCKED**: Database schema mismatch - Photo model expects `extra_data` column that doesn't exist in PostgreSQL

**NEXT**: Fix database schema, test upload workflow, complete frontend integration

## Server Management (AUTOMATED SOLUTION)
**ALWAYS USE THE AUTOMATED SCRIPT** - Never manually start servers to avoid port conflicts:

```bash
# Clean startup (kills any existing processes)
./scripts/server-manager.sh start

# Check status
./scripts/server-manager.sh status

# Stop all servers
./scripts/server-manager.sh stop

# Restart servers
./scripts/server-manager.sh restart
```

**Manual Commands (ONLY if script fails)**:
- Backend: `cd lumen-gcp/backend && source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 &`
- Frontend: `cd lumen-gcp/frontend && python3 -m http.server 8001`

**Access URLs**:
- Backend API: http://100.106.201.33:8080
- API Docs: http://100.106.201.33:8080/docs  
- Frontend App: http://100.106.201.33:8001/lumen-app.html

## File Paths Reference
**Main App**: `lumen-gcp/frontend/lumen-app.html`
**Backend API**: `lumen-gcp/backend/app/main.py`
**CSS**: `lumen-gcp/frontend/css/lumen.css`
**JavaScript**: `lumen-gcp/frontend/js/lumen-gallery.js`

## Network Access
All development accessible via Tailscale network (100.106.201.33). Never use localhost URLs.

### Frontend Development
```bash
cd lumen-gcp/frontend
npm install
npm start                    # Start Expo development server
npm run web                  # Run web version
npm run build:web           # Build for web deployment
npm run deploy:web          # Deploy to Firebase hosting
```

### Deployment
```bash
./lumen-gcp/deploy/deploy.sh [PROJECT_ID]  # Deploy backend to Cloud Run
```

### Infrastructure
```bash
cd lumen-gcp/infrastructure/terraform
terraform init
terraform plan
terraform apply
```

### Cost Monitoring
```bash
python lumen-gcp/infrastructure/scripts/monitor_costs.py
```

## Architecture

The application follows a microservices architecture deployed on Google Cloud:

1. **API Layer** (backend/app/main.py): FastAPI application serving REST endpoints
   - Authentication via Firebase Admin SDK
   - Database connections via Cloud SQL Connector
   - Image storage in Cloud Storage buckets
   - Content moderation using Vertex AI

2. **Frontend**: Expo-based React Native app supporting iOS, Android, and web
   - Firebase authentication integration
   - API communication to backend services

3. **Infrastructure**: Managed through Terraform
   - Cloud Run for containerized backend
   - Cloud SQL PostgreSQL for data storage
   - Cloud Storage for media files
   - Vertex AI for ML capabilities

## Key Dependencies

### Backend
- FastAPI 0.104.1 - Web framework
- SQLAlchemy 2.0.23 - ORM
- google-cloud-* libraries - GCP integrations
- firebase-admin 6.3.0 - Authentication
- stripe 7.8.0 - Payment processing

### Frontend
- Expo ~49.0.0 - React Native framework
- React Navigation 6.x - Navigation
- Firebase 10.5.0 - Authentication client

## Network Access and Development Environment

This project runs on a Linux terminal environment accessible via Tailscale network. All development servers, tests, and deployments can be accessed from any device (Windows, macOS, mobile) connected to the Tailscale network using the appropriate Tailscale IP addresses.

### Development Server Access
- Backend API: http://[TAILSCALE_IP]:8080
- API Documentation: http://[TAILSCALE_IP]:8080/docs  
- Frontend (when running): http://[TAILSCALE_IP]:3000 or http://[TAILSCALE_IP]:19006

### Testing and Deployment Access
- All testing endpoints and deployment previews are accessible via Tailscale IP
- No port forwarding required - direct access through Tailscale mesh network
- Can be accessed from any device connected to the Tailscale network

## Important Notes

- The project uses Google Cloud services extensively - ensure gcloud CLI is authenticated
- Daily budget monitoring is implemented to control costs (target: $3-7/day)
- No test files currently exist in the backend - consider implementing tests
- CORS is currently set to allow all origins in development - needs configuration for production
- Development environment runs on Linux but accessible from any OS via Tailscale

## Development Philosophy
- **NO MOCKS**: Never use mock data or temporary workarounds - they take too long and cause distractions
- Always implement real functionality with actual services
- Fix issues directly rather than working around them
- **QUALITY OVER SCALE**: Professional photography focus, not viral growth
- **USER EMPOWERMENT**: Users own their data, complete export capabilities

## MVP Requirements for Demo/User Testing
**Critical features needed for showing around and talking to people:**

### User Experience Essentials
- Logout button in user profile menu
- User profile edit form (display name, bio, city, photography styles)
- Model-specific fields (gender, age, height, weight) for models

### Core Functionality
- Image upload system (drag & drop, Firebase Storage)
- User uploads view (own photos, edit/delete)
- Photo stream display (all photos, 500px-style layout)
- Infinite scroll and basic filtering

### Technical Implementation
- Backend server running successfully
- PostgreSQL database initialized with schema + seed data
- Photo upload endpoints
- User profile management endpoints
- Replace frontend mock data with real backend APIs

## Multi-AI Coordination System

### Roles & Responsibilities
- **Claude Code**: Head developer (technical implementation lead) - THIS ROLE
- **Claude Desktop**: Systems architect and business planner
- **Gemini CLI**: GCP and Firebase specialist / developer

### Shared Workspace
- **Environment**: Same VS Code terminal with multiple AI assistants
- **Coordination File**: `SHARED-STATUS.md` - ALWAYS CHECK AND UPDATE
- **Reference Files**: `CLAUDE.md` (this), `GEMINI.md`, `SHARED-STATUS.md`

### Documentation Structure

This project uses a prefix-based documentation system:

- **CODE-** prefix: Technical implementation documents (Claude Code territory)
- **STRATEGY-** prefix: Business strategy and planning documents (Claude Desktop territory)

### Claude Code Responsibilities (Head Developer)

- **Technical Leadership**: Guide implementation decisions and coordinate with specialists
- **Code Implementation**: Write, debug, and test all application code
- **Architecture Implementation**: Implement technical architecture decisions
- **Quality Assurance**: Ensure code quality, testing, and documentation
- **Team Coordination**: Update `SHARED-STATUS.md` and direct specialist tasks

### Coordination Protocol

- **Always check** `SHARED-STATUS.md` before starting work
- **Update status** when completing tasks or encountering blockers
- **Direct specialists** (Gemini CLI) on GCP/Firebase tasks
- **Communicate handoffs** clearly between development phases

## Development Environment

- Python 3.11.x reference environment
- Firebase authentication working (Google OAuth with redirect fallback)
- 500px open source repo research needed for gallery patterns