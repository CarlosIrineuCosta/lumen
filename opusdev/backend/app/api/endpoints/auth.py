"""Authentication endpoints for Lumen API"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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
            user=UserProfile(
                uid=user.uid,
                email=user.email,
                email_verified=user.email_verified,
                name=user.name,
                picture=user.picture
            ),
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
    return UserProfile(
        uid=user.uid,
        email=user.email,
        email_verified=user.email_verified,
        name=user.name,
        picture=user.picture
    )

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