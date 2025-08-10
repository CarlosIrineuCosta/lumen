#!/bin/bash
# Lumen Backend Startup Script for Linux

echo "Starting Lumen Backend Server..."
echo

# Navigate to backend directory  
cd /home/cdc/Storage/NVMe/projects/wasenet/lumen-gcp/backend

# Activate virtual environment (Linux)
source venv/bin/activate

# Set environment variables
export GOOGLE_APPLICATION_CREDENTIALS=firebase_service_account.json
export ALLOWED_ORIGINS=http://localhost:8000,http://localhost:3000,http://100.106.201.33:8000

echo "Starting FastAPI server on http://100.106.201.33:8080"
echo "API docs at: http://100.106.201.33:8080/docs"
echo

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080