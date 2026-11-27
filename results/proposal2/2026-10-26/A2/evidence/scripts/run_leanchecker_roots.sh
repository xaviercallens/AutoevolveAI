#!/bin/bash
# (e) the toolchain's own leanchecker on the root/statement modules (per-module replay into imports)
set -u
cd /home/callensxavier_gmail_com/proposal2/A2/ns-copy || exit 2
LC=/home/callensxavier_gmail_com/.elan/toolchains/leanprover--lean4---v4.34.0-rc2/bin/leanchecker
LAKE=/home/callensxavier_gmail_com/.elan/toolchains/leanprover--lean4---v4.34.0-rc2/bin/lake
for m in NavierStokes.ComparatorSolution NavierStokes.ComparatorR3Theorem NavierStokes.ComparatorTheorem NavierStokes.ComparatorDefinitions Euler.Solution Euler.SolutionDefinitions ComparatorChallenges.NavierStokes ComparatorChallenges.Euler; do
  s=$(date +%s)
  "$LAKE" env "$LC" "$m"
  rc=$?
  echo "leanchecker $m rc=$rc secs=$(( $(date +%s) - s ))"
done
echo "ALL DONE $(date -u +%FT%TZ)"
