#!/bin/bash
# Resumable launcher: rerun this script after a reboot; it continues from enclosure_ckpt.json.
cd "$(dirname "$0")/.."
echo "launch $(date -u +%FT%TZ) p=24 tau=1e-22 cpu_cap=21600s" >> logs/robertson_run.log
exec taskset -c 1 sage --python3 code/run_robertson.py logs/enclosure_ckpt.json logs/robertson_run.log 21600 24 1e-22
