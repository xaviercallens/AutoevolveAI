#!/bin/bash
# Stage 2 of B1 (cores 6,7): controls, then SCHA for a = 1.0, 0.5, 0.7, 1.3.
set -e
PY="/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I"
B=/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal2/2026-10-26/B1
taskset -c 6,7 $PY $B/code/b1_controls.py $B/data/controls.json > $B/data/controls.log 2>&1
taskset -c 6,7 $PY $B/code/b1c_scha.py $B/data/scha.json 1.0 0.5 0.7 1.3 > $B/data/scha.log 2>&1
echo done
