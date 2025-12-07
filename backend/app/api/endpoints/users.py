"""User management endpoints for Lumen API"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from typing import Optional, List
from datetime import datetime

from ...auth_middleware import get_current_user, AuthUser
from ...models.user import (
    UserProfileFull, UserProfilePublic, CreateUserRequest, 
    UpdateUserRequest, UserSearchQuery, UserType, PhotographyStyle
)
from ...services.user_service import UserService
from ...services.mappers import map_update_request_to_dto

logger = logging.getLogger(__name__)

router = APIRouter()
user_service = UserService()

@router.post("/register", response_model=UserProfileFull)
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
        return full_profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user profile: {str(e)}"
        )

@router.get("/me", response_model=UserProfileFull)
async def get_current_user_profile(user_token: dict = Depends(get_current_user)):
    """Get current user's full profile"""
    firebase_user = AuthUser(user_token)
    
    # Use auto-registration method to get or create user profile
    profile = await user_service.get_or_create_user_profile(firebase_user, include_private=True)
    
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
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User profile not found"
        )
    
    return profile

@router.put("/me", response_model=UserProfileFull)
async def update_user_profile(
    update_request: UpdateUserRequest,
    user_token: dict = Depends(get_current_user)
):
    """Update current user's profile"""
    firebase_user = AuthUser(user_token)
    
    # Map the API request model to the service layer DTO
    update_dto = map_update_request_to_dto(update_request)
    
    logger.info(f"🌐 API Endpoint - Updating profile for UID: {firebase_user.uid}")
    
    profile = await user_service.update_user_profile(firebase_user.uid, update_dto)
    if not profile:
        logger.error(f"❌ API - User profile not found for UID: {firebase_user.uid}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User profile not found"
        )
    
    logger.info(f"✅ API - Profile update successful, returning response")
    return profile

@router.get("/stats")
async def get_user_stats(user_token: dict = Depends(get_current_user)):
    """Get user statistics"""
    firebase_user = AuthUser(user_token)
    
    stats = await user_service.get_user_stats(firebase_user.uid)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User profile not found"
        )
    
    return stats

@router.get("/{user_id}/public", response_model=UserProfilePublic)
async def get_user_public_profile(user_id: str):
    """Get any user's public profile"""
    profile = await user_service.get_public_profile(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not found"
        )
    
    return profile

@router.get("/handle/{handle}/public", response_model=UserProfilePublic)
async def get_user_by_handle(handle: str):
    """Get user's public profile by handle"""
    try:
        profile = await user_service.get_user_by_handle(handle)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )

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


@router.post("/me/profile-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    user_token: dict = Depends(get_current_user)
):
    """Upload a custom profile image"""
    firebase_user = AuthUser(user_token)
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Validate file size (max 5MB)
    file_content = await file.read()
    if len(file_content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )
    
    try:
        # Upload to Google Cloud Storage
        image_url = await user_service.upload_profile_image(
            firebase_user.uid, 
            file_content, 
            file.filename or "profile.jpg",
            file.content_type
        )
        
        # Update user profile with new image URL
        await user_service.update_profile_image(firebase_user.uid, image_url)
        
        return {
            "message": "Profile image uploaded successfully",
            "image_url": image_url
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload profile image: {str(e)}"
        )


@router.delete("/me/profile-image")
async def remove_profile_image(user_token: dict = Depends(get_current_user)):
    """Remove custom profile image (revert to Gmail image)"""
    firebase_user = AuthUser(user_token)
    
    try:
        await user_service.remove_profile_image(firebase_user.uid)
        return {"message": "Profile image removed successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove profile image: {str(e)}"
        )


@router.get("/experience-levels", response_model=List[str])
async def get_experience_levels():
    """Get available experience levels"""
    from ...models.user import ExperienceLevel
    return [level.value for level in ExperienceLevel]


@router.get("/location-preferences", response_model=List[str])  
async def get_location_preferences():
    """Get available location preferences"""
    from ...models.user import LocationPreference
    return [pref.value for pref in LocationPreference]


@router.delete("/me")
async def delete_user_account(
    user_token: dict = Depends(get_current_user),
    confirmation: str = None
):
    """
    Delete current user's account and ALL associated data.
    
    IMPORTANT: This will permanently delete:
    - User profile
    - All photos uploaded by the user
    - All photo files from Google Cloud Storage
    - All user interactions (likes, follows, etc.)
    
    Requires confirmation parameter with value "DELETE-MY-ACCOUNT" for safety.
    """
    firebase_user = AuthUser(user_token)
    
    # Safety check - require explicit confirmation
    if confirmation != "DELETE-MY-ACCOUNT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account deletion requires confirmation. Pass confirmation='DELETE-MY-ACCOUNT' to proceed."
        )
    
    try:
        # Get deletion summary before proceeding
        deletion_summary = await user_service.get_deletion_summary(firebase_user.uid)
        
        # Perform the deletion
        await user_service.delete_user_account(firebase_user.uid)
        
        # Also delete from Firebase Auth
        # Note: This requires admin SDK permissions
        try:
            from firebase_admin import auth as firebase_auth
            firebase_auth.delete_user(firebase_user.uid)
        except Exception as fb_error:
            # Log but don't fail - user data is already deleted from our system
            print(f"Warning: Failed to delete Firebase auth user: {fb_error}")
        
        return {
            "message": "Account successfully deleted",
            "deleted_items": deletion_summary
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )
# Cities endpoints for location selection
@router.get("/cities/search")
async def search_cities(q: str, limit: int = 10):
    """Search cities by name for autocomplete"""
    from sqlalchemy import text
    from app.database.connection import SessionLocal
    
    db = SessionLocal()
    try:
        # Search cities by name (case-insensitive)
        result = db.execute(
            text("SELECT id, name, country, region FROM cities WHERE LOWER(name) LIKE LOWER(:query) ORDER BY name LIMIT :limit"),
            {"query": f"%{q}%", "limit": limit}
        )
        cities = [{"id": row[0], "name": row[1], "country": row[2], "region": row[3]} for row in result]
        return {"cities": cities}
    finally:
        db.close()

@router.get("/cities/countries")
async def get_countries():
    """Get list of all countries"""
    from sqlalchemy import text
    from app.database.connection import SessionLocal
    
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT DISTINCT country FROM cities ORDER BY country"))
        countries = [row[0] for row in result]
        return {"countries": countries}
    finally:
        db.close()

@router.get("/cities/by-country/{country}")
async def get_cities_by_country(country: str):
    """Get cities for a specific country"""
    from sqlalchemy import text
    from app.database.connection import SessionLocal
    
    db = SessionLocal()
    try:
        result = db.execute(
            text("SELECT id, name, region FROM cities WHERE country = :country ORDER BY name"),
            {"country": country}
        )
        cities = [{"id": row[0], "name": row[1], "region": row[2]} for row in result]
        return {"cities": cities, "country": country}
    finally:
        db.close()


@router.get("/{user_id}/photos")
async def get_user_photos(
    user_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get user's photos with pagination"""
    try:
        photos_data = await user_service.get_user_photos(user_id, page=page, limit=limit)
        return photos_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user photos: {str(e)}"
        )


@router.get("/{user_id}/stats")
async def get_user_stats(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get user's statistics (photo count, likes, etc.)"""
    try:
        # Handle 'me' parameter by resolving to current user's ID
        if user_id == 'me':
            firebase_user = AuthUser(current_user)
            actual_user_id = firebase_user.uid
        else:
            actual_user_id = user_id
            
        stats = await user_service.get_user_stats(actual_user_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user stats: {str(e)}"
        )


@router.get("/me/photos")
async def get_my_photos(
    user_token: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get current user's photos with pagination"""
    firebase_user = AuthUser(user_token)
    
    try:
        photos_data = await user_service.get_user_photos(firebase_user.uid, page=page, limit=limit)
        return photos_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get your photos: {str(e)}"
        )
