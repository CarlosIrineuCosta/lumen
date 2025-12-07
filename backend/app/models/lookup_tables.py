"""
Lookup tables for Lumen Photography Platform
Contains reference data: user types, specialties, cities
"""

from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, ARRAY, Text, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base


class UserType(Base):
    """User types: Photographer, Model"""
    __tablename__ = "user_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String(20), unique=True, nullable=False)
    display_name = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Specialty(Base):
    """Photography specialties: Art Nude, Portrait, Dance, etc."""
    __tablename__ = "specialties"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    applicable_to = Column(ARRAY(Text), default=['photographer', 'model'])
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class City(Base):
    """Geopolitically filtered cities for art photography networking"""
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    region = Column(String(100))
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    population = Column(Integer)
    is_capital = Column(Boolean, default=False)
    tier = Column(Integer, default=1)  # 1=liberal, 2=emerging, 3=selective, 4=very selective
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        {'schema': None},  # Ensure we're using default schema
    )