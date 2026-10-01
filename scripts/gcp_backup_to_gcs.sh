#!/bin/bash
# Backup all Laya-LoRA + Qwen3.8 + xAutoresearch assets to GCP Socrate AI data lake
# Usage: bash scripts/gcp_backup_to_gcs.sh

set -e
BUCKET="${BUCKET:-gs://socrateai-datalake-gen-lang-client-0625573011}"

echo "=== Backing up to $BUCKET ==="

# 1. Back up compiled paper and LaTeX source
echo "[1/6] Backing up academic paper..."
gsutil -m cp papers/laya_coding_companion_paper.pdf "$BUCKET/papers/laya_coding_companion_paper.pdf"
gsutil -m cp papers/laya_coding_companion_paper.pdf "$BUCKET/xautoresearch/paper_v3.pdf"
gsutil -m cp papers/laya_coding_companion_paper.tex "$BUCKET/papers/laya_coding_companion_paper.tex"

# 2. Back up empirical benchmark results
echo "[2/6] Backing up empirical benchmarks..."
if [ -d "results/dual_process_benchmark" ] && [ "$(ls -A results/dual_process_benchmark 2>/dev/null)" ]; then
  gsutil -m cp -r results/dual_process_benchmark/ "$BUCKET/benchmarks/dual_process_benchmark/"
fi
if [ -d "results/qwen38_benchmark" ] && [ "$(ls -A results/qwen38_benchmark 2>/dev/null)" ]; then
  gsutil -m cp -r results/qwen38_benchmark/ "$BUCKET/benchmarks/qwen38_benchmark/"
fi
if [ -d "artifacts/laya_coding_companion" ] && [ "$(ls -A artifacts/laya_coding_companion 2>/dev/null)" ]; then
  gsutil -m cp -r artifacts/laya_coding_companion/ "$BUCKET/artifacts/laya_coding_companion/"
fi
if [ -d "results/ar_h5" ] && [ "$(ls -A results/ar_h5 2>/dev/null)" ]; then
  gsutil -m cp -r results/ar_h5/ "$BUCKET/xautoresearch/ar_h5/"
fi

# 3. Back up xAutoresearch telemetry
echo "[3/6] Backing up xAutoresearch telemetry..."
if [ -f "/mnt/data/home/xavkal/xautoresearch/results.tsv" ]; then
  gsutil -m cp /mnt/data/home/xavkal/xautoresearch/results.tsv "$BUCKET/xautoresearch/results.tsv"
fi
if [ -d "/mnt/data/xautoresearch/run_logs" ] && [ "$(ls -A /mnt/data/xautoresearch/run_logs 2>/dev/null)" ]; then
  gsutil -m cp -r /mnt/data/xautoresearch/run_logs/ "$BUCKET/xautoresearch/run_logs/"
fi

# 4. Back up model checkpoints
echo "[4/6] Backing up model checkpoints..."
if [ -d "/mnt/data/home/xavkal/laya_coding_checkpoints/stage3" ] && [ "$(ls -A /mnt/data/home/xavkal/laya_coding_checkpoints/stage3 2>/dev/null)" ]; then
  gsutil -m cp -r /mnt/data/home/xavkal/laya_coding_checkpoints/stage3 "$BUCKET/checkpoints/"
fi
if [ -d "/mnt/data/home/xavkal/laya_coding_checkpoints/v2" ] && [ "$(ls -A /mnt/data/home/xavkal/laya_coding_checkpoints/v2 2>/dev/null)" ]; then
  gsutil -m cp -r /mnt/data/home/xavkal/laya_coding_checkpoints/v2 "$BUCKET/checkpoints/"
fi

# 5. Back up training receipts
echo "[5/6] Backing up training receipts..."
if [ -d "results/laya_v2_training" ] && [ "$(ls -A results/laya_v2_training 2>/dev/null)" ]; then
  gsutil -m cp -r results/laya_v2_training/ "$BUCKET/receipts/laya_v2_training/"
fi

# 6. Verify backup listing
echo "[6/6] Verifying GCS data lake contents..."
gsutil ls -r "$BUCKET/"

echo "=== Backup to GCP Socrate AI Data Lake Complete ==="
