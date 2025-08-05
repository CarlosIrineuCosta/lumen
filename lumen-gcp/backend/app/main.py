from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import Firebase configuration to initialize on startup
from .firebase_config import firebase_config
from .api.endpoints import auth, users, photos

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Lumen API",
    description="Artistic Photography Platform API - Instagram for Professional Photography",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:19006").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(photos.router, prefix="/api/v1/photos", tags=["photos"])

@app.get("/")
async def root():
    return {
        "message": "Lumen API - Artistic Photography Platform",
        "description": "Instagram for Professional Photography",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "project_id": os.getenv("PROJECT_ID"),
        "firebase_enabled": firebase_config.app is not None,
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "photos": "/api/v1/photos"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
