#!/bin/bash
# GCP T4 startup script for xautoresearch
# Installs uv + deps, runs train.py, uploads results to GCS

set -e

# Install uv if not present
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Set up project directory
mkdir -p /opt/xautoresearch
cd /opt/xautoresearch

# Assume pyproject.toml and train.py are already downloaded or available via metadata/git.
uv pip install torch

# Run prepare and train
uv run python prepare.py || true
uv run python train.py > run.log 2>&1

# Upload log to GCS
gsutil cp run.log gs://socrate-ai-datalake/xautoresearch/runs/$(hostname)-$(date +%Y%m%d-%H%M%S).log
