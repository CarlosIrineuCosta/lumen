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

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
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
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))  # NULL if user deleted

    # Always store display info (survives user deletion)
    display_name = Column(String(100), nullable=False)
    handle = Column(String(50))  # For linking if user exists
    role = Column(String(50))  # photographer, model, mua, stylist, etc

    # Flexible role data
    role_data = Column(JSONB, default={})  # {credit_text, collaboration_type, etc}

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    photo = relationship("Photo", back_populates="collaborators")
    user = relationship("User", backref="collaborations")

    def __repr__(self):
        return f"<PhotoCollaborator(photo='{self.photo_id}', name='{self.display_name}', role='{self.role}')>"

    @property
    def is_linked_user(self):
        """Check if this collaborator is a registered user"""
        return self.user_id is not None

    @property
    def profile_url(self):
        """Get profile URL if linked user, otherwise None"""
        return f"/users/{self.handle}" if self.handle else None


class PhotoInteraction(Base):
    """Photo interactions: likes, saves, reports, etc."""
    __tablename__ = "photo_interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    photo_id = Column(UUID(as_uuid=True), ForeignKey("photos.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    interaction_type = Column(String(20), nullable=False)  # like, save, report, etc
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    photo = relationship("Photo", back_populates="interactions")
    user = relationship("User", backref="photo_interactions")

    # Unique constraint to prevent duplicate interactions
    __table_args__ = (
        UniqueConstraint('photo_id', 'user_id', 'interaction_type', name='unique_photo_user_interaction'),
    )

    def __repr__(self):
        return f"<PhotoInteraction(photo='{self.photo_id}', user='{self.user.handle if self.user else 'Unknown'}', type='{self.interaction_type}')>"


class UserConnection(Base):
    """Professional networking connections between users"""
    __tablename__ = "user_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requester_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default='pending')  # pending, accepted, declined, blocked
    message = Column(Text)  # Initial connection message
    connection_data = Column(JSONB, default={})  # {collaboration_interest, project_types, etc}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], back_populates="sent_connections")
    target = relationship("User", foreign_keys=[target_id], back_populates="received_connections")

    # Unique constraint to prevent duplicate connection requests
    __table_args__ = (
        UniqueConstraint('requester_id', 'target_id', name='unique_user_connection'),
    )

    def __repr__(self):
        return f"<UserConnection(requester='{self.requester.handle if self.requester else 'Unknown'}', target='{self.target.handle if self.target else 'Unknown'}', status='{self.status}')>"

    @property
    def is_accepted(self):
        """Check if connection is accepted"""
        return self.status == 'accepted'

    @property
    def is_pending(self):
        """Check if connection is pending"""
        return self.status == 'pending'

    @property
    def is_blocked(self):
        """Check if connection is blocked"""
        return self.status == 'blocked'

    def accept(self):
        """Accept the connection request"""
        self.status = 'accepted'
        self.updated_at = func.now()

    def decline(self):
        """Decline the connection request"""
        self.status = 'declined'
        self.updated_at = func.now()

    def block(self):
        """Block the connection (and user)"""
        self.status = 'blocked'
        self.updated_at = func.now()

    @property
    def collaboration_interests(self):
        """Get collaboration interests from connection data"""
        return self.connection_data.get('collaboration_interest', [])

    @property
    def project_types(self):
        """Get interested project types from connection data"""
        return self.connection_data.get('project_types', [])