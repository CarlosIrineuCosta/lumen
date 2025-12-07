#!/bin/bash

# Start the Lumen backend server using the mandatory startup script
# This prevents database connection issues by properly loading environment variables

echo "Starting Lumen backend server using mandatory startup script..."
exec ./scripts/start-server.sh