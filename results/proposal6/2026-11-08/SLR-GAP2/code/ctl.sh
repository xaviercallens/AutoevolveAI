#!/bin/bash
cd /home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal6/2026-11-08/SLR-GAP2/code
V=/home/callensxavier_gmail_com/.cache/slrvenv/bin/python
taskset -c 1-6 $V cpsat_gen.py 64 8 200 ctl_n63 --evmin 4 --workers 6 --family ctl_pos --outdir ../certificates/ctl
taskset -c 1-6 $V cpsat_gen.py 45 8 200 ctl_neg_n44 --evmin 4 --workers 6 --family ctl_neg --outdir ../certificates/ctl
