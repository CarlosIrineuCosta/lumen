"""Authentication middleware for FastAPI using Firebase"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .firebase_config import firebase_config

# Security scheme
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get current authenticated user from Firebase token
    """
    try:
        # Extract token from Authorization header
        token = credentials.credentials
        
        # Verify token with Firebase
        decoded_token = firebase_config.verify_token(token)
        
        if not decoded_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return decoded_token
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Optional authentication - returns user if authenticated, None if not
    """
    try:
        if not credentials:
            return None
            
        token = credentials.credentials
        decoded_token = firebase_config.verify_token(token)
        return decoded_token
        
    except Exception:
        return None

class AuthUser:
    """User model from Firebase token"""
    
    def __init__(self, decoded_token: dict):
        self.uid = decoded_token.get('uid')
        self.email = decoded_token.get('email')
        self.email_verified = decoded_token.get('email_verified', False)
        self.name = decoded_token.get('name')
        self.picture = decoded_token.get('picture')
        self.firebase_token = decoded_token