"""Authentication endpoints for Lumen API"""

import html

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import joinedload

from ...auth_middleware import get_current_user, get_optional_user, AuthUser

router = APIRouter()

class UserProfile(BaseModel):
    """User profile response model"""
    uid: str
    email: Optional[str] = None
    email_verified: bool = False
    name: Optional[str] = None
    picture: Optional[str] = None

class AuthStatus(BaseModel):
    """Authentication status response"""
    authenticated: bool
    user: Optional[UserProfile] = None
    message: str


def _sanitize_str(value: Optional[str]) -> Optional[str]:
    """HTML-escape user controlled strings before returning from the API."""
    if value is None:
        return None
    return html.escape(value, quote=True)


def _serialize_auth_user(user: AuthUser) -> UserProfile:
    """Create a sanitized user profile payload from a Firebase user."""
    return UserProfile(
        uid=_sanitize_str(user.uid) or "",
        email=_sanitize_str(user.email),
        email_verified=user.email_verified,
        name=_sanitize_str(user.name),
        picture=_sanitize_str(user.picture)
    )


def _serialize_db_user(user, include_location: bool = False) -> dict:
    """Serialize a SQLAlchemy user model using safe strings."""
    payload = {
        "id": _sanitize_str(user.id) or "",
        "email": _sanitize_str(getattr(user, "email", None)),
        "handle": _sanitize_str(getattr(user, "handle", None)),
        "display_name": _sanitize_str(getattr(user, "display_name", None)),
        "user_type": getattr(user, "primary_user_type", None)
    }

    if include_location and getattr(user, "city", None):
        payload.update({
            "city": _sanitize_str(getattr(user.city, "name", None)),
            "country": _sanitize_str(getattr(user.city, "country", None))
        })

    return payload

@router.get("/status", response_model=AuthStatus)
async def auth_status(user_token: dict = Depends(get_optional_user)):
    """
    Check authentication status
    Public endpoint - returns user info if authenticated
    """
    if user_token:
        user = AuthUser(user_token)
        return AuthStatus(
            authenticated=True,
            user=_serialize_auth_user(user),
            message="User is authenticated"
        )
    else:
        return AuthStatus(
            authenticated=False,
            message="User is not authenticated"
        )

@router.get("/profile", response_model=UserProfile)
async def get_profile(user_token: dict = Depends(get_current_user)):
    """
    Get current user profile
    Requires authentication
    """
    user = AuthUser(user_token)
    return _serialize_auth_user(user)

@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side handles token removal)
    """
    return {"message": "Logged out successfully"}

@router.get("/test")
async def test_endpoint():
    """
    Test endpoint to verify API is working
    """
    return {
        "message": "Lumen API is running!",
        "status": "healthy",
        "firebase_enabled": True
    }

@router.get("/demo-protected")
async def demo_protected_endpoint(user_token: dict = Depends(get_current_user)):
    """
    Demo endpoint that requires authentication
    Try accessing this without a valid Firebase token - it will return 401 Unauthorized
    """
    user = AuthUser(user_token)
    return {
        "message": "This is a protected endpoint - you are authenticated!",
        "user_id": user.uid,
        "email": user.email,
        "timestamp": datetime.utcnow().isoformat()
    }
from pydantic import BaseModel, validator
from typing import Optional

class RegistrationRequest(BaseModel):
    """User registration request model"""
    display_name: str
    user_type: int  # 1=photographer, 2=model, 3=studio  
    city_id: int
    
    @validator('display_name')
    def validate_display_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Display name must be at least 2 characters')
        return v.strip()
    
    @validator('user_type')
    def validate_user_type(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError('User type must be 1 (photographer), 2 (model), or 3 (studio)')
        return v

@router.post("/register")
async def register_user(
    registration: RegistrationRequest,
    user_token: dict = Depends(get_current_user)
):
    """
    Register new user - REQUIRED for first-time users
    """
    from app.database.connection import SessionLocal
    from app.models.user import User
    from app.models.lookup_tables import City
    import re
    
    firebase_user = AuthUser(user_token)
    db = SessionLocal()
    
    try:
        # Check if already registered
        existing = db.query(User).filter(User.id == firebase_user.uid).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="User already registered"
            )
        
        # Validate city exists
        city = db.query(City).filter(City.id == registration.city_id).first()
        if not city:
            raise HTTPException(
                status_code=400,
                detail="Invalid city selected"
            )
        
        # Generate unique handle from display name
        base_handle = re.sub(r'[^a-zA-Z0-9_]', '', registration.display_name.lower().replace(' ', '_'))
        if len(base_handle) < 3:
            base_handle = f"user_{firebase_user.uid[:8]}"
        
        # Ensure handle is unique
        counter = 1
        handle = base_handle[:47]  # Leave room for suffix
        while db.query(User).filter(User.handle == handle).first():
            handle = f"{base_handle[:44]}_{counter}"  # Max 50 chars
            counter += 1
        
        # Create user with REQUIRED fields
        user = User(
            id=firebase_user.uid,
            email=firebase_user.email,
            handle=handle,
            display_name=registration.display_name,
            city_id=registration.city_id,
            primary_user_type=registration.user_type
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)

        user_payload = _serialize_db_user(user)
        user_payload.update({
            "city": _sanitize_str(city.name),
            "country": _sanitize_str(city.country)
        })

        return {
            "success": True,
            "message": "Registration successful",
            "user": user_payload
        }
        
    finally:
        db.close()

@router.get("/check-registration")
async def check_registration(user_token: dict = Depends(get_current_user)):
    """Check if user has completed registration"""
    from app.database.connection import SessionLocal
    from app.models.user import User

    firebase_user = AuthUser(user_token)
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .options(joinedload(User.city))
            .filter(User.id == firebase_user.uid)
            .first()
        )

        if user:
            return {
                "registered": True,
                "user": _serialize_db_user(user, include_location=True)
            }

        return {
            "registered": False,
            "firebase_user": {
                "uid": _sanitize_str(firebase_user.uid) or "",
                "email": _sanitize_str(firebase_user.email),
                "name": _sanitize_str(firebase_user.name)
            }
        }
    finally:
        db.close()
