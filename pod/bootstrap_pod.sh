#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "🚀 Bootstrapping Remote RunPod GPU Environment for LoRA"
echo "=========================================================="

# 1. System checks
nvidia-smi

# 2. Install Astral uv
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# 3. Synchronize Python environment with training extras
echo "📦 Installing dependencies (Torch, Transformers, PEFT, TRL, BitsAndBytes)..."
uv pip install --system \
    "torch" \
    "transformers>=4.45.0" \
    "peft>=0.13.0" \
    "trl>=0.11.0" \
    "accelerate>=0.34.0" \
    "bitsandbytes>=0.43.0" \
    "datasets" \
    "scipy"

echo "✅ Pod bootstrap complete. Ready for distillation training."
