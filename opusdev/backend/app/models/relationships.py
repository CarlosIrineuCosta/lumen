"""
Relationship models for Lumen Photography Platform
Handles user specialties, photo collaborators, interactions, and networking
"""

from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database.connection import Base


class UserSpecialty(Base):
    """Many-to-many relationship between users and photography specialties"""
    __tablename__ = "user_specialties"

    user_id = Column(String(128), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)  # Firebase UID
    specialty_id = Column(Integer, ForeignKey("specialties.id"), primary_key=True)
    is_primary = Column(Boolean, default=False)  # Mark main specialty
    experience_level = Column(String(20), default='intermediate')  # beginner, intermediate, advanced, professional
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="specialties")
    specialty = relationship("Specialty", backref="user_specialties")

    def __repr__(self):
        return f"<UserSpecialty(user='{self.user.handle if self.user else 'Unknown'}', specialty='{self.specialty.name if self.specialty else 'Unknown'}')>"

class PhotoCollaborator(Base):
    """Photo collaborators with @ tagging support"""
    __tablename__ = "photo_collaborators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    photo_id = Column(UUID(as_uuid=True), ForeignKey("photos.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(128), ForeignKey("users.id", ondelete="SET NULL"))  # Firebase UID, NULL if user deleted

    # Always store display info (survives user deletion)
    display_name = Column(String(100), nullable=False)
    handle = Column(String(50))  # For linking if user exists
    role = Column(String(50))  # photographer, model, mua, stylist, etc

    # Flexible role data
    role_data = Column(JSONB, default={})  # {credit_text, collaboration_type, etc}

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    photo = relationship("Photo", back_populates="collaborators")
    user = relationship("User", backref="photo_collaborations")

    def __repr__(self):
        return f"<PhotoCollaborator(photo='{self.photo_id}', display_name='{self.display_name}', role='{self.role}')>"

class PhotoInteraction(Base):
    """Track user interactions with photos (likes, saves, etc)"""
    __tablename__ = "photo_interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    photo_id = Column(UUID(as_uuid=True), ForeignKey("photos.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(128), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # Firebase UID
    interaction_type = Column(String(20), nullable=False)  # like, save, report
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Ensure unique interaction per user/photo/type
    __table_args__ = (
        UniqueConstraint('photo_id', 'user_id', 'interaction_type', name='uix_photo_user_interaction'),
    )

    # Relationships
    photo = relationship("Photo", back_populates="interactions")
    user = relationship("User", backref="photo_interactions")

    def __repr__(self):
        return f"<PhotoInteraction(photo='{self.photo_id}', user='{self.user_id}', type='{self.interaction_type}')>"


class UserConnection(Base):
    """User-to-user connections for networking"""
    __tablename__ = "user_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requester_id = Column(String(128), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # Firebase UID
    target_id = Column(String(128), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # Firebase UID
    status = Column(String(20), default='pending')  # pending, accepted, rejected, blocked
    connection_type = Column(String(50))  # collaboration, networking, friends
    message = Column(Text)  # Optional connection request message
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Ensure unique connection between two users
    __table_args__ = (
        UniqueConstraint('requester_id', 'target_id', name='uix_requester_target'),
    )

    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], back_populates="sent_connections")
    target = relationship("User", foreign_keys=[target_id], back_populates="received_connections")

    def __repr__(self):
        return f"<UserConnection(requester='{self.requester_id}', target='{self.target_id}', status='{self.status}')>"


# Pydantic models for API serialization
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserSpecialtyResponse(BaseModel):
    """User specialty for API responses"""
    specialty_name: str
    specialty_id: int
    is_primary: bool
    experience_level: str
    
    class Config:
        from_attributes = True


class ConnectionRequest(BaseModel):
    """Create connection request"""
    target_user_id: str  # Firebase UID
    connection_type: str = "networking"
    message: Optional[str] = None


class ConnectionResponse(BaseModel):
    """Connection for API responses"""
    id: str
    requester_id: str  # Firebase UID
    target_id: str  # Firebase UID
    requester_handle: Optional[str] = None
    target_handle: Optional[str] = None
    requester_display_name: Optional[str] = None
    target_display_name: Optional[str] = None
    status: str
    connection_type: Optional[str] = None
    message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True