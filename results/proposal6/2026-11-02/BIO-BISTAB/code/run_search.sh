#!/bin/bash
# usage: run_search.sh <core> <part> <first_seed> <last_seed>
PY=/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/.venv/bin/python
cd "$(dirname "$0")"
for s in $(seq $3 $4); do
  taskset -c $1 $PY p6_search.py $2 2 5000 $s > ../logs/p6_seed${s}_part$2.log 2>&1
done
echo done > ../logs/p6_done_part$2.flag
