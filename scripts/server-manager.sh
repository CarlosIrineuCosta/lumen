#!/bin/bash
# Lumen Server Manager - Clean startup and management script

set -e

# Configuration
BACKEND_PORT=8080
FRONTEND_PORT=8000
PROJECT_ROOT="/home/cdc/Storage/NVMe/projects/lumen"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Kill processes on specific ports
kill_port() {
    local port=$1
    local pids=$(lsof -ti :$port 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        log "Killing processes on port $port: $pids"
        echo $pids | xargs kill -9 2>/dev/null || true
        sleep 2
    else
        log "Port $port is already free"
    fi
}

# Clean up all Lumen-related processes
cleanup_all() {
    log "Cleaning up all Lumen server processes..."
    
    # Kill by port
    kill_port $BACKEND_PORT
    kill_port $FRONTEND_PORT
    
    # Kill by process name patterns
    pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
    pkill -f "python.*-m.*http.server.*$FRONTEND_PORT" 2>/dev/null || true
    pkill -f "lumen-gcp" 2>/dev/null || true
    
    sleep 3
    log "Cleanup complete"
}

# Start backend server
start_backend() {
    log "Starting backend server on port $BACKEND_PORT..."
    
    if [ ! -d "$BACKEND_DIR" ]; then
        error "Backend directory not found: $BACKEND_DIR"
        exit 1
    fi
    
    cd "$BACKEND_DIR"
    
    # Activate virtual environment
    if [ ! -f "venv/bin/activate" ]; then
        error "Virtual environment not found in $BACKEND_DIR/venv"
        exit 1
    fi
    
    source venv/bin/activate
    
    # Start server in background
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT > backend.log 2>&1 &
    local backend_pid=$!
    
    # Wait for server to start
    log "Waiting for backend to start (PID: $backend_pid)..."
    sleep 5
    
    # Test connection
    if curl -s http://100.106.201.33:$BACKEND_PORT/health > /dev/null; then
        log "✅ Backend server started successfully at http://100.106.201.33:$BACKEND_PORT"
        log "   API docs: http://100.106.201.33:$BACKEND_PORT/docs"
    else
        error "❌ Backend server failed to start properly"
        tail -10 backend.log
        exit 1
    fi
}

# Start frontend server
start_frontend() {
    log "Starting frontend server on port $FRONTEND_PORT..."
    
    if [ ! -d "$FRONTEND_DIR" ]; then
        error "Frontend directory not found: $FRONTEND_DIR"
        exit 1
    fi
    
    cd "$FRONTEND_DIR"
    
    # Start server in background
    nohup python3 -m http.server $FRONTEND_PORT > frontend.log 2>&1 &
    local frontend_pid=$!
    
    # Wait for server to start
    log "Waiting for frontend to start (PID: $frontend_pid)..."
    sleep 3
    
    # Test connection
    if curl -s http://100.106.201.33:$FRONTEND_PORT > /dev/null; then
        log "✅ Frontend server started successfully at http://100.106.201.33:$FRONTEND_PORT"
        log "   App URL: http://100.106.201.33:$FRONTEND_PORT"
    else
        error "❌ Frontend server failed to start properly"
        tail -10 frontend.log
        exit 1
    fi
}

# Check server status
status() {
    log "Checking server status..."
    
    # Backend status
    if curl -s http://100.106.201.33:$BACKEND_PORT/health > /dev/null; then
        log "✅ Backend server is running at http://100.106.201.33:$BACKEND_PORT"
    else
        warn "❌ Backend server is not responding"
    fi
    
    # Frontend status
    if curl -s http://100.106.201.33:$FRONTEND_PORT > /dev/null; then
        log "✅ Frontend server is running at http://100.106.201.33:$FRONTEND_PORT"
    else
        warn "❌ Frontend server is not responding"
    fi
    
    # Show processes
    echo
    log "Active processes:"
    ps aux | grep -E "(uvicorn|http.server)" | grep -v grep || echo "No servers found"
}

# Main command handler
case "${1:-}" in
    "start")
        cleanup_all
        start_backend
        start_frontend
        status
        ;;
    "stop")
        cleanup_all
        ;;
    "restart")
        cleanup_all
        start_backend
        start_frontend
        status
        ;;
    "status")
        status
        ;;
    "clean")
        cleanup_all
        ;;
    *)
        echo "Lumen Server Manager"
        echo "Usage: $0 {start|stop|restart|status|clean}"
        echo ""
        echo "Commands:"
        echo "  start   - Clean startup of both servers"
        echo "  stop    - Stop all servers"
        echo "  restart - Stop and start all servers"
        echo "  status  - Check server status"
        echo "  clean   - Kill all server processes"
        echo ""
        echo "Backend:  http://100.106.201.33:$BACKEND_PORT"
        echo "Frontend: http://100.106.201.33:$FRONTEND_PORT"
        exit 1
        ;;
esac