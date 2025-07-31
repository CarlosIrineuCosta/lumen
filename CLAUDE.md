# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Lumen project - an artistic photography platform built on Google Cloud Platform. The project consists of:
- **Backend**: FastAPI Python service deployed on Cloud Run
- **Frontend**: React Native (Expo) with web support
- **Infrastructure**: Terraform-managed GCP resources

## Development Commands

### Backend Development
```bash
cd lumen-gcp/backend
pip install -r requirements.txt
uvicorn app.main:app --reload  # Runs on http://localhost:8080
```

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