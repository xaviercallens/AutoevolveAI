#!/usr/bin/env bash
set -e

PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
LAYA_IMAGE="gcr.io/${PROJECT_ID}/laya-coding-cpu"
QWEN_IMAGE="gcr.io/${PROJECT_ID}/qwen38-t4"

echo "Deploying Laya (CPU)..."
gcloud run deploy laya-service \
    --image $LAYA_IMAGE \
    --port 8001 \
    --min-instances 0 \
    --max-instances 10 \
    --cpu 2 \
    --memory 2Gi \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated

echo "Deploying Qwen3.8 (T4 GPU)..."
gcloud run deploy qwen-service \
    --image $QWEN_IMAGE \
    --port 8080 \
    --min-instances 0 \
    --max-instances 3 \
    --cpu 8 \
    --memory 32Gi \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars="NVIDIA_VISIBLE_DEVICES=all"

echo "Deployments complete."
echo "Routing Logic Note: Implement a gateway (e.g. API Gateway or a simple proxy layer)"
echo "where Laya decides first, and uncertain cases (0.3 <= noul <= 0.7) go to Qwen3.8."
