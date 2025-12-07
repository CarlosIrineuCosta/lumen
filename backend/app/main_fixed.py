from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import pathlib

# Import Firebase configuration
from .firebase_config import firebase_config
from .api.endpoints import auth, users, photos

# Load environment variables from backend directory
backend_dir = pathlib.Path(__file__).parent.parent
env_file = backend_dir / '.env'
if env_file.exists():
    load_dotenv(env_file)
    print(f"Loaded .env from: {env_file}")
else:
    print(f"Warning: .env file not found at {env_file}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Lumen API",
    description="Artistic Photography Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - CRITICAL FIX
# Parse ALLOWED_ORIGINS from environment and ensure proper configuration
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_str:
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]
else:
    # Default fallback origins
    allowed_origins = [
        "http://localhost:8000",
        "http://localhost:8080", 
        "http://100.106.201.33:8000",
        "http://100.106.201.33:8080",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080"
    ]

logger.info(f"CORS Allowed Origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Mount static storage directory for local development
storage_path = os.getenv("STORAGE_BASE_PATH", "/home/cdc/lumen-dev-storage")
if os.path.exists(storage_path):
    app.mount("/storage", StaticFiles(directory=storage_path), name="storage")
    logger.info(f"Mounted storage directory: {storage_path}")

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(photos.router, prefix="/api/v1/photos", tags=["photos"])

@app.get("/")
async def root():
    return {
        "message": "Lumen API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "cors_origins": allowed_origins,
        "storage_mounted": os.path.exists(storage_path)
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)