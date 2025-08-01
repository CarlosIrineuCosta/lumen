"""Photo models for Lumen API"""

from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class PhotoVisibility(str, Enum):
    """Photo visibility enumeration"""
    PUBLIC = "public"
    PRIVATE = "private"
    FOLLOWERS_ONLY = "followers_only"
    UNLISTED = "unlisted"

class PhotoStatus(str, Enum):
    """Photo processing status"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"

class PhotoMetadata(BaseModel):
    """Photo metadata from EXIF and processing"""
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    lens_model: Optional[str] = None
    focal_length: Optional[str] = None
    aperture: Optional[str] = None
    shutter_speed: Optional[str] = None
    iso: Optional[int] = None
    taken_at: Optional[datetime] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    color_space: Optional[str] = None
    orientation: Optional[int] = None

class PhotoLocation(BaseModel):
    """Photo location information"""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country: Optional[str] = None
    state_province: Optional[str] = None
    city: Optional[str] = None
    location_name: Optional[str] = None
    venue_name: Optional[str] = None

class PhotoEngagement(BaseModel):
    """Photo engagement metrics"""
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    views_count: int = 0
    saves_count: int = 0

class PhotoUrls(BaseModel):
    """Photo URL variants"""
    original: str
    large: Optional[str] = None
    medium: Optional[str] = None
    small: Optional[str] = None
    thumbnail: str
    
class Photo(BaseModel):
    """Complete photo model"""
    id: str
    user_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    alt_text: Optional[str] = None
    
    # URLs
    urls: PhotoUrls
    
    # Classification and content
    tags: List[str] = []
    photography_style: Optional[str] = None
    subject_matter: List[str] = []
    color_palette: List[str] = []
    
    # Technical metadata
    metadata: PhotoMetadata = PhotoMetadata()
    
    # Location
    location: Optional[PhotoLocation] = None
    
    # Visibility and permissions
    visibility: PhotoVisibility = PhotoVisibility.PUBLIC
    allow_downloads: bool = True
    allow_comments: bool = True
    
    # Engagement
    engagement: PhotoEngagement = PhotoEngagement()
    
    # Status and processing
    status: PhotoStatus = PhotoStatus.READY
    processing_info: Optional[Dict[str, Any]] = None
    
    # Collections and albums
    album_ids: List[str] = []
    collection_ids: List[str] = []
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    
    # Moderation
    moderation_status: str = "pending"  # pending, approved, flagged, rejected
    moderation_flags: List[str] = []
    
    # Additional expandable metadata
    custom_metadata: Dict[str, Any] = {}

class CreatePhotoRequest(BaseModel):
    """Request model for creating a new photo"""
    title: Optional[str] = None
    description: Optional[str] = None
    alt_text: Optional[str] = None
    tags: List[str] = []
    photography_style: Optional[str] = None
    visibility: PhotoVisibility = PhotoVisibility.PUBLIC
    allow_downloads: bool = True
    allow_comments: bool = True
    location: Optional[PhotoLocation] = None
    custom_metadata: Dict[str, Any] = {}

    @validator('title')
    def validate_title(cls, v):
        if v and len(v.strip()) > 200:
            raise ValueError('Title must be less than 200 characters')
        return v.strip() if v else None

    @validator('description')
    def validate_description(cls, v):
        if v and len(v.strip()) > 2000:
            raise ValueError('Description must be less than 2000 characters')
        return v.strip() if v else None

class UpdatePhotoRequest(BaseModel):
    """Request model for updating photo metadata"""
    title: Optional[str] = None
    description: Optional[str] = None
    alt_text: Optional[str] = None
    tags: Optional[List[str]] = None
    photography_style: Optional[str] = None
    visibility: Optional[PhotoVisibility] = None
    allow_downloads: Optional[bool] = None
    allow_comments: Optional[bool] = None
    location: Optional[PhotoLocation] = None
    custom_metadata: Optional[Dict[str, Any]] = None

class PhotoResponse(BaseModel):
    """Public photo response model"""
    id: str
    user_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    alt_text: Optional[str] = None
    urls: PhotoUrls
    tags: List[str] = []
    photography_style: Optional[str] = None
    visibility: PhotoVisibility
    location: Optional[PhotoLocation] = None
    engagement: PhotoEngagement
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

class PhotoListResponse(BaseModel):
    """Photo list response model"""
    photos: List[PhotoResponse]
    total: int
    page: int
    per_page: int
    has_more: bool

class PhotoSearchQuery(BaseModel):
    """Photo search query model"""
    user_id: Optional[str] = None
    tags: Optional[List[str]] = None
    photography_style: Optional[str] = None
    visibility: Optional[PhotoVisibility] = None
    location_country: Optional[str] = None
    location_city: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    limit: int = 20
    offset: int = 0
    sort_by: str = "created_at"  # created_at, updated_at, likes_count, views_count
    sort_order: str = "desc"  # asc, desc