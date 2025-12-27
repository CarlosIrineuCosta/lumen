# Lumen Platform Migration to Swiss VPS
## Complete Migration Guide - August 11, 2025

### Strategic Decision: Swiss Hosting for Legal Protection

**Platform**: Professional artistic photography (including artistic nude)
**Provider**: EDIS Global Switzerland (Zurich datacenter)  
**Plan**: KVM Smart - €4.99/month
**Legal Strategy**: Swiss privacy laws + EU GDPR compliance for maximum protection

---

## Server Specifications

```
EDIS Global KVM Smart (Switzerland)
├── RAM: 1 GB
├── SSD: 15 GB  
├── Traffic: 1 TB/month
├── CPU: 1 x AMD EPYC core
├── Network: 2 x 10 Gbps
└── Location: Zurich, Switzerland
```

**Scaling Plan**: When 10+ users paying €5/month, upgrade to larger instance.

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│           Swiss VPS (EDIS Global)       │
├─────────────────────────────────────────┤
│ FastAPI Backend (Local)                 │
│ PostgreSQL Database (Local)             │
│ Photo Storage (EU Object Storage)       │
│ SSL Certificates (Let's Encrypt)        │
└─────────────────────────────────────────┘
           ↑
    Firebase Auth (Google OAuth only)
```

**Key Decision**: Keep Firebase Auth (free, reliable) but move all data to Swiss/EU infrastructure.

---

## Migration Steps

### Phase 1: VPS Setup (Day 1)

#### 1.1 Order EDIS Global VPS
1. Go to EDIS Global website
2. Select KVM Smart plan (€4.99/month)
3. Choose **Zurich, Switzerland** datacenter
4. Select Ubuntu 22.04 LTS
5. Configure SSH key access
6. Complete order

#### 1.2 Initial Server Setup
```bash
# Connect to new VPS
ssh root@your-swiss-ip

# Update system
apt update && apt upgrade -y

# Install essential packages
apt install -y postgresql postgresql-contrib nginx certbot python3-certbot-nginx
apt install -y python3.11 python3.11-venv python3-pip git curl

# Create application user
adduser lumen
usermod -aG sudo lumen
```

#### 1.3 PostgreSQL Setup
```bash
# Switch to postgres user
sudo -u postgres psql

-- Create database and user
CREATE DATABASE lumen_db;
CREATE USER lumen_user WITH PASSWORD 'secure_swiss_password_2025';
GRANT ALL PRIVILEGES ON DATABASE lumen_db TO lumen_user;
\q

# Configure PostgreSQL for network access
sudo nano /etc/postgresql/14/main/postgresql.conf
# Set: listen_addresses = 'localhost'

sudo nano /etc/postgresql/14/main/pg_hba.conf
# Add: local   lumen_db   lumen_user   md5

sudo systemctl restart postgresql
```

#### 1.4 Firewall Configuration
```bash
# Configure UFW firewall
ufw allow 22     # SSH
ufw allow 80     # HTTP
ufw allow 443    # HTTPS
ufw allow 8080   # Backend API
ufw enable
```

### Phase 2: Object Storage Setup (Day 1)

#### 2.1 Choose EU Storage Provider
**Recommended**: Scaleway Object Storage (Paris)
- €0.02/GB/month
- EU-based (GDPR compliant)
- S3-compatible API
- Strong privacy policies

#### 2.2 Configure Storage
```bash
# Install AWS CLI for S3-compatible access
pip3 install awscli

# Configure Scaleway credentials
aws configure --profile scaleway
# Access Key ID: [Your Scaleway Access Key]
# Secret Access Key: [Your Scaleway Secret Key]
# Default region: fr-par
# Default output format: json
```

#### 2.3 Create Storage Bucket
```bash
# Create bucket for photos
aws s3 mb s3://lumen-photos-swiss --profile scaleway --endpoint-url https://s3.fr-par.scw.cloud

# Set bucket policy for private access
aws s3api put-bucket-versioning --bucket lumen-photos-swiss --versioning-configuration Status=Enabled --profile scaleway --endpoint-url https://s3.fr-par.scw.cloud
```

### Phase 3: Backend Migration (Day 2)

#### 3.1 Clone and Setup Application
```bash
# Switch to lumen user
su - lumen

# Clone repository
git clone https://github.com/your-repo/lumen-backend.git
cd lumen-backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3.2 Update Configuration
```bash
# Create Swiss environment file
nano .env
```

```env
# Swiss VPS Configuration
DATABASE_URL=postgresql://lumen_user:secure_swiss_password_2025@localhost/lumen_db
DB_USER=lumen_user
DB_PASSWORD=secure_swiss_password_2025
DB_NAME=lumen_db
DB_HOST=localhost
DB_PORT=5432

# Object Storage (Scaleway)
STORAGE_PROVIDER=scaleway
STORAGE_BUCKET=lumen-photos-swiss
STORAGE_ENDPOINT=https://s3.fr-par.scw.cloud
STORAGE_REGION=fr-par
AWS_ACCESS_KEY_ID=your_scaleway_access_key
AWS_SECRET_ACCESS_KEY=your_scaleway_secret_key

# Firebase Auth (unchanged)
FIREBASE_PROJECT_ID=lumen-photo-app-20250731
FIREBASE_PRIVATE_KEY_ID=your_firebase_key_id
FIREBASE_PRIVATE_KEY=your_firebase_private_key
FIREBASE_CLIENT_EMAIL=your_firebase_client_email

# API Configuration
API_V1_PREFIX=/api/v1
DEBUG=False
ENVIRONMENT=production

# CORS for Swiss hosting
ALLOWED_ORIGINS=https://your-domain.ch,https://your-domain.com

# Security
SECRET_KEY=generate_new_swiss_secret_key_here
```

#### 3.3 Update Database Models
**CRITICAL**: Fix the Firebase UID vs UUID issue identified in analysis.

```python
# Update User model to use Firebase UID consistently
# File: app/models/user.py

class User(Base):
    __tablename__ = "users"
    
    # Use Firebase UID directly (28-char string)
    id = Column(String(128), primary_key=True)  # Firebase UID
    email = Column(String(255), unique=True, nullable=False)
    # ... rest unchanged
```

#### 3.4 Update PhotoService for EU Storage
```python
# File: app/services/photo_service.py
# Replace Google Cloud Storage with Scaleway S3-compatible storage

import boto3
from botocore.config import Config

class PhotoService:
    def __init__(self, db):
        self.db = db
        self.s3_client = boto3.client(
            's3',
            endpoint_url='https://s3.fr-par.scw.cloud',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name='fr-par',
            config=Config(signature_version='s3v4')
        )
        self.bucket_name = 'lumen-photos-swiss'
```

### Phase 4: Data Migration (Day 2-3)

#### 4.1 Export from Google Cloud SQL
```bash
# On local machine, export existing data
gcloud sql export sql lumen-db gs://temp-export-bucket/lumen_export.sql --database=lumen_db

# Download export
gsutil cp gs://temp-export-bucket/lumen_export.sql ./lumen_export.sql
```

#### 4.2 Import to Swiss PostgreSQL
```bash
# Transfer SQL file to Swiss VPS
scp lumen_export.sql lumen@swiss-vps-ip:~/

# On Swiss VPS, import data
sudo -u postgres psql lumen_db < lumen_export.sql

# Update user IDs to use Firebase UIDs (run custom migration script)
```

#### 4.3 Migrate Photos to EU Storage
```bash
# Create migration script to transfer photos from GCS to Scaleway
# This will be a custom Python script to:
# 1. List all photos in Google Cloud Storage
# 2. Download each photo
# 3. Upload to Scaleway Object Storage
# 4. Update database URLs
```

### Phase 5: Domain and SSL (Day 3)

#### 5.1 DNS Configuration
```bash
# Point your domain to Swiss VPS IP
# A record: yourdomain.com -> swiss-vps-ip
# A record: api.yourdomain.com -> swiss-vps-ip
```

#### 5.2 SSL Certificate Setup
```bash
# Install SSL certificate
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Configure auto-renewal
sudo systemctl enable certbot.timer
```

#### 5.3 Nginx Configuration
```nginx
# /etc/nginx/sites-available/lumen
server {
    listen 443 ssl;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Phase 6: Testing and Deployment (Day 3-4)

#### 6.1 Run Application
```bash
# Start backend
cd ~/lumen-backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# Create systemd service for auto-start
sudo nano /etc/systemd/system/lumen-backend.service
```

#### 6.2 System Service Configuration
```ini
[Unit]
Description=Lumen Backend API
After=network.target

[Service]
Type=simple
User=lumen
WorkingDirectory=/home/lumen/lumen-backend
Environment=PATH=/home/lumen/lumen-backend/venv/bin
ExecStart=/home/lumen/lumen-backend/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable lumen-backend
sudo systemctl start lumen-backend
sudo systemctl status lumen-backend
```

---

## Final Steps

### Testing Checklist
- [ ] PostgreSQL connection working
- [ ] Object storage upload/download working
- [ ] Firebase authentication working
- [ ] SSL certificates valid
- [ ] Photo upload/display pipeline working
- [ ] Database queries returning correct data

### Monitoring Setup
```bash
# Install basic monitoring
apt install -y htop iotop nethogs

# Monitor disk usage (important with 15GB limit)
df -h
du -sh /home/lumen/lumen-backend/
```

---

## Cost Monitoring

**Monthly Costs**:
- VPS: €4.99
- Object Storage: ~€2-5 (scales with usage)
- **Total**: ~€7-10/month vs previous R$ 12 + GCS costs

**Scaling Trigger**: When 10+ users paying €5/month = €50 revenue
**Upgrade Path**: Next tier VPS with more storage and RAM

---

## Security Considerations

1. **Regular backups** of PostgreSQL to object storage
2. **UFW firewall** properly configured
3. **SSH key-only access** (disable password auth)
4. **Let's Encrypt SSL** auto-renewal
5. **Swiss privacy laws** compliance
6. **EU GDPR** compliance via object storage location

---

## Support Contacts

- **EDIS Global Support**: Swiss hosting provider
- **Scaleway Support**: EU object storage
- **Firebase Support**: Authentication (if needed)

This migration achieves full EU/Swiss compliance while maintaining cost efficiency and technical simplicity.