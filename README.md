# Lumen Photography Platform

Professional photo sharing platform for photographers, built on Google Cloud Platform with modern web technologies.

## Current Status: Alpha Development

**Working Features:**
- Firebase Authentication (Email/Password)
- FastAPI Backend with JWT validation
- User management and profiles
- Photo gallery with interactive interface
- Dark mode UI optimized for development
- Upload interface with drag/drop functionality
- Instagram-like responsive design
- Like system and photo interactions

## Architecture

- **Backend**: FastAPI (Python 3.11) with Firebase Admin SDK
- **Frontend**: Vanilla JavaScript with Firebase Client SDK
- **Database**: Cloud SQL PostgreSQL (planned)
- **Storage**: Google Cloud Storage (in progress)
- **Authentication**: Firebase Auth
- **Deployment**: Google Cloud Run (planned)
- **Development**: Accessible via Tailscale network

## Development Setup

### Prerequisites
- Python 3.11+
- Google Cloud Project with Firebase enabled
- Tailscale for network access (development)

### Local Development

1. **Backend Setup**
```bash
cd lumen-gcp/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Environment Configuration**
```bash
# Copy and configure environment variables
cp .env.example .env
# Add your Firebase service account credentials
```

3. **Run Development Server**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=firebase_service_account.json
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

4. **Frontend Development**
```bash
cd lumen-gcp/frontend
python3 -m http.server 8000
```

### Access Points (via Tailscale)
- **API**: http://[TAILSCALE_IP]:8080
- **Web App**: http://[TAILSCALE_IP]:8000/lumen-app.html
- **API Docs**: http://[TAILSCALE_IP]:8080/docs

## Project Structure

```
lumen-gcp/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── main.py         # FastAPI app
│   │   ├── firebase_config.py
│   │   ├── auth_middleware.py
│   │   └── api/endpoints/  # API routes
│   ├── venv/               # Python virtual environment
│   ├── .env                # Environment variables (not in git)
│   └── requirements.txt    # Python dependencies
├── frontend/               # Web interface
│   ├── lumen-app.html     # Main application
│   └── firebase-test-client.html
├── infrastructure/         # Cloud infrastructure (planned)
└── docs/                  # Documentation
```

## Security Notes

- Firebase service account keys are gitignored
- Environment variables contain sensitive data
- CORS configured for development origins
- All authentication via Firebase JWT tokens

## Roadmap

### Next Milestones
- Real file upload to Cloud Storage
- Database integration (Cloud SQL)
- Production deployment pipeline
- Mobile app (React Native/Expo)
- Advanced photo features (likes, comments, followers)

### Future Features
- AI content moderation (Vertex AI)
- Payment integration (Stripe)
- Professional photographer portfolios
- Advanced photo editing tools

## Development Environment

**Target Budget**: $3-7 USD/day
**GCP Project**: lumen-photo-app-20250731
**Firebase**: Email/Password authentication enabled
**Network**: Accessible via Tailscale mesh network

## Contributing

This is currently in alpha development. The codebase is functional but not production-ready.

## License

Private development project - not yet licensed for public use.

---

**Status**: Alpha Development
**Last Updated**: July 31, 2025
**Developer**: Carlos Irineu