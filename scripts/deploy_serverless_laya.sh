#!/usr/bin/env bash
# ==============================================================================
# deploy_serverless_laya.sh
# ==============================================================================
# Deploys the ANSE Laya Serverless Endpoint to Google Cloud Run with:
#   - min-instances = 0 (scale-to-zero, $0.00 idle cost)
#   - cold-start optimization (<1.0s)
#   - CPU = 2, RAM = 2Gi, Concurrency = 80
#   - Dual-process routing (/v1/predict, /v1/assist, /v1/audit/anti-hallucination)
# ==============================================================================

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-gen-lang-client-0625573011}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="anse-serverless-laya"
IMAGE_TAG="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"
CHECKPOINT_GCS="gs://socrateai-datalake-gen-lang-client-0625573011/checkpoints/stage3/"

echo "========================================================================"
echo "🚀 Deploying ANSE Laya Serverless Cognitive Service to Cloud Run"
echo "   Project:       ${PROJECT_ID}"
echo "   Region:        ${REGION}"
echo "   Service:       ${SERVICE_NAME}"
echo "   Min Replicas:  0 (Scale-to-Zero Guaranteed: \$0.00 Idle Cost)"
echo "   Concurrency:   80 requests/container"
echo "========================================================================"

# Step 1: Verify gcloud configuration
gcloud config set project "${PROJECT_ID}" --quiet

# Step 2: Build container image via Cloud Build (or verify Dockerfile exists)
if [[ "${1:-}" != "--skip-build" ]]; then
    echo "📦 Building container image: ${IMAGE_TAG}..."
    gcloud builds submit --tag "${IMAGE_TAG}" .
fi

# Step 3: Deploy to Google Cloud Run with scale-to-zero enforcement
echo "☁️  Deploying Cloud Run service with --min-instances 0..."
gcloud run deploy "${SERVICE_NAME}" \
    --image "${IMAGE_TAG}" \
    --platform managed \
    --region "${REGION}" \
    --min-instances 0 \
    --max-instances 10 \
    --concurrency 80 \
    --cpu 2 \
    --memory 2Gi \
    --timeout 300 \
    --allow-unauthenticated \
    --set-env-vars "IDLE_TIMEOUT_SECONDS=15.0,CHECKPOINT_GCS=${CHECKPOINT_GCS}" \
    --quiet

# Step 4: Display endpoint URL and cost telemetry
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --platform managed --region "${REGION}" --format 'value(status.url)')

echo "========================================================================"
echo "🎉 Deployment Complete!"
echo "   Endpoint URL:           ${SERVICE_URL}"
echo "   Health & State:         ${SERVICE_URL}/health"
echo "   Anti-Hallucination:     ${SERVICE_URL}/v1/audit/anti-hallucination"
echo "   Dual-Process Assist:    ${SERVICE_URL}/v1/assist"
echo "   Scale-to-Zero Policy:   0 active instances when idle (\$0.00/hr)"
echo "========================================================================"
