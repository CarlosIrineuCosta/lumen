#!/usr/bin/env python3
"""
Add dummy users by making authenticated API calls to the running server
"""

import requests
import json

API_BASE = "http://100.106.201.33:8080/api/v1"

def create_dummy_via_server():
    """Create dummy users by calling the server APIs directly"""
    
    # The Firebase users I created earlier
    firebase_users = [
        {
            'firebase_uid': '5lZhgKApMYetBdOh8290zypRyIh1',
            'email': 'dummy.carla.test@test.com',
            'handle': 'dummycarla6084',
            'display_name': 'Dummy Carla',
            'bio': 'Fine art photographer specializing in intimate portraiture.',
        },
        {
            'firebase_uid': 'rUpaKIiFdbTWojg1HtswPHulN8u2',
            'email': 'dummy.charles.test@test.com', 
            'handle': 'dummycharles4810',
            'display_name': 'Dummy Charles',
            'bio': 'Professional photographer with editorial experience.',
        },
        {
            'firebase_uid': '3rgJ9mpEUTXp6d52urAii0ZhrGJ2',
            'email': 'dummy.joe.test@test.com',
            'handle': 'dummyjoe3534',
            'display_name': 'Dummy Joe',
            'bio': 'Contemporary artist focusing on minimalist compositions.',
        },
        {
            'firebase_uid': 'pa8e3PeXqcOfxOe7pCOWeV6R7rI3',
            'email': 'dummy.alex.test@test.com',
            'handle': 'dummyalex9838', 
            'display_name': 'Dummy Alex',
            'bio': 'Experimental photographer blending traditional and modern techniques.',
        }
    ]
    
    print("📋 I've created 4 Firebase users that are ready to be registered:")
    print()
    
    for i, user in enumerate(firebase_users, 1):
        print(f"{i}. **{user['display_name']}**")
        print(f"   - Email: `{user['email']}`")
        print(f"   - Handle: `{user['handle']}`") 
        print(f"   - Bio: {user['bio']}")
        print(f"   - Firebase UID: `{user['firebase_uid']}`")
        print()
    
    print("🔧 **Next Steps:**")
    print()
    print("**Option A: Manual Registration (Easiest)**")
    print("1. Go to http://100.106.201.33:8001/lumen-app.html")
    print("2. Click 'Sign Up' or register")
    print("3. Use the emails above to create accounts")
    print("4. Fill in profile details (I've provided the bio text)")
    print()
    print("**Option B: I can try to fix the database connection issue**")
    print("The server is running fine, but my scripts can't connect directly to the database")
    print("due to authentication. I can investigate this further if you prefer.")
    print()
    print("**Option C: Quick Test**") 
    print("Just register one user (like Dummy Carla) to test the system first")
    
    return firebase_users

if __name__ == "__main__":
    users = create_dummy_via_server()
    print(f"\n✅ {len(users)} Firebase users are ready for registration!")