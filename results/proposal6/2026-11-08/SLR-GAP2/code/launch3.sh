#!/bin/bash
cd /home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal6/2026-11-08/SLR-GAP2/code
J=4 ./sweep_fam.sh 1-6 6 90 b2q8s 40 94 1 -- --b 2 --evmin 4 --evp 2,3 --odp 3,5 --qs 8 --dmult 8 > ../logs/fam_b2q8s.log 2>&1
J=8 ./sweep_fam.sh 1-6 6 90 b4q8w 40 94 1 -- --b 4 --evmin 8 --evp 2,3 --odp 3,5,7 --qs 8 --dmult 8 > ../logs/fam_b4q8w.log 2>&1
