#!/bin/bash
# Negative + positive control for A2Replay.lean
set -u
TC=/home/callensxavier_gmail_com/.elan/toolchains/leanprover--lean4---v4.34.0-rc2/bin
D=/home/callensxavier_gmail_com/proposal2/A2/controls/forged
export LEAN_PATH="$D/lib:$(cat /home/callensxavier_gmail_com/proposal2/A2/logs/lake_LEAN_PATH.txt)"
cd "$D" || exit 2
echo "A2Forged" > corpus_forged.txt
echo "Lean" > ext_forged.txt
echo "--- NEGATIVE control: replay forged module (expect failure)"
"$TC/lean" --run /home/callensxavier_gmail_com/proposal2/A2/lean_scripts/A2Replay.lean corpus_forged.txt ext_forged.txt
echo "replay forged rc=$?"
echo "--- POSITIVE control: replay NavierStokes.ComparatorDefinitions against Mathlib (expect OK)"
echo "NavierStokes.ComparatorDefinitions" > corpus_pos.txt
echo "Mathlib" > ext_pos.txt
"$TC/lean" --run /home/callensxavier_gmail_com/proposal2/A2/lean_scripts/A2Replay.lean corpus_pos.txt ext_pos.txt
echo "replay positive rc=$?"
