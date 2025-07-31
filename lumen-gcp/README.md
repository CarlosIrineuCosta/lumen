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
