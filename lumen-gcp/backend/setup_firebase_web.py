#!/usr/bin/env python3
"""
Script to help set up Firebase web configuration
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

def setup_firebase_web():
    """Guide through Firebase web app setup"""
    
    project_id = os.getenv("PROJECT_ID")
    
    print("Firebase Web App Setup Guide")
    print("=" * 40)
    print(f"Project ID: {project_id}")
    print()
    
    print("Steps to complete Firebase setup:")
    print()
    
    print("1. Go to Firebase Console:")
    print("   https://console.firebase.google.com/")
    print()
    
    print("2. Add your existing GCP project:")
    print(f"   - Click 'Add project'")
    print(f"   - Select 'lumen-photo-app-20250731' (your existing GCP project)")
    print(f"   - Follow the setup wizard")
    print()
    
    print("3. Enable Authentication:")
    print("   - Go to 'Authentication' in the left sidebar")
    print("   - Click 'Get started'")
    print("   - Go to 'Sign-in method' tab")
    print("   - Enable 'Email/Password' provider")
    print()
    
    print("4. Add a Web App:")
    print("   - Go to Project Settings (gear icon)")
    print("   - Scroll down to 'Your apps'")
    print("   - Click 'Web' icon (</>) to add web app")
    print("   - App nickname: 'Lumen Web Client'")
    print("   - Check 'Also set up Firebase Hosting' (optional)")
    print("   - Click 'Register app'")
    print()
    
    print("5. Copy the Firebase config:")
    print("   - You'll see a config object like this:")
    print("""
    const firebaseConfig = {
        apiKey: "AIza...",
        authDomain: "lumen-photo-app-20250731.firebaseapp.com",
        projectId: "lumen-photo-app-20250731",
        storageBucket: "lumen-photo-app-20250731.appspot.com",
        messagingSenderId: "123456789",
        appId: "1:123456789:web:abcdef"
    };
    """)
    print()
    
    print("6. Update the test client:")
    print("   - Open: /home/cdc/projects/wasenet/lumen-gcp/frontend/firebase-test-client.html")
    print("   - Replace the firebaseConfig object with your actual values")
    print()
    
    print("7. Access the test client:")
    print("   - Open: http://100.106.201.33:8000/firebase-test-client.html")
    print("   - (You'll need to serve the HTML file)")
    print()
    
    print("Quick server command:")
    print("cd /home/cdc/projects/wasenet/lumen-gcp/frontend")
    print("python3 -m http.server 8000")
    print()
    
    # Check if we can get some info automatically
    try:
        # Try to read the service account file for project info
        with open('firebase_service_account.json', 'r') as f:
            service_account = json.load(f)
            
        print("Auto-detected info from service account:")
        print(f"- Project ID: {service_account.get('project_id')}")
        print(f"- Client Email: {service_account.get('client_email')}")
        print(f"- Auth Domain: {service_account.get('project_id')}.firebaseapp.com")
        print()
        
    except Exception as e:
        print(f"Could not read service account file: {e}")
        print()
    
    print("After setup, you'll be able to:")
    print("- Sign up new users")
    print("- Sign in existing users") 
    print("- Test protected API endpoints")
    print("- See authentication working end-to-end")

if __name__ == "__main__":
    setup_firebase_web()