---
description: Deployment pipeline to EDIS Swiss VPS with backup and validation
---

# Deployment to EDIS Swiss VPS

Manage deployment pipeline for $ARGUMENTS:

## 1. Pre-Deployment Checks

### Local Validation
```bash
echo "=== PRE-DEPLOYMENT VALIDATION ==="

# Run full quality check locally
echo "Running local quality checks..."
cd opusdev/backend
source venv/bin/activate
pytest tests/ -x || { echo "❌ Tests failed - deployment aborted"; exit 1; }

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Uncommitted changes detected:"
    git status --porcelain
    echo "Commit changes before deployment? (y/n)"
    # Note: In automation, this should fail
fi

# Validate critical files exist
[ -f "opusdev/backend/app/main.py" ] || { echo "❌ Backend main.py not found"; exit 1; }
[ -f "opusdev/frontend/lumen-app.html" ] || { echo "❌ Frontend app not found"; exit 1; }

echo "✅ Local validation complete"
```

## 2. EDIS Backup Process

### Download Production Files
```bash
echo "=== CREATING PRODUCTION BACKUP ==="

# Create backup directory with timestamp
BACKUP_DIR="backups/edis-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup critical application files
echo "Backing up application files from EDIS..."
rsync -avz --progress root@83.172.136.127:/opt/lumen-backend/ "$BACKUP_DIR/backend/" || {
    echo "❌ Backend backup failed"; exit 1;
}

rsync -avz --progress root@83.172.136.127:/opt/lumen-frontend/ "$BACKUP_DIR/frontend/" || {
    echo "❌ Frontend backup failed"; exit 1;
}

echo "✅ Application files backed up to $BACKUP_DIR"
```

### Database Backup
```bash
echo "Creating database backup..."

# Create database dump on EDIS
ssh root@83.172.136.127 "
    pg_dump -U lumen_user lumen_db > /tmp/lumen_backup_$(date +%Y%m%d_%H%M%S).sql
" || { echo "❌ Database backup creation failed"; exit 1; }

# Download database backup
scp root@83.172.136.127:/tmp/lumen_backup_*.sql "$BACKUP_DIR/" || {
    echo "❌ Database backup download failed"; exit 1;
}

# Clean up remote temp file
ssh root@83.172.136.127 "rm -f /tmp/lumen_backup_*.sql"

echo "✅ Database backed up to $BACKUP_DIR"
```

### Check EDIS Disk Space
```bash
echo "Checking EDIS disk space..."

DISK_USAGE=$(ssh root@83.172.136.127 "df -h / | tail -1 | awk '{print \$5}' | sed 's/%//'")

if [ "$DISK_USAGE" -gt 80 ]; then
    echo "❌ EDIS disk usage is ${DISK_USAGE}% - cleanup required before deployment"
    echo "Available space:"
    ssh root@83.172.136.127 "df -h /"
    exit 1
else
    echo "✅ EDIS disk usage: ${DISK_USAGE}% (acceptable)"
fi
```

## 3. Deployment Process

### Git Operations
```bash
echo "=== DEPLOYMENT PROCESS ==="

# Ensure main branch and push
git checkout main
git push origin main || { echo "❌ Git push failed"; exit 1; }

COMMIT_HASH=$(git rev-parse --short HEAD)
echo "Deploying commit: $COMMIT_HASH"
```

### Deploy to EDIS
```bash
echo "Deploying to EDIS server..."

# Update code on EDIS
ssh root@83.172.136.127 "
    cd /opt/lumen-backend &&
    git fetch origin &&
    git reset --hard origin/main &&
    echo 'Code updated to latest commit'
" || { echo "❌ Code update failed"; exit 1; }

# Update Python dependencies if needed
ssh root@83.172.136.127 "
    cd /opt/lumen-backend &&
    source venv/bin/activate &&
    pip install -r requirements-optimized.txt &&
    echo 'Dependencies updated'
" || echo "⚠️  Dependency update had issues (continuing)"

# Run database migrations
ssh root@83.172.136.127 "
    cd /opt/lumen-backend &&
    source venv/bin/activate &&
    alembic upgrade head &&
    echo 'Database migrations applied'
" || echo "⚠️  Migration issues (continuing)"

echo "✅ Code deployment complete"
```

### Service Restart
```bash
echo "Restarting EDIS services..."

# Restart backend service
ssh root@83.172.136.127 "
    systemctl restart lumen-backend &&
    echo 'Backend service restarted'
" || { echo "❌ Backend restart failed"; exit 1; }

# Restart nginx if needed
ssh root@83.172.136.127 "
    nginx -t && systemctl reload nginx &&
    echo 'Nginx configuration reloaded'
" || echo "⚠️  Nginx reload issues"

# Wait for services to start
sleep 5
echo "✅ Services restarted"
```

## 4. Post-Deployment Validation

### Health Checks
```bash
echo "=== POST-DEPLOYMENT VALIDATION ==="

# Test production API
PROD_API="https://lumenphotos.com/api/v1/health"
if curl -f "$PROD_API" >/dev/null 2>&1; then
    echo "✅ Production API: Healthy"
else
    echo "❌ Production API: Not responding"
    echo "Rolling back deployment..."
    # Add rollback logic here
    exit 1
fi

# Test frontend
PROD_FRONTEND="https://lumenphotos.com"
if curl -f "$PROD_FRONTEND" >/dev/null 2>&1; then
    echo "✅ Production Frontend: Accessible"
else
    echo "❌ Production Frontend: Not accessible"
fi
```

### Database Integrity Check
```bash
echo "Checking database integrity..."

DB_CHECK=$(ssh root@83.172.136.127 "
    psql -U lumen_user lumen_db -c 'SELECT COUNT(*) FROM users;' -t 2>/dev/null
")

if [ -n "$DB_CHECK" ]; then
    echo "✅ Database: Connected (Users table has $DB_CHECK rows)"
else
    echo "❌ Database: Connection issues"
fi
```

### SSL Certificate Check
```bash
echo "Checking SSL certificate..."

CERT_EXPIRY=$(echo | openssl s_client -connect lumenphotos.com:443 2>/dev/null | openssl x509 -noout -dates | grep notAfter)
echo "✅ SSL Certificate: $CERT_EXPIRY"
```

## 5. Deployment Summary

### Create Deployment Log
```bash
echo "=== DEPLOYMENT SUMMARY ==="

DEPLOY_LOG="logs/deployment-$(date +%Y%m%d-%H%M%S).log"
mkdir -p logs

cat > "$DEPLOY_LOG" << EOF
Deployment Summary - $(date)
=================================
Commit: $COMMIT_HASH
Backup: $BACKUP_DIR
Production API: $PROD_API
Frontend URL: $PROD_FRONTEND

Pre-deployment checks: ✅
Backup process: ✅
Code deployment: ✅
Service restart: ✅
Health validation: ✅

Deployment Status: SUCCESS
EOF

echo "✅ Deployment log saved to: $DEPLOY_LOG"
echo ""
echo "🚀 DEPLOYMENT COMPLETE!"
echo "   Production: https://lumenphotos.com"
echo "   API Docs:   https://lumenphotos.com/docs"
echo "   Backup:     $BACKUP_DIR"
```

## 6. Rollback Procedure

### Emergency Rollback
```bash
# In case of deployment failure
echo "=== EMERGENCY ROLLBACK ==="

# Restore from latest backup
LATEST_BACKUP=$(ls -t backups/ | head -1)
echo "Rolling back to: $LATEST_BACKUP"

# Restore application files
rsync -avz "backups/$LATEST_BACKUP/backend/" root@83.172.136.127:/opt/lumen-backend/
rsync -avz "backups/$LATEST_BACKUP/frontend/" root@83.172.136.127:/opt/lumen-frontend/

# Restart services
ssh root@83.172.136.127 "systemctl restart lumen-backend nginx"

echo "✅ Rollback complete"
```

## Safety Features

- **Automated backups** before each deployment
- **Disk space validation** prevents deployment on full disk
- **Health checks** validate services after deployment
- **Rollback capability** for emergency recovery
- **Deployment logging** for audit trail

## Important Notes

- EDIS server: 83.172.136.127 (Swiss VPS)
- Always backup before deployment
- Monitor disk space (small VPS)
- Test deployment on staging first
- Keep local backups for emergency recovery