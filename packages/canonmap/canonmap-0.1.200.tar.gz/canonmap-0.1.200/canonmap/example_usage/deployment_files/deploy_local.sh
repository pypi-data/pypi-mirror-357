#!/bin/bash

# CanonMap API Deployment Script
# This script deploys the CanonMap API with response models to Google Cloud Run

set -e

# Configuration
IMAGE_NAME="canonmap-api"
REGION="us-central1"
PROJECT_ID="projectn-445619"
REPO="services-artifacts"
SERVICE="canonmap-service"

echo "🚀 CanonMap API Deployment with Response Models"
echo "================================================"

# Authenticate and configure
echo "🔐 Configuring Google Cloud..."
gcloud auth configure-docker $REGION-docker.pkg.dev
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION

# Ensure Artifact Registry repository exists
echo "📁 Ensuring Artifact Registry repository exists..."
if ! gcloud artifacts repositories describe $REPO --location=$REGION >/dev/null 2>&1; then
  echo "Creating repository $REPO..."
  gcloud artifacts repositories create $REPO \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for CanonMap API with response models"
else
  echo "✅ Repository $REPO already exists"
fi

# Build and tag Docker image
echo "🔨 Building Docker image..."
docker build -t canonmap-api:latest -f Dockerfile .

echo "🏷️  Tagging image for Artifact Registry..."
docker tag canonmap-api:latest $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$IMAGE_NAME

# Push to Artifact Registry
echo "📤 Pushing image to Artifact Registry..."
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$IMAGE_NAME

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$IMAGE_NAME \
  --platform managed \
  --memory 8Gi \
  --cpu 4 \
  --port 8080 \
  --timeout 600 \
  --allow-unauthenticated \
  --set-env-vars="CANONMAP_VERBOSE=true" \
  --set-env-vars="CANONMAP_TROUBLESHOOTING=false"

echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Service Information:"
echo "  - Service Name: $SERVICE"
echo "  - Region: $REGION"
echo "  - Project: $PROJECT_ID"
echo "  - Memory: 8Gi"
echo "  - CPU: 4 cores"
echo "  - Timeout: 600 seconds"
echo ""
echo "🔗 API Endpoints:"
echo "  - Health Check: https://$SERVICE-$REGION.a.run.app/health"
echo "  - Generate Artifacts: https://$SERVICE-$REGION.a.run.app/generate-artifacts"
echo "  - Entity Mapping: https://$SERVICE-$REGION.a.run.app/entity-mapping"
echo "  - API Documentation: https://$SERVICE-$REGION.a.run.app/docs"
echo ""
echo "📚 Response Models Available:"
echo "  - ArtifactGenerationResponse: Comprehensive artifact generation results"
echo "  - EntityMappingResponse: Detailed entity mapping results"
echo "  - Error handling and processing statistics included"
echo ""
echo "🧪 Test the API:"
echo "  curl https://$SERVICE-$REGION.a.run.app/health"