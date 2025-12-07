#!/bin/bash

# Quick Test Environment Setup for Lumen
# Automates the complete test environment setup in under 2 minutes
# Solves the "manual uploading and Profile testing" problem

set -e

PROJECT_ROOT="/home/cdc/Storage/NVMe/projects/lumen"
BACKEND_DIR="$PROJECT_ROOT/backend"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Process tracking
FIREBASE_PID=""
BACKEND_PID=""

echo -e "${BLUE}================================"
echo "LUMEN QUICK TEST ENVIRONMENT SETUP"
echo -e "================================${NC}"
echo "Automated solution for test data setup"
echo "Target completion: Under 2 minutes"
echo

# Function to cleanup on exit
cleanup() {
    echo -e "${YELLOW}Cleaning up processes...${NC}"
    if [[ -n "$FIREBASE_PID" ]]; then
        kill $FIREBASE_PID 2>/dev/null || true
    fi
    if [[ -n "$BACKEND_PID" ]]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    wait
}
trap cleanup EXIT

# Function to check if a service is running
check_service() {
    local url=$1
    local service_name=$2
    local max_attempts=15
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} $service_name is ready"
            return 0
        fi
        
        if [ $attempt -eq 1 ]; then
            echo -e "  ${YELLOW}Waiting for $service_name...${NC}"
        fi
        
        sleep 2
        ((attempt++))
    done
    
    echo -e "  ${RED}✗${NC} $service_name failed to start"
    return 1
}

# Function to log with timestamp
log_step() {
    echo -e "${CYAN}[$(date '+%H:%M:%S')]${NC} $1"
}

# Step 1: Prerequisites Check
log_step "Checking prerequisites..."

# Check dependencies
missing_deps=()
if ! command -v firebase &> /dev/null; then
    missing_deps+=("firebase-tools")
fi
if ! command -v python3 &> /dev/null; then
    missing_deps+=("python3")
fi
if ! command -v psql &> /dev/null; then
    missing_deps+=("postgresql-client")
fi

if [[ ${#missing_deps[@]} -ne 0 ]]; then
    echo -e "${RED}ERROR: Missing dependencies: ${missing_deps[*]}${NC}"
    exit 1
fi

# Check PostgreSQL database
if ! psql -lqt | cut -d \| -f 1 | grep -qw lumen_test; then
    echo -e "${RED}ERROR: lumen_test database not found${NC}"
    echo "Create with: createdb lumen_test"
    exit 1
fi

echo -e "  ${GREEN}✓${NC} All prerequisites satisfied"

# Step 2: Start Firebase Emulator
log_step "Starting Firebase emulator suite..."

cd "$PROJECT_ROOT"
firebase emulators:start --only auth,storage --project lumen-photo-app-20250731 > /tmp/firebase_emulator.log 2>&1 &
FIREBASE_PID=$!

# Wait for Firebase emulator
if check_service "http://localhost:9099" "Firebase Auth Emulator"; then
    if check_service "http://localhost:9199" "Firebase Storage Emulator"; then
        echo -e "  ${GREEN}✓${NC} Firebase emulator suite running (auth:9099, storage:9199)"
    else
        echo -e "${RED}ERROR: Firebase storage emulator failed${NC}"
        exit 1
    fi
else
    echo -e "${RED}ERROR: Firebase auth emulator failed${NC}"
    exit 1
fi

# Step 3: Start Backend Server
log_step "Starting backend server..."

cd "$BACKEND_DIR"
source venv/bin/activate

# Set environment variables
export TESTING=true
export FIREBASE_USE_EMULATOR=true
export DATABASE_URL="postgresql:///lumen_test"

python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 > /tmp/backend_server.log 2>&1 &
BACKEND_PID=$!

if check_service "http://localhost:8080/health" "Backend Server"; then
    echo -e "  ${GREEN}✓${NC} Backend server ready (localhost:8080)"
else
    echo -e "${RED}ERROR: Backend server failed to start${NC}"
    exit 1
fi

# Step 4: Create Test Users
log_step "Creating Firebase test users..."

if python3 "$SCRIPTS_DIR/create_test_users.py"; then
    echo -e "  ${GREEN}✓${NC} Created 13 test users with diverse profiles"
else
    echo -e "${RED}ERROR: Test user creation failed${NC}"
    exit 1
fi

# Step 5: Seed Database
log_step "Seeding PostgreSQL database..."

cd "$BACKEND_DIR"
if python3 "$SCRIPTS_DIR/seed_test_data.py"; then
    echo -e "  ${GREEN}✓${NC} Database seeded with users and sample data"
else
    echo -e "${RED}ERROR: Database seeding failed${NC}"
    exit 1
fi

# Step 6: Upload Test Photos
log_step "Generating and uploading test photos..."

if python3 "$SCRIPTS_DIR/test_photo_manager.py"; then
    echo -e "  ${GREEN}✓${NC} Test photos generated and uploaded"
else
    echo -e "${RED}ERROR: Photo upload failed${NC}"
    exit 1
fi

# Step 7: Verification
log_step "Verifying test environment..."

# Check user count
user_count=$(python3 -c "
import sys
sys.path.insert(0, '$BACKEND_DIR')
from sqlalchemy import create_engine, text
engine = create_engine('postgresql:///lumen_test')
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM users'))
    print(result.scalar())
")

# Check photo count  
photo_count=$(python3 -c "
import sys
sys.path.insert(0, '$BACKEND_DIR')
from sqlalchemy import create_engine, text
engine = create_engine('postgresql:///lumen_test')
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM photos'))
    print(result.scalar())
")

echo -e "  ${GREEN}✓${NC} Database verification:"
echo "    - Users: $user_count"
echo "    - Photos: $photo_count"

# API health check
api_status=$(curl -s http://localhost:8080/health | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "error")
echo -e "  ${GREEN}✓${NC} API Status: $api_status"

# Step 8: Environment Summary
echo
echo -e "${GREEN}========================================="
echo "TEST ENVIRONMENT SETUP COMPLETE!"
echo -e "=========================================${NC}"
echo
echo -e "${BLUE}Services Running:${NC}"
echo "  • Firebase Auth Emulator:    http://localhost:9099"
echo "  • Firebase Storage Emulator: http://localhost:9199" 
echo "  • Backend API:               http://localhost:8080"
echo "  • API Documentation:         http://localhost:8080/docs"
echo
echo -e "${BLUE}Test Data Available:${NC}"
echo "  • Test Users: $user_count (all types: photographers, models, clients, admin)"
echo "  • Test Photos: $photo_count (various categories with metadata)"
echo "  • User Connections: Social graph with follows/connections"
echo "  • Authentication: Ready for testing with Firebase emulator"
echo
echo -e "${BLUE}Credentials File:${NC}"
echo "  • Location: backend/tests/fixtures/test_credentials.json"
echo "  • Password: TestPass123! (all test users)"
echo "  • Admin: admin@lumen-test.local"
echo
echo -e "${BLUE}Quick Test Commands:${NC}"
echo "  • Run all tests:     cd backend && python -m pytest"
echo "  • Overnight runner:  ./scripts/overnight-test-runner.sh"
echo "  • UI discovery:      python3 scripts/playwright_ui_discovery.py"
echo "  • Reset test data:   python3 scripts/seed_test_data.py"
echo
echo -e "${BLUE}Frontend Testing:${NC}"
echo "  • Start frontend:    python3 -m http.server 8000"
echo "  • Access URL:        http://localhost:8000"
echo "  • UI discovery:      Will test authentication, photos, navigation"
echo
echo -e "${YELLOW}Note: Services will continue running until you stop this script (Ctrl+C)${NC}"
echo -e "${YELLOW}Tip: Open a new terminal to run tests or start the frontend${NC}"

# Keep running to maintain services
echo
echo -e "${CYAN}Test environment ready! Press Ctrl+C to stop all services.${NC}"

# Wait for user interrupt
while true; do
    sleep 10
    # Periodic health checks
    if ! curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo -e "${RED}WARNING: Backend server stopped responding${NC}"
        break
    fi
    if ! curl -s http://localhost:9099 > /dev/null 2>&1; then
        echo -e "${RED}WARNING: Firebase emulator stopped responding${NC}"
        break
    fi
done