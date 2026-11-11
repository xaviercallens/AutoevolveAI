#!/bin/bash
cd /home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal6/2026-11-08/SLR-GAP2/code
J=8 ./sweep_fam.sh 1-6 6 45 b2q8J8 40 87 1 -- --b 2 --evmin 4 --evp 2,3 --odp 3,5 --qs 8 --dmult 8 > ../logs/fam_b2q8J8b.log 2>&1
