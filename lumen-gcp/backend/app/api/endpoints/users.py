"""User management endpoints for Lumen API"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from datetime import datetime

from ...auth_middleware import get_current_user, AuthUser
from ...models.user import (
    UserProfileFull, UserProfilePublic, CreateUserRequest, 
    UpdateUserRequest, UserSearchQuery, UserType, PhotographyStyle
)
from ...services.user_service import UserService

router = APIRouter()
user_service = UserService()

@router.post("/register", response_model=UserProfilePublic)
async def register_user(
    request: CreateUserRequest,
    user_token: dict = Depends(get_current_user)
):
    """Register a new user profile (complete profile after Firebase auth)"""
    firebase_user = AuthUser(user_token)
    
    # Check if user already has a profile
    if await user_service.user_exists(firebase_user.uid):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User profile already exists"
        )
    
    # Create the user profile
    try:
        full_profile = await user_service.create_user_profile(firebase_user, request)
        return full_profile.public_profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user profile: {str(e)}"
        )

@router.get("/me", response_model=UserProfileFull)
async def get_current_user_profile(user_token: dict = Depends(get_current_user)):
    """Get current user's full profile"""
    firebase_user = AuthUser(user_token)
    
    profile = await user_service.get_user_profile(firebase_user.uid, include_private=True)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. Please complete registration."
        )
    
    # Update last login
    await user_service.update_last_login(firebase_user.uid)
    
    return profile

@router.get("/me/public", response_model=UserProfilePublic)
async def get_current_user_public_profile(user_token: dict = Depends(get_current_user)):
    """Get current user's public profile"""
    firebase_user = AuthUser(user_token)
    
    profile = await user_service.get_public_profile(firebase_user.uid)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return profile

@router.put("/me", response_model=UserProfileFull)
async def update_user_profile(
    request: UpdateUserRequest,
    user_token: dict = Depends(get_current_user)
):
    """Update current user's profile"""
    firebase_user = AuthUser(user_token)
    
    profile = await user_service.update_user_profile(firebase_user.uid, request)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return profile

@router.get("/stats")
async def get_user_stats(user_token: dict = Depends(get_current_user)):
    """Get user statistics"""
    firebase_user = AuthUser(user_token)
    
    stats = await user_service.get_user_stats(firebase_user.uid)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return stats

@router.get("/{user_id}/public", response_model=UserProfilePublic)
async def get_user_public_profile(user_id: str):
    """Get any user's public profile"""
    profile = await user_service.get_public_profile(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return profile

@router.post("/search", response_model=List[UserProfilePublic])
async def search_users(query: UserSearchQuery):
    """Search for users based on criteria"""
    try:
        results = await user_service.search_users(query)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/types", response_model=List[str])
async def get_user_types():
    """Get available user types"""
    return [user_type.value for user_type in UserType]

@router.get("/styles", response_model=List[str])
async def get_photography_styles():
    """Get available photography styles"""
    return [style.value for style in PhotographyStyle]