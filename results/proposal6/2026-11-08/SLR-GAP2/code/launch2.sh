#!/bin/bash
cd /home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal6/2026-11-08/SLR-GAP2/code
J=4 ./sweep_fam.sh 1-2 2 60 b3s 40 94 2 -- --b 3 --evmin 6 --evp 2,3 --odp 2,5 --qs 12 --dmult 24 --jstep 6  > ../logs/fam_b3s.log 2>&1 &
J=4 ./sweep_fam.sh 3-4 2 60 b4q8 40 94 2 -- --b 4 --evmin 8 --evp 2,3 --odp 3,5 --qs 8 --dmult 8 > ../logs/fam_b4.log 2>&1 &
J=2 ./sweep_fam.sh 5-6 2 60 b2w 40 94 2 -- --b 2 --evmin 2 --evp 2,3,5 --odp 3,5,7 --qs 8 --dmult 8 > ../logs/fam_b2w.log 2>&1 &
wait
