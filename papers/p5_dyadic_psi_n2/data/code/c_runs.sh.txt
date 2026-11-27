#!/bin/bash
# Independent int-only C enumeration: 5 modes x 2 halves of the F0 range, one half per core.
# Usage: c_runs.sh HALF   (HALF = 0 -> F0 [0,16384) on core 4; HALF = 1 -> [16384,32768) on core 5)
set -e
L=/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal5/2026-10-27/DH-Psi2
B=$L/code/psi_exhaust
O=$L/data/c_enum
mkdir -p "$O"
H=$1
LO=$((H * 16384))
HI=$((LO + 16384))
CORE=$((4 + H))
taskset -c $CORE "$B" 3 1 $LO $HI > "$O/PSI_h$H.json"
taskset -c $CORE "$B" 1 1 $LO $HI > "$O/R_h$H.json"
taskset -c $CORE "$B" 4 1 $LO $HI > "$O/PLANT4_h$H.json"
taskset -c $CORE "$B" 1 0 $LO $HI > "$O/HF_R_h$H.json"
taskset -c $CORE "$B" 3 0 $LO $HI > "$O/HF_PSI_h$H.json"
taskset -c $CORE "$B" 3 1 0 0 200 > "$O/bruteforce_PSI_h$H.json"
taskset -c $CORE "$B" 4 1 0 0 100 > "$O/bruteforce_PLANT4_h$H.json"
taskset -c $CORE "$B" 3 0 0 0 100 > "$O/bruteforce_HF_PSI_h$H.json"
echo done > "$O/DONE_h$H"
