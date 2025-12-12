#!/usr/bin/env python3
"""
Create dummy photographers using API endpoints
This approach avoids database connection issues
"""

import requests
import uuid
import random
import json

API_BASE = "http://100.106.201.33:8080/api/v1"

def create_dummy_photographers_via_api():
    """Create dummy photographers using API endpoints"""
    
    photographers = [
        {
            'name': 'Dummy Carla',
            'email': f'dummy.carla.{uuid.uuid4().hex[:8]}@test.com',
            'username': f'dummycarla{random.randint(1000, 9999)}',
            'city': 'São Paulo',
            'bio': 'Fine art photographer specializing in intimate portraiture.',
            'artistic_statement': 'Beauty emerges through vulnerability and authentic human connection.',
            'images_pattern': 'CarlaB_*'
        },
        {
            'name': 'Dummy Charles',
            'email': f'dummy.charles.{uuid.uuid4().hex[:8]}@test.com',
            'username': f'dummycharles{random.randint(1000, 9999)}',
            'city': 'Los Angeles',
            'bio': 'Professional photographer with editorial experience.',
            'artistic_statement': 'Exploring the intersection of light and human emotion.',
            'images_pattern': 'CharlesK_*'
        },
        {
            'name': 'Dummy Joe',
            'email': f'dummy.joe.{uuid.uuid4().hex[:8]}@test.com',
            'username': f'dummyjoe{random.randint(1000, 9999)}',
            'city': 'Miami',
            'bio': 'Contemporary artist focusing on minimalist compositions.',
            'artistic_statement': 'Simplicity reveals the essence of artistic expression.',
            'images_pattern': None
        },
        {
            'name': 'Dummy Alex',
            'email': f'dummy.alex.{uuid.uuid4().hex[:8]}@test.com',
            'username': f'dummyalex{random.randint(1000, 9999)}',
            'city': 'Portland',
            'bio': 'Experimental photographer blending traditional and modern techniques.',
            'artistic_statement': 'Art challenges boundaries and invites new perspectives.',
            'images_pattern': None
        }
    ]
    
    # First, let's check what user registration requires
    response = requests.get(f"{API_BASE}/users/styles")
    if response.status_code == 200:
        available_styles = response.json()
        print(f"✅ Available photography styles: {available_styles}")
    else:
        print("⚠️ Could not get photography styles, using defaults")
        available_styles = ['portrait', 'fashion', 'artistic_nude', 'commercial']
    
    success_count = 0
    
    for photographer in photographers:
        try:
            # Prepare registration data
            registration_data = {
                "handle": photographer['username'],
                "display_name": photographer['name'],
                "bio": photographer['bio'],
                "city_id": 1,  # Default city ID
                "user_type": "photographer",
                "photography_styles": ["artistic_nude", "portrait", "fashion"]
            }
            
            print(f"\n👤 Creating {photographer['name']}...")
            print(f"📧 Email: {photographer['email']}")
            print(f"📝 Registration data: {json.dumps(registration_data, indent=2)}")
            
            # Try to register the user
            response = requests.post(
                f"{API_BASE}/users/register",
                json=registration_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200 or response.status_code == 201:
                print(f"✅ Successfully registered {photographer['name']}")
                success_count += 1
            else:
                print(f"❌ Registration failed for {photographer['name']}: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error creating {photographer['name']}: {e}")
    
    print(f"\n🎉 Successfully created {success_count}/{len(photographers)} dummy photographers")
    return success_count

if __name__ == "__main__":
    print("🚀 Creating dummy photographers via API...")
    create_dummy_photographers_via_api()
    print("\n📷 Photos can be uploaded next using the upload API")