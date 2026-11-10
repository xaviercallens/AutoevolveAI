#!/bin/bash
# usage: sweep_fam.sh CORES WORKERS TLIM FAMILY NLO NHI NSTEP -- extra args
cd /home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal6/2026-11-08/SLR-GAP2/code
V=/home/callensxavier_gmail_com/.cache/slrvenv/bin/python
CORES=$1; W=$2; T=$3; FAM=$4; LO=$5; HI=$6; ST=$7; shift 8
for ((N=HI; N>=LO; N-=ST)); do
  taskset -c $CORES $V cpsat_gen.py $N ${J:-8} $T ${FAM}_N$N --workers $W --family $FAM --outdir ../certificates "$@"
done
