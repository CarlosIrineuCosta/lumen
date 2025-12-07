"""
User model for Lumen Photography Platform
Flexible schema with JSONB for future expansion
"""

from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database.connection import Base


class User(Base):
    """Main user model with flexible profile data"""
    __tablename__ = "users"

    # ⚠️ CRITICAL WARNING: Firebase UID vs Database vs GCS Consistency Issue!
    # Database uses String(128) format to match Firebase UID strings in GCS files!
    # Changing this breaks ALL image loading! See CLAUDE.md "CRITICAL SYSTEM DEPENDENCIES"
    # Primary key - using Firebase UID directly (stored as string in database)
    id = Column(String(128), primary_key=True)  # Firebase UID stored as string (28-char alphanumeric)
    email = Column(String(255), unique=True, nullable=False)
    handle = Column(String(50), unique=True, nullable=False)

    # Required core fields
    display_name = Column(String(100), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    primary_user_type = Column(Integer, ForeignKey("user_types.id"), nullable=False)
    
    # Legal compliance fields (mandatory)
    birth_date = Column(Date, nullable=False)  # For age verification
    country_code = Column(String(3), nullable=False)  # ISO country code for legal age validation
    tos_accepted_at = Column(DateTime(timezone=True), nullable=False)  # TOS acceptance timestamp

    # Model-specific mandatory fields (NULL for photographers)
    gender = Column(String(20))  # Male, Female, Non-binary, Other
    age = Column(Integer)
    height_cm = Column(Integer)
    weight_kg = Column(Integer)

    # Optional physical characteristics (models)
    ethnicity = Column(String(50))
    eye_color = Column(String(30))
    hair_color = Column(String(30))
    measurements = Column(JSONB)  # {chest: 90, waist: 60, hips: 90, dress_size: "M", shoe_size: 38}
    has_tattoos = Column(Boolean, default=False)
    has_piercings = Column(Boolean, default=False)

    # Profile data
    profile_image_url = Column(String(500))
    bio = Column(Text)
    website = Column(String(500))

    # Flexible expansion fields (JSONB for unknown future needs)
    profile_data = Column(JSONB, default={})  # {portfolio_url, gear, experience_years, languages, etc}
    availability_data = Column(JSONB, default={})  # {open_for_work, travel_range, rates, etc}
    privacy_settings = Column(JSONB, default={
        "show_city": False, 
        "show_country": True, 
        "show_age": True
    })

    # Subscription and billing
    stripe_customer_id = Column(String(255))  # Stripe customer ID
    stripe_subscription_id = Column(String(255))  # Current active subscription ID
    subscription_tier = Column(String(50), default='free')  # free, hobbyist, professional, studio
    subscription_status = Column(String(50), default='active')  # active, canceled, past_due, etc.
    subscription_data = Column(JSONB, default={})  # {trial_end, cancel_at_period_end, etc.}

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    city = relationship("City", backref="users")
    user_type = relationship("UserType", backref="users")
    photos = relationship("Photo", back_populates="user", cascade="all, delete-orphan")
    series = relationship("Series", back_populates="user", cascade="all, delete-orphan")
    specialties = relationship("UserSpecialty", back_populates="user", cascade="all, delete-orphan")
    
    # Connection relationships
    sent_connections = relationship(
        "UserConnection", 
        foreign_keys="UserConnection.requester_id",
        back_populates="requester",
        cascade="all, delete-orphan"
    )
    received_connections = relationship(
        "UserConnection",
        foreign_keys="UserConnection.target_id", 
        back_populates="target",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(handle='{self.handle}', display_name='{self.display_name}')>"

    @property
    def firebase_uid(self):
        """Backward compatibility property - id IS the Firebase UID"""
        return self.id

    @property
    def is_model(self):
        """Check if user type is model"""
        return self.user_type and self.user_type.type_name == 'model'
    
    @property
    def is_photographer(self):
        """Check if user type is photographer"""  
        return self.user_type and self.user_type.type_name == 'photographer'

    @property
    def location_display(self):
        """Return location string based on privacy settings"""
        if not self.city:
            return "Unknown"
        
        if self.privacy_settings.get("show_city", False):
            return f"{self.city.name}, {self.city.country}"
        else:
            return self.city.country

    def get_mandatory_model_fields(self):
        """Return dict of mandatory model fields for validation"""
        if not self.is_model:
            return {}
        
        return {
            "gender": self.gender,
            "age": self.age, 
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg
        }

    def validate_model_requirements(self):
        """Check if model has all mandatory fields"""
        if not self.is_model:
            return True
        
        mandatory_fields = self.get_mandatory_model_fields()
        return all(value is not None for value in mandatory_fields.values())

# Pydantic models for API serialization
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class UserType(str, Enum):
    PHOTOGRAPHER = "photographer"
    MODEL = "model"
    STUDIO = "studio"
    MAKEUP_ARTIST = "makeup_artist"
    STYLIST = "stylist"


class PhotographyStyle(str, Enum):
    PORTRAIT = "portrait"
    FASHION = "fashion"
    ARTISTIC_NUDE = "artistic_nude"
    COMMERCIAL = "commercial"
    LIFESTYLE = "lifestyle"
    FITNESS = "fitness"
    POLE_DANCE = "pole_dance"
    BIKINI = "bikini"
    BOUDOIR = "boudoir"
    STREET = "street"
    LANDSCAPE = "landscape"
    EVENT = "event"
    WEDDING = "wedding"
    CORPORATE = "corporate"
    EDITORIAL = "editorial"
    BEAUTY = "beauty"
    CONCEPTUAL = "conceptual"
    DOCUMENTARY = "documentary"

class ExperienceLevel(str, Enum):
    BEGINNER = "beginner"
    AMATEUR = "amateur"
    SEMI_PRO = "semi_pro"
    PROFESSIONAL = "professional"
    EXPERT = "expert"


class LocationPreference(str, Enum):
    STUDIO = "studio"
    OUTDOOR = "outdoor"
    URBAN = "urban"
    NATURE = "nature"
    HOME = "home"
    LOCATION = "location"


class ProfileImageSource(str, Enum):
    GMAIL = "gmail"
    UPLOADED = "uploaded"
    NONE = "none"


class UserProfilePublic(BaseModel):
    """Public user profile data"""
    id: str  # This is the Firebase UID
    handle: str
    display_name: str
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    city_name: Optional[str] = None
    user_type: str
    photography_styles: List[str] = []
    portfolio_count: int = 0
    is_verified: bool = False
    
    # New public fields
    artistic_statement: Optional[str] = None
    tagline: Optional[str] = None
    experience_level: Optional[str] = None
    experience_years: Optional[int] = None
    specializes_in: List[str] = []
    open_for_work: bool = True
    available_for_travel: bool = False
    location_preferences: List[str] = []
    website: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserProfilePrivate(UserProfilePublic):
    """Private user profile data (sensitive fields)"""
    email: str
    # Note: id is the Firebase UID, no separate firebase_uid field
    privacy_settings: Dict = {}
    
    
class UserProfileFull(UserProfilePrivate):
    """Full user profile data (for own profile)"""
    city_id: int
    profile_completion: int
    gender: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    # Legal compliance fields
    birth_date: Optional[str] = None  # For frontend compatibility
    country_code: Optional[str] = None
    tos_accepted_at: Optional[datetime] = None
    
    # Full profile data
    mission_statement: Optional[str] = None
    camera_gear: List[str] = []
    modeling_types: List[str] = []
    comfortable_with: List[str] = []
    special_skills: List[str] = []
    studio_access: Optional[bool] = None
    rates: Optional[Dict] = None
    social_links: Optional[Dict] = None
    availability_data: Optional[Dict] = None
    contact_preferences: Optional[Dict] = None
    travel_notes: Optional[str] = None


class CreateUserRequest(BaseModel):
    """Request model for creating new user"""
    handle: str = Field(..., min_length=3, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    city_id: int
    user_type: UserType    
    # Model-specific fields (required for models)
    gender: Optional[str] = None
    age: Optional[int] = Field(None, ge=18, le=65)
    height_cm: Optional[int] = Field(None, ge=140, le=220)
    weight_kg: Optional[int] = Field(None, ge=40, le=200)
    
    photography_styles: List[PhotographyStyle] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "handle": "photographer_jane",
                "display_name": "Jane Smith",
                "bio": "Professional portrait photographer",
                "city_id": 1,
                "user_type": "photographer",
                "photography_styles": ["portrait", "fashion"]
            }
        }


class ProfileImageData(BaseModel):
    """Profile image information"""
    current_source: ProfileImageSource = ProfileImageSource.GMAIL
    uploaded_image_url: Optional[str] = None
    gmail_image_url: Optional[str] = None
    upload_date: Optional[datetime] = None
    image_verified: bool = False

class AvailabilityData(BaseModel):
    """User availability information"""
    open_for_work: bool = True
    available_for_travel: bool = False
    travel_range_km: Optional[int] = Field(None, ge=0, le=5000)
    travel_internationally: bool = False
    travel_notes: Optional[str] = Field(None, max_length=500)
    location_preferences: List[LocationPreference] = []
    available_days: List[str] = []  # ["monday", "tuesday", "weekend"]
    available_times: List[str] = []  # ["morning", "afternoon", "evening"]
    timezone: Optional[str] = None


class ContactPreferences(BaseModel):
    """User contact preferences"""
    preferred_contact: str = "email"  # email, phone, app_messaging
    response_time: str = "within_24h"
    booking_lead_time: str = "1_week"
    allow_direct_booking: bool = True
    require_references: bool = False


class UpdateUserRequest(BaseModel):
    """Request model for updating user profile"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    handle: Optional[str] = Field(None, min_length=1, max_length=50, alias='username')  # Add handle/username field
    bio: Optional[str] = Field(None, max_length=500)
    city_id: Optional[int] = None
    profile_image_url: Optional[str] = None
    
    # Legal compliance fields (cannot be updated after initial registration)
    birth_date: Optional[str] = None  # Allow date string format
    country_code: Optional[str] = Field(None, max_length=3)
    tos_accepted: Optional[bool] = None
    
    # Artistic expression
    artistic_statement: Optional[str] = Field(None, max_length=2000)
    tagline: Optional[str] = Field(None, max_length=200)
    mission_statement: Optional[str] = Field(None, max_length=500)
    
    # Model-specific fields
    gender: Optional[str] = None
    age: Optional[int] = Field(None, ge=18, le=65)
    height_cm: Optional[int] = Field(None, ge=140, le=220)
    weight_kg: Optional[int] = Field(None, ge=40, le=200)
    
    # Extended profile data
    photography_styles: Optional[List[PhotographyStyle]] = None
    experience_level: Optional[ExperienceLevel] = None
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    
    # Photographer-specific
    camera_gear: Optional[List[str]] = None
    specializes_in: Optional[List[str]] = None
    studio_access: Optional[bool] = None
    rates: Optional[Dict] = None  # {hourly_rate, day_rate, currency, negotiable}
    
    # Model-specific
    modeling_types: Optional[List[str]] = None
    comfortable_with: Optional[List[str]] = None
    special_skills: Optional[List[str]] = None
    
    # Studio-specific
    studio_size_sqft: Optional[int] = None
    included_equipment: Optional[List[str]] = None
    hourly_rate: Optional[float] = None
    
    # Social and contact
    website: Optional[str] = None
    social_links: Optional[Dict] = None
    
    # Settings
    availability_data: Optional[AvailabilityData] = None
    contact_preferences: Optional[ContactPreferences] = None
    privacy_settings: Optional[Dict] = None
    profile_data: Optional[Dict] = None  # For profile completion tracking


class UserSearchQuery(BaseModel):
    """Search parameters for finding users"""
    query: Optional[str] = None
    user_type: Optional[UserType] = None
    city_id: Optional[int] = None
    photography_styles: Optional[List[PhotographyStyle]] = None
    max_distance_km: Optional[int] = Field(None, ge=1, le=500)
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class UserLocation(BaseModel):
    """User location data"""
    city_id: int
    city_name: str
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class UserContact(BaseModel):
    """User contact information"""
    email: str
    instagram: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None


class UserPreferences(BaseModel):
    """User preferences and settings"""
    privacy_settings: Dict = {}
    notification_settings: Dict = {}
    content_preferences: Dict = {}