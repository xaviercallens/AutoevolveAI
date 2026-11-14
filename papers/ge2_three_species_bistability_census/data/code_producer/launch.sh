#!/bin/bash
# usage: launch.sh n npairs stage   (6 shards on cores 1-6; resumable: rerun the same command after a reboot)
cd /home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal7/2026-11-11/GE2
n=$1
np=$2
st=${3:-1}
for s in 0 1 2 3 4 5; do
  core=$((s+1))
  setsid nohup taskset -c $core python3 code/run_census.py $n $s 6 $np $st >> logs/driver_n${n}_s${s}.out 2>&1 &
done
