#!/bin/bash
set -u
cd /home/callensxavier_gmail_com/proposal2/A2/ns-copy || exit 2
echo "START $(date -u +%FT%TZ)"
/home/callensxavier_gmail_com/.elan/toolchains/leanprover--lean4---v4.34.0-rc2/bin/lake env lean ../audit/SolutionAudit_Euler.lean
echo "rc=$?"
echo "END $(date -u +%FT%TZ)"
