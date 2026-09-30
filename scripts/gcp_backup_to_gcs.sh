#!/bin/bash
# Backup xautoresearch results to GCP Socrate AI data lake
# Usage: bash scripts/gcp_backup_to_gcs.sh
BUCKET="gs://socrate-ai-datalake"
gsutil -m cp -r /mnt/data/xautoresearch/results.tsv $BUCKET/xautoresearch/results.tsv
gsutil -m cp -r /mnt/data/xautoresearch/run_logs/ $BUCKET/xautoresearch/run_logs/
gsutil -m cp -r results/ar_h5/ $BUCKET/xautoresearch/ar_h5/
gsutil -m cp papers/laya_coding_companion_paper.pdf $BUCKET/xautoresearch/paper_v3.pdf
echo "Backup complete"
