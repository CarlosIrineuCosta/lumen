"""User service for managing user profiles in Firestore"""

import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from firebase_admin import firestore
from ..models.user import (
    UserProfileFull, UserProfilePublic, UserProfilePrivate,
    CreateUserRequest, UpdateUserRequest, UserSearchQuery,
    UserLocation, UserContact, UserPreferences, UserType, PhotographyStyle
)
from ..auth_middleware import AuthUser

class UserService:
    def __init__(self):
        self.db = firestore.client()
        self.users_collection = self.db.collection('users')
    
    async def create_user_profile(self, firebase_user: AuthUser, request: CreateUserRequest) -> UserProfileFull:
        """Create a new user profile in Firestore"""
        
        # Create location object
        location = UserLocation(
            country=request.country,
            city=request.city,
            zip_code=request.zip_code,
            willing_to_travel=request.willing_to_travel
        ) if any([request.country, request.city, request.zip_code]) else None
        
        # Create contact information
        contact = UserContact(
            primary_email=firebase_user.email,
            work_email=request.work_email,
            phone=request.phone,
            website=request.website,
            instagram_handle=request.instagram_handle
        )
        
        # Create preferences
        preferences = UserPreferences(
            profile_visibility=request.profile_visibility,
            allow_messages=request.allow_messages,
            preferred_language=request.preferred_language
        )
        
        # Create public profile
        public_profile = UserProfilePublic(
            uid=firebase_user.uid,
            display_name=request.display_name,
            bio=request.bio,
            profile_picture_url=firebase_user.picture,
            user_type=request.user_type,
            photography_styles=request.photography_styles,
            location=location,
            portfolio_url=request.website,
            instagram_handle=request.instagram_handle,
            member_since=datetime.utcnow(),
            photo_count=0,
            follower_count=0,
            following_count=0,
            verified=firebase_user.email_verified
        )
        
        # Create private profile
        private_profile = UserProfilePrivate(
            contact=contact,
            preferences=preferences
        )
        
        # Create full profile
        now = datetime.utcnow()
        user_profile = UserProfileFull(
            uid=firebase_user.uid,
            public_profile=public_profile,
            private_profile=private_profile,
            firebase_data={
                "email": firebase_user.email,
                "email_verified": firebase_user.email_verified,
                "name": firebase_user.name,
                "picture": firebase_user.picture
            },
            metadata=request.metadata,
            created_at=now,
            updated_at=now,
            last_login=now
        )
        
        # Save to Firestore
        doc_ref = self.users_collection.document(firebase_user.uid)
        doc_ref.set(user_profile.dict())
        
        return user_profile
    
    async def get_user_profile(self, uid: str, include_private: bool = False) -> Optional[UserProfileFull]:
        """Get user profile by UID"""
        doc_ref = self.users_collection.document(uid)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        profile = UserProfileFull(**data)
        
        # Remove private data if not authorized
        if not include_private:
            profile.private_profile = None
        
        return profile
    
    async def get_public_profile(self, uid: str) -> Optional[UserProfilePublic]:
        """Get only public profile data"""
        profile = await self.get_user_profile(uid, include_private=False)
        return profile.public_profile if profile else None
    
    async def update_user_profile(self, uid: str, request: UpdateUserRequest) -> Optional[UserProfileFull]:
        """Update user profile"""
        doc_ref = self.users_collection.document(uid)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        # Get current data
        current_data = doc.to_dict()
        current_profile = UserProfileFull(**current_data)
        
        # Update fields
        updates = {"updated_at": datetime.utcnow()}
        
        if request.display_name:
            updates["public_profile.display_name"] = request.display_name
        
        if request.bio is not None:
            updates["public_profile.bio"] = request.bio
        
        if request.user_type:
            updates["public_profile.user_type"] = request.user_type.value
        
        if request.photography_styles is not None:
            updates["public_profile.photography_styles"] = [style.value for style in request.photography_styles]
        
        if request.location:
            updates["public_profile.location"] = request.location.dict()
        
        # Update contact info
        if request.work_email is not None:
            updates["private_profile.contact.work_email"] = request.work_email
        
        if request.phone is not None:
            updates["private_profile.contact.phone"] = request.phone
        
        if request.website is not None:
            updates["private_profile.contact.website"] = request.website
            updates["public_profile.portfolio_url"] = request.website
        
        if request.instagram_handle is not None:
            updates["private_profile.contact.instagram_handle"] = request.instagram_handle
            updates["public_profile.instagram_handle"] = request.instagram_handle
        
        # Update preferences
        if request.preferences:
            updates["private_profile.preferences"] = request.preferences.dict()
        
        # Update metadata
        if request.metadata is not None:
            updates["metadata"] = {**current_profile.metadata, **request.metadata}
        
        # Apply updates
        doc_ref.update(updates)
        
        # Return updated profile
        return await self.get_user_profile(uid, include_private=True)
    
    async def update_last_login(self, uid: str):
        """Update user's last login timestamp"""
        doc_ref = self.users_collection.document(uid)
        doc_ref.update({"last_login": datetime.utcnow()})
    
    async def search_users(self, query: UserSearchQuery) -> List[UserProfilePublic]:
        """Search for users based on criteria"""
        collection_ref = self.users_collection
        
        # Start with base query
        firestore_query = collection_ref
        
        # Apply filters
        if query.user_type:
            firestore_query = firestore_query.where("public_profile.user_type", "==", query.user_type.value)
        
        if query.location_country:
            firestore_query = firestore_query.where("public_profile.location.country", "==", query.location_country)
        
        if query.location_city:
            firestore_query = firestore_query.where("public_profile.location.city", "==", query.location_city)
        
        if query.willing_to_travel is not None:
            firestore_query = firestore_query.where("public_profile.location.willing_to_travel", "==", query.willing_to_travel)
        
        if query.verified_only:
            firestore_query = firestore_query.where("public_profile.verified", "==", True)
        
        # Apply pagination
        firestore_query = firestore_query.offset(query.offset).limit(query.limit)
        
        # Execute query
        results = firestore_query.get()
        
        profiles = []
        for doc in results:
            data = doc.to_dict()
            if data and "public_profile" in data:
                profiles.append(UserProfilePublic(**data["public_profile"]))
        
        return profiles
    
    async def user_exists(self, uid: str) -> bool:
        """Check if user profile exists"""
        doc_ref = self.users_collection.document(uid)
        doc = doc_ref.get()
        return doc.exists
    
    async def delete_user_profile(self, uid: str) -> bool:
        """Delete user profile (soft delete by setting deleted flag)"""
        doc_ref = self.users_collection.document(uid)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        # Soft delete
        doc_ref.update({
            "deleted": True,
            "deleted_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        return True
    
    async def get_user_stats(self, uid: str) -> Dict[str, Any]:
        """Get user statistics"""
        profile = await self.get_user_profile(uid, include_private=False)
        
        if not profile:
            return {}
        
        return {
            "user_id": uid,
            "total_photos": profile.public_profile.photo_count,
            "total_followers": profile.public_profile.follower_count,
            "total_following": profile.public_profile.following_count,
            "account_created": profile.created_at.isoformat(),
            "last_active": profile.last_login.isoformat() if profile.last_login else None,
            "verified": profile.public_profile.verified,
            "user_type": profile.public_profile.user_type.value if profile.public_profile.user_type else None
        }