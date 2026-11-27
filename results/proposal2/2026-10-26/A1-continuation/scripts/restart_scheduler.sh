#!/bin/bash
# Replace the running scheduler with the current scheduler.py WITHOUT losing running workers: SIGKILL the scheduler
# (its Lean workers run in their own sessions and survive), then start a new one, which adopts every still-running
# worker by pid. (A plain SIGTERM instead stops the workers too and re-queues them.)
PIDF=/home/callensxavier_gmail_com/a1l1_oleans/scheduler.pid
if [ -f "$PIDF" ]; then kill -9 "$(cat "$PIDF")" 2>/dev/null; fi
sleep 1
bash /home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal2/2026-10-26/A1-continuation/scripts/start_scheduler.sh
