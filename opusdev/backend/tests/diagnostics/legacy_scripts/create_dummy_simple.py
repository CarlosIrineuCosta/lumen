#!/usr/bin/env python3
"""
Simple script to create dummy photographers using direct database access

MOVED FROM: /create_dummy_simple.py to organized test structure
"""

import os
import sys
import uuid
import random
import asyncio
from pathlib import Path
from datetime import datetime

# Add the backend to Python path - updated for new location
sys.path.append('../../..')

# Import Firebase admin
from firebase_admin import auth, credentials
import firebase_admin

# Import database components
from app.database.connection import SessionLocal
from app.models.user import User
from app.models.photo import Photo

# Initialize Firebase Admin - updated path
cred = credentials.Certificate('../../../firebase_service_account.json')
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

def create_dummy_photographers():
    """Create dummy photographers with direct database access"""
    
    photographers = [
        {
            'name': 'Dummy Carla',
            'email': f'dummy.carla.{uuid.uuid4().hex[:8]}@test.com',
            'username': f'dummycarla{random.randint(1000, 9999)}',
            'city': 'São Paulo',
            'bio': 'Fine art photographer specializing in intimate portraiture.',
            'artistic_statement': 'Beauty emerges through vulnerability and authentic human connection.',
        },
        {
            'name': 'Dummy Charles',
            'email': f'dummy.charles.{uuid.uuid4().hex[:8]}@test.com',
            'username': f'dummycharles{random.randint(1000, 9999)}',
            'city': 'Los Angeles',
            'bio': 'Professional photographer with editorial experience.',
            'artistic_statement': 'Exploring the intersection of light and human emotion.',
        },
        {
            'name': 'Dummy Joe',
            'email': f'dummy.joe.{uuid.uuid4().hex[:8]}@test.com',
            'username': f'dummyjoe{random.randint(1000, 9999)}',
            'city': 'Miami',
            'bio': 'Contemporary artist focusing on minimalist compositions.',
            'artistic_statement': 'Simplicity reveals the essence of artistic expression.',
        },
        {
            'name': 'Dummy Alex',
            'email': f'dummy.alex.{uuid.uuid4().hex[:8]}@test.com',
            'username': f'dummyalex{random.randint(1000, 9999)}',
            'city': 'Portland',
            'bio': 'Experimental photographer blending traditional and modern techniques.',
            'artistic_statement': 'Art challenges boundaries and invites new perspectives.',
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
            
            # Create database user record (simplified)
            new_user = User(
                id=firebase_uid,
                email=photographer['email'],
                handle=photographer['username'],
                display_name=photographer['name'],
                bio=photographer['bio'],
                profile_data={
                    'user_type': 'photographer',
                    'city': photographer['city'],
                    'photography_styles': ['artistic_nude', 'portrait', 'fashion'],
                    'artistic_statement': photographer['artistic_statement'],
                    'mission_statement': f"Creating powerful imagery through {photographer['city']}-based photography.",
                    'availability_data': {
                        'available_for_hire': True,
                        'available_for_collaborations': True,
                        'rate_range': f'${random.randint(200, 400)}-{random.randint(500, 800)}'
                    }
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(new_user)
            db.commit()
            
            print(f"✅ Created photographer: {photographer['name']}")
            success_count += 1
            
    except Exception as e:
        print(f"❌ Error creating photographers: {e}")
        db.rollback()
    finally:
        db.close()
    
    print(f"\n✅ Successfully created {success_count} dummy photographers")
    print("Note: Photos will need to be added separately via API calls")

if __name__ == "__main__":
    print("🚀 Creating dummy photographers...")
    create_dummy_photographers()
    print("🎉 Done! You can now test the photographers section")