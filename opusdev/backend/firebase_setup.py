#!/usr/bin/env python3
"""Firebase setup script for Lumen project"""

import os
import json
from google.cloud import resourcemanager_v3
from dotenv import load_dotenv

load_dotenv()

def setup_firebase():
    """Set up Firebase for the Lumen project"""
    
    project_id = os.getenv("PROJECT_ID")
    print(f"🔥 Setting up Firebase for project: {project_id}")
    
    try:
        # Initialize the Resource Manager client
        client = resourcemanager_v3.ProjectsClient()
        
        # Get project details
        project_name = f"projects/{project_id}"
        project = client.get_project(name=project_name)
        
        print(f"✅ Project found: {project.display_name}")
        print(f"📍 Project ID: {project.project_id}")
        
        # Create Firebase configuration template
        firebase_config = {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": "REPLACE_WITH_ACTUAL_KEY_ID",
            "private_key": "REPLACE_WITH_ACTUAL_PRIVATE_KEY",
            "client_email": f"lumen-firebase-sa@{project_id}.iam.gserviceaccount.com",
            "client_id": "REPLACE_WITH_ACTUAL_CLIENT_ID",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/lumen-firebase-sa%40{project_id}.iam.gserviceaccount.com"
        }
        
        # Save template (will need actual credentials)
        with open('firebase_service_account_template.json', 'w') as f:
            json.dump(firebase_config, f, indent=2)
            
        print("✅ Firebase service account template created")
        print("\n📋 Next steps:")
        print("1. Go to Firebase Console: https://console.firebase.google.com/")
        print(f"2. Add project: {project_id}")
        print("3. Enable Authentication")
        print("4. Download service account key")
        print("5. Replace firebase_service_account_template.json with actual credentials")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    print("\n🔥 Firebase setup preparation complete!")

if __name__ == "__main__":
    setup_firebase()