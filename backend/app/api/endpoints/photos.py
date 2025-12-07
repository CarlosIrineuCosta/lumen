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
from ...services.location_service import LocationService
from ...database.connection import get_db
from ...storage.interfaces import StorageException

router = APIRouter()

@router.get("/recent", response_model=PhotoListResponse)
async def get_recent_photos(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get recent public photos - main feed endpoint"""
    try:
        photo_service = PhotoService(db)
        return await photo_service.get_recent_photos(page=page, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent photos: {str(e)}")

@router.get("/", response_model=PhotoListResponse)
async def list_photos(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List public photos with pagination - no authentication required"""
    try:
        photo_service = PhotoService(db)
        return await photo_service.get_recent_photos(page=page, limit=limit)
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
    camera: Optional[str] = Form(None),  # Camera make/model
    lens: Optional[str] = Form(None),    # Lens description
    settings: Optional[str] = Form(None), # Camera settings
    location: Optional[str] = Form(None), # Location string for city lookup
    is_collaborative: bool = Form(False),
    model_release_status: str = Form("none"),
    content_rating: str = Form("general"),
    category: str = Form("portrait"),  # Art photography category
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
        
        # Structure camera data
        camera_data = {}
        if camera:
            camera_data['camera'] = camera
        if lens:
            camera_data['lens'] = lens  
        if settings:
            camera_data['settings'] = settings
        
        # Resolve location string to city_id if provided
        resolved_city_id = city_id  # Use explicit city_id if provided
        if location and not city_id:
            location_service = LocationService(db)
            resolved_city_id = location_service.resolve_city(location)
        
        # Create request object with image_url (will be set by service)
        request = CreatePhotoRequest(
            title=title,
            description=description,
            image_url="",  # Will be set by service after upload
            user_tags=tag_list,
            city_id=resolved_city_id,
            location_name=location_name,
            is_collaborative=is_collaborative,
            model_release_status=model_release_status,
            content_rating=content_rating,
            category=category,
            is_public=is_public,
            is_portfolio=is_portfolio,
            camera_data=camera_data if camera_data else None
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

        # Return photo response directly
        return photo

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except StorageException as e:
        raise HTTPException(status_code=503, detail=f"Storage service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/user", response_model=PhotoListResponse)
async def get_current_user_photos(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_token: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's photos - /user endpoint"""
    firebase_user = AuthUser(user_token)
    
    # Get PostgreSQL user UUID for this Firebase user
    photo_service = PhotoService(db)
    try:
        user_id = await photo_service.ensure_user_exists(firebase_user)
        return await photo_service.get_user_photos(
            user_id=user_id,  # Already a string (Firebase UID)
            viewer_user_id=user_id,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user photos: {str(e)}")

@router.get("/my-photos", response_model=PhotoListResponse)
async def get_my_photos(
    portfolio_only: bool = Query(False, description="Filter to portfolio photos only"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_token: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's photos - optionally filtered to portfolio only"""
    firebase_user = AuthUser(user_token)
    
    try:
        photo_service = PhotoService(db)
        return await photo_service.get_user_photos(
            user_id=firebase_user.uid,
            viewer_user_id=firebase_user.uid,
            portfolio_only=portfolio_only,
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
        photo = await photo_service.get_photo_by_id(photo_id, viewer_user_id)
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found")
        
        return photo
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get photo: {str(e)}")


# Photo Management Endpoints
@router.get("/mine", response_model=PhotoListResponse)
async def get_my_photos_management(
    include_deleted: bool = Query(False),
    series_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    user_token: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's photos for management (including deleted if requested)"""
    firebase_user = AuthUser(user_token)

    try:
        photo_service = PhotoService(db)
        return await photo_service.get_user_photos_for_management(
            user_id=firebase_user.uid,
            include_deleted=include_deleted,
            series_id=series_id,
            category=category,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get photos: {str(e)}")


@router.put("/{photo_id}", response_model=PhotoResponse)
async def update_photo(
    photo_id: str,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    user_tags: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    series_id: Optional[int] = Form(None),
    is_public: Optional[bool] = Form(None),
    is_portfolio: Optional[bool] = Form(None),
    user_token: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update photo details (owner only)"""
    firebase_user = AuthUser(user_token)

    # Parse tags
    tag_list = None
    if user_tags is not None:
        tag_list = [tag.strip() for tag in user_tags.split(',') if tag.strip()]

    try:
        photo_service = PhotoService(db)

        # Create update request
        update_data = {}
        if title is not None:
            update_data['title'] = title
        if description is not None:
            update_data['description'] = description
        if tag_list is not None:
            update_data['user_tags'] = tag_list
        if category is not None:
            update_data['category'] = category
        if series_id is not None:
            update_data['series_id'] = series_id
        if is_public is not None:
            update_data['is_public'] = is_public
        if is_portfolio is not None:
            update_data['is_portfolio'] = is_portfolio

        updated_photo = await photo_service.update_photo(
            photo_id=photo_id,
            user_id=firebase_user.uid,
            update_data=update_data
        )

        if not updated_photo:
            raise HTTPException(status_code=404, detail="Photo not found or access denied")

        return updated_photo
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update photo: {str(e)}")


@router.delete("/{photo_id}")
async def delete_photo(
    photo_id: str,
    permanent: bool = Query(False, description="Permanently delete (default: soft delete)"),
    user_token: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete photo (soft delete by default, permanent if specified)"""
    firebase_user = AuthUser(user_token)

    try:
        photo_service = PhotoService(db)
        success = await photo_service.delete_photo(
            photo_id=photo_id,
            user_id=firebase_user.uid,
            permanent=permanent
        )

        if not success:
            raise HTTPException(status_code=404, detail="Photo not found or access denied")

        delete_type = "permanently deleted" if permanent else "moved to trash"
        return {"message": f"Photo {delete_type} successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete photo: {str(e)}")


@router.patch("/{photo_id}/visibility")
async def toggle_photo_visibility(
    photo_id: str,
    is_public: bool = Form(...),
    user_token: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle photo visibility (public/private)"""
    firebase_user = AuthUser(user_token)

    try:
        photo_service = PhotoService(db)
        updated_photo = await photo_service.update_photo(
            photo_id=photo_id,
            user_id=firebase_user.uid,
            update_data={"is_public": is_public}
        )

        if not updated_photo:
            raise HTTPException(status_code=404, detail="Photo not found or access denied")

        visibility = "public" if is_public else "private"
        return {"message": f"Photo set to {visibility}", "is_public": is_public}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update visibility: {str(e)}")


@router.post("/batch")
async def batch_update_photos(
    photo_ids: List[str] = Form(...),
    action: str = Form(...),  # "delete", "set_series", "set_category", "set_visibility"
    series_id: Optional[int] = Form(None),
    category: Optional[str] = Form(None),
    is_public: Optional[bool] = Form(None),
    user_token: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Batch operations on multiple photos"""
    firebase_user = AuthUser(user_token)

    try:
        photo_service = PhotoService(db)

        if action == "delete":
            count = await photo_service.batch_delete_photos(
                photo_ids=photo_ids,
                user_id=firebase_user.uid
            )
        elif action == "set_series":
            if series_id is None:
                raise HTTPException(status_code=400, detail="series_id required for set_series action")
            count = await photo_service.batch_update_photos(
                photo_ids=photo_ids,
                user_id=firebase_user.uid,
                update_data={"series_id": series_id}
            )
        elif action == "set_category":
            if category is None:
                raise HTTPException(status_code=400, detail="category required for set_category action")
            count = await photo_service.batch_update_photos(
                photo_ids=photo_ids,
                user_id=firebase_user.uid,
                update_data={"category": category}
            )
        elif action == "set_visibility":
            if is_public is None:
                raise HTTPException(status_code=400, detail="is_public required for set_visibility action")
            count = await photo_service.batch_update_photos(
                photo_ids=photo_ids,
                user_id=firebase_user.uid,
                update_data={"is_public": is_public}
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid action")

        return {"message": f"Updated {count} photos", "action": action}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch operation failed: {str(e)}")



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
    portfolio_only: bool = Query(False, description="Filter to portfolio photos only"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_token: dict = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get photos for a specific user - optionally filtered to portfolio only"""
    viewer_user_id = None
    if user_token:
        viewer_user = AuthUser(user_token)
        viewer_user_id = viewer_user.uid
    
    try:
        photo_service = PhotoService(db)
        return await photo_service.get_user_photos(
            user_id=user_id,
            viewer_user_id=viewer_user_id,
            portfolio_only=portfolio_only,
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
