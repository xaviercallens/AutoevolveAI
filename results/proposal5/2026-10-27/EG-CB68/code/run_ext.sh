#!/bin/bash
# EG-CB68 exploratory extension (PREREG_ADDENDUM_1/2): arbitrary-root caps 35, 36, ... with the certificate
# streamed into cb_check_fast; next cap only if (last wall time x 2.2) fits before the deadline.
set -u
cd "$(dirname "$0")/.."
deadline=$(date -u -d "2026-11-01 14:45" +%s)
until grep -q rcert-done logs/rcert34_fast.out; do sleep 30; done
cap=35
while true; do
  t0=$(date +%s)
  bash code/run_rcert.sh $cap fast > logs/rcert${cap}_fast.out 2>&1
  t1=$(date +%s)
  echo "cap $cap wall_s $((t1 - t0)) finished $(date -u)" >> logs/ext_progress.txt
  grep -q '"accepted":true' data/main/R_cap${cap}_checkfast.json || { echo "cap $cap NOT accepted: stop" >> logs/ext_progress.txt; break; }
  proj=$(( (t1 - t0) * 22 / 10 ))
  if [ $((t1 + proj)) -gt $deadline ]; then echo "stop: cap $((cap + 1)) projected ${proj}s exceeds deadline" >> logs/ext_progress.txt; break; fi
  cap=$((cap + 1))
done
echo ext-done >> logs/ext_progress.txt
