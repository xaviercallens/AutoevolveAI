#!/bin/bash
# A2 rebuild driver: NS closure first, then Euler closure, then the challenge modules.
# Pinned to cores 0-3 by the caller (taskset); LEAN_NUM_THREADS caps lake's job pool and lean's threads.
set -u
cd /home/callensxavier_gmail_com/proposal2/A2/ns-copy || exit 2
export LEAN_NUM_THREADS=4
LAKE=/home/callensxavier_gmail_com/.elan/toolchains/leanprover--lean4---v4.34.0-rc2/bin/lake
LOGD=/home/callensxavier_gmail_com/proposal2/A2/logs
for tgt in NavierStokes.ComparatorSolution Euler.Solution ComparatorChallenges.NavierStokes ComparatorChallenges.Euler; do
  echo "=== START $tgt $(date -u +%FT%TZ)" >> "$LOGD/build_progress.log"
  start=$(date +%s)
  "$LAKE" build -v "$tgt" > "$LOGD/build_${tgt}.log" 2>&1
  rc=$?
  end=$(date +%s)
  echo "=== END $tgt rc=$rc elapsed_s=$((end-start)) $(date -u +%FT%TZ)" >> "$LOGD/build_progress.log"
done
echo "=== ALL DONE $(date -u +%FT%TZ)" >> "$LOGD/build_progress.log"
