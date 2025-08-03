"""
User model for Lumen Photography Platform
Flexible schema with JSONB for future expansion
"""

from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database.connection import Base


class User(Base):
    """Main user model with flexible profile data"""
    __tablename__ = "users"

    # Primary key and Firebase integration
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firebase_uid = Column(String(128), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    handle = Column(String(50), unique=True, nullable=False)

    # Required core fields
    display_name = Column(String(100), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    primary_user_type = Column(Integer, ForeignKey("user_types.id"), nullable=False)

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

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    city = relationship("City", backref="users")
    user_type = relationship("UserType", backref="users") 
    photos = relationship("Photo", back_populates="user", cascade="all, delete-orphan")
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


class PhotographyStyle(str, Enum):
    PORTRAIT = "portrait"
    FASHION = "fashion"
    ARTISTIC_NUDE = "artistic_nude"
    COMMERCIAL = "commercial"
    LIFESTYLE = "lifestyle"
    FITNESS = "fitness"
    POLE_DANCE = "pole_dance"
    BIKINI = "bikini"


class UserProfilePublic(BaseModel):
    """Public user profile data"""
    id: str
    handle: str
    display_name: str
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    city_name: Optional[str] = None
    user_type: str
    photography_styles: List[str] = []
    portfolio_count: int = 0
    is_verified: bool = False
    
    class Config:
        from_attributes = True


class UserProfilePrivate(UserProfilePublic):
    """Private user profile data (sensitive fields)"""
    email: str
    firebase_uid: str
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


class UpdateUserRequest(BaseModel):
    """Request model for updating user profile"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    city_id: Optional[int] = None
    profile_image_url: Optional[str] = None
    
    # Model-specific fields
    gender: Optional[str] = None
    age: Optional[int] = Field(None, ge=18, le=65)
    height_cm: Optional[int] = Field(None, ge=140, le=220)
    weight_kg: Optional[int] = Field(None, ge=40, le=200)
    
    photography_styles: Optional[List[PhotographyStyle]] = None
    privacy_settings: Optional[Dict] = None


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