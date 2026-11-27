#!/bin/bash
cd /home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal6/2026-11-08/SLR-GAP2/code
./sweep_fam.sh 1-3 3 40 b3q12 40 95 3 -- --b 3 --evmin 6 --evp 2,3 --odp 2,5 --qs 12 --dmult 24 --jstep 3 > ../logs/fam_b3.log 2>&1 &
./sweep_fam.sh 4-6 3 40 b6q12 40 95 3 -- --b 6 --evmin 12 --evp 2,3 --odp 2,3,5 --qs 12 --dmult 24 --jstep 3 > ../logs/fam_b6.log 2>&1 &
wait
