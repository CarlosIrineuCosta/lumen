"""Firebase configuration for Lumen backend"""

import os
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv

load_dotenv()

class FirebaseConfig:
    """Firebase configuration and initialization"""
    
    def __init__(self):
        self.app = None
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Get credentials file path
                cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                project_id = os.getenv("FIREBASE_PROJECT_ID")
                
                if not cred_path or not os.path.exists(cred_path):
                    print("⚠️  Firebase credentials not found. Authentication disabled.")
                    return None
                
                # Initialize Firebase Admin SDK
                cred = credentials.Certificate(cred_path)
                self.app = firebase_admin.initialize_app(cred, {
                    'projectId': project_id
                })
                
                print(f"✅ Firebase initialized for project: {project_id}")
                return self.app
            else:
                self.app = firebase_admin.get_app()
                print("✅ Firebase already initialized")
                return self.app
                
        except Exception as e:
            print(f"❌ Firebase initialization error: {e}")
            print("🔧 Authentication will be disabled")
            return None
    
    def verify_token(self, id_token: str):
        """Verify Firebase ID token"""
        try:
            if not self.app:
                raise Exception("Firebase not initialized")
                
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            print(f"Token verification error: {e}")
            return None
    
    def get_user(self, uid: str):
        """Get user information by UID"""
        try:
            if not self.app:
                raise Exception("Firebase not initialized")
                
            user = auth.get_user(uid)
            return user
        except Exception as e:
            print(f"Get user error: {e}")
            return None

# Global Firebase instance
firebase_config = FirebaseConfig()