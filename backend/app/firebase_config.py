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
        self.is_emulator_mode = False
        self.initialize_firebase()
    
    def setup_emulator_environment(self):
        """Configure environment variables for Firebase emulator"""
        # Check for testing environment or explicit emulator mode
        is_testing = os.getenv("TESTING") == "true"
        use_emulator = os.getenv("FIREBASE_USE_EMULATOR", "false").lower() in ["true", "1", "yes"]
        
        if is_testing or use_emulator:
            # Set Firebase emulator environment variables, allowing overrides from the shell
            auth_host = os.getenv("FIREBASE_AUTH_EMULATOR_HOST", "localhost:9099")
            storage_host = os.getenv("FIREBASE_STORAGE_EMULATOR_HOST", "localhost:9199")
            os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = auth_host
            os.environ["FIREBASE_STORAGE_EMULATOR_HOST"] = storage_host
            os.environ["GCLOUD_PROJECT"] = os.getenv("GCLOUD_PROJECT", "demo-lumen-project")  # Emulator demo project
            self.is_emulator_mode = True
            print("Firebase emulator mode enabled")
            return True
        return False
    
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Setup emulator environment if needed
            self.setup_emulator_environment()
            
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                if self.is_emulator_mode:
                    # For emulator mode, use a minimal configuration
                    project_id = os.getenv("GCLOUD_PROJECT", "demo-lumen-project")
                    self.app = firebase_admin.initialize_app(options={
                        'projectId': project_id
                    })
                    print(f"Firebase initialized in emulator mode for project: {project_id}")
                else:
                    # Production mode - use GOOGLE_APPLICATION_CREDENTIALS
                    # The SDK automatically finds this environment variable.
                    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                        print("GOOGLE_APPLICATION_CREDENTIALS not set. Firebase disabled.")
                        return None

                    project_id = os.getenv("FIREBASE_PROJECT_ID")
                    self.app = firebase_admin.initialize_app(options={
                        'projectId': project_id
                    })
                    print(f"Firebase initialized for project: {project_id}")
                
                return self.app
            else:
                self.app = firebase_admin.get_app()
                print("Firebase already initialized")
                return self.app
                
        except Exception as e:
            print(f"Firebase initialization error: {e}")
            print("Authentication will be disabled")
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
