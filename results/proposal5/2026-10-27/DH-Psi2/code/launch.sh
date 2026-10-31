#!/bin/bash
# Launch the two Python workers detached, pinned to cores 4 and 5.
D=/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery
P=$D/.venv/bin/python
L=$D/results/proposal5/2026-10-27/DH-Psi2
setsid nohup taskset -c 4 "$P" "$L/code/run_worker.py" 0 2 > "$L/logs/worker0.log" 2>&1 < /dev/null &
setsid nohup taskset -c 5 "$P" "$L/code/run_worker.py" 1 2 > "$L/logs/worker1.log" 2>&1 < /dev/null &
