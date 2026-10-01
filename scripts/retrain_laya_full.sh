#!/bin/bash
set -e

echo "================================================="
echo "Laya Coding Companion - Full Retrain Pipeline"
echo "================================================="

CHECKPOINT_DIR="/mnt/data/home/xavkal/laya_coding_checkpoints/v2/"
GCS_BACKUP_PATH="gs://autoevolve-backups/laya_v2_checkpoints/"

echo ">>> Phase 1: Training Stage 1"
uv run python scripts/train_laya_coding.py --stage 1 --full_scale --checkpoint_dir "$CHECKPOINT_DIR"

echo ">>> Phase 2: Training Stage 2"
uv run python scripts/train_laya_coding.py --stage 2 --full_scale --checkpoint_dir "$CHECKPOINT_DIR"

echo ">>> Phase 3: Training Stage 3"
uv run python scripts/train_laya_coding.py --stage 3 --full_scale --checkpoint_dir "$CHECKPOINT_DIR"

echo ">>> Phase 4: Calibrating Quality Gate Threshold"
uv run python scripts/calibrate_threshold.py --checkpoint_dir "$CHECKPOINT_DIR/stage3"

echo ">>> Phase 5: Running Benchmark (Tests)"
uv run pytest tests/ -k laya -v || echo "Tests failed or no tests found, continuing..."

echo ">>> Phase 6: Backing up to GCS"
gsutil -m cp -r "$CHECKPOINT_DIR" "$GCS_BACKUP_PATH" || echo "GCS backup failed, please verify gsutil is configured."

echo "================================================="
echo "Pipeline Complete."
echo "================================================="
