#!/bin/bash
# EG-CB68 extension: oracle B (half-path joins) at arbitrary-root caps 35, 36 on core 3, after the Python R34 check,
# for transcript-hash agreement with the oracle-A certificate runs. Skips a cap if it cannot finish before the deadline.
set -u
cd "$(dirname "$0")/.."
deadline=$(date -u -d "2026-11-01 14:45" +%s)
until grep -q rcert-py-done logs/rcert34_py.out; do sleep 30; done
for cap in 35 36; do
  now=$(date +%s)
  if [ $((now + 1100 * 2 ** (cap - 33))) -gt $deadline ]; then echo "skip B cap $cap (deadline)" >> logs/ext_progress.txt; continue; fi
  taskset -c 3 code/cb_search $cap 0 B > data/main/R_cap${cap}_B.json
  echo "B cap $cap done $(date -u)" >> logs/ext_progress.txt
done
