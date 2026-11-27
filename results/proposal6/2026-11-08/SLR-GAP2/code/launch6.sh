#!/bin/bash
cd /home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal6/2026-11-08/SLR-GAP2/code
J=8 ./sweep_fam.sh 1-6 6 60 b2q4e2 40 62 1 -- --b 2 --evmin 2 --evp 2,3 --odp 3,5,7 --qs 4 --dmult 8 > ../logs/fam_b2q4e2.log 2>&1
