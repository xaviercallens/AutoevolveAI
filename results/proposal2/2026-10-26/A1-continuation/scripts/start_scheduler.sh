#!/bin/bash
# Start the A1-continuation L1 scheduler detached (survives the session). Safe to run twice: the second instance
# exits because the first holds the flock. Usage: bash start_scheduler.sh
mkdir -p /home/callensxavier_gmail_com/a1l1_oleans/logs
setsid nohup nice -n 5 /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I \
  /home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal2/2026-10-26/A1-continuation/scripts/scheduler.py \
  >> /home/callensxavier_gmail_com/a1l1_oleans/logs/scheduler.stdout 2>&1 < /dev/null &
echo "launched; pid file: /home/callensxavier_gmail_com/a1l1_oleans/scheduler.pid"
