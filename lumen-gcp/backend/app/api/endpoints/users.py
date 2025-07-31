"""User management endpoints for Lumen API"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ...auth_middleware import get_current_user, AuthUser

router = APIRouter()

class UserResponse(BaseModel):
    """User response model"""
    uid: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    email_verified: bool = False
    created_at: datetime
    last_login: datetime

class UpdateUserRequest(BaseModel):
    """Update user request model"""
    display_name: Optional[str] = None
    bio: Optional[str] = None

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(user_token: dict = Depends(get_current_user)):
    """Get current user's profile"""
    user = AuthUser(user_token)
    
    return UserResponse(
        uid=user.uid,
        email=user.email,
        display_name=user.name,
        photo_url=user.picture,
        email_verified=user.email_verified,
        created_at=datetime.utcnow(),  # In real app, get from database
        last_login=datetime.utcnow()
    )

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    update_data: UpdateUserRequest,
    user_token: dict = Depends(get_current_user)
):
    """Update current user's profile"""
    user = AuthUser(user_token)
    
    # In a real app, you'd update the database here
    # For now, return the current user with updated data
    
    return UserResponse(
        uid=user.uid,
        email=user.email,
        display_name=update_data.display_name or user.name,
        photo_url=user.picture,
        email_verified=user.email_verified,
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )

@router.get("/stats")
async def get_user_stats(user_token: dict = Depends(get_current_user)):
    """Get user statistics"""
    user = AuthUser(user_token)
    
    return {
        "user_id": user.uid,
        "total_photos": 0,  # From database in real app
        "total_likes": 0,
        "total_followers": 0,
        "total_following": 0,
        "account_created": datetime.utcnow().isoformat(),
        "last_active": datetime.utcnow().isoformat()
    }