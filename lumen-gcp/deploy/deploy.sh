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
