"""Enhanced User Service with Auto-Registration"""

import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from ..database.connection import SessionLocal
from ..models.user import User
from ..auth_middleware import AuthUser

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self):
        self.storage_base_url = os.getenv('STORAGE_BASE_URL', 'http://100.106.201.33:8080/storage')
    
    async def get_or_create_user_profile(self, firebase_user: AuthUser, include_private: bool = True):
        """Get existing profile or create a minimal one automatically"""
        db = SessionLocal()
        try:
            # Check if user exists
            user = db.query(User).filter(User.id == firebase_user.uid).first()
            
            if not user:
                logger.info(f"Auto-creating profile for new user: {firebase_user.uid}")
                
                # Auto-create minimal profile
                user = User(
                    id=firebase_user.uid,
                    email=firebase_user.email,
                    handle=firebase_user.email.split('@')[0],  # Default handle from email
                    display_name=firebase_user.name or firebase_user.email.split('@')[0],
                    city_id=1,  # Default city (should be "Unknown" in cities table)
                    primary_user_type=1,  # Default to photographer
                    profile_image_url=firebase_user.picture,
                    bio="",
                    profile_data={
                        "profile_complete": False,
                        "needs_onboarding": True,
                        "photography_styles": [],
                        "experience_level": "beginner"
                    },
                    availability_data={
                        "open_for_work": False,
                        "available_for_collaborations": False
                    },
                    privacy_settings={
                        "show_city": False,
                        "show_country": True,
                        "show_age": False
                    }
                )
                
                db.add(user)
                db.commit()
                db.refresh(user)
                logger.info(f"Successfully created profile for user: {firebase_user.uid}")
            
            # Return the profile
            return self._user_to_profile_dict(user, include_private)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in get_or_create_user_profile: {str(e)}")
            raise
        finally:
            db.close()
    
    def _user_to_profile_dict(self, user: User, include_private: bool = True) -> dict:
        """Convert User model to profile dictionary"""
        profile = {
            "id": user.id,
            "handle": user.handle,
            "display_name": user.display_name,
            "email": user.email if include_private else None,
            "bio": user.bio or "",
            "profile_image_url": user.profile_image_url,
            "user_type": self._get_user_type_name(user.primary_user_type),
            "city_id": user.city_id,
            "city_name": user.city.name if user.city else "Unknown",
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "profile_completion": self._calculate_profile_completion(user),
            "needs_onboarding": user.profile_data.get("needs_onboarding", False)
        }
        
        # Add profile data fields
        if user.profile_data:
            profile.update({
                "artistic_statement": user.profile_data.get("artistic_statement", ""),
                "tagline": user.profile_data.get("tagline", ""),
                "mission_statement": user.profile_data.get("mission_statement", ""),
                "photography_styles": user.profile_data.get("photography_styles", []),
                "experience_level": user.profile_data.get("experience_level", "beginner"),
                "experience_years": user.profile_data.get("experience_years")
            })
        
        # Add model-specific fields
        if user.primary_user_type == 2:  # Model
            profile["model_details"] = {
                "gender": user.gender,
                "age": user.age,
                "height": f"{user.height_cm}cm" if user.height_cm else None,
                "weight": f"{user.weight_kg}kg" if user.weight_kg else None
            }
        
        # Add availability data
        profile["availability_data"] = user.availability_data or {}
        
        # Add privacy settings if private
        if include_private:
            profile["privacy_settings"] = user.privacy_settings or {}
        
        return profile
    
    def _get_user_type_name(self, type_id: int) -> str:
        """Map user type ID to name"""
        type_map = {
            1: "photographer",
            2: "model", 
            3: "studio",
            4: "makeup_artist",
            5: "stylist"
        }
        return type_map.get(type_id, "photographer")
    
    def _calculate_profile_completion(self, user: User) -> int:
        """Calculate profile completion percentage"""
        required_fields = ['display_name', 'handle', 'bio', 'city_id']
        optional_fields = ['artistic_statement', 'tagline', 'mission_statement', 
                          'photography_styles', 'experience_level']
        
        completed = 0
        total = len(required_fields) + len(optional_fields)
        
        # Check required fields
        for field in required_fields:
            if getattr(user, field, None):
                completed += 1
        
        # Check optional fields in profile_data
        if user.profile_data:
            for field in optional_fields:
                if user.profile_data.get(field):
                    completed += 1
        
        return int((completed / total) * 100)
    
    async def update_user_profile(self, uid: str, update_data: dict) -> Optional[dict]:
        """Update user profile with validation"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == uid).first()
            if not user:
                return None
            
            # Update basic fields
            basic_fields = ['display_name', 'handle', 'bio', 'website']
            for field in basic_fields:
                if field in update_data and update_data[field] is not None:
                    setattr(user, field, update_data[field])
            
            # Update profile_data JSON fields
            if not user.profile_data:
                user.profile_data = {}
            
            profile_fields = ['artistic_statement', 'tagline', 'mission_statement',
                            'photography_styles', 'experience_level', 'experience_years']
            for field in profile_fields:
                if field in update_data:
                    user.profile_data[field] = update_data[field]
            
            # Mark profile as complete if it was onboarding
            if user.profile_data.get("needs_onboarding"):
                user.profile_data["needs_onboarding"] = False
                user.profile_data["profile_complete"] = True
            
            # Update model-specific fields
            if user.primary_user_type == 2:  # Model
                model_fields = ['gender', 'age', 'height_cm', 'weight_kg']
                for field in model_fields:
                    if field in update_data and update_data[field] is not None:
                        setattr(user, field, update_data[field])
            
            # Update availability
            if 'availability_data' in update_data:
                user.availability_data = update_data['availability_data']
            
            # Update privacy settings
            if 'privacy_settings' in update_data:
                user.privacy_settings = update_data['privacy_settings']
            
            user.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(user)
            
            return self._user_to_profile_dict(user, include_private=True)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating profile for {uid}: {str(e)}")
            raise
        finally:
            db.close()
    
    async def update_last_login(self, uid: str):
        """Update user's last active timestamp"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == uid).first()
            if user:
                user.last_active = datetime.utcnow()
                db.commit()
        finally:
            db.close()
    
    async def user_exists(self, uid: str) -> bool:
        """Check if user profile exists"""
        db = SessionLocal()
        try:
            return db.query(User).filter(User.id == uid).first() is not None
        finally:
            db.close()