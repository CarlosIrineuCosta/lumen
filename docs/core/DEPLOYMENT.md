# Lumen Deployment Documentation

# Overview

This document covers deployment procedures for the Lumen photography platform using the Poor Man's Modules (PMM) architecture. The system is designed for deployment on a Swiss EDIS VPS for data sovereignty and legal compliance.

# Architecture Summary

- **Frontend**: Vanilla JavaScript with PMM pattern (no build process)
- **Backend**: FastAPI with Python 3.11
- **Database**: PostgreSQL 16
- **Storage**: Local filesystem (no cloud dependencies)
- **Server**: EDIS Swiss VPS (83.172.136.127)

# Deployment Environment

## Server Specifications

- **Provider**: EDIS Global (Switzerland)
- **Location**: Zurich, CH
- **IP Address**: 83.172.136.127
- **OS**: Ubuntu 22.04 LTS
- **Resources**: 4 vCPUs, 8GB RAM, 200GB SSD
- **Cost**: €19.90/month

## Domain Configuration

- **Primary**: lumen.photos (or your chosen domain)
- **SSL**: Let's Encrypt via Certbot
- **DNS**: Cloudflare (proxy disabled for Swiss hosting)

# Frontend Deployment

## No Build Process Required!

The PMM architecture means frontend deployment is simply copying files:

```bash
# 1. SSH to server
ssh root@83.172.136.127

# 2. Navigate to web directory
cd /var/www/lumen

# 3. Pull latest code (or upload via SFTP)
git pull origin main

# 4. Set permissions
chown -R www-data:www-data frontend/
chmod -R 755 frontend/

# 5. That's it! No build, no npm, no compilation
```

## Frontend File Structure

```
/var/www/lumen/frontend/
├── index.html           # Main HTML file
├── css/                 # Styles (glass morphism)
├── js/                  # PMM modules
│   ├── config.js       # Configuration
│   └── modules/        # All Lumen* modules
├── templates/          # HTML templates
└── lib/                # CDN fallback (optional)
```

## Nginx Configuration

```nginx
server {
    listen 80;
    server_name lumen.photos;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name lumen.photos;

    ssl_certificate /etc/letsencrypt/live/lumen.photos/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/lumen.photos/privkey.pem;

    # Frontend - serve static files directly
    location / {
        root /var/www/lumen/frontend;
        try_files $uri $uri/ /index.html;

        # Cache static assets
        location ~* \.(css|js|jpg|jpeg|png|gif|ico|svg|woff|woff2)$ {
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }

    # API proxy
    location /api {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Photo storage
    location /storage {
        alias /var/www/lumen/storage;
        expires 365d;
        add_header Cache-Control "public, immutable";
    }
}
```

# Backend Deployment

## Python Environment Setup

```bash
# 1. Install Python 3.11
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# 2. Create virtual environment
cd /var/www/lumen/backend
python3.11 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
cp .env.example .env
nano .env  # Edit with production values
```

## Environment Variables (.env)

```bash
# Database
DATABASE_URL=postgresql://lumen_user:SECURE_PASSWORD@localhost:5432/lumen_production

# Redis
REDIS_URL=redis://localhost:6379/0

# Firebase Admin SDK
FIREBASE_CREDENTIALS_PATH=/var/www/lumen/backend/firebase-adminsdk.json

# Storage
STORAGE_PATH=/var/www/lumen/storage
PHOTO_UPLOAD_MAX_SIZE=104857600  # 100MB

# Security
SECRET_KEY=your-very-secure-secret-key-here
CORS_ORIGINS=https://lumen.photos

# Environment
ENVIRONMENT=production
DEBUG=false
```

## Systemd Service

Create `/etc/systemd/system/lumen-backend.service`:

```ini
[Unit]
Description=Lumen Backend API
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/lumen/backend
Environment="PATH=/var/www/lumen/backend/venv/bin"
ExecStart=/var/www/lumen/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable lumen-backend
sudo systemctl start lumen-backend
sudo systemctl status lumen-backend
```

# Database Setup

## PostgreSQL 16 Installation

```bash
# Add PostgreSQL 16 repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt install postgresql-16

# Create database and user
sudo -u postgres psql
```

```sql
CREATE USER lumen_user WITH PASSWORD 'SECURE_PASSWORD';
CREATE DATABASE lumen_production OWNER lumen_user;
GRANT ALL PRIVILEGES ON DATABASE lumen_production TO lumen_user;

-- Enable extensions
\c lumen_production
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
```

## Run Migrations

```bash
cd /var/www/lumen/backend
source venv/bin/activate
alembic upgrade head
```

# Storage Setup

```bash
# Create storage directories
mkdir -p /var/www/lumen/storage/{photos,temp,cache}
chown -R www-data:www-data /var/www/lumen/storage
chmod -R 755 /var/www/lumen/storage
```

# Security Hardening

## Firewall Configuration

```bash
# Install UFW
sudo apt install ufw

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

## Fail2Ban Setup

```bash
# Install Fail2Ban
sudo apt install fail2ban

# Configure for Nginx
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local

# Add/modify:
[nginx-http-auth]
enabled = true

[nginx-noscript]
enabled = true

[nginx-badbots]
enabled = true

[nginx-noproxy]
enabled = true

# Restart Fail2Ban
sudo systemctl restart fail2ban
```

# Backup Strategy

## Database Backups

```bash
# Create backup script
sudo nano /opt/lumen/scripts/backup-db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/lumen/db"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U lumen_user -h localhost lumen_production | gzip > $BACKUP_DIR/lumen_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "lumen_*.sql.gz" -mtime +30 -delete
```

## Schedule with Cron

```bash
# Add to crontab
crontab -e

# Daily database backup at 2 AM
0 2 * * * /opt/lumen/scripts/backup-db.sh
```

# Monitoring

## Health Check Endpoint

The API provides a health check at `/api/health`:

```bash
curl https://lumen.photos/api/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2025-09-08T12:00:00Z",
  "database": "connected",
  "redis": "connected",
  "storage": "available"
}
```

## Log Monitoring

```bash
# View backend logs
sudo journalctl -u lumen-backend -f

# View Nginx access logs
tail -f /var/log/nginx/access.log

# View Nginx error logs
tail -f /var/log/nginx/error.log
```

# Update Procedure

## Zero-Downtime Deployment

```bash
# 1. Pull latest code
cd /var/www/lumen
git pull origin main

# 2. Update frontend (instant, no build needed!)
# Files are immediately live

# 3. Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# 4. Restart backend (minimal downtime)
sudo systemctl reload lumen-backend
```

# Rollback Procedure

```bash
# 1. Revert to previous commit
cd /var/www/lumen
git log --oneline  # Find the commit to revert to
git checkout <commit-hash>

# 2. Restart backend if needed
sudo systemctl restart lumen-backend
```

# Performance Optimization

## Frontend (PMM Benefits)

- No build process = instant deployment
- No bundling = better caching
- CDN libraries = parallel loading
- Direct file serving = minimal overhead

## Backend

- Use Redis for session storage
- Enable PostgreSQL query caching
- Configure Nginx caching for static assets
- Use image variants to optimize bandwidth

# Troubleshooting

## Common Issues

1. **Frontend not updating**

   - Clear browser cache
   - Check file permissions: `ls -la /var/www/lumen/frontend`
1. **API returns 502**

   - Check backend service: `sudo systemctl status lumen-backend`
   - Check logs: `sudo journalctl -u lumen-backend -n 50`
1. **Database connection errors**

   - Verify PostgreSQL is running: `sudo systemctl status postgresql`
   - Check credentials in `.env`
1. **CORS errors**

   - Verify CORS_ORIGINS in backend `.env`
   - Check Nginx proxy headers

# Support

a For deployment issues, check:

- Backend logs: `sudo journalctl -u lumen-backend -f`
- Nginx logs: `/var/log/nginx/error.log`
- Application logs: `/var/www/lumen/backend/logs/`

---

**Note**: This deployment uses the Poor Man's Modules pattern - no build tools, no complexity, just copy files and go!
