"""
Photo model for Lumen Photography Platform
Supports collaborative tagging and flexible metadata
"""

from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database.connection import Base


class Photo(Base):
    """Photo model with collaboration and flexible metadata"""
    __tablename__ = "photos"

    # Primary key and ownership
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # ⚠️ CRITICAL WARNING: This user_id MUST map to actual Firebase UID strings in GCS!
    # Database uses String(128) format to match Firebase UID strings in GCS paths!
    # See CLAUDE.md "CRITICAL SYSTEM DEPENDENCIES" before changing!
    user_id = Column(String(128), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # Firebase UID

    # Core photo data
    title = Column(String(200))
    description = Column(Text)
    # NOTE: image_url and thumbnail_url generated dynamically from id + user_id

    # Location (optional)
    city_id = Column(Integer, ForeignKey("cities.id"))
    location_name = Column(String(200))  # Specific venue/studio name
    # Technical metadata (flexible for different cameras/equipment)
    camera_data = Column(JSONB)  # {make, model, lens, settings: {iso, aperture, shutter, focal_length}}

    # Content classification
    ai_tags = Column(JSONB)  # Auto-generated tags from AI processing
    user_tags = Column(ARRAY(Text))  # User-defined tags
    content_rating = Column(String(20), default='general')  # general, artistic_nude, mature

    # Collaboration and rights
    is_collaborative = Column(Boolean, default=False)
    model_release_status = Column(String(20), default='none')  # none, verbal, signed

    # Flexible expansion for future features
    extra_metadata = Column(JSONB, default={})  # Any future photo-related data

    # Visibility and status
    is_public = Column(Boolean, default=True)
    is_portfolio = Column(Boolean, default=False)  # Curated portfolio piece vs general feed
    status = Column(String(20), default='active')  # active, archived, deleted

    # Timestamps
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="photos")
    city = relationship("City", backref="photos")
    collaborators = relationship("PhotoCollaborator", back_populates="photo", cascade="all, delete-orphan")
    interactions = relationship("PhotoInteraction", back_populates="photo", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Photo(id='{self.id}', title='{self.title}', user='{self.user.handle if self.user else 'Unknown'}')>"

    @property
    def like_count(self):
        """Count of likes for this photo"""
        return len([i for i in self.interactions if i.interaction_type == 'like'])

    @property
    def collaborator_names(self):
        """Get list of collaborator display names"""
        return [c.display_name for c in self.collaborators]

    @property
    def photographer_name(self):
        """Get photographer name (either owner or collaborator marked as photographer)"""
        # Check if owner is photographer
        if self.user and self.user.is_photographer:
            return self.user.display_name
        
        # Check collaborators for photographer role
        photographer_collab = next(
            (c for c in self.collaborators if c.role == 'photographer'), 
            None
        )
        
        return photographer_collab.display_name if photographer_collab else self.user.display_name

    @property
    def location_display(self):
        """Return location string for display"""
        if self.location_name and self.city:
            return f"{self.location_name}, {self.city.name}"
        elif self.city:
            return f"{self.city.name}, {self.city.country}"
        elif self.location_name:
            return self.location_name
        else:
            return "Unknown"

    def add_collaborator(self, user_or_name, role="model"):
        """Add a collaborator to this photo"""
        from app.models.relationships import PhotoCollaborator
        
        if isinstance(user_or_name, str):
            # Text-only collaborator
            collaborator = PhotoCollaborator(
                photo_id=self.id,
                display_name=user_or_name,
                role=role
            )
        else:
            # User object collaborator
            collaborator = PhotoCollaborator(
                photo_id=self.id,
                user_id=user_or_name.id,
                display_name=user_or_name.display_name,
                handle=user_or_name.handle,
                role=role
            )        
        self.collaborators.append(collaborator)
        return collaborator

    def get_tags_combined(self):
        """Get all tags (AI + user) as a single list"""
        tags = []
        
        if self.ai_tags and isinstance(self.ai_tags, list):
            tags.extend(self.ai_tags)
        
        if self.user_tags:
            tags.extend(self.user_tags)
        
        return list(set(tags))  # Remove duplicates

    def is_liked_by(self, user_id):
        """Check if photo is liked by specific user"""
        return any(
            i.user_id == user_id and i.interaction_type == 'like' 
            for i in self.interactions
        )


# Pydantic models for API serialization
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class PhotoVisibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    FRIENDS_ONLY = "friends_only"


class PhotoCollaboratorResponse(BaseModel):
    """Collaborator information in photo response"""
    display_name: str
    handle: Optional[str] = None
    role: str = "model"
    user_id: Optional[str] = None


class PhotoResponse(BaseModel):
    """Photo response model for API"""
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: str
    thumbnail_url: Optional[str] = None
    photographer_name: str
    location_display: str
    user_tags: List[str] = []
    ai_tags: List[str] = []
    collaborators: List[PhotoCollaboratorResponse] = []
    like_count: int = 0
    is_liked: bool = False
    is_portfolio: bool = False
    upload_date: datetime
    camera_data: Optional[Dict] = None
    
    class Config:
        from_attributes = True


class CreatePhotoRequest(BaseModel):
    """Request model for creating new photo"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    image_url: str
    thumbnail_url: Optional[str] = None
    city_id: Optional[int] = None
    location_name: Optional[str] = Field(None, max_length=200)
    user_tags: List[str] = []
    collaborators: List[str] = []  # Display names or handles
    is_collaborative: bool = False
    model_release_status: str = "none"
    content_rating: str = "general"
    is_public: bool = True
    is_portfolio: bool = False
    camera_data: Optional[Dict] = None
    
    model_config = {"protected_namespaces": ()}


class UpdatePhotoRequest(BaseModel):
    """Request model for updating photo"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    city_id: Optional[int] = None
    location_name: Optional[str] = Field(None, max_length=200)
    user_tags: Optional[List[str]] = None
    content_rating: Optional[str] = None
    is_public: Optional[bool] = None
    is_portfolio: Optional[bool] = None
    
    model_config = {"protected_namespaces": ()}


class PhotoSearchQuery(BaseModel):
    """Search parameters for photos"""
    query: Optional[str] = None
    user_id: Optional[str] = None
    city_id: Optional[int] = None
    tags: Optional[List[str]] = None
    content_rating: Optional[str] = None
    is_portfolio_only: bool = False
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class PhotoListResponse(BaseModel):
    """Response model for photo lists"""
    photos: List[PhotoResponse]
    total_count: int
    page: int
    limit: int
    has_more: bool

class PhotoUrls(BaseModel):
    """Photo URL data"""
    image_url: str
    thumbnail_url: Optional[str] = None
    preview_url: Optional[str] = None


class PhotoMetadata(BaseModel):
    """Photo metadata extracted from image"""
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: int
    mime_type: Optional[str] = None
    color_space: Optional[str] = None
    orientation: int = 1
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    lens_model: Optional[str] = None
    focal_length: Optional[float] = None
    aperture: Optional[float] = None
    shutter_speed: Optional[str] = None
    iso: Optional[int] = None
    flash: Optional[bool] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    date_taken: Optional[datetime] = None

class PhotoEngagement(BaseModel):
    """Photo engagement metrics"""
    likes_count: int = 0
    comments_count: int = 0
    views_count: int = 0
    shares_count: int = 0


class PhotoStatus(str, Enum):
    """Photo processing status"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"