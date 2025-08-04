"""Photo management endpoints for Lumen API"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from ...auth_middleware import get_current_user, get_optional_user, AuthUser
from ...models.photo import (
    PhotoResponse, PhotoListResponse, CreatePhotoRequest, 
    UpdatePhotoRequest, PhotoSearchQuery
)
from ...services.photo_service import PhotoService
from ...database.connection import get_db

router = APIRouter()

@router.get("/", response_model=PhotoListResponse)
async def list_photos(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List public photos with pagination - no authentication required"""
    try:
        photo_service = PhotoService(db)
        return await photo_service.get_public_photos(page=page, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get photos: {str(e)}")

@router.post("/upload", response_model=PhotoResponse)
async def upload_photo(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    user_tags: Optional[str] = Form(None),  # Comma-separated tags
    city_id: Optional[int] = Form(None),
    location_name: Optional[str] = Form(None),
    is_collaborative: bool = Form(False),
    model_release_status: str = Form("none"),
    content_rating: str = Form("general"),
    is_public: bool = Form(True),
    is_portfolio: bool = Form(False),
    user_token: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a photo file to Google Cloud Storage"""
    firebase_user = AuthUser(user_token)
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Parse tags
        tag_list = []
        if user_tags:
            tag_list = [tag.strip() for tag in user_tags.split(',') if tag.strip()]
        
        # Create request object with image_url (will be set by service)
        request = CreatePhotoRequest(
            title=title,
            description=description,
            image_url="",  # Will be set by service after upload
            user_tags=tag_list,
            city_id=city_id,
            location_name=location_name,
            is_collaborative=is_collaborative,
            model_release_status=model_release_status,
            content_rating=content_rating,
            is_public=is_public,
            is_portfolio=is_portfolio
        )
        
        # Upload photo
        photo_service = PhotoService(db)
        photo = await photo_service.upload_photo(
            firebase_user=firebase_user,
            file_content=file_content,
            filename=file.filename or "upload.jpg",
            content_type=file.content_type,
            request=request
        )
        
        # Convert to response
        return photo_service._to_photo_response(photo)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/my-photos", response_model=PhotoListResponse)
async def get_my_photos(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_token: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's photos"""
    firebase_user = AuthUser(user_token)
    
    try:
        photo_service = PhotoService(db)
        return await photo_service.get_user_photos(
            user_id=firebase_user.uid,
            viewer_user_id=firebase_user.uid,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get photos: {str(e)}")

@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(
    photo_id: str,
    user_token: dict = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get a specific photo by ID"""
    viewer_user_id = None
    if user_token:
        viewer_user = AuthUser(user_token)
        viewer_user_id = viewer_user.uid
    
    try:
        photo_service = PhotoService(db)
        photo = await photo_service.get_photo(photo_id, viewer_user_id)
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found")
        
        return photo_service._to_photo_response(photo)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get photo: {str(e)}")

@router.put("/{photo_id}", response_model=PhotoResponse)
async def update_photo(
    photo_id: str,
    request: UpdatePhotoRequest,
    user_token: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update photo metadata"""
    firebase_user = AuthUser(user_token)
    
    try:
        photo_service = PhotoService(db)
        photo = await photo_service.update_photo(photo_id, firebase_user.uid, request)
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found or access denied")
        
        return photo_service._to_photo_response(photo)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update photo: {str(e)}")

@router.delete("/{photo_id}")
async def delete_photo(
    photo_id: str,
    user_token: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a photo"""
    firebase_user = AuthUser(user_token)
    
    try:
        photo_service = PhotoService(db)
        success = await photo_service.delete_photo(photo_id, firebase_user.uid)
        if not success:
            raise HTTPException(status_code=404, detail="Photo not found or access denied")
        
        return {"message": "Photo deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete photo: {str(e)}")

@router.post("/{photo_id}/like")
async def like_photo(
    photo_id: str,
    user_token: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Like a photo"""
    firebase_user = AuthUser(user_token)
    
    try:
        # TODO: Implement like functionality in PostgreSQL service
        raise HTTPException(status_code=501, detail="Like functionality not yet implemented")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to like photo: {str(e)}")

@router.get("/user/{user_id}", response_model=PhotoListResponse)
async def get_user_photos(
    user_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_token: dict = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get photos for a specific user"""
    viewer_user_id = None
    if user_token:
        viewer_user = AuthUser(user_token)
        viewer_user_id = viewer_user.uid
    
    try:
        photo_service = PhotoService(db)
        return await photo_service.get_user_photos(
            user_id=user_id,
            viewer_user_id=viewer_user_id,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get photos: {str(e)}")

@router.post("/search", response_model=PhotoListResponse)
async def search_photos(
    query: PhotoSearchQuery,
    user_token: dict = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Search photos based on criteria"""
    # TODO: Implement photo search
    raise HTTPException(status_code=501, detail="Photo search not yet implemented")