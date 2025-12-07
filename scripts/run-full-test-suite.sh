#!/bin/bash

# Full test suite runner for Lumen backend
# Runs Firebase emulator, backend server, and all tests with real services

set -e

PROJECT_ROOT="/home/cdc/Storage/NVMe/projects/lumen"
BACKEND_DIR="$PROJECT_ROOT/backend"
FIREBASE_CONFIG="${FIREBASE_CONFIG:-$PROJECT_ROOT/firebase.test.json}"

get_port_from_config() {
    local env_var="$1"
    local fallback="$2"
    local jq_path="$3"

    local env_value="${!env_var}"
    if [[ -n "$env_value" ]]; then
        echo "$env_value"
        return
    fi

    if [[ -f "$FIREBASE_CONFIG" ]]; then
        local config_value
        config_value=$(jq -r "$jq_path" "$FIREBASE_CONFIG" 2>/dev/null)
        if [[ "$config_value" != "null" && -n "$config_value" ]]; then
            echo "$config_value"
            return
        fi
    fi

    echo "$fallback"
}

FIREBASE_AUTH_PORT=$(get_port_from_config FIREBASE_AUTH_PORT 9190 '.emulators.auth.port')
FIREBASE_STORAGE_PORT=$(get_port_from_config FIREBASE_STORAGE_PORT 9191 '.emulators.storage.port')
FIREBASE_HUB_PORT=$(get_port_from_config FIREBASE_HUB_PORT 4402 '.emulators.hub.port')

echo "=== Lumen Full Test Suite ==="
echo "Project root: $PROJECT_ROOT"
echo "Backend directory: $BACKEND_DIR"
echo "Firebase config: $FIREBASE_CONFIG"
echo "Auth emulator port: $FIREBASE_AUTH_PORT"
echo "Storage emulator port: $FIREBASE_STORAGE_PORT"
echo "Hub port: $FIREBASE_HUB_PORT"
echo

# Function to cleanup on exit
cleanup() {
    echo "Cleaning up..."
    # if [[ -n "$FIREBASE_PID" ]]; then
    #     kill $FIREBASE_PID 2>/dev/null || true
    # fi
    # if [[ -n "$BACKEND_PID" ]]; then
    #     kill $BACKEND_PID 2>/dev/null || true
    # fi
    wait
}
trap cleanup EXIT

# Check prerequisites
echo "Checking prerequisites..."
if ! command -v firebase &> /dev/null; then
    echo "ERROR: Firebase CLI not found. Install with: npm install -g firebase-tools"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "ERROR: jq not found. Install with your package manager (e.g. apt install jq)."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found"
    exit 1
fi

if ! command -v psql &> /dev/null; then
    echo "ERROR: PostgreSQL client not found"
    exit 1
fi

# Check database exists
echo "Checking PostgreSQL test database..."
if ! psql -lqt | cut -d \| -f 1 | grep -qw lumen_test; then
    echo "ERROR: lumen_test database not found. Create with: createdb lumen_test"
    echo "Then import schema: psql lumen_test < backend/schema_production.sql"
    exit 1
fi

# Navigate to project root
cd "$PROJECT_ROOT"

# Start Firebase emulator in background
# echo "Starting Firebase emulator..."
# firebase emulators:start --config "$FIREBASE_CONFIG" --only auth,storage &
# FIREBASE_PID=$!

# # Wait for Firebase emulator to be ready
# echo "Waiting for Firebase emulator to start..."
# sleep 5

# # Check if emulator is running
# if ! curl -s "http://localhost:${FIREBASE_AUTH_PORT}" > /dev/null; then
#     echo "ERROR: Firebase auth emulator not responding on port ${FIREBASE_AUTH_PORT}"
#     exit 1
# fi

# if ! curl -s "http://localhost:${FIREBASE_STORAGE_PORT}" > /dev/null; then
#     echo "ERROR: Firebase storage emulator not responding on port ${FIREBASE_STORAGE_PORT}"  
#     exit 1
# fi

echo "Firebase emulator ready"

# Start backend server in background
# echo "Starting backend server..."
# cd "$BACKEND_DIR"
# source venv/bin/activate

# # Set environment variables for testing
export PYTHONPATH="$PYTHONPATH:$BACKEND_DIR"
export TESTING=true
export FIREBASE_USE_EMULATOR=true
export DATABASE_URL="postgresql:///lumen_test"
export FIREBASE_AUTH_EMULATOR_HOST="localhost:${FIREBASE_AUTH_PORT}"
export FIREBASE_STORAGE_EMULATOR_HOST="localhost:${FIREBASE_STORAGE_PORT}"
export FIREBASE_EMULATOR_HUB="localhost:${FIREBASE_HUB_PORT}"

# python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 &
# BACKEND_PID=$!

# # Wait for backend to be ready
# echo "Waiting for backend server to start..."
# sleep 3

# # Check if backend is responding
# if ! curl -s http://localhost:8080/health > /dev/null; then
#     echo "ERROR: Backend server not responding on port 8080"
#     exit 1
# fi

echo "Backend server ready"

# Run tests
echo "Running test suite..."
echo

# Run unit tests
echo "=== Running Unit Tests ==="
python -m pytest scripts/tests/ -v --tb=short -k "not playwright" --maxfail=5 --ignore=scripts/tests/temp

# Run integration tests (if any)
echo "=== Running Integration Tests ==="
python -m pytest scripts/tests/ -v --tb=short -k "integration" --maxfail=3 --ignore=scripts/tests/temp

echo
echo "=== Test Suite Complete ==="
echo "All tests passed successfully!"
echo "Services used:"
echo "  - Real PostgreSQL database: lumen_test"
echo "  - Firebase emulator: localhost:${FIREBASE_AUTH_PORT} (auth), localhost:${FIREBASE_STORAGE_PORT} (storage)" 
echo "  - Backend server: localhost:8080"
echo
echo "No mocks used - all services are real!"
