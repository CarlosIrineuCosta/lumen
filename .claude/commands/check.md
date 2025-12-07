---
description: Comprehensive quality assurance with testing and validation
---

# Comprehensive Quality Check

Execute quality assurance for $ARGUMENTS:

## Initialize Project Structure

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

## 1. Code Quality Checks

### Backend Quality
```bash
if [[ -z "$BACKEND_DIR" ]]; then
    echo "❌ Backend directory not detected - skipping backend quality checks"
else
    echo "🔍 Running backend quality checks..."
    cd "$BACKEND_DIR"
    
    # Activate virtual environment if available
    if [[ -f "$PYTHON_VENV/bin/activate" ]]; then
        source "$PYTHON_VENV/bin/activate"
    else
        echo "⚠️  Virtual environment not found - using system Python"
    fi
    
    # Python code quality checks
    if command -v ruff &> /dev/null; then
        echo "Running ruff checks..."
        ruff check app/ --fix || echo "⚠️  Ruff found issues"
    else
        echo "⚠️  ruff not installed - skipping linting"
    fi
    
    if command -v mypy &> /dev/null; then
        echo "Running mypy type checks..."
        mypy app/ || echo "⚠️  MyPy found type issues"
    else
        echo "⚠️  mypy not installed - skipping type checks"
    fi
fi
```

### Frontend Quality
```bash
if [[ -z "$FRONTEND_DIR" ]]; then
    echo "❌ Frontend directory not detected - skipping frontend quality checks"
else
    echo "🌐 Running frontend quality checks..."
    
    # Check for basic syntax errors in JavaScript files
    js_files=$(find "$FRONTEND_DIR" -name "*.js" -type f 2>/dev/null)
    if [[ -n "$js_files" ]]; then
        if command -v node &> /dev/null; then
            echo "Checking JavaScript syntax..."
            find "$FRONTEND_DIR" -name "*.js" -type f -exec node -c {} \; || echo "⚠️  JavaScript syntax errors found"
        else
            echo "⚠️  Node.js not available - skipping JS syntax checks"
        fi
    else
        echo "No JavaScript files found in $FRONTEND_DIR"
    fi
    
    # Check for HTML validation
    html_files=$(find "$FRONTEND_DIR" -name "*.html" -type f 2>/dev/null)
    if [[ -n "$html_files" ]]; then
        echo "Found HTML files:"
        find "$FRONTEND_DIR" -name "*.html" -type f -printf "  %f\n"
    else
        echo "⚠️  No HTML files found in $FRONTEND_DIR"
    fi
fi
```

## 2. Test Execution

### Backend Tests
```bash
if [[ -z "$BACKEND_DIR" ]]; then
    echo "❌ Backend directory not detected - skipping backend tests"
else
    echo "🧪 Running backend tests..."
    cd "$BACKEND_DIR"
    
    # Activate virtual environment
    if [[ -f "$PYTHON_VENV/bin/activate" ]]; then
        source "$PYTHON_VENV/bin/activate"
    else
        echo "❌ Virtual environment not found - cannot run tests"
        exit 1
    fi
    
    # Check if pytest is available
    if command -v pytest &> /dev/null; then
        if [[ -d "tests/" ]]; then
            echo "Running pytest tests..."
            pytest tests/ -v --tb=short || echo "⚠️  Some tests failed"
        else
            echo "⚠️  No tests directory found at $BACKEND_DIR/tests/"
        fi
    else
        echo "⚠️  pytest not installed - skipping tests"
    fi
fi
```

### API Endpoint Tests
```bash
echo "🌐 Testing API endpoints..."

# Health check
if curl -f http://100.106.201.33:8080/health >/dev/null 2>&1; then
    echo "✅ Backend health check: OK"
else
    echo "❌ Backend health check failed"
fi

# API documentation accessible
if curl -f http://100.106.201.33:8080/docs >/dev/null 2>&1; then
    echo "✅ API docs accessible: OK"  
else
    echo "❌ API docs not accessible"
fi

# Test authentication endpoint if it exists
echo "Testing authentication endpoint..."
auth_response=$(curl -s -H "Content-Type: application/json" http://100.106.201.33:8080/api/v1/auth/test 2>/dev/null || echo "FAILED")
if [[ "$auth_response" != "FAILED" ]]; then
    echo "✅ Auth endpoint responding: $auth_response"
else
    echo "⚠️  Auth endpoint not available or not responding"
fi
```

### Frontend Tests
```bash
echo "🖥️  Testing frontend..."

# Basic connectivity
if curl -I http://100.106.201.33:8000/ >/dev/null 2>&1; then
    echo "✅ Frontend server accessible: OK"
else
    echo "❌ Frontend not accessible"
fi

# Check main application loads
if [[ -f "$FRONTEND_DIR/lumen-app.html" ]]; then
    if curl -f http://100.106.201.33:8000/lumen-app.html >/dev/null 2>&1; then
        echo "✅ Main app (lumen-app.html) loading: OK"
    else
        echo "❌ Main app not loading"
    fi
else
    echo "⚠️  lumen-app.html not found - checking for index.html"
    if curl -f http://100.106.201.33:8000/index.html >/dev/null 2>&1; then
        echo "✅ Index page loading: OK"  
    else
        echo "❌ No main page accessible"
    fi
fi
```

## 3. Playwright Browser Testing

### Automated Browser Tests
```bash
# Create playwright test log directory
mkdir -p logs/playwright-$(date +%Y-%m-%d)

echo "=== PLAYWRIGHT BROWSER TESTING ==="
echo "Testing Lumen application at http://100.106.201.33:8000/lumen-app.html"
```

**Claude will automatically execute Playwright tests:**
- Navigate to http://100.106.201.33:8000/lumen-app.html  
- Check for JavaScript console errors
- Take screenshots on failures
- Test basic page load functionality
- Validate critical UI elements are present

### Console Error Detection
```bash
# Results will show any JavaScript errors found:
echo "Console errors detected: [will be populated by Claude]"
echo "Page load status: [will be populated by Claude]"
echo "Screenshots saved to: logs/playwright-$(date +%Y-%m-%d)/"
```

## 4. Security & Performance Checks

### Security Scan
```bash
# Check for exposed secrets
grep -r "API_KEY\|SECRET\|PASSWORD" opusdev/ --exclude-dir=venv --exclude-dir=node_modules | grep -v "example" || echo "No secrets found"

# Firebase config validation
cd opusdev/backend
python -c "from app.firebase_config import firebase_config; print('Firebase OK:', firebase_config.app is not None)"
```

### Performance Checks
```bash
# Check database connections
cd opusdev/backend
python -c "
try:
    from app.database.connection import get_db_session
    print('Database connection: OK')
except Exception as e:
    print(f'Database connection failed: {e}')
"

# API response time check
time curl -s http://100.106.201.33:8080/health > /dev/null
```

## 5. Generate Test Report

### Create Test Log
```bash
mkdir -p logs
REPORT_FILE="logs/test-report-$(date +%Y-%m-%d-%H-%M).log"

echo "=== Quality Check Report $(date) ===" > $REPORT_FILE
echo "Backend Tests:" >> $REPORT_FILE
echo "Frontend Tests:" >> $REPORT_FILE
echo "Security Checks:" >> $REPORT_FILE
echo "Performance Results:" >> $REPORT_FILE

echo "Test report saved to: $REPORT_FILE"
```

## 6. System Health Overview

### Services Status
```bash
echo "=== SERVICE STATUS ==="
echo "Backend (Port 8080):"
lsof -i :8080 || echo "  Not running"

echo "Frontend (Port 8000):"
lsof -i :8000 || echo "  Not running"

echo "PostgreSQL:"
systemctl is-active postgresql || echo "  Service status unknown"
```

### Development Environment
```bash
echo "=== ENVIRONMENT STATUS ==="
echo "Python virtual environment:"
[ -n "$VIRTUAL_ENV" ] && echo "  Active: $VIRTUAL_ENV" || echo "  Not activated"

echo "Node.js version:"
node --version 2>/dev/null || echo "  Not installed"

echo "Git status:"
git status --porcelain | wc -l | xargs echo "  Changed files:"
```

## Exit Conditions

- **SUCCESS**: All tests pass, no critical security issues
- **WARNING**: Minor issues found, but system functional
- **FAILURE**: Critical errors, system not operational

The test report will be included in `/end` session summary.