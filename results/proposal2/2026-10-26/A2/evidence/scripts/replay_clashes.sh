#!/bin/bash
set -u
TC=/home/callensxavier_gmail_com/.elan/toolchains/leanprover--lean4---v4.34.0-rc2/bin
A=/home/callensxavier_gmail_com/proposal2/A2
export LEAN_PATH="$(cat $A/logs/lake_LEAN_PATH.txt)"
"$TC/lean" --run $A/lean_scripts/A2Replay.lean $A/audit/replay_corpus_$1.txt $A/audit/replay_ext_$1.txt --clashes-only
echo "rc=$?"
