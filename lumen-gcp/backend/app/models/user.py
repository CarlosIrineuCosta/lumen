"""User models for Lumen API"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class UserType(str, Enum):
    """User type enumeration"""
    PHOTOGRAPHER = "photographer"
    MODEL = "model"
    BOTH = "both"
    CLIENT = "client"
    VIEWER = "viewer"

class PhotographyStyle(str, Enum):
    """Photography style enumeration"""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    STREET = "street"
    FASHION = "fashion"
    WEDDING = "wedding"
    COMMERCIAL = "commercial"
    FINE_ART = "fine_art"
    DOCUMENTARY = "documentary"
    NATURE = "nature"
    ARCHITECTURE = "architecture"
    SPORTS = "sports"
    EVENT = "event"

class UserLocation(BaseModel):
    """User location model"""
    country: Optional[str] = None
    country_code: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    willing_to_travel: bool = False
    travel_radius_km: Optional[int] = None

class UserContact(BaseModel):
    """User contact information"""
    primary_email: str
    work_email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    instagram_handle: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None

class UserPreferences(BaseModel):
    """User preferences and settings"""
    profile_visibility: str = "public"  # public, private, photographers_only, models_only
    allow_messages: bool = True
    allow_collaboration_requests: bool = True
    notification_email: bool = True
    notification_push: bool = True
    preferred_language: str = "en"
    timezone: Optional[str] = None

class UserProfilePublic(BaseModel):
    """Public user profile (visible to all users)"""
    uid: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    user_type: Optional[UserType] = None
    photography_styles: List[PhotographyStyle] = []
    location: Optional[UserLocation] = None
    portfolio_url: Optional[str] = None
    instagram_handle: Optional[str] = None
    member_since: datetime
    photo_count: int = 0
    follower_count: int = 0
    following_count: int = 0
    verified: bool = False

class UserProfilePrivate(BaseModel):
    """Private user profile (only visible to user and authorized parties)"""
    contact: UserContact
    preferences: UserPreferences
    experience_level: Optional[str] = None  # beginner, intermediate, advanced, professional
    equipment: List[str] = []  # Camera equipment, software, etc.
    certifications: List[str] = []
    languages_spoken: List[str] = []
    availability: Optional[Dict[str, Any]] = None  # Schedule, preferred times, etc.
    rates: Optional[Dict[str, Any]] = None  # Pricing information
    emergency_contact: Optional[Dict[str, str]] = None

class UserProfileFull(BaseModel):
    """Complete user profile combining public and private data"""
    uid: str
    public_profile: UserProfilePublic
    private_profile: UserProfilePrivate
    firebase_data: Dict[str, Any] = {}  # Firebase auth data
    metadata: Dict[str, Any] = {}  # Additional expandable fields
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

class CreateUserRequest(BaseModel):
    """Request model for creating a new user profile"""
    display_name: str
    bio: Optional[str] = None
    user_type: Optional[UserType] = None
    photography_styles: List[PhotographyStyle] = []
    
    # Location
    country: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[str] = None
    willing_to_travel: bool = False
    
    # Contact (work email is optional, primary comes from Firebase)
    work_email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    instagram_handle: Optional[str] = None
    
    # Preferences
    profile_visibility: str = "public"
    allow_messages: bool = True
    preferred_language: str = "en"
    
    # Additional expandable fields
    metadata: Dict[str, Any] = {}

    @validator('display_name')
    def validate_display_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Display name must be at least 2 characters')
        return v.strip()

    @validator('instagram_handle')
    def validate_instagram_handle(cls, v):
        if v and not v.startswith('@'):
            v = '@' + v
        return v

class UpdateUserRequest(BaseModel):
    """Request model for updating user profile"""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    user_type: Optional[UserType] = None
    photography_styles: Optional[List[PhotographyStyle]] = None
    
    # Location updates
    location: Optional[UserLocation] = None
    
    # Contact updates  
    work_email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    instagram_handle: Optional[str] = None
    
    # Preferences updates
    preferences: Optional[UserPreferences] = None
    
    # Additional expandable fields
    metadata: Optional[Dict[str, Any]] = None

class UserSearchQuery(BaseModel):
    """User search query model"""
    user_type: Optional[UserType] = None
    photography_styles: Optional[List[PhotographyStyle]] = None
    location_country: Optional[str] = None
    location_city: Optional[str] = None
    willing_to_travel: Optional[bool] = None
    verified_only: bool = False
    limit: int = 20
    offset: int = 0