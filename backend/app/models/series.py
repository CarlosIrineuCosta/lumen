"""
Series model for Lumen Photography Platform
Allows photographers to organize photos into collections
"""

from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database.connection import Base


class Series(Base):
    """Series/Collection model for organizing photos"""
    __tablename__ = "series"

    # Primary key and ownership
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(128), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Series metadata
    title = Column(String(200), nullable=False)
    description = Column(Text)

    # Cover photo and statistics
    cover_photo_id = Column(UUID(as_uuid=True), ForeignKey("photos.id", ondelete="SET NULL"))
    photo_count = Column(Integer, default=0)  # Denormalized for performance

    # Privacy settings
    is_public = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="series")
    photos = relationship("Photo", back_populates="series", foreign_keys="Photo.series_id")
    cover_photo = relationship("Photo", foreign_keys=[cover_photo_id], post_update=True)