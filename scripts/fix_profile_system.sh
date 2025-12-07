#!/bin/bash

echo "Fixing Lumen Profile System..."

# Navigate to backend
cd /home/cdc/Storage/NVMe/projects/wasenet/opusdev/backend

# Stop current backend
pkill -f "uvicorn app.main:app"

# Apply database fixes
psql -U lumen_dev -d lumen_development -f database/schema_fix.sql

# Copy fixed files
cp app/main_fixed.py app/main.py
cp app/services/user_service_fixed.py app/services/user_service.py

# Restart backend with proper environment
source venv/bin/activate
export PYTHONPATH=/home/cdc/Storage/NVMe/projects/wasenet/opusdev/backend
nohup python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080 > backend.log 2>&1 &

echo "Backend restarted. Check backend.log for details."

# Update frontend
cd /home/cdc/Storage/NVMe/projects/wasenet/opusdev
cp js/app_profile_fix.js js/app.js

echo "Profile system fix complete!"
echo "Test at: http://100.106.201.33:8000"