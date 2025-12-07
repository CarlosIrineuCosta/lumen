#!/bin/bash
# Deployment script for optimized Lumen storage on EDIS server

set -e  # Exit on any error

REMOTE_HOST="edis-lumen"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/lumen/backups"
DEPLOYMENT_LOG="/tmp/lumen-deploy-${TIMESTAMP}.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$DEPLOYMENT_LOG"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" | tee -a "$DEPLOYMENT_LOG"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}" | tee -a "$DEPLOYMENT_LOG"
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}" | tee -a "$DEPLOYMENT_LOG"
}

# Validate prerequisites
check_prerequisites() {
    log "Checking deployment prerequisites..."
    
    # Check SSH connectivity
    if ! ssh -o ConnectTimeout=10 "$REMOTE_HOST" "echo 'SSH connection successful'"; then
        error "Cannot connect to EDIS server via SSH"
    fi
    
    # Check local files exist
    if [[ ! -f "backend/app/storage/local_storage.py" ]]; then
        error "Storage files not found. Run from project root directory."
    fi
    
    success "Prerequisites check passed"
}

# Create backup of current deployment
create_backup() {
    log "Creating backup of current deployment..."
    
    ssh "$REMOTE_HOST" bash << 'EOF'
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        BACKUP_DIR="/opt/lumen/backups"
        
        mkdir -p "$BACKUP_DIR"
        
        # Backup current backend if exists
        if [[ -d "/opt/lumen/backend" ]]; then
            tar -czf "$BACKUP_DIR/backend-backup-$TIMESTAMP.tar.gz" -C "/opt/lumen" backend
            echo "Backend backup created: backend-backup-$TIMESTAMP.tar.gz"
        fi
        
        # Backup current frontend if exists
        if [[ -d "/opt/lumen/frontend" ]]; then
            tar -czf "$BACKUP_DIR/frontend-backup-$TIMESTAMP.tar.gz" -C "/opt/lumen" frontend
            echo "Frontend backup created: frontend-backup-$TIMESTAMP.tar.gz"
        fi
        
        # Backup nginx config if exists
        if [[ -f "/etc/nginx/sites-available/lumen" ]]; then
            cp "/etc/nginx/sites-available/lumen" "$BACKUP_DIR/nginx-lumen-$TIMESTAMP.conf"
            echo "Nginx config backup created: nginx-lumen-$TIMESTAMP.conf"
        fi
        
        # List backups
        echo "Available backups:"
        ls -la "$BACKUP_DIR" | tail -5
EOF
    
    success "Backup completed"
}

# Deploy backend with optimized storage
deploy_backend() {
    log "Deploying optimized backend..."
    
    # Create deployment package
    log "Creating backend deployment package..."
    tar -czf "/tmp/lumen-backend-optimized-${TIMESTAMP}.tar.gz" \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='test.db' \
        --exclude='*.log' \
        --exclude='tests' \
        --exclude='.git' \
        backend/
    
    # Transfer to EDIS server
    log "Transferring backend to EDIS server..."
    scp "/tmp/lumen-backend-optimized-${TIMESTAMP}.tar.gz" "$REMOTE_HOST:/tmp/"
    
    # Deploy on server
    ssh "$REMOTE_HOST" bash << EOF
        cd /tmp
        
        # Extract new backend
        mkdir -p /opt/lumen/backend-new
        tar -xzf "lumen-backend-optimized-${TIMESTAMP}.tar.gz" -C /opt/lumen/backend-new --strip-components=1
        
        # Setup virtual environment if doesn't exist
        if [[ ! -d "/opt/lumen/backend-new/venv" ]]; then
            echo "Creating Python virtual environment..."
            python3 -m venv /opt/lumen/backend-new/venv
        fi
        
        # Install/update dependencies
        echo "Installing dependencies..."
        source /opt/lumen/backend-new/venv/bin/activate
        pip install --upgrade pip
        pip install -r /opt/lumen/backend-new/requirements.txt
        
        # Install additional dependencies for optimized storage
        pip install pillow>=10.0.0 aiofiles>=23.0.0 redis>=4.0.0
        
        # Move old backend and activate new one
        if [[ -d "/opt/lumen/backend" ]]; then
            mv /opt/lumen/backend /opt/lumen/backend-old-${TIMESTAMP}
        fi
        mv /opt/lumen/backend-new /opt/lumen/backend
        
        # Set permissions
        chown -R www-data:www-data /opt/lumen/backend
        chmod -R 755 /opt/lumen/backend
        
        echo "Backend deployment completed"
EOF
    
    success "Backend deployed successfully"
}

# Setup storage directories
setup_storage() {
    log "Setting up optimized storage structure..."
    
    ssh "$REMOTE_HOST" bash << 'EOF'
        # Create storage directory structure
        mkdir -p /opt/lumen/storage/{images,cache,temp,metadata,backups}
        
        # Create size-specific directories
        for size in thumb small medium large original; do
            mkdir -p "/opt/lumen/storage/images/$size"
            mkdir -p "/opt/lumen/storage/cache/$size"
        done
        
        # Set permissions
        chown -R www-data:www-data /opt/lumen/storage
        chmod -R 755 /opt/lumen/storage
        
        # Create cache directory for nginx
        mkdir -p /var/cache/nginx/lumen
        chown -R www-data:www-data /var/cache/nginx/lumen
        
        echo "Storage structure created:"
        tree -d /opt/lumen/storage/ -L 3 || ls -la /opt/lumen/storage/
EOF
    
    success "Storage structure setup completed"
}

# Deploy optimized nginx configuration
deploy_nginx_config() {
    log "Deploying optimized Nginx configuration..."
    
    # Transfer nginx config
    scp "config/nginx/lumen-optimized.conf" "$REMOTE_HOST:/tmp/lumen-optimized.conf"
    
    ssh "$REMOTE_HOST" bash << 'EOF'
        # Backup current config
        if [[ -f "/etc/nginx/sites-available/lumen" ]]; then
            cp /etc/nginx/sites-available/lumen /opt/lumen/backups/nginx-backup-$(date +%Y%m%d_%H%M%S).conf
        fi
        
        # Install new config
        mv /tmp/lumen-optimized.conf /etc/nginx/sites-available/lumen
        
        # Enable site
        ln -sf /etc/nginx/sites-available/lumen /etc/nginx/sites-enabled/
        rm -f /etc/nginx/sites-enabled/default
        
        # Test configuration
        if nginx -t; then
            echo "Nginx configuration test passed"
        else
            echo "Nginx configuration test failed!"
            exit 1
        fi
EOF
    
    success "Nginx configuration deployed"
}

# Setup environment configuration
setup_environment() {
    log "Setting up production environment..."
    
    ssh "$REMOTE_HOST" bash << 'EOF'
        # Create production environment file
        cat > /opt/lumen/backend/.env << 'ENVEOF'
# Environment
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://lumen:LumenDB2025!@localhost/lumen_production
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lumen_production
DB_USER=lumen
DB_PASSWORD=LumenDB2025!

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=LumenRedis2025!

# Storage Configuration
STORAGE_PATH=/opt/lumen/storage
MAX_STORAGE_GB=40
CACHE_TTL_DAYS=7
IMAGE_BASE_URL=http://83.172.136.127/images

# CORS
ALLOWED_ORIGINS=http://83.172.136.127,https://83.172.136.127,http://83.172.136.127:8080

# Security
SECRET_KEY=$(openssl rand -hex 32)

# Performance
UVICORN_WORKERS=2
UVICORN_MAX_REQUESTS=1000
ENVEOF
        
        # Set permissions
        chown www-data:www-data /opt/lumen/backend/.env
        chmod 600 /opt/lumen/backend/.env
        
        echo "Environment configuration created"
EOF
    
    success "Environment setup completed"
}

# Setup systemd service
setup_systemd_service() {
    log "Setting up systemd service..."
    
    ssh "$REMOTE_HOST" bash << 'EOF'
        # Create systemd service file
        cat > /etc/systemd/system/lumen-backend.service << 'SERVICEEOF'
[Unit]
Description=Lumen Photography Platform API (Optimized)
After=network.target postgresql.service redis.service
Requires=postgresql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/lumen/backend
Environment=PATH=/opt/lumen/backend/venv/bin
EnvironmentFile=/opt/lumen/backend/.env
ExecStart=/opt/lumen/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8080 --workers 2
Restart=always
RestartSec=3
StandardOutput=append:/var/log/lumen/backend.log
StandardError=append:/var/log/lumen/backend-error.log

# Performance tunings
LimitNOFILE=65536
KillMode=mixed
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
SERVICEEOF
        
        # Create log directory
        mkdir -p /var/log/lumen
        chown www-data:www-data /var/log/lumen
        
        # Reload systemd and enable service
        systemctl daemon-reload
        systemctl enable lumen-backend
        
        echo "Systemd service configured"
EOF
    
    success "Systemd service setup completed"
}

# Start services
start_services() {
    log "Starting services..."
    
    ssh "$REMOTE_HOST" bash << 'EOF'
        # Start backend service
        systemctl restart lumen-backend
        sleep 5
        
        # Check backend status
        if systemctl is-active --quiet lumen-backend; then
            echo "Backend service started successfully"
        else
            echo "Backend service failed to start"
            systemctl status lumen-backend --no-pager
            exit 1
        fi
        
        # Reload nginx
        systemctl reload nginx
        
        # Check nginx status
        if systemctl is-active --quiet nginx; then
            echo "Nginx service running"
        else
            echo "Nginx service failed"
            systemctl status nginx --no-pager
            exit 1
        fi
EOF
    
    success "Services started successfully"
}

# Run health checks
run_health_checks() {
    log "Running health checks..."
    
    ssh "$REMOTE_HOST" bash << 'EOF'
        echo "Checking service status..."
        systemctl status lumen-backend --no-pager | head -10
        systemctl status nginx --no-pager | head -10
        systemctl status postgresql --no-pager | head -10
        systemctl status redis-server --no-pager | head -10
        
        echo "Testing API endpoints..."
        
        # Test health endpoint
        if curl -s http://127.0.0.1:8080/health | grep -q "healthy\|ok"; then
            echo "✓ Backend health check passed"
        else
            echo "✗ Backend health check failed"
        fi
        
        # Test through nginx
        if curl -s http://83.172.136.127/health | grep -q "healthy\|ok"; then
            echo "✓ Nginx proxy health check passed"
        else
            echo "✗ Nginx proxy health check failed"
        fi
        
        # Check storage directory
        if [[ -d "/opt/lumen/storage" ]]; then
            echo "✓ Storage directory exists"
            du -sh /opt/lumen/storage/
        else
            echo "✗ Storage directory missing"
        fi
        
        # Check Redis connectivity
        if redis-cli ping | grep -q "PONG"; then
            echo "✓ Redis connection working"
        else
            echo "✗ Redis connection failed"
        fi
EOF
    
    success "Health checks completed"
}

# Main deployment function
main() {
    log "Starting Lumen optimized storage deployment to EDIS server"
    log "Deployment log: $DEPLOYMENT_LOG"
    
    check_prerequisites
    create_backup
    deploy_backend
    setup_storage
    deploy_nginx_config
    setup_environment
    setup_systemd_service
    start_services
    run_health_checks
    
    success "Deployment completed successfully!"
    
    echo ""
    echo -e "${GREEN}===========================================${NC}"
    echo -e "${GREEN}   LUMEN OPTIMIZED DEPLOYMENT COMPLETE   ${NC}"
    echo -e "${GREEN}===========================================${NC}"
    echo ""
    echo -e "Frontend URL: ${BLUE}http://83.172.136.127${NC}"
    echo -e "API URL: ${BLUE}http://83.172.136.127/api${NC}"
    echo -e "API Docs: ${BLUE}http://83.172.136.127/docs${NC}"
    echo -e "Health Check: ${BLUE}http://83.172.136.127/health${NC}"
    echo ""
    echo -e "Deployment log saved to: ${BLUE}$DEPLOYMENT_LOG${NC}"
    echo ""
    
    # Show next steps
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Test image upload functionality"
    echo "2. Monitor performance with /metrics endpoint"
    echo "3. Set up SSL certificates with Let's Encrypt"
    echo "4. Configure domain name (optional)"
    echo "5. Set up monitoring and alerting"
}

# Execute main function
main "$@"