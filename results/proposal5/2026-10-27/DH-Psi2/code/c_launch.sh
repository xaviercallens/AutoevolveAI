#!/bin/bash
L=/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal5/2026-10-27/DH-Psi2
setsid nohup bash "$L/code/c_runs.sh" 0 > "$L/logs/c_h0.log" 2>&1 < /dev/null &
setsid nohup bash "$L/code/c_runs.sh" 1 > "$L/logs/c_h1.log" 2>&1 < /dev/null &
