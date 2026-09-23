#!/bin/bash
set -e

MODEL_PATH="/models/${MODEL_FILE}"
MMPROJ_PATH="/models/${MMPROJ_FILE}"

echo "=== ANSE Qwen3.8-27B (UD-Q3_K_XL) T4 Runner ==="
echo "Checking model weights..."

if [ ! -f "$MODEL_PATH" ]; then
    echo "Downloading ${MODEL_FILE} from ${MODEL_REPO} via huggingface-cli..."
    python3 -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='${MODEL_REPO}', filename='${MODEL_FILE}', local_dir='/models')"
fi

EXTRA_ARGS=""
if [ "$ENABLE_VISION" = "true" ]; then
    if [ ! -f "$MMPROJ_PATH" ]; then
        echo "Downloading vision projector ${MMPROJ_FILE}..."
        python3 -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='${MODEL_REPO}', filename='${MMPROJ_FILE}', local_dir='/models')"
    fi
    EXTRA_ARGS="--mmproj ${MMPROJ_PATH}"
    echo "Vision projector enabled: ${MMPROJ_PATH}"
fi

echo "Launching llama-server on NVIDIA T4 (sm_75)..."
echo "  Context Size:       ${CONTEXT_SIZE}"
echo "  GPU Layers:         ${N_GPU_LAYERS} (100% offload)"
echo "  KV Cache Type:      ${KV_CACHE_TYPE}"
echo "  FlashAttention:     Enabled (-fa)"
echo "  Parallel Slots:     ${PARALLEL_SLOTS}"
echo "  Host/Port:          ${HOST}:${PORT}"

exec /usr/local/bin/llama-server \
    -m "${MODEL_PATH}" \
    ${EXTRA_ARGS} \
    -ngl "${N_GPU_LAYERS}" \
    -c "${CONTEXT_SIZE}" \
    --cache-type-k "${KV_CACHE_TYPE}" \
    --cache-type-v "${KV_CACHE_TYPE}" \
    -fa \
    --parallel "${PARALLEL_SLOTS}" \
    --host "${HOST}" \
    --port "${PORT}"
