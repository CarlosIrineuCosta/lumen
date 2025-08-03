# CLAUDE.md

Instructions for Claude Code when working with this repository.

## Critical Rules
- **NEVER USE EMOJIS** - Never add emojis to any files or responses
- **NEVER GET STUCK IN LOOPS** - Always use `nohup` with `&` for servers, never wait for output
- **NO MOCKS** - Never use mock data or temporary workarounds, always implement real functionality
- **READ ALL MD FILES ON START** - Always check project_status.md, CLAUDE.md, and README.md first

## Project Overview
Lumen - Instagram-like photography platform with real photo uploads, Firebase auth, and Google Cloud Storage.

## Server Management
**Backend**: `cd lumen-gcp/backend && source venv/bin/activate && nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8080 > server.log 2>&1 &`
**Frontend**: `cd lumen-gcp/frontend && python3 -m http.server 8000`
**Access**: http://100.106.201.33:8080 (API), http://100.106.201.33:8000/lumen-app.html (Web)

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