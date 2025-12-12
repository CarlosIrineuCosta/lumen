#!/usr/bin/env python3
"""
Final script to create dummy photographers using direct SQL
Uses the same environment as the running backend server
"""

import os
import sys
import uuid
import random
import psycopg2
from datetime import datetime
import json

# Set environment to match the running backend
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/cdc/Storage/NVMe/projects/wasenet/opusdev/backend/firebase_service_account.json'

# Add the backend to Python path  
sys.path.append('/home/cdc/Storage/NVMe/projects/wasenet/opusdev/backend')

# Import Firebase admin
from firebase_admin import auth, credentials
import firebase_admin

# Initialize Firebase if not already done
if not firebase_admin._apps:
    cred = credentials.Certificate(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
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
        if "already exists" in str(e):
            print(f"⚠️ Firebase user {display_name} already exists")
            return None
        print(f"❌ Failed to create Firebase user {display_name}: {e}")
        return None

def insert_dummy_data():
    """Insert dummy data directly using psql command"""
    
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
    
    success_count = 0
    
    for photographer in photographers:
        # Create Firebase user first
        firebase_uid = create_firebase_user(photographer['email'], photographer['name'])
        if not firebase_uid:
            continue
            
        # Prepare SQL data
        profile_data = json.dumps({
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
        })
        
        availability_data = json.dumps({
            'open_for_work': True,
            'available_for_travel': random.choice([True, False]),
            'available_for_collaborations': True,
            'rate_range': f'${random.randint(200, 400)}-{random.randint(500, 800)}',
            'location_preferences': ['studio', 'outdoor', 'urban']
        })
        
        privacy_settings = json.dumps({
            'show_city': True,
            'show_country': True, 
            'show_age': False
        })
        
        # Create SQL INSERT statement
        sql_insert = f"""
        INSERT INTO users (
            id, email, handle, display_name, bio, city_id, primary_user_type,
            profile_data, availability_data, privacy_settings,
            created_at, updated_at, last_active
        ) VALUES (
            '{firebase_uid}',
            '{photographer['email']}',
            '{photographer['username']}',
            '{photographer['name']}',
            '{photographer['bio']}',
            1,
            1,
            '{profile_data}',
            '{availability_data}',
            '{privacy_settings}',
            NOW(),
            NOW(),
            NOW()
        ) ON CONFLICT (id) DO NOTHING;
        """
        
        # Write SQL to temp file and execute
        temp_sql = f'/tmp/insert_dummy_{firebase_uid[:8]}.sql'
        with open(temp_sql, 'w') as f:
            f.write(sql_insert)
        
        # Execute SQL using gcloud sql connect
        import subprocess
        try:
            result = subprocess.run([
                'gcloud', 'sql', 'connect', 'lumen-db-20250731', 
                '--user=postgres', '--database=lumen_photos', 
                f'--quiet', f'--sql-file={temp_sql}'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Created database record for {photographer['name']}")
                success_count += 1
            else:
                print(f"❌ Database error for {photographer['name']}: {result.stderr}")
                
            # Clean up temp file
            os.remove(temp_sql)
            
        except Exception as e:
            print(f"❌ Error executing SQL for {photographer['name']}: {e}")
    
    print(f"\n✅ Successfully created {success_count} dummy photographers")
    return success_count

if __name__ == "__main__":
    print("🚀 Creating dummy photographers with Firebase users and database records...")
    insert_dummy_data()
    print("🎉 Done! Check the photographers section to see the new dummy users")