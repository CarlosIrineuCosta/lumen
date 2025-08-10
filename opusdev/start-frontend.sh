#!/bin/bash
# Lumen Frontend Startup Script for Linux

echo "Starting Lumen Frontend Server..."
echo

# Navigate to opusdev directory
cd /home/cdc/Storage/NVMe/projects/wasenet/opusdev

echo "Starting HTTP server on http://100.106.201.33:8000"
echo "PWA will be available at: http://100.106.201.33:8000"
echo

# Start the frontend server
python3 -m http.server 8000