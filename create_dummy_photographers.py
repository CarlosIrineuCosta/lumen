#!/usr/bin/env python3
"""
Script to create dummy photographers for testing purposes
Creates real Firebase users and uploads their photos to the system
"""

import os
import sys
import uuid
import random
from pathlib import Path

# Add the backend to Python path
sys.path.append('/home/cdc/Storage/NVMe/projects/wasenet/opusdev/backend')

from firebase_admin import auth, credentials
import firebase_admin
from app.services.user_service import UserService
from app.services.photo_service import PhotoService
from app.models.user import CreateUserRequest, PhotographyStyle, UserType, ExperienceLevel

# Initialize Firebase Admin
cred = credentials.Certificate('/home/cdc/Storage/NVMe/projects/wasenet/opusdev/backend/firebase_service_account.json')
firebase_admin.initialize_app(cred)

class DummyPhotographerCreator:
    def __init__(self):
        self.user_service = UserService()
        self.photo_service = PhotoService()
        self.temp_images_path = Path('/home/cdc/Storage/NVMe/projects/wasenet/temp-images')
        
        # Define our dummy photographers based on image groupings
        self.photographers = [
            {
                'name': 'Dummy Carla',
                'email': f'dummy.carla.{uuid.uuid4().hex[:8]}@test.com',
                'username': f'dummycarla{random.randint(1000, 9999)}',
                'city': 'São Paulo',
                'bio': 'Fine art photographer specializing in intimate portraiture and natural lighting.',
                'artistic_statement': 'Beauty emerges through vulnerability and authentic human connection.',
                'mission_statement': 'Creating timeless art that celebrates the human form.',
                'images_pattern': 'CarlaB_*'
            },
            {
                'name': 'Dummy Charles',
                'email': f'dummy.charles.{uuid.uuid4().hex[:8]}@test.com',
                'username': f'dummycharles{random.randint(1000, 9999)}',
                'city': 'Los Angeles',
                'bio': 'Professional photographer with 15 years experience in editorial and fine art.',
                'artistic_statement': 'Exploring the intersection of light, shadow, and human emotion.',
                'mission_statement': 'Capturing moments that transcend the ordinary.',
                'images_pattern': 'CharlesK_*'
            },
            {
                'name': 'Dummy Joe',
                'email': f'dummy.joe.{uuid.uuid4().hex[:8]}@test.com',
                'username': f'dummyjoe{random.randint(1000, 9999)}',
                'city': 'Miami',
                'bio': 'Contemporary artist focusing on minimalist compositions and natural beauty.',
                'artistic_statement': 'Simplicity reveals the essence of artistic expression.',
                'mission_statement': 'Creating powerful imagery through subtle storytelling.',
                'images_pattern': None  # Will get random remaining images
            },
            {
                'name': 'Dummy Alex',
                'email': f'dummy.alex.{uuid.uuid4().hex[:8]}@test.com',
                'username': f'dummyalex{random.randint(1000, 9999)}',
                'city': 'Portland',
                'bio': 'Experimental photographer blending traditional techniques with modern vision.',
                'artistic_statement': 'Art challenges boundaries and invites new perspectives.',
                'mission_statement': 'Pushing creative limits through innovative visual narratives.',
                'images_pattern': None  # Will get random remaining images
            }
        ]
        
    def get_photography_styles(self):
        """Always include artistic_nude plus random other styles"""
        all_styles = [style.value for style in PhotographyStyle]
        styles = ['artistic_nude']  # Always include this
        
        # Add 2-4 random additional styles
        other_styles = [s for s in all_styles if s != 'artistic_nude']
        additional = random.sample(other_styles, random.randint(2, 4))
        styles.extend(additional)
        
        return styles
    
    def create_firebase_user(self, email, display_name):
        """Create a Firebase user without requiring OAuth login"""
        try:
            user_record = auth.create_user(
                email=email,
                display_name=display_name,
                email_verified=True
            )
            print(f"✅ Created Firebase user: {display_name} ({user_record.uid})")
            return user_record.uid
        except Exception as e:
            print(f"❌ Failed to create Firebase user {display_name}: {e}")
            return None
    
    def get_images_for_photographer(self, pattern, remaining_images):
        """Get images matching pattern or random selection"""
        all_images = list(self.temp_images_path.glob('*.jpg'))
        
        if pattern:
            # Get images matching the pattern
            import fnmatch
            matched_images = [img for img in all_images if fnmatch.fnmatch(img.name, pattern)]
            # Remove matched images from remaining list
            for img in matched_images:
                if img in remaining_images:
                    remaining_images.remove(img)
            return matched_images
        else:
            # Get 2-3 random images from remaining
            if len(remaining_images) >= 2:
                selected = random.sample(remaining_images, min(3, len(remaining_images)))
                for img in selected:
                    remaining_images.remove(img)
                return selected
            return remaining_images.copy()  # Return whatever is left
    
    async def create_dummy_photographer(self, photographer_data, remaining_images):
        """Create a complete photographer with profile and photos"""
        
        # Create Firebase user
        firebase_uid = self.create_firebase_user(
            photographer_data['email'], 
            photographer_data['name']
        )
        
        if not firebase_uid:
            return False
        
        # Create user profile
        user_request = CreateUserRequest(
            display_name=photographer_data['name'],
            username=photographer_data['username'],
            bio=photographer_data['bio'],
            city=photographer_data['city'],
            user_type=UserType.PHOTOGRAPHER,
            experience_level=random.choice(list(ExperienceLevel)).value,
            photography_styles=self.get_photography_styles(),
            artistic_statement=photographer_data['artistic_statement'],
            mission_statement=photographer_data['mission_statement'],
            availability_data={
                'available_for_hire': random.choice([True, False]),
                'available_for_collaborations': True,
                'rate_range': f'${random.randint(150, 500)}-{random.randint(600, 1200)}'
            }
        )
        
        # Create mock AuthUser object
        class MockAuthUser:
            def __init__(self, uid, email, display_name):
                self.uid = uid
                self.email = email
                self.display_name = display_name
        
        mock_user = MockAuthUser(firebase_uid, photographer_data['email'], photographer_data['name'])
        
        try:
            # Create user profile in database
            profile = await self.user_service.create_user_profile(mock_user, user_request)
            print(f"✅ Created profile for {photographer_data['name']}")
            
            # Get images for this photographer
            images = self.get_images_for_photographer(photographer_data['images_pattern'], remaining_images)
            print(f"📷 Found {len(images)} images for {photographer_data['name']}")
            
            # Upload each image
            for img_path in images:
                await self.upload_photo(firebase_uid, img_path, photographer_data['name'])
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create photographer {photographer_data['name']}: {e}")
            return False
    
    async def upload_photo(self, user_id, image_path, photographer_name):
        """Upload a photo for the photographer"""
        try:
            # Read image file
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Generate photo metadata
            titles = [
                "Artistic Study", "Light and Shadow", "Natural Beauty", "Intimate Portrait",
                "Fine Art Series", "Contemporary Vision", "Minimalist Study", "Classic Form"
            ]
            
            descriptions = [
                "Exploring the interplay of light and form in natural settings.",
                "A study in contemporary portraiture and artistic expression.",
                "Capturing the essence of natural beauty through careful composition.",
                "Fine art photography celebrating human expression.",
                "An intimate exploration of light, shadow, and form."
            ]
            
            # Upload photo
            result = await self.photo_service.upload_photo(
                user_id=user_id,
                image_data=image_data,
                filename=image_path.name,
                content_type='image/jpeg',
                title=random.choice(titles),
                description=random.choice(descriptions),
                is_portfolio=random.choice([True, False]),
                is_public=True,
                camera=f"{random.choice(['Canon', 'Nikon', 'Sony'])} {random.choice(['EOS R5', 'D850', 'A7R IV'])}",
                settings=f"ISO {random.randint(100, 800)} | f/{random.choice([1.4, 1.8, 2.8])} | 1/{random.randint(60, 250)}s"
            )
            
            print(f"✅ Uploaded {image_path.name} for {photographer_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to upload {image_path.name}: {e}")
            return False
    
    async def create_all_photographers(self):
        """Create all dummy photographers"""
        print("🚀 Creating dummy photographers for testing...")
        
        # Get all available images
        remaining_images = list(self.temp_images_path.glob('*.jpg'))
        print(f"📁 Found {len(remaining_images)} images to distribute")
        
        success_count = 0
        
        for photographer_data in self.photographers:
            print(f"\n👤 Creating {photographer_data['name']}...")
            
            if await self.create_dummy_photographer(photographer_data, remaining_images):
                success_count += 1
            else:
                print(f"❌ Failed to create {photographer_data['name']}")
        
        print(f"\n✅ Successfully created {success_count}/{len(self.photographers)} dummy photographers")
        
        if remaining_images:
            print(f"📷 {len(remaining_images)} images not used: {[img.name for img in remaining_images]}")


if __name__ == "__main__":
    import asyncio
    
    print("Creating dummy photographers with real Firebase users and photo uploads...")
    
    creator = DummyPhotographerCreator()
    asyncio.run(creator.create_all_photographers())
    
    print("\n🎉 Dummy photographer creation complete!")
    print("Note: These users can be deleted later using direct SQL or Firebase Admin")