# Lumen Development Commands

## Essential Development Commands

### Backend Server Management
```bash
# Start backend development server
cd lumen-gcp/backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Start backend in background (production-like)
cd lumen-gcp/backend && source venv/bin/activate
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 > server.log 2>&1 &

# View server logs
tail -f lumen-gcp/backend/server.log
```

### Frontend Server Management
```bash
# Start frontend web server
cd lumen-gcp/frontend
python3 -m http.server 8000

# Alternative port (if 8000 is busy)
cd lumen-gcp/frontend && python3 -m http.server 8001
```

### Database Operations
```bash
# Initialize database with schema (when ready)
cd lumen-gcp/backend
psql -h [CLOUD_SQL_IP] -U [USERNAME] -d lumen_db -f database/schema.sql

# Load seed data (for testing)
psql -h [CLOUD_SQL_IP] -U [USERNAME] -d lumen_db -f database/seed_data.sql
```

## Testing Commands

### Backend API Testing
```bash
# Test GCP setup
cd lumen-gcp/backend
python test_gcp_setup.py

# Test individual components
python -c "from app.firebase_config import firebase_config; print('Firebase:', firebase_config.app is not None)"
```

### Web Interface Testing
- **Test Clients**: Open `http://100.106.201.33:8000/simple-test-client.html`
- **Firebase Auth**: Open `http://100.106.201.33:8000/firebase-test-client.html`
- **Main App**: Open `http://100.106.201.33:8000/lumen-app.html`

### API Endpoint Testing
```bash
# Test public endpoints
curl http://100.106.201.33:8080/
curl http://100.106.201.33:8080/health
curl http://100.106.201.33:8080/api/v1/auth/test

# Test with authentication (requires Firebase token)
curl -H "Authorization: Bearer [FIREBASE_TOKEN]" http://100.106.201.33:8080/api/v1/auth/status
```

## Development Utilities

### Environment Management
```bash
# Activate Python virtual environment
cd lumen-gcp/backend && source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Check environment variables
cd lumen-gcp/backend && source .env && env | grep -E "(PROJECT_ID|FIREBASE|GCS)"
```

### Code Quality (When Implemented)
```bash
# Code formatting (future implementation)
# black backend/app/
# isort backend/app/

# Type checking (future implementation) 
# mypy backend/app/

# Linting (future implementation)
# ruff backend/app/
```

## Deployment Commands

### Local Deployment
```bash
# Build and deploy to Google Cloud
cd lumen-gcp
./deploy/deploy.sh [PROJECT_ID]

# Deploy with custom project
./deploy/deploy.sh lumen-photography-platform
```

### Infrastructure Management
```bash
# Initialize Terraform
cd lumen-gcp/infrastructure/terraform
terraform init

# Plan infrastructure changes
terraform plan

# Apply infrastructure changes
terraform apply

# Destroy infrastructure (careful!)
terraform destroy
```

## Monitoring Commands

### Cost Monitoring
```bash
# Check daily costs
cd lumen-gcp/infrastructure/scripts
python monitor_costs.py

# Simple cost check
python simple_cost_monitor.py
```

### Log Management
```bash
# View backend logs
tail -f lumen-gcp/backend/server.log

# View frontend access logs
tail -f lumen-gcp/frontend/webserver.log

# Google Cloud logs (when deployed)
gcloud logging read "resource.type=\"cloud_run_revision\"" --limit 50
```

## Network Access

### Service URLs
- **Backend API**: http://100.106.201.33:8080
- **API Documentation**: http://100.106.201.33:8080/docs
- **Web Application**: http://100.106.201.33:8000/lumen-app.html
- **Test Clients**: http://100.106.201.33:8000/[client-name].html

### Network Utilities
```bash
# Check if services are running
curl -I http://100.106.201.33:8080/health
curl -I http://100.106.201.33:8000/

# Check port availability
netstat -tulpn | grep :8080
netstat -tulpn | grep :8000
```

## Firebase Management

### Authentication Setup
```bash
# Run Firebase web setup guide
cd lumen-gcp/backend
python setup_firebase_web.py

# Test Firebase configuration
python -c "from app.firebase_config import firebase_config; print('Firebase initialized:', firebase_config.app is not None)"
```

## Database Management

### Connection Testing
```bash
# Test Cloud SQL connection (when configured)
cd lumen-gcp/backend
python -c "from app.database.connection import get_db_session; print('Database connection test')"
```

## Development Workflow

### Starting Development Session
```bash
# 1. Start backend
cd lumen-gcp/backend && source venv/bin/activate
nohup python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080 > server.log 2>&1 &

# 2. Start frontend  
cd lumen-gcp/frontend && python3 -m http.server 8000 &

# 3. Open development URLs
# Backend: http://100.106.201.33:8080/docs
# Frontend: http://100.106.201.33:8000/lumen-app.html
```

### Stopping Development Session
```bash
# Stop background servers
pkill -f "uvicorn app.main:app"
pkill -f "python3 -m http.server"

# Or kill specific PIDs
ps aux | grep uvicorn
kill [PID]
```

## Emergency Commands

### Service Recovery
```bash
# Restart all services
cd lumen-gcp
pkill -f uvicorn; pkill -f "http.server"
sleep 2
cd backend && source venv/bin/activate && nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 > server.log 2>&1 &
cd ../frontend && python3 -m http.server 8000 &
```

### Quick Status Check
```bash
# Check all services
echo "Backend:" && curl -s http://100.106.201.33:8080/health | head -1
echo "Frontend:" && curl -s -I http://100.106.201.33:8000/ | head -1
echo "Processes:" && ps aux | grep -E "(uvicorn|http.server)" | grep -v grep
```

## Important Notes

### Network Access
- All services accessible via Tailscale network (100.106.201.33)
- No localhost development - always use Tailscale IP
- Services can be accessed from any device on Tailscale network

### Development Philosophy
- **NO MOCKS**: Always implement real functionality
- **Background Processes**: Use `nohup` and `&` for servers
- **Real Data**: Connect to actual services (Firebase, Cloud SQL, etc.)

### File Locations
- **Backend**: `/home/cdc/projects/wasenet/lumen-gcp/backend/`
- **Frontend**: `/home/cdc/projects/wasenet/lumen-gcp/frontend/` 
- **Database**: `/home/cdc/projects/wasenet/lumen-gcp/backend/database/`
- **Infrastructure**: `/home/cdc/projects/wasenet/lumen-gcp/infrastructure/`