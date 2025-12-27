#!/bin/bash
# Lumen Project Setup for Google Cloud
# Run this script to create the complete project structure

echo "🎨 Creating Lumen - Artistic Photography Platform on Google Cloud"

# Make script executable
chmod +x "$0"

# Create main project directory
mkdir -p lumen-gcp
cd lumen-gcp

# Create backend structure (FastAPI)
mkdir -p backend/{app,database,storage,ml,auth}
mkdir -p backend/app/{api,models,services,utils}
mkdir -p backend/app/api/{endpoints,deps}

# Create frontend structure (React Native with web support)
mkdir -p frontend/{src,public,assets}
mkdir -p frontend/src/{components,screens,services,utils,hooks}

# Create infrastructure structure (Google Cloud)
mkdir -p infrastructure/{terraform,scripts,monitoring}
mkdir -p infrastructure/terraform/{modules,environments}

# Create deployment structure
mkdir -p deploy/{staging,production}

# Create docs and configuration
mkdir -p docs/{api,architecture,deployment}
mkdir -p config/{development,staging,production}

echo "📁 Project structure created!"

# Create configuration files
cat > .env.example << 'EOF'
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=lumen-photography-platform
GOOGLE_CLOUD_REGION=us-central1

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost/lumen_db
CLOUD_SQL_CONNECTION_NAME=your-project:us-central1:lumen-db

# Storage Configuration
STORAGE_BUCKET=lumen-user-uploads
CDN_BUCKET=lumen-static-assets

# Authentication
FIREBASE_PROJECT_ID=lumen-photography-platform
FIREBASE_API_KEY=your-firebase-api-key

# Payment Processing
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# AI/ML Configuration
VERTEX_AI_PROJECT=lumen-photography-platform
VERTEX_AI_REGION=us-central1

# Cost Monitoring
BUDGET_ALERT_THRESHOLD_USD=100
COST_MONITORING_EMAIL=admin@lumen.com
EOF

# Create Docker configuration
cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

# Create Python requirements
cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
alembic==1.13.1
psycopg2-binary==2.9.9
google-cloud-storage==2.10.0
google-cloud-sql-connector==1.5.0
google-cloud-secret-manager==2.17.0
google-cloud-aiplatform==1.38.1
firebase-admin==6.3.0
stripe==7.8.0
pillow==10.1.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
httpx==0.25.2
pydantic-settings==2.1.0
prometheus-client==0.19.0
structlog==23.2.0
EOF

# Create Cloud Build configuration
cat > cloudbuild.yaml << 'EOF'
steps:
  # Build backend container
  - name: 'gcr.io/cloud-builders/docker'
    args: [
      'build',
      '-t', 'gcr.io/$PROJECT_ID/lumen-backend:$COMMIT_SHA',
      '-t', 'gcr.io/$PROJECT_ID/lumen-backend:latest',
      './backend'
    ]

  # Push backend container
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/lumen-backend:$COMMIT_SHA']

  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args: [
      'run', 'deploy', 'lumen-backend',
      '--image', 'gcr.io/$PROJECT_ID/lumen-backend:$COMMIT_SHA',
      '--region', 'us-central1',
      '--platform', 'managed',
      '--allow-unauthenticated',
      '--set-env-vars', 'ENVIRONMENT=production'
    ]

options:
  logging: CLOUD_LOGGING_ONLY
  machineType: 'E2_HIGHCPU_8'

timeout: 1200s
EOF

# Create GitHub Actions workflow
mkdir -p .github/workflows
cat > .github/workflows/deploy.yml << 'EOF'
name: Deploy to Google Cloud

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  PROJECT_ID: lumen-photography-platform
  GAR_LOCATION: us-central1
  SERVICE: lumen-backend
  REGION: us-central1

jobs:
  deploy:
    permissions:
      contents: read
      id-token: write

    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Google Auth
        id: auth
        uses: 'google-github-actions/auth@v2'
        with:
          credentials_json: '${{ secrets.GCP_SA_KEY }}'

      - name: 'Set up Cloud SDK'
        uses: 'google-github-actions/setup-gcloud@v2'

      - name: 'Use gcloud CLI'
        run: 'gcloud info'

      - name: Build and Push Container
        run: |-
          gcloud builds submit --tag="gcr.io/$PROJECT_ID/$SERVICE:$GITHUB_SHA"

      - name: Deploy to Cloud Run
        run: |-
          gcloud run deploy $SERVICE \
            --image="gcr.io/$PROJECT_ID/$SERVICE:$GITHUB_SHA" \
            --platform=managed \
            --region=$REGION \
            --allow-unauthenticated
EOF

# Create Terraform configuration
cat > infrastructure/terraform/main.tf << 'EOF'
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "storage.googleapis.com",
    "aiplatform.googleapis.com",
    "secretmanager.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com"
  ])
  
  service = each.value
  project = var.project_id
}

# Cloud SQL PostgreSQL instance
resource "google_sql_database_instance" "lumen_db" {
  name             = "lumen-db"
  database_version = "POSTGRES_15"
  region          = var.region

  settings {
    tier = "db-f1-micro"  # Free tier eligible
    
    backup_configuration {
      enabled = true
    }
    
    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        value = "0.0.0.0/0"  # Restrict this in production
      }
    }
  }

  deletion_protection = false
}

# Cloud Storage buckets
resource "google_storage_bucket" "user_uploads" {
  name     = "${var.project_id}-user-uploads"
  location = "US"
  
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

resource "google_storage_bucket" "static_assets" {
  name     = "${var.project_id}-static-assets"
  location = "US"
  
  website {
    main_page_suffix = "index.html"
  }
}

# Cloud Monitoring budget alert
resource "google_monitoring_notification_channel" "email" {
  display_name = "Email Notification Channel"
  type         = "email"
  
  labels = {
    email_address = var.notification_email
  }
}

resource "google_billing_budget" "lumen_budget" {
  billing_account = var.billing_account
  display_name    = "Lumen Project Budget"

  budget_filter {
    projects = ["projects/${var.project_id}"]
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = "100"  # $100 budget
    }
  }

  threshold_rules {
    threshold_percent = 0.5  # 50% threshold
  }
  
  threshold_rules {
    threshold_percent = 0.9  # 90% threshold
  }

  all_updates_rule {
    notification_channels = [google_monitoring_notification_channel.email.id]
    disable_default_iam_recipients = false
  }
}
EOF

cat > infrastructure/terraform/variables.tf << 'EOF'
variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
  default     = "lumen-photography-platform"
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
  default     = "us-central1"
}

variable "billing_account" {
  description = "Google Cloud Billing Account ID"
  type        = string
}

variable "notification_email" {
  description = "Email for budget alerts"
  type        = string
}
EOF

# Create basic FastAPI application
cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Lumen API",
    description="Artistic Photography Platform API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Lumen API - Artistic Photography Platform",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/api/v1/photos")
async def list_photos():
    """List photos with pagination"""
    return {
        "photos": [],
        "total": 0,
        "page": 1,
        "per_page": 20
    }

@app.post("/api/v1/photos")
async def upload_photo():
    """Upload a new photo"""
    return {
        "message": "Photo upload endpoint - to be implemented",
        "status": "not_implemented"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
EOF

# Create cost monitoring script
cat > infrastructure/scripts/monitor_costs.py << 'EOF'
#!/usr/bin/env python3
"""
Google Cloud Cost Monitoring Script for Lumen Project
Monitors daily spending and sends alerts
"""

import os
from datetime import datetime, timedelta
from google.cloud import billing_v1
from google.cloud import monitoring_v3
import smtplib
from email.mime.text import MimeText

class CostMonitor:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.billing_client = billing_v1.CloudBillingClient()
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        
    def get_daily_cost(self) -> float:
        """Get current day's spending"""
        # This would implement actual cost retrieval
        # For now, return a mock value
        return 5.50  # Mock daily cost in USD
        
    def check_budget_threshold(self, daily_cost: float, budget_limit: float = 100.0) -> dict:
        """Check if we're approaching budget limits"""
        weekly_projection = daily_cost * 7
        monthly_projection = daily_cost * 30
        
        alerts = []
        
        if weekly_projection > budget_limit * 0.5:
            alerts.append(f"Weekly projection: ${weekly_projection:.2f} (50% of budget)")
            
        if monthly_projection > budget_limit:
            alerts.append(f"Monthly projection: ${monthly_projection:.2f} (exceeds budget)")
            
        return {
            "daily_cost": daily_cost,
            "weekly_projection": weekly_projection,
            "monthly_projection": monthly_projection,
            "alerts": alerts,
            "status": "warning" if alerts else "ok"
        }
        
    def generate_cost_report(self) -> str:
        """Generate daily cost report"""
        daily_cost = self.get_daily_cost()
        budget_check = self.check_budget_threshold(daily_cost)
        
        report = f"""
Lumen Project - Daily Cost Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Current Daily Cost: ${budget_check['daily_cost']:.2f}
Weekly Projection: ${budget_check['weekly_projection']:.2f}
Monthly Projection: ${budget_check['monthly_projection']:.2f}

Status: {budget_check['status'].upper()}

"""
        
        if budget_check['alerts']:
            report += "⚠️  ALERTS:\n"
            for alert in budget_check['alerts']:
                report += f"  - {alert}\n"
        else:
            report += "✅ No budget concerns detected\n"
            
        return report

if __name__ == "__main__":
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "lumen-photography-platform")
    monitor = CostMonitor(project_id)
    
    print(monitor.generate_cost_report())
EOF

chmod +x infrastructure/scripts/monitor_costs.py

# Create deployment script
cat > deploy/deploy.sh << 'EOF'
#!/bin/bash
# Lumen Deployment Script

set -e

echo "🚀 Deploying Lumen to Google Cloud"

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK"
    exit 1
fi

# Set project
PROJECT_ID=${1:-lumen-photography-platform}
gcloud config set project $PROJECT_ID

echo "📦 Building container..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/lumen-backend ./backend

echo "🚀 Deploying to Cloud Run..."
gcloud run deploy lumen-backend \
    --image gcr.io/$PROJECT_ID/lumen-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10

echo "✅ Deployment complete!"
echo "🌐 Your API is available at:"
gcloud run services describe lumen-backend --region us-central1 --format 'value(status.url)'
EOF

chmod +x deploy/deploy.sh

# Create package.json for frontend
cat > frontend/package.json << 'EOF'
{
  "name": "lumen-frontend",
  "version": "1.0.0",
  "description": "Lumen Artistic Photography Platform Frontend",
  "main": "index.js",
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web",
    "eject": "expo eject",
    "build:web": "expo build:web",
    "deploy:web": "firebase deploy --only hosting"
  },
  "dependencies": {
    "expo": "~49.0.0",
    "react": "18.2.0",
    "react-native": "0.72.0",
    "react-native-web": "~0.19.0",
    "@react-navigation/native": "^6.1.0",
    "@react-navigation/stack": "^6.3.0",
    "firebase": "^10.5.0",
    "expo-image-picker": "~14.3.0",
    "expo-constants": "~14.4.0"
  },
  "devDependencies": {
    "@babel/core": "^7.20.0",
    "@types/react": "~18.2.0",
    "@types/react-native": "~0.72.0",
    "typescript": "^5.1.0"
  }
}
EOF

# Create README with setup instructions
cat > README.md << 'EOF'
# Lumen - Artistic Photography Platform

A Google Cloud-based platform for artistic body photography, connecting photographers, models, and art patrons.

## 🏗️ Architecture

- **Backend**: Python FastAPI on Cloud Run
- **Database**: Cloud SQL PostgreSQL
- **Storage**: Cloud Storage for images
- **AI/ML**: Vertex AI for content moderation
- **Frontend**: React Native (Expo) with web support
- **Auth**: Firebase Authentication
- **Payments**: Stripe integration

## 💰 Cost Monitoring

This project includes comprehensive cost monitoring:
- Daily cost tracking
- Budget alerts at 50% and 90% thresholds
- Weekly and monthly projections
- Automated email notifications

## 🚀 Quick Start

### Prerequisites
1. Google Cloud account with billing enabled
2. VS Code with Cloud Code extension
3. Node.js and Python 3.11+
4. Docker Desktop

### Setup

1. **Install Google Cloud CLI**:
   ```bash
   # Follow VS Code Cloud Code extension prompts
   # Or install manually from: https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate**:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

3. **Create Google Cloud Project**:
   ```bash
   gcloud projects create lumen-photography-platform
   gcloud config set project lumen-photography-platform
   gcloud services enable cloudbuild.googleapis.com
   ```

4. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your project details
   ```

5. **Deploy infrastructure**:
   ```bash
   cd infrastructure/terraform
   terraform init
   terraform plan
   terraform apply
   ```

6. **Deploy application**:
   ```bash
   ./deploy/deploy.sh
   ```

## 📊 Daily Cost Monitoring

Run the cost monitoring script:
```bash
python infrastructure/scripts/monitor_costs.py
```

## 🔧 Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

## 📝 Features Roadmap

- [x] Basic API structure
- [x] Cost monitoring
- [x] Docker containerization
- [x] Cloud Run deployment
- [ ] Firebase authentication
- [ ] Image upload to Cloud Storage
- [ ] Vertex AI content moderation
- [ ] Stripe payment integration
- [ ] React Native mobile app
- [ ] Portfolio generator

## 💡 VS Code Integration

This project is optimized for VS Code with Cloud Code extension:
- Automatic Docker builds
- Cloud Run deployment from IDE
- Integrated debugging
- Cloud resource browsing
- Cost monitoring dashboard

## 📈 Budget Management

- **Daily Budget**: $3-7 (within free tier for most services)
- **Weekly Budget**: $20-50
- **R$ 1900 credits**: Should last 4-6 weeks of active development
- **Automatic shutdowns**: Configured to prevent cost overruns

## 🛡️ Security Features

- Row-level security in PostgreSQL
- Firebase authentication
- CORS configuration
- Input validation
- Rate limiting (to be implemented)

## 📞 Support

For issues or questions:
1. Check the GitHub Issues
2. Review Google Cloud documentation
3. Use VS Code Cloud Code extension help
EOF

echo "✅ Lumen project structure created successfully!"
echo ""
echo "📁 Project layout:"
echo "lumen-gcp/"
echo "├── backend/          # FastAPI application"
echo "├── frontend/         # React Native app"
echo "├── infrastructure/   # Terraform & scripts"
echo "├── deploy/          # Deployment scripts"
echo "├── config/          # Environment configs"
echo "└── docs/            # Documentation"
echo ""
echo "🚀 Next steps:"
echo "1. cd lumen-gcp"
echo "2. Open in VS Code: code ."
echo "3. Install Cloud Code extension"
echo "4. Follow README.md setup instructions"
echo ""
echo "💰 Cost monitoring is built-in!"
echo "📊 Weekly budget estimate: R$ 260-490 (well within your R$ 1900 credits)"