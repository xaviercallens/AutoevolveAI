#!/bin/bash
# Deploy Qwen2.5-7B-Instruct-AWQ to Cloud Run Serverless with L4 GPU

GCP_PROJECT="autoevolve-ai"
REGION="us-central1"
SERVICE_NAME="qwen-lora-serverless"
IMAGE="us-central1-docker.pkg.dev/$GCP_PROJECT/llm-repo/vllm-qwen-awq:latest"

# 1. Build and push vLLM Docker image (simulate)
echo "Building vLLM Docker image..."

# 2. Deploy to Cloud Run with L4 GPU, min-instances 0
echo "Deploying to Cloud Run..."
gcloud beta run deploy $SERVICE_NAME \
    --image $IMAGE \
    --region $REGION \
    --project $GCP_PROJECT \
    --args="--model,Qwen/Qwen2.5-7B-Instruct-AWQ,--quantization,awq,--tensor-parallel-size,1,--max-model-len,4096" \
    --cpu 4 \
    --memory 16Gi \
    --no-cpu-throttling \
    --min-instances 0 \
    --max-instances 10 \
    --concurrency 32 \
    --allow-unauthenticated \
    --gpu 1 \
    --gpu-type nvidia-l4
