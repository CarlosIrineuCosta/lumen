#!/usr/bin/env python3
"""
Firebase Emulator Test User Creation System
Creates realistic test users for development and testing
"""

import json
import requests
import uuid
from typing import List, Dict, Any
import random
import time
import os

class FirebaseEmulatorUserManager:
    """Manages test users in Firebase emulator"""
    
    def __init__(self, project_id: str = "demo-lumen-project"):
        self.project_id = project_id
        self.auth_emulator_url = "http://localhost:9290"
        self.api_key = "fake-api-key-for-emulator"
        
    def create_user_with_email_password(self, email: str, password: str, display_name: str = None) -> Dict[str, Any]:
        """Create a user in Firebase emulator with email/password auth"""
        
        # Create user account
        create_url = f"{self.auth_emulator_url}/www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser"
        
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        if display_name:
            payload["displayName"] = display_name
            
        response = requests.post(
            create_url,
            params={"key": self.api_key},
            json=payload
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Created user: {email} (UID: {user_data.get('localId')})")
            return user_data
        else:
            print(f"❌ Failed to create user {email}: {response.text}")
            return None
    
    def get_user_token(self, email: str, password: str) -> str:
        """Get ID token for user (for API testing)"""
        
        signin_url = f"{self.auth_emulator_url}/www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword"
        
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(
            signin_url,
            params={"key": self.api_key},
            json=payload
        )
        
        if response.status_code == 200:
            return response.json().get('idToken')
        return None
    
    def delete_user(self, uid: str) -> bool:
        """Delete a user from Firebase emulator"""
        
        delete_url = f"{self.auth_emulator_url}/emulator/v1/projects/{self.project_id}/accounts/{uid}"
        
        response = requests.delete(delete_url)
        return response.status_code == 200
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users in Firebase emulator"""
        
        list_url = f"{self.auth_emulator_url}/emulator/v1/projects/{self.project_id}/accounts"
        
        response = requests.get(list_url)
        
        if response.status_code == 200:
            return response.json().get('users', [])
        return []
    
    def clear_all_users(self) -> int:
        """Clear all users from Firebase emulator"""
        
        users = self.list_users()
        deleted_count = 0
        
        for user in users:
            if self.delete_user(user['localId']):
                deleted_count += 1
        
        print(f"🧹 Cleared {deleted_count} users from emulator")
        return deleted_count


def generate_test_users() -> List[Dict[str, Any]]:
    """Generate diverse test user profiles"""
    
    user_types = [
        {
            "type": "photographer",
            "specialties": ["portrait", "wedding", "landscape", "street", "fashion", "commercial"],
            "bio_templates": [
                "Professional photographer with {} years of experience in {}",
"A photographer specializing in {} and {} photography",
                "Award-winning {} photographer based in {}",
                "Freelance photographer passionate about {} and {}"
            ]
        },
        {
            "type": "model",
            "specialties": ["fashion", "commercial", "fitness", "portrait", "artistic"],
            "bio_templates": [
                "Professional model working in {} and {} industries",
"A model with experience in {} and {}",
                "Aspiring model focusing on {} and {} work",
                "Experienced {} model available for {} projects"
            ]
        },
        {
            "type": "makeup_artist",
            "specialties": ["bridal", "fashion", "editorial", "special_effects", "beauty"],
            "bio_templates": [
                "Makeup artist specializing in {} and {} looks",
                "Professional MUA with {} years in {} industry",
                "{} makeup artist passionate about {} artistry",
                "Freelance makeup artist for {} and {} projects"
            ]
        },
        {
            "type": "client",
            "specialties": ["wedding", "portrait", "commercial", "event", "family"],
            "bio_templates": [
                "Looking for talented photographers for {} projects",
                "Event planner seeking {} and {} photographers",
                "Business owner needing {} and {} photography",
                "Planning {} events and looking for creative talent"
            ]
        }
    ]
    
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", 
              "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville"]
    
    first_names = [
        "Emma", "Liam", "Olivia", "Noah", "Ava", "Elijah", "Sophia", "Lucas", "Isabella", "Mason",
        "Mia", "Logan", "Charlotte", "James", "Amelia", "Benjamin", "Harper", "Oliver", "Evelyn"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez",
        "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor"
    ]
    
    test_users = []
    
    for i in range(12):  # Create 12 test users
        user_type = random.choice(user_types)
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        city = random.choice(cities)
        
        # Create unique email
        username = f"{first_name.lower()}.{last_name.lower()}.{i+1}"
        email = f"test.{username}@lumen-test.local"
        
        # Generate bio
        specialties = random.sample(user_type["specialties"], min(2, len(user_type["specialties"])))
        bio_template = random.choice(user_type["bio_templates"])
        
        if "{} years" in bio_template:
            years = random.randint(2, 15)
            bio = bio_template.format(years, specialties[0])
        elif len(specialties) >= 2:
            bio = bio_template.format(specialties[0], specialties[1])
        else:
            bio = bio_template.format(specialties[0], city)
        
        # Create user profile
        user = {
            "email": email,
            "password": "TestPass123!",  # Same for all test users
            "display_name": f"{first_name} {last_name}",
            "profile": {
                "handle": f"{first_name.lower()}{last_name.lower()}{i+1}",
                "bio": bio,
                "city": city,
                "user_type": user_type["type"],
                "specialties": specialties,
                "experience_years": random.randint(1, 15),
                "portfolio_url": f"https://portfolio.{username}.example.com",
                "instagram": f"@{first_name.lower()}{last_name.lower()}photo" if user_type["type"] == "photographer" else f"@{first_name.lower()}{last_name.lower()}",
                "website": f"https://{username}.example.com"
            }
        }
        
        test_users.append(user)
    
    # Add admin user
    admin_user = {
        "email": "admin@lumen-test.local",
        "password": "AdminPass123!",
        "display_name": "Admin User",
        "profile": {
            "handle": "admin",
            "bio": "Platform administrator",
            "city": "San Francisco",
            "user_type": "admin",
            "specialties": ["platform_management"],
            "experience_years": 5,
            "is_admin": True
        }
    }
    
    test_users.append(admin_user)
    
    return test_users


def save_test_credentials(users: List[Dict[str, Any]], filepath: str = None):
    """Save test user credentials to file"""
    
    if not filepath:
        filepath = "/home/cdc/Storage/NVMe/projects/lumen/backend/tests/fixtures/test_credentials.json"
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Create credentials file
    credentials = {
        "firebase_emulator": {
            "project_id": "demo-lumen-project",
            "auth_url": "http://localhost:9099",
            "storage_url": "http://localhost:9199"
        },
        "users": []
    }
    
    for user in users:
        cred_entry = {
            "email": user["email"],
            "password": user["password"],
            "display_name": user["display_name"],
            "profile": user["profile"]
        }
        credentials["users"].append(cred_entry)
    
    with open(filepath, 'w') as f:
        json.dump(credentials, f, indent=2)
    
    print(f"💾 Saved credentials to: {filepath}")


def main():
    """Main function to create all test users"""
    
    print("🔥 Firebase Emulator Test User Creation")
    print("=" * 50)
    
    # Check if Firebase emulator is running
    try:
        response = requests.get("http://localhost:9290", timeout=5)
    except requests.exceptions.ConnectionError:
        print("❌ Firebase emulator not running!")
        print("Start it with: firebase emulators:start --only auth,storage")
        return False
    
    manager = FirebaseEmulatorUserManager()
    
    # Clear existing users
    print("🧹 Clearing existing test users...")
    manager.clear_all_users()
    
    # Generate user profiles
    print("👥 Generating test user profiles...")
    test_users = generate_test_users()
    
    print(f"📝 Creating {len(test_users)} test users...")
    
    created_users = []
    
    for user in test_users:
        firebase_user = manager.create_user_with_email_password(
            email=user["email"],
            password=user["password"],
            display_name=user["display_name"]
        )
        
        if firebase_user:
            # Add Firebase UID to profile
            user["profile"]["firebase_uid"] = firebase_user["localId"]
            user["firebase_data"] = firebase_user
            created_users.append(user)
            
            # Brief pause to avoid rate limits
            time.sleep(0.1)
    
    print(f"\n✅ Successfully created {len(created_users)} users")
    
    # Save credentials
    save_test_credentials(created_users)
    
    # Display summary
    print("\n📊 User Summary:")
    print("-" * 30)
    
    type_counts = {}
    for user in created_users:
        user_type = user["profile"]["user_type"]
        type_counts[user_type] = type_counts.get(user_type, 0) + 1
    
    for user_type, count in type_counts.items():
        print(f"  {user_type}: {count}")
    
    print(f"\n🔐 All users have password: TestPass123!")
    print("💡 Use these credentials for testing authentication flows")
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)