# 🔧 Missing Backend Endpoints

## Required for MVP

### 1. Google OAuth Redirect (CRITICAL)
Add to `backend/app/api/endpoints/auth.py`:

```python
from fastapi import Request
from fastapi.responses import RedirectResponse
import firebase_admin.auth as firebase_auth

@router.get("/google")
async def google_auth():
    """Redirect to Google OAuth"""
    # For Firebase Auth, this is handled client-side
    # Return instructions for now
    return {
        "message": "Google Auth should be initiated from frontend",
        "frontend_url": "http://localhost:8000",
        "instructions": "Use Firebase Auth client SDK"
    }

@router.get("/callback")
async def auth_callback(code: str):
    """Handle OAuth callback - not needed for Firebase"""
    return RedirectResponse("http://localhost:8000?auth=success")
```

### 2. Nearby Photos Endpoint
Add to `backend/app/api/endpoints/photos.py`:

```python
@router.get("/nearby", response_model=PhotoListResponse)
async def get_nearby_photos(
    radius: int = Query(30, ge=1, le=100),  # km
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get photos near a location"""
    # For MVP, just return recent photos
    # TODO: Implement geographic search
    photo_service = PhotoService(db)
    return await photo_service.get_public_photos(page=page, limit=limit)
```

### 3. User Photos by ID
Add to `backend/app/api/endpoints/photos.py`:

```python
@router.get("/user/{user_id}", response_model=PhotoListResponse)
async def get_user_photos_by_id(
    user_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get photos for a specific user"""
    photo_service = PhotoService(db)
    return await photo_service.get_user_photos(
        user_id=user_id,
        viewer_user_id=None,  # Public view
        page=page,
        limit=limit
    )
```

### 4. List Photographers
Add to `backend/app/api/endpoints/users.py`:

```python
@router.get("/photographers", response_model=List[UserResponse])
async def list_photographers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all photographers"""
    # For MVP, return recent users who have uploaded photos
    # TODO: Implement proper photographer listing
    return {
        "photographers": [],
        "page": page,
        "limit": limit,
        "total": 0,
        "has_more": False
    }
```

## Frontend Auth Fix

Since we're using Firebase Auth, the frontend needs Firebase SDK:

### Add to index.html (before closing </head>):
```html
<!-- Firebase SDK -->
<script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-auth-compat.js"></script>
```

### Update app.js auth method:
```javascript
// Initialize Firebase
const firebaseConfig = {
    apiKey: "AIzaSyBJvE7-sY_IxF5i0EaKvwJIGkF8L8XqW0E",
    authDomain: "lumen-photo-app-20250731.firebaseapp.com",
    projectId: "lumen-photo-app-20250731"
};

firebase.initializeApp(firebaseConfig);

async signInWithGoogle() {
    const provider = new firebase.auth.GoogleAuthProvider();
    try {
        const result = await firebase.auth().signInWithPopup(provider);
        const token = await result.user.getIdToken();
        localStorage.setItem('authToken', token);
        this.authToken = token;
        this.user = result.user;
        this.hideAuthModal();
        this.updateUserUI();
        this.loadPhotos();
    } catch (error) {
        console.error('Auth error:', error);
    }
}
```

## Quick Backend Patches

### Temporary fixes to get MVP running:

1. **Allow any origin temporarily** (for testing only!):
```python
# In backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TEMPORARY - FIX BEFORE PRODUCTION
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **Mock data for testing**:
If database is empty, return mock photos in `/api/v1/photos/recent`:
```python
if not photos:
    # Return mock data for testing
    return {
        "photos": [
            {
                "id": "mock-1",
                "url": "https://picsum.photos/400/600",
                "thumbnail_url": "https://picsum.photos/200/300",
                "title": "Test Photo 1",
                "photographer_name": "Test User",
                "location": "San Francisco",
                "width": 400,
                "height": 600
            }
        ],
        "page": 1,
        "limit": 20,
        "total": 1,
        "has_more": False
    }
```