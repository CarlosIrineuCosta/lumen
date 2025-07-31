"""Photo management endpoints for Lumen API"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from ...auth_middleware import get_current_user, get_optional_user, AuthUser

router = APIRouter()

class PhotoResponse(BaseModel):
    """Photo response model"""
    id: str
    user_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: str
    thumbnail_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    likes_count: int = 0
    is_public: bool = True

class CreatePhotoRequest(BaseModel):
    """Create photo request model"""
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: bool = True

class PhotoListResponse(BaseModel):
    """Photo list response model"""
    photos: List[PhotoResponse]
    total: int
    page: int
    per_page: int

@router.get("/", response_model=PhotoListResponse)
async def list_photos(
    page: int = 1,
    per_page: int = 20,
    user_token: dict = Depends(get_optional_user)
):
    """List photos with pagination"""
    
    # Mock data for now - in real app, fetch from database
    mock_photos = []
    for i in range(5):
        mock_photos.append(PhotoResponse(
            id=f"photo_{i}",
            user_id="demo_user",
            title=f"Sample Photo {i+1}",
            description=f"This is a sample photo description {i+1}",
            image_url=f"https://picsum.photos/800/600?random={i}",
            thumbnail_url=f"https://picsum.photos/200/200?random={i}",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            likes_count=i * 5,
            is_public=True
        ))
    
    return PhotoListResponse(
        photos=mock_photos,
        total=len(mock_photos),
        page=page,
        per_page=per_page
    )

@router.post("/", response_model=PhotoResponse)
async def create_photo(
    photo_data: CreatePhotoRequest,
    user_token: dict = Depends(get_current_user)
):
    """Create a new photo entry (metadata only for now)"""
    user = AuthUser(user_token)
    
    # Generate a unique photo ID
    photo_id = str(uuid.uuid4())
    
    # In real app, you'd save to database and handle file upload
    return PhotoResponse(
        id=photo_id,
        user_id=user.uid,
        title=photo_data.title or "Untitled Photo",
        description=photo_data.description,
        image_url=f"https://picsum.photos/800/600?random={hash(photo_id) % 1000}",
        thumbnail_url=f"https://picsum.photos/200/200?random={hash(photo_id) % 1000}",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        likes_count=0,
        is_public=photo_data.is_public
    )

@router.get("/my-photos", response_model=PhotoListResponse)
async def get_my_photos(
    page: int = 1,
    per_page: int = 20,
    user_token: dict = Depends(get_current_user)
):
    """Get current user's photos"""
    user = AuthUser(user_token)
    
    # Mock user photos
    mock_photos = []
    for i in range(3):
        mock_photos.append(PhotoResponse(
            id=f"user_photo_{i}",
            user_id=user.uid,
            title=f"My Photo {i+1}",
            description=f"Photo uploaded by {user.email}",
            image_url=f"https://picsum.photos/800/600?random={hash(user.uid + str(i)) % 1000}",
            thumbnail_url=f"https://picsum.photos/200/200?random={hash(user.uid + str(i)) % 1000}",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            likes_count=i * 2,
            is_public=True
        ))
    
    return PhotoListResponse(
        photos=mock_photos,
        total=len(mock_photos),
        page=page,
        per_page=per_page
    )

@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(
    photo_id: str,
    user_token: dict = Depends(get_optional_user)
):
    """Get a specific photo by ID"""
    
    # Mock photo data
    return PhotoResponse(
        id=photo_id,
        user_id="demo_user",
        title="Sample Photo",
        description="A beautiful photo from our platform",
        image_url=f"https://picsum.photos/800/600?random={hash(photo_id) % 1000}",
        thumbnail_url=f"https://picsum.photos/200/200?random={hash(photo_id) % 1000}",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        likes_count=42,
        is_public=True
    )

@router.post("/{photo_id}/like")
async def like_photo(
    photo_id: str,
    user_token: dict = Depends(get_current_user)
):
    """Like a photo"""
    user = AuthUser(user_token)
    
    # In real app, toggle like in database
    return {
        "photo_id": photo_id,
        "user_id": user.uid,
        "liked": True,
        "timestamp": datetime.utcnow().isoformat()
    }