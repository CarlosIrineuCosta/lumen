"""
Data Transfer Objects (DTOs) for the service layer.

These models define the explicit data contracts for operations within the service layer,
making the code more robust, predictable, and easier to test.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict

class UserProfileUpdateDTO(BaseModel):
    """Data contract for updating a user profile."""
    display_name: Optional[str] = None
    handle: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    artistic_statement: Optional[str] = None
    tagline: Optional[str] = None
    mission_statement: Optional[str] = None
    photography_styles: Optional[List[str]] = None
    experience_level: Optional[str] = None
    experience_years: Optional[int] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    availability_data: Optional[Dict] = None
    privacy_settings: Optional[Dict] = None
