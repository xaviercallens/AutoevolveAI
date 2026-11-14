#!/bin/bash
# Build the forged-kernel control module and run leanchecker on it (expected: rejection).
set -u
TC=/home/callensxavier_gmail_com/.elan/toolchains/leanprover--lean4---v4.34.0-rc2/bin
D=/home/callensxavier_gmail_com/proposal2/A2/controls/forged
export LEAN_PATH="$D/lib:$(cat /home/callensxavier_gmail_com/proposal2/A2/logs/lake_LEAN_PATH.txt)"
cd "$D" || exit 2
echo "--- compile (lean -o)"
"$TC/lean" -R src -o lib/A2Forged.olean -i lib/A2Forged.ilean src/A2Forged.lean
echo "compile rc=$?"
ls -la lib
echo "--- import-and-print-axioms from a fresh file"
printf 'import A2Forged\n#print axioms A2Forged.uses_forged\n#check (A2Forged.uses_forged : False)\n' > Importer.lean
"$TC/lean" Importer.lean
echo "importer rc=$?"
echo "--- leanchecker A2Forged"
timeout 600 "$TC/leanchecker" A2Forged
echo "leanchecker rc=$?"
