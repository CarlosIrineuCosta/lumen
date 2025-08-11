# Lumen PWA - Professional Photography Platform

## Overview
Clean, Glass-inspired Progressive Web App for professional photographers. No ads, no algorithms, just pure photography.

## Project Structure
```
opusdev/
├── index.html          # Main PWA entry point
├── manifest.json       # PWA manifest configuration
├── service-worker.js   # Offline functionality
├── css/
│   └── app.css        # Glass-inspired minimal design
├── js/
│   └── app.js         # Main application logic
└── assets/
    └── icons/         # PWA icons (need to be generated)
```

## Features
- **PWA Support**: Installable, works offline
- **CSS Grid Masonry**: Native masonry layout (Firefox) with fallback
- **Minimal Design**: Glass-inspired, photography-focused
- **OAuth Integration**: Google sign-in via backend
- **Photo Upload**: Direct to Google Cloud Storage
- **Infinite Scroll**: Smooth photo loading
- **Responsive**: Works on all devices

## Setup Instructions

### 1. Generate Icons
Use a tool like https://realfavicongenerator.net/ to generate PWA icons from a base logo.
Place them in `assets/icons/` with these sizes:
- icon-32.png
- icon-72.png
- icon-96.png
- icon-128.png
- icon-144.png
- icon-152.png
- icon-192.png
- icon-384.png
- icon-512.png

### 2. Update Backend CORS
Edit `backend/app/main.py` to allow the PWA domain:
```python
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://100.106.201.33:8000",
]
```

### 3. Run Development Server
```bash
cd /home/cdc/Storage/NVMe/projects/wasenet/opusdev
python -m http.server 8000
```

Then open: http://localhost:8000

### 4. Backend API
Ensure backend is running:
```bash
cd /home/cdc/Storage/NVMe/projects/wasenet/lumen-gcp/backend
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## API Endpoints Required
- `GET /api/v1/auth/profile` - User profile
- `GET /api/v1/auth/google` - OAuth redirect
- `GET /api/v1/photos/recent` - Recent photos
- `GET /api/v1/photos/nearby` - Geographic search
- `GET /api/v1/users/photographers` - List photographers
- `POST /api/v1/photos/upload` - Upload photos

## Testing Checklist
- [ ] OAuth login works
- [ ] Photos display in grid
- [ ] Masonry layout working
- [ ] Upload functionality
- [ ] PWA installs correctly
- [ ] Service worker caches assets
- [ ] Responsive on mobile
- [ ] Infinite scroll works

## Files Backed Up
Old files moved to: `docs/backup-2025-08-09/`
- Test HTML files
- React/Vite components
- Old documentation
- Portfolio generator

## Next Steps
1. Generate PWA icons
2. Test OAuth flow
3. Verify photo grid displays
4. Test on mobile devices
5. Add upload functionality
6. Polish UI details

## Browser Support
- Chrome/Edge: Full support
- Firefox: Native masonry support
- Safari: PWA support on iOS 11.3+
- Android: Full PWA support

## Notes
- Using vanilla JS for simplicity and performance
- No jQuery or React dependencies
- Glass-inspired minimal design
- Focus on photography, not engagement metrics