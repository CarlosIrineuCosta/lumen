# Lumen Photography Platform

Professional photo sharing platform for artistic photography. Instagram-like interface with real-time uploads, user authentication, and cloud storage.

## Current Status: Working Alpha

**Live Features:**
- Firebase Authentication (Email/Password)
- Real photo uploads to Google Cloud Storage
- Instagram-like dark mode interface
- User profiles and photo galleries
- Like system and interactions

## Quick Access

- **Web App**: http://100.106.201.33:8000/lumen-app.html
- **API**: http://100.106.201.33:8080
- **API Docs**: http://100.106.201.33:8080/docs

## Architecture

- **Backend**: FastAPI (Python 3.11) + Firebase Admin SDK
- **Frontend**: Vanilla JavaScript + Firebase Client SDK
- **Storage**: Google Cloud Storage
- **Authentication**: Firebase Auth
- **Database**: In-memory (Cloud SQL planned)
- **Network**: Accessible via Tailscale

## Development

```bash
# Start backend
cd lumen-gcp/backend
source venv/bin/activate
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8080 > server.log 2>&1 &

# Start frontend
cd lumen-gcp/frontend
python3 -m http.server 8000
```

**Status**: Alpha Development | **Last Updated**: July 31, 2025 | **Developer**: Carlos Irineu