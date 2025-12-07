"""
Complete the user_service.py migration to Firebase UID as primary key
This script completes the service file with all necessary methods
"""

# Read the old file for reference
old_content = '''
            if request.city_id:
                user.city_id = request.city_id
            if request.profile_image_url:
                user.profile_image_url = request.profile_image_url
            if request.website:
                user.website = request.website
            
            # Update model-specific fields
            if request.gender:
                user.gender = request.gender
            if request.age:
                user.age = request.age
            if request.height_cm:
                user.height_cm = request.height_cm
            if request.weight_kg:
                user.weight_kg = request.weight_kg
            
            # Update profile_data (JSONB)
            profile_data = user.profile_data or {}
            if request.artistic_statement is not None:
                profile_data["artistic_statement"] = request.artistic_statement
            if request.tagline is not None:
                profile_data["tagline"] = request.tagline
            if request.mission_statement is not None:
                profile_data["mission_statement"] = request.mission_statement
            if request.photography_styles is not None:
                profile_data["photography_styles"] = [style.value for style in request.photography_styles]
            if request.experience_level is not None:
                profile_data["experience_level"] = request.experience_level.value
            if request.experience_years is not None:
                profile_data["experience_years"] = request.experience_years
            if request.camera_gear is not None:
                profile_data["camera_gear"] = request.camera_gear
            if request.specializes_in is not None:
                profile_data["specializes_in"] = request.specializes_in
            if request.studio_access is not None:
                profile_data["studio_access"] = request.studio_access
            if request.rates is not None:
                profile_data["rates"] = request.rates
            if request.modeling_types is not None:
                profile_data["modeling_types"] = request.modeling_types
            if request.comfortable_with is not None:
                profile_data["comfortable_with"] = request.comfortable_with
            if request.special_skills is not None:
                profile_data["special_skills"] = request.special_skills
            if request.studio_size_sqft is not None:
                profile_data["studio_size_sqft"] = request.studio_size_sqft
            if request.included_equipment is not None:
                profile_data["included_equipment"] = request.included_equipment
            if request.hourly_rate is not None:
                profile_data["hourly_rate"] = request.hourly_rate
            if request.social_links is not None:
                profile_data["social_links"] = request.social_links
            if request.contact_preferences is not None:
                profile_data["contact_preferences"] = request.contact_preferences.dict() if hasattr(request.contact_preferences, 'dict') else request.contact_preferences
            
            user.profile_data = profile_data
            
            # Update availability_data (JSONB)
            if request.availability_data is not None:
                availability_data = user.availability_data or {}
                if hasattr(request.availability_data, 'dict'):
                    availability_data.update(request.availability_data.dict())
                else:
                    availability_data.update(request.availability_data)
                user.availability_data = availability_data
            
            # Update privacy settings
            if request.privacy_settings is not None:
                user.privacy_settings = request.privacy_settings
            
            user.updated_at = datetime.utcnow()
            
            db.commit()
            return await self.get_user_profile(uid, include_private=True)
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to update user profile: {str(e)}")
        finally:
            db.close()
    
    async def update_last_login(self, uid: str):
        """Update user's last login timestamp"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == uid).first()
            if user:
                user.last_active = datetime.utcnow()
                db.commit()
        finally:
            db.close()
    
    async def search_users(self, query: UserSearchQuery) -> List[UserProfilePublic]:
        """Search for users based on criteria"""
        db = SessionLocal()
        try:
            db_query = db.query(User).options(
                joinedload(User.city),
                joinedload(User.user_type)
            )
            
            # Apply filters
            if query.user_type:
                # TODO: Join with user_types table to filter by type name
                pass
            
            if query.city_id:
                db_query = db_query.filter(User.city_id == query.city_id)
            
            if query.photography_styles:
                # Filter by photography styles in JSONB
                style_values = [style.value for style in query.photography_styles]
                for style in style_values:
                    db_query = db_query.filter(
                        User.profile_data["photography_styles"].astext.contains(style)
                    )
            
            # Apply pagination
            offset = (query.page - 1) * query.limit
            db_query = db_query.offset(offset).limit(query.limit)
            
            users = db_query.all()
            
            # Convert to public profiles
            profiles = []
            for user in users:
                profiles.append(UserProfilePublic(
                    id=user.id,  # This is the Firebase UID
                    handle=user.handle,
                    display_name=user.display_name,
                    bio=user.bio,
                    profile_image_url=user.profile_image_url,
                    city_name=user.city.name if user.city else None,
                    user_type=user.user_type.type_name if user.user_type else "photographer",
                    photography_styles=user.profile_data.get("photography_styles", []),
                    portfolio_count=len(user.photos) if user.photos else 0,
                    is_verified=False,
                    artistic_statement=user.profile_data.get("artistic_statement"),
                    tagline=user.profile_data.get("tagline"),
                    experience_level=user.profile_data.get("experience_level"),
                    experience_years=user.profile_data.get("experience_years"),
                    specializes_in=user.profile_data.get("specializes_in", []),
                    open_for_work=user.availability_data.get("open_for_work", True),
                    available_for_travel=user.availability_data.get("available_for_travel", False),
                    location_preferences=user.availability_data.get("location_preferences", []),
                    website=user.website
                ))
            
            return profiles
        finally:
            db.close()
    
    async def user_exists(self, uid: str) -> bool:
        """Check if user profile exists"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == uid).first()
            return user is not None
        finally:
            db.close()
    
    async def delete_user_profile(self, uid: str) -> bool:
        """Delete user profile (soft delete by setting deleted flag)"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == uid).first()
            
            if not user:
                return False
            
            # Add deleted flag to profile_data (soft delete)
            profile_data = user.profile_data or {}
            profile_data["deleted"] = True
            profile_data["deleted_at"] = datetime.utcnow().isoformat()
            user.profile_data = profile_data
            user.updated_at = datetime.utcnow()
            
            db.commit()
            return True
        finally:
            db.close()
    
    async def get_user_stats(self, uid: str) -> Dict[str, Any]:
        """Get user statistics"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == uid).first()
            
            if not user:
                return {}
            
            return {
                "user_id": uid,
                "total_photos": len(user.photos) if user.photos else 0,
                "total_followers": 0,  # TODO: Implement followers
                "total_following": 0,  # TODO: Implement following
                "account_created": user.created_at.isoformat(),
                "last_active": user.last_active.isoformat() if user.last_active else None,
                "verified": False,  # TODO: Implement verification
                "user_type": user.user_type.type_name if user.user_type else "photographer"
            }
        finally:
            db.close()
    
    async def upload_profile_image(self, uid: str, file_content: bytes, filename: str, content_type: str) -> str:
        """Upload profile image to Google Cloud Storage"""
        import uuid
        try:
            # Generate unique filename
            file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
            unique_filename = f"users/{uid}/profile_{uuid.uuid4().hex[:8]}.{file_extension}"
            
            # Get bucket
            bucket = self.storage_client.bucket(self.bucket_name)
            
            # Create blob
            blob = bucket.blob(unique_filename)
            
            # Set content type
            blob.content_type = content_type
            
            # Upload file
            blob.upload_from_string(file_content)
            
            # Make blob publicly accessible
            blob.make_public()
            
            # Return public URL
            return blob.public_url
            
        except Exception as e:
            raise ValueError(f"Failed to upload profile image: {str(e)}")
    
    async def update_profile_image(self, uid: str, image_url: str):
        """Update user's profile image URL in database"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == uid).first()
            if user:
                user.profile_image_url = image_url
                
                # Update profile data with image info
                profile_data = user.profile_data or {}
                profile_data["profile_image"] = {
                    "source": ProfileImageSource.UPLOADED.value,
                    "url": image_url,
                    "upload_date": datetime.utcnow().isoformat(),
                    "verified": True
                }
                user.profile_data = profile_data
                user.updated_at = datetime.utcnow()
                
                db.commit()
        finally:
            db.close()
    
    async def remove_profile_image(self, uid: str):
        """Remove custom profile image (revert to Gmail image)"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == uid).first()
            if user:
                # TODO: Delete old image from Google Cloud Storage if it exists
                
                # Reset to Gmail image or default
                profile_data = user.profile_data or {}
                gmail_image_url = profile_data.get("profile_image", {}).get("gmail_url")
                user.profile_image_url = gmail_image_url
                
                # Update profile data
                profile_data["profile_image"] = {
                    "source": ProfileImageSource.GMAIL.value,
                    "url": gmail_image_url,
                    "upload_date": None,
                    "verified": False
                }
                user.profile_data = profile_data
                user.updated_at = datetime.utcnow()
                
                db.commit()
        finally:
            db.close()
'''

print("Content to append saved. Use this for completing the file.")
