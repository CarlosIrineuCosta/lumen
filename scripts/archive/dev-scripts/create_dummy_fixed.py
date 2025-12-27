#!/usr/bin/env python3
"""
Fixed script to create dummy photographers with proper database schema
Creates real Firebase users and database records for testing
"""

import os
import sys
import uuid
import random
import asyncio
from pathlib import Path
from datetime import datetime

# Add the backend to Python path
sys.path.append('/home/cdc/Storage/NVMe/projects/wasenet/opusdev/backend')

# Import Firebase admin
from firebase_admin import auth, credentials
import firebase_admin

# Import database components
from app.database.connection import SessionLocal
from app.models.user import User

# Check if Firebase is already initialized
if not firebase_admin._apps:
    # Initialize Firebase Admin
    cred = credentials.Certificate('/home/cdc/Storage/NVMe/projects/wasenet/opusdev/backend/firebase_service_account.json')
    firebase_admin.initialize_app(cred)

def create_firebase_user(email, display_name):
    """Create a Firebase user"""
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

def get_or_create_city_id(db, city_name):
    """Get city ID or create if not exists (simplified for testing)"""
    # For now, just return 1 (assuming São Paulo exists)
    # In real implementation, you'd query/create the city
    if city_name == "São Paulo":
        return 1  # Assuming this exists
    else:
        return 2  # Default for other cities

def create_dummy_photographers():
    """Create dummy photographers with direct database access"""
    
    photographers = [
        {
            'name': 'Dummy Carla',
            'email': f'dummy.carla.{uuid.uuid4().hex[:8]}@test.com',
            'username': f'dummycarla{random.randint(1000, 9999)}',
            'city': 'São Paulo',
            'country': 'Brazil',
            'bio': 'Fine art photographer specializing in intimate portraiture.',
            'artistic_statement': 'Beauty emerges through vulnerability and authentic human connection.',
            'images_pattern': 'CarlaB_*'
        },
        {
            'name': 'Dummy Charles',
            'email': f'dummy.charles.{uuid.uuid4().hex[:8]}@test.com',
            'username': f'dummycharles{random.randint(1000, 9999)}',
            'city': 'Los Angeles',
            'country': 'USA',
            'bio': 'Professional photographer with editorial experience.',
            'artistic_statement': 'Exploring the intersection of light and human emotion.',
            'images_pattern': 'CharlesK_*'
        },
        {
            'name': 'Dummy Joe',
            'email': f'dummy.joe.{uuid.uuid4().hex[:8]}@test.com',
            'username': f'dummyjoe{random.randint(1000, 9999)}',
            'city': 'Miami',
            'country': 'USA',
            'bio': 'Contemporary artist focusing on minimalist compositions.',
            'artistic_statement': 'Simplicity reveals the essence of artistic expression.',
            'images_pattern': None
        },
        {
            'name': 'Dummy Alex',
            'email': f'dummy.alex.{uuid.uuid4().hex[:8]}@test.com',
            'username': f'dummyalex{random.randint(1000, 9999)}',
            'city': 'Portland',
            'country': 'USA',
            'bio': 'Experimental photographer blending traditional and modern techniques.',
            'artistic_statement': 'Art challenges boundaries and invites new perspectives.',
            'images_pattern': None
        }
    ]
    
    db = SessionLocal()
    success_count = 0
    
    try:
        for photographer in photographers:
            # Create Firebase user
            firebase_uid = create_firebase_user(photographer['email'], photographer['name'])
            if not firebase_uid:
                continue
            
            # Get city ID (simplified)
            city_id = get_or_create_city_id(db, photographer['city'])
            
            # Create database user record
            new_user = User(
                id=firebase_uid,  # Firebase UID as primary key
                email=photographer['email'],
                handle=photographer['username'],
                display_name=photographer['name'],
                bio=photographer['bio'],
                city_id=city_id,
                primary_user_type=1,  # Assuming 1 = photographer
                profile_data={
                    'photography_styles': ['artistic_nude', 'portrait', 'fashion', 'beauty'],
                    'artistic_statement': photographer['artistic_statement'],
                    'mission_statement': f"Creating powerful imagery through {photographer['city']}-based photography.",
                    'experience_level': random.choice(['amateur', 'semi_pro', 'professional']),
                    'experience_years': random.randint(2, 15),
                    'specializes_in': ['artistic nude photography', 'portrait work'],
                    'camera_gear': [
                        random.choice(['Canon EOS R5', 'Nikon D850', 'Sony A7R IV']),
                        random.choice(['50mm f/1.4', '85mm f/1.8', '24-70mm f/2.8'])
                    ]
                },
                availability_data={
                    'open_for_work': True,
                    'available_for_travel': random.choice([True, False]),
                    'available_for_collaborations': True,
                    'rate_range': f'${random.randint(200, 400)}-{random.randint(500, 800)}',
                    'location_preferences': ['studio', 'outdoor', 'urban']
                },
                privacy_settings={
                    'show_city': True,
                    'show_country': True,
                    'show_age': False
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_active=datetime.utcnow()
            )
            
            db.add(new_user)
            db.commit()
            
            print(f"✅ Created photographer: {photographer['name']} in {photographer['city']}")
            success_count += 1
            
    except Exception as e:
        print(f"❌ Error creating photographers: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    
    print(f"\n✅ Successfully created {success_count} dummy photographers")
    print("📷 Photos will need to be uploaded separately via API")
    
    return success_count

if __name__ == "__main__":
    print("🚀 Creating dummy photographers with real Firebase users...")
    success = create_dummy_photographers()
    print(f"🎉 Done! Created {success} photographers for testing")