---
description: Local development environment manager with auto-restart
---

# Development Environment Manager

Manage local development servers with auto-restart for $ARGUMENTS:

## Initialize and Validate Project Structure

```bash
# Load structure detection library
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source "$SCRIPT_DIR/lib/structure-validator.sh"

# Validate project context and initialize structure
if ! check_project_context || ! init_project_structure; then
    echo "❌ Failed to initialize project structure"
    exit 1
fi

echo "✅ Project structure validated"
validate_critical_files
```

## 1. Start Development Services

### Backend with Auto-Restart
```bash
if [[ -z "$BACKEND_DIR" ]]; then
    echo "❌ Backend directory not detected"
    exit 1
fi

echo "🚀 Starting backend server..."
cd "$BACKEND_DIR"

# Validate virtual environment
if [[ ! -f "$PYTHON_VENV/bin/activate" ]]; then
    echo "❌ Python virtual environment not found at: $PYTHON_VENV"
    echo "Please create virtual environment: python -m venv venv"
    exit 1
fi

source "$PYTHON_VENV/bin/activate"

# Stop any existing backend processes
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "uvicorn.*main:app" 2>/dev/null || true

# Verify main.py exists
MAIN_PY="$BACKEND_DIR/app/main.py"
if [[ ! -f "$MAIN_PY" ]]; then
    echo "❌ FastAPI main.py not found at: $MAIN_PY"
    exit 1
fi

# Start with auto-reload (restarts on .py file changes)
echo "Starting backend with auto-restart on file changes..."
echo "Backend directory: $BACKEND_DIR"
echo "Virtual environment: $PYTHON_VENV"

nohup python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080 > server.log 2>&1 &

BACKEND_PID=$(pgrep -f 'uvicorn.*app.main:app' || echo "unknown")
echo "Backend started with PID: $BACKEND_PID"
echo "Logs: tail -f $BACKEND_DIR/server.log"
```

### Frontend Server  
```bash
if [[ -z "$FRONTEND_DIR" ]]; then
    echo "❌ Frontend directory not detected"
    exit 1
fi

echo "🌐 Starting frontend server..."
cd "$FRONTEND_DIR"

# Validate main HTML file exists
if [[ ! -f "$FRONTEND_DIR/lumen-app.html" ]] && [[ ! -f "$FRONTEND_DIR/index.html" ]]; then
    echo "❌ No main HTML file found in: $FRONTEND_DIR"
    echo "Expected: lumen-app.html or index.html"
    exit 1
fi

# Stop any existing frontend processes  
pkill -f "python3 -m http.server 8000" 2>/dev/null || true

# Start frontend server
echo "Starting frontend server..."
echo "Frontend directory: $FRONTEND_DIR"

nohup python3 -m http.server 8000 > webserver.log 2>&1 &

FRONTEND_PID=$(pgrep -f 'python3 -m http.server 8000' || echo "unknown")
echo "Frontend started with PID: $FRONTEND_PID" 
echo "Logs: tail -f $FRONTEND_DIR/webserver.log"
```

## 2. Development URLs

### Service Access Points
```bash
echo "=== DEVELOPMENT SERVICES ==="
get_project_urls

# Show specific file paths detected
if [[ -f "$FRONTEND_DIR/lumen-app.html" ]]; then
    echo "Main App: http://100.106.201.33:8000/lumen-app.html"
fi

# List available HTML test clients
echo ""
echo "Available HTML files in frontend:"
find "$FRONTEND_DIR" -name "*.html" -maxdepth 1 -printf "  http://100.106.201.33:8000/%f\n" 2>/dev/null || echo "  No HTML files found"
```

## 3. Cache Management

### Clear Development Caches
```bash
echo "=== CLEARING DEVELOPMENT CACHES ==="

# Clear Redis cache if running
redis-cli FLUSHALL 2>/dev/null && echo "Redis cache cleared" || echo "Redis not running or accessible"

# Clear Python bytecode cache from detected backend directory
if [[ -n "$BACKEND_DIR" ]]; then
    echo "Clearing Python cache from: $BACKEND_DIR"
    find "$BACKEND_DIR" -name "*.pyc" -delete 2>/dev/null || true
    find "$BACKEND_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    echo "Python bytecode cache cleared"
else
    echo "⚠️  Backend directory not detected - skipping Python cache clear"
fi

# Clear log files if they exist
if [[ -n "$BACKEND_DIR" ]] && [[ -f "$BACKEND_DIR/server.log" ]]; then
    echo "Clearing backend logs..."
    > "$BACKEND_DIR/server.log"
fi

if [[ -n "$FRONTEND_DIR" ]] && [[ -f "$FRONTEND_DIR/webserver.log" ]]; then
    echo "Clearing frontend logs..." 
    > "$FRONTEND_DIR/webserver.log"
fi

# Remind about browser cache
echo ""
echo "REMEMBER: Clear browser cache for frontend changes:"
echo "  - Chrome/Firefox: Ctrl+Shift+R (hard refresh)"
echo "  - Or open DevTools and right-click refresh button"
```

## 4. Service Health Checks

### Verify Services Started
```bash
sleep 2
echo "=== SERVICE STATUS CHECK ==="

# Backend health check
if curl -s http://100.106.201.33:8080/health >/dev/null 2>&1; then
    echo "✅ Backend: Running and healthy"
    echo "   URL: http://100.106.201.33:8080"
else
    echo "❌ Backend: Not responding"
    if [[ -n "$BACKEND_DIR" ]] && [[ -f "$BACKEND_DIR/server.log" ]]; then
        echo "   Check logs: tail -f $BACKEND_DIR/server.log"
        echo "   Recent errors:"
        tail -5 "$BACKEND_DIR/server.log" | sed 's/^/     /'
    else
        echo "   No log file found"
    fi
fi

# Frontend health check  
if curl -s -I http://100.106.201.33:8000/ >/dev/null 2>&1; then
    echo "✅ Frontend: Running and accessible"
    echo "   URL: http://100.106.201.33:8000"
else
    echo "❌ Frontend: Not responding"
    if [[ -n "$FRONTEND_DIR" ]] && [[ -f "$FRONTEND_DIR/webserver.log" ]]; then
        echo "   Check logs: tail -f $FRONTEND_DIR/webserver.log"
    else
        echo "   No log file found"
    fi
fi

# Process status
echo ""
echo "Running processes:"
ps aux | grep -E "(uvicorn|http\.server)" | grep -v grep | while read line; do
    echo "  $line"
done

# Show detected paths for reference
echo ""
echo "Detected project structure:"
echo "  Backend: $BACKEND_DIR"
echo "  Frontend: $FRONTEND_DIR" 
echo "  Scripts: $SCRIPTS_DIR"
```

## 5. Stop Development Services

### Graceful Shutdown
```bash
echo "=== STOPPING DEVELOPMENT SERVICES ==="

# Stop backend
pkill -f "uvicorn app.main:app" && echo "Backend stopped" || echo "Backend not running"

# Stop frontend
pkill -f "python3 -m http.server 8000" && echo "Frontend stopped" || echo "Frontend not running"

# Verify shutdown
sleep 1
if pgrep -f "(uvicorn|http\.server)" >/dev/null; then
    echo "⚠️  Some processes still running:"
    ps aux | grep -E "(uvicorn|http\.server)" | grep -v grep
else
    echo "✅ All development services stopped"
fi
```

## 6. Development Workflow Commands

### Quick Restart (Both Services)
```bash
echo "=== QUICK RESTART ==="

# Use server manager if available
if [[ -n "$SCRIPTS_DIR" ]] && [[ -x "$SCRIPTS_DIR/server-manager.sh" ]]; then
    echo "Using server manager for restart..."
    "$SCRIPTS_DIR/server-manager.sh" restart
else
    echo "Manual restart (server manager not found)..."
    
    # Stop services
    pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
    pkill -f "python3 -m http.server 8000" 2>/dev/null || true
    
    sleep 2
    
    # Clear caches
    if [[ -n "$BACKEND_DIR" ]]; then
        find "$BACKEND_DIR" -name "*.pyc" -delete 2>/dev/null || true
    fi
    
    # Restart backend
    if [[ -n "$BACKEND_DIR" ]] && [[ -n "$PYTHON_VENV" ]]; then
        cd "$BACKEND_DIR"
        source "$PYTHON_VENV/bin/activate"
        nohup python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080 > server.log 2>&1 &
    fi
    
    # Restart frontend
    if [[ -n "$FRONTEND_DIR" ]]; then
        cd "$FRONTEND_DIR"
        nohup python3 -m http.server 8000 > webserver.log 2>&1 &
    fi
    
    echo "Services restarted with cache clear"
fi
```

### Backend Only Restart
```bash
echo "=== BACKEND RESTART ==="

if [[ -z "$BACKEND_DIR" ]] || [[ -z "$PYTHON_VENV" ]]; then
    echo "❌ Backend configuration not detected"
    exit 1
fi

pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
sleep 2

cd "$BACKEND_DIR"
source "$PYTHON_VENV/bin/activate"
nohup python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080 > server.log 2>&1 &

echo "Backend restarted from: $BACKEND_DIR"
echo "Using venv: $PYTHON_VENV"
```

## 7. Debugging Support

### Show Recent Logs
```bash
echo "=== RECENT LOGS ==="

# Backend logs
if [[ -n "$BACKEND_DIR" ]] && [[ -f "$BACKEND_DIR/server.log" ]]; then
    echo "Backend logs (last 20 lines):"
    tail -n 20 "$BACKEND_DIR/server.log" 2>/dev/null || echo "  Error reading backend logs"
else
    echo "Backend logs: Not found at $BACKEND_DIR/server.log"
fi

echo ""

# Frontend logs  
if [[ -n "$FRONTEND_DIR" ]] && [[ -f "$FRONTEND_DIR/webserver.log" ]]; then
    echo "Frontend logs (last 10 lines):"
    tail -n 10 "$FRONTEND_DIR/webserver.log" 2>/dev/null || echo "  Error reading frontend logs"
else
    echo "Frontend logs: Not found at $FRONTEND_DIR/webserver.log"
fi
```

### Live Log Monitoring
```bash
echo "=== LIVE LOG MONITORING ==="
echo "To monitor logs in real-time:"

if [[ -n "$BACKEND_DIR" ]]; then
    echo "  Backend:  tail -f $BACKEND_DIR/server.log"
fi

if [[ -n "$FRONTEND_DIR" ]]; then
    echo "  Frontend: tail -f $FRONTEND_DIR/webserver.log"
fi

if [[ -n "$BACKEND_DIR" ]] && [[ -n "$FRONTEND_DIR" ]]; then
    echo "  Both:     tail -f $BACKEND_DIR/server.log -f $FRONTEND_DIR/webserver.log"
fi
```

## Auto-Restart Features

The backend server uses `--reload` flag which automatically restarts when:
- Python files (*.py) are modified
- Configuration files change
- Requirements are updated

For frontend changes:
- Static files (HTML, CSS, JS) are served fresh on each request
- No restart needed for content changes
- Browser cache may need manual refresh

## Notes

- Services run on Tailscale network (100.106.201.33)
- Background processes continue after terminal closes
- Log files rotate automatically to prevent disk usage
- Redis cache clearing prevents stale data issues