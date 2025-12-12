# 🚀 LUMEN PRODUCTION WORKFLOW

## Quick Start (Windows)

### Terminal 1 - Backend
```cmd
cd L:\Storage\NVMe\projects\wasenet\opusdev
start-backend.bat
```

### Terminal 2 - Frontend
```cmd
cd L:\Storage\NVMe\projects\wasenet\opusdev
start-frontend.bat
```

Then open: http://localhost:8000

---

## Complete Production Setup

### 1️⃣ Backend Preparation

#### Check Database Connection
```bash
cd L:\Storage\NVMe\projects\wasenet\lumen-gcp\backend
python -c "from app.database.connection import get_db; print('DB Connected!')"
```

#### Verify Firebase Auth
```bash
python -c "from app.firebase_config import firebase_config; print('Firebase OK!')"
```

#### Start Backend Server
```bash
# Windows
venv\Scripts\activate
set GOOGLE_APPLICATION_CREDENTIALS=firebase_service_account.json
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### 2️⃣ Frontend Setup

#### Generate PWA Icons
1. Create a simple "LUMEN" logo (512x512px)
2. Go to https://realfavicongenerator.net/
3. Upload logo and generate icons
4. Download and extract to `opusdev/assets/icons/`

#### Start Frontend Server
```bash
cd L:\Storage\NVMe\projects\wasenet\opusdev
python -m http.server 8000
```

### 3️⃣ Test Workflow

#### A. Test Backend API
```bash
# Check if backend is running
curl http://100.106.201.33:8080/

# Check auth endpoint
curl http://100.106.201.33:8080/api/v1/auth/status
```

#### B. Test Frontend
1. Open http://localhost:8000
2. Should see LUMEN header and auth modal
3. Click "Continue with Google"
4. Should redirect to Google OAuth

### 4️⃣ OAuth Setup Verification

#### Check Firebase Console
1. Go to https://console.firebase.google.com/
2. Select "lumen-photo-app-20250731"
3. Authentication → Sign-in method
4. Ensure Google is enabled
5. Add authorized domain: `localhost:8000`

#### OAuth Redirect URIs
Add these to Google Cloud Console:
- http://localhost:8000
- http://100.106.201.33:8000
- http://localhost:8080/api/v1/auth/callback

---

## 📋 Pre-Flight Checklist

### Backend Ready?
- [ ] Database connected (PostgreSQL running)
- [ ] Firebase credentials in place
- [ ] CORS updated for localhost:8000
- [ ] Backend server running on :8080

### Frontend Ready?
- [ ] PWA files in opusdev/
- [ ] Icons generated (or use placeholders)
- [ ] Service worker registered
- [ ] Frontend server on :8000

### API Endpoints Working?
- [ ] GET /api/v1/auth/status
- [ ] GET /api/v1/auth/google
- [ ] GET /api/v1/photos/recent
- [ ] POST /api/v1/photos/upload

---

## 🔥 Quick Test Commands

### Test Everything at Once
```powershell
# PowerShell script to test all endpoints
$base = "http://100.106.201.33:8080"
Invoke-WebRequest "$base/" | Select StatusCode
Invoke-WebRequest "$base/api/v1/auth/status" | Select StatusCode
```

### Test with Python
```python
import requests
base = "http://100.106.201.33:8080"
print(requests.get(f"{base}/").json())
print(requests.get(f"{base}/api/v1/auth/status").status_code)
```

---

## 🚨 Troubleshooting

### CORS Error?
```python
# In backend/.env add:
ALLOWED_ORIGINS=http://localhost:8000,http://100.106.201.33:8000
```

### Database Connection Failed?
```bash
# Check PostgreSQL is running
psql -U postgres -d lumen_db -h localhost
```

### Firebase Auth Error?
```bash
# Verify credentials file exists
ls L:\Storage\NVMe\projects\wasenet\lumen-gcp\backend\firebase_service_account.json
```

### Frontend Not Loading?
```bash
# Check if ports are in use
netstat -an | findstr :8000
netstat -an | findstr :8080
```

---

## 📱 PWA Installation Test

1. Open Chrome on mobile or desktop
2. Navigate to http://localhost:8000
3. Look for install prompt (address bar on desktop, banner on mobile)
4. Install and test offline mode

---

## 🎯 Success Criteria

✅ Backend API responds at :8080
✅ Frontend loads at :8000
✅ Auth modal appears if not logged in
✅ Google OAuth redirects properly
✅ Photos load in grid after login
✅ PWA installs successfully
✅ Service worker caches assets

---

## 📝 Notes

- Keep both terminal windows open (backend + frontend)
- Backend changes auto-reload with --reload flag
- Frontend changes visible on browser refresh
- Check browser console for errors
- Check backend terminal for API logs