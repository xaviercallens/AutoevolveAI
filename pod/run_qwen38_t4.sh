#!/bin/bash
# High-Performance Runner for Qwen3.8-27B (UD-Q3_K_XL) on NVIDIA T4 (16GB GDDR6)
# Target Architecture: Turing (sm_75)
# Engine: llama.cpp (llama-server)

set -e

WORKDIR="${HOME}/qwen38_t4"
mkdir -p "${WORKDIR}/models"
cd "${WORKDIR}"

echo "=========================================================================="
echo "ANSE High-Throughput Runner: Qwen3.8-27B (UD-Q3_K_XL) on NVIDIA T4 (16GB)"
echo "=========================================================================="

# 1. Check GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo "ERROR: nvidia-smi not found. NVIDIA drivers required."
    exit 1
fi
nvidia-smi

# 2. Install dependencies & llama.cpp if not present
if [ ! -f "${WORKDIR}/llama-server" ]; then
    echo "Building llama.cpp for CUDA sm_75 (Turing / T4)..."
    sudo apt-get update && sudo apt-get install -y cmake git build-essential curl python3-pip
    pip3 install huggingface_hub
    
    git clone https://github.com/ggerganov/llama.cpp.git src
    cd src
    cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="75" -DGGML_CUDA_FA_ALL_QUANTS=ON
    cmake --build build --config Release -j$(nproc) --target llama-server
    cp build/bin/llama-server "${WORKDIR}/llama-server"
    cd "${WORKDIR}"
fi

# 3. Download Model
MODEL_FILE="Qwen3.8-27B-UD-Q3_K_XL.gguf"
if [ ! -f "${WORKDIR}/models/${MODEL_FILE}" ]; then
    echo "Downloading ${MODEL_FILE} from unsloth/Qwen3.8-27B-GGUF (12.24 GiB)..."
    python3 -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='unsloth/Qwen3.8-27B-GGUF', filename='${MODEL_FILE}', local_dir='${WORKDIR}/models')"
fi

# 4. Optional Vision Projector
VISION_ARGS=""
if [ "$1" == "--vision" ]; then
    MMPROJ_FILE="mmproj-F16.gguf"
    if [ ! -f "${WORKDIR}/models/${MMPROJ_FILE}" ]; then
        echo "Downloading vision projector ${MMPROJ_FILE} (0.86 GiB)..."
        python3 -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='unsloth/Qwen3.8-27B-GGUF', filename='${MMPROJ_FILE}', local_dir='${WORKDIR}/models')"
    fi
    VISION_ARGS="--mmproj ${WORKDIR}/models/${MMPROJ_FILE}"
    CONTEXT=4096
    echo "Vision enabled. Setting context to 4096 to preserve VRAM safety cushion."
else
    CONTEXT=8192
fi

# 5. Launch llama-server with exact T4 physical allocations:
# - Model fits 100% in VRAM: -ngl 99
# - Quantized KV cache: --cache-type-k q8_0 --cache-type-v q8_0 (halves KV memory)
# - FlashAttention: -fa (prevents quadratic memory spikes)
echo "Starting llama-server on port 8080..."
exec "${WORKDIR}/llama-server" \
    -m "${WORKDIR}/models/${MODEL_FILE}" \
    ${VISION_ARGS} \
    -ngl 99 \
    -c ${CONTEXT} \
    --cache-type-k q8_0 \
    --cache-type-v q8_0 \
    -fa \
    --parallel 2 \
    --host 0.0.0.0 \
    --port 8080
