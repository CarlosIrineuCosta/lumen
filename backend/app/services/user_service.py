"""Enhanced User Service with Auto-Registration"""

import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import flag_modified

from ..database.connection import SessionLocal
from ..models.user import User
from ..auth_middleware import AuthUser
from .dtos import UserProfileUpdateDTO

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
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "profile_completion": self._calculate_profile_completion(user),
            "needs_onboarding": (user.profile_data or {}).get("needs_onboarding", False),
            
            # Model-specific fields (required in UserProfileFull)
            "gender": user.gender,
            "age": user.age,
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg,
            
            # Legal compliance fields
            "birth_date": user.birth_date.isoformat() if user.birth_date else None,
            "country_code": user.country_code,
            "tos_accepted_at": user.tos_accepted_at,
            
            # Public profile fields
            "portfolio_count": self._get_user_photo_count(user.id),
            "is_verified": False,
            "open_for_work": True,
            "available_for_travel": False,
            "location_preferences": [],
            "specializes_in": [],
            "website": user.website
        }
        
        # Add profile data fields
        profile_data = user.profile_data or {}
        profile.update({
            "artistic_statement": profile_data.get("artistic_statement") or None,
            "tagline": profile_data.get("tagline") or None,
            "mission_statement": profile_data.get("mission_statement") or None,
            "photography_styles": profile_data.get("photography_styles") or [],
            "experience_level": profile_data.get("experience_level") or None,
            "experience_years": profile_data.get("experience_years") or None,
            "camera_gear": profile_data.get("camera_gear") or [],
            "modeling_types": profile_data.get("modeling_types") or [],
            "comfortable_with": profile_data.get("comfortable_with") or [],
            "special_skills": profile_data.get("special_skills") or [],
            "studio_access": profile_data.get("studio_access") or None,
            "rates": profile_data.get("rates") or None,
            "social_links": profile_data.get("social_links") or None,
            "contact_preferences": profile_data.get("contact_preferences") or None,
            "travel_notes": profile_data.get("travel_notes") or None
        })
        
        # Add availability data
        profile["availability_data"] = user.availability_data or None
        
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
    
    def _get_user_photo_count(self, user_id: str) -> int:
        """Get count of user's photos"""
        from ..models.photo import Photo
        from ..database.connection import SessionLocal
        
        db = SessionLocal()
        try:
            count = db.query(Photo).filter(Photo.user_id == user_id).count()
            return count
        except Exception as e:
            logger.error(f"Error getting photo count for user {user_id}: {str(e)}")
            return 0
        finally:
            db.close()
    
    async def update_user_profile(self, uid: str, update_dto: UserProfileUpdateDTO) -> Optional[dict]:
        """Update user profile with validation"""
        logger.info(f"🔍 Starting profile update for UID: {uid}")
        logger.info(f"📝 DTO received: {update_dto.dict(exclude_unset=True)}")
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == uid).first()
            logger.info(f"👤 User found: {user is not None}")
            if user:
                logger.info(f"📊 Current user data - display_name: '{user.display_name}', handle: '{user.handle}', bio: '{user.bio}'")
            
            if not user:
                logger.warning(f"❌ No user found with UID: {uid}")
                return None
            
            update_data = update_dto.dict(exclude_unset=True)

            # Update basic fields
            basic_fields = ['display_name', 'handle', 'bio', 'website']
            for field in basic_fields:
                if field in update_data:
                    old_value = getattr(user, field)
                    new_value = update_data[field]
                    setattr(user, field, new_value)
                    logger.info(f"🔄 Updated {field}: '{old_value}' → '{new_value}'")
            
            # Update profile_data JSON fields with proper JSONB handling
            if not user.profile_data:
                user.profile_data = {}
                logger.info("🆕 Initialized empty profile_data")
            
            profile_data_updated = False
            profile_fields = ['artistic_statement', 'tagline', 'mission_statement',
                            'photography_styles', 'experience_level', 'experience_years']
            for field in profile_fields:
                if field in update_data:
                    old_value = user.profile_data.get(field)
                    user.profile_data[field] = update_data[field]
                    profile_data_updated = True
                    logger.info(f"🔄 Updated profile_data.{field}: '{old_value}' → '{update_data[field]}'")
            
            # Mark profile as complete if it was onboarding
            if user.profile_data.get("needs_onboarding"):
                user.profile_data["needs_onboarding"] = False
                user.profile_data["profile_complete"] = True
                profile_data_updated = True
                logger.info("✅ Marked profile as complete")
            
            # Critical: Flag JSONB field as modified for SQLAlchemy
            if profile_data_updated:
                flag_modified(user, 'profile_data')
                logger.info("🏁 Flagged profile_data as modified for SQLAlchemy")
            
            # Update model-specific fields
            if user.primary_user_type == 2:  # Model
                model_fields = ['gender', 'age', 'height_cm', 'weight_kg']
                for field in model_fields:
                    if field in update_data:
                        setattr(user, field, update_data[field])
            
            # Update availability
            if 'availability_data' in update_data:
                user.availability_data = update_data['availability_data']
            
            # Update privacy settings
            if 'privacy_settings' in update_data:
                user.privacy_settings = update_data['privacy_settings']
            
            user.updated_at = datetime.utcnow()
            logger.info(f"⏰ Updated timestamp to: {user.updated_at}")
            
            # Commit changes with verification
            logger.info("💾 Committing database changes...")
            db.commit()
            logger.info("✅ Database commit successful")
            
            # Refresh user object from database
            db.refresh(user)
            logger.info("🔄 Refreshed user object from database")
            
            # Verify the changes were persisted
            logger.info(f"📊 Final user data - display_name: '{user.display_name}', handle: '{user.handle}', bio: '{user.bio}'")
            logger.info(f"🎯 Profile update completed successfully for UID: {uid}")
            
            return self._user_to_profile_dict(user, include_private=True)
            
        except Exception as e:
            logger.error(f"💥 Exception occurred during profile update for {uid}")
            logger.error(f"📋 Update data that failed: {update_dto.dict()}")
            logger.error(f"🔥 Error details: {str(e)}")
            logger.error(f"📝 Exception type: {type(e).__name__}")
            db.rollback()
            logger.info("🔄 Database rollback completed")
            raise
        finally:
            db.close()
            logger.info("🔐 Database connection closed")
    
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

    async def get_user_by_handle(self, handle: str):
        """Get user's public profile by handle"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.handle == handle).first()
            if not user:
                return None
            return self._user_to_profile_dict(user, include_private=False)
        except Exception as e:
            logger.error(f"Failed to get user by handle {handle}: {str(e)}")
            raise
        finally:
            db.close()

    async def get_public_profile(self, user_id: str):
        """Get user's public profile by ID"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            return self._user_to_profile_dict(user, include_private=False)
        except Exception as e:
            logger.error(f"Failed to get public profile for {user_id}: {str(e)}")
            raise
        finally:
            db.close()

    async def get_user_photos(self, user_id: str, page: int = 1, limit: int = 20):
        """Get user's photos with pagination"""
        from ..models.photo import Photo
        from sqlalchemy import desc
        
        db = SessionLocal()
        try:
            offset = (page - 1) * limit
            
            # Query user's photos
            photos_query = db.query(Photo).filter(
                Photo.user_id == user_id
            ).order_by(desc(Photo.upload_date))
            
            # Get total count for pagination
            total_count = photos_query.count()
            
            # Apply pagination
            photos = photos_query.offset(offset).limit(limit).all()
            
            # Convert to response format
            photo_list = []
            for photo in photos:
                photo_data = {
                    "id": str(photo.id),
                    "title": photo.title,
                    "description": photo.description,
                    "image_url": photo.image_url,
                    "thumbnail_url": photo.thumbnail_url,
                    "upload_date": photo.upload_date.isoformat() if photo.upload_date else None,
                    "like_count": photo.like_count,  # This is a property that counts interactions
                    "user_tags": photo.user_tags or [],
                    "ai_tags": photo.ai_tags or {},
                    "location_name": photo.location_name,
                    "camera_data": photo.camera_data or {},
                    "photographer_name": photo.photographer_name,
                    "location_display": photo.location_display,
                }
                photo_list.append(photo_data)
            
            return {
                "photos": photo_list,
                "total_count": total_count,
                "page": page,
                "limit": limit,
                "has_more": (offset + limit) < total_count
            }
            
        except Exception as e:
            logger.error(f"Failed to get photos for user {user_id}: {str(e)}")
            raise
        finally:
            db.close()

    async def get_user_stats(self, user_id: str):
        """Get user's statistics (photo count, likes, etc.)"""
        from ..models.photo import Photo
        from sqlalchemy import func
        
        db = SessionLocal()
        try:
            # Count photos
            photo_count = db.query(Photo).filter(Photo.user_id == user_id).count()
            
            # Count total likes across all user's photos
            # Since like_count is a property that counts interactions, we need to count them directly
            total_likes = 0
            photos = db.query(Photo).filter(Photo.user_id == user_id).all()
            for photo in photos:
                total_likes += photo.like_count
            
            # Get user's join date
            user = db.query(User).filter(User.id == user_id).first()
            join_date = user.created_at if user else None
            
            return {
                "user_id": user_id,
                "photo_count": photo_count,
                "total_likes": total_likes,
                "join_date": join_date.isoformat() if join_date else None,
                # TODO: Add follower/following counts when relationships are implemented
                "follower_count": 0,
                "following_count": 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats for user {user_id}: {str(e)}")
            raise
        finally:
            db.close()
