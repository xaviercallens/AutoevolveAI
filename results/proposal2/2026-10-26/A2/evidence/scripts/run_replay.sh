#!/bin/bash
# Kernel replay of all corpus declarations of one closure (ns|euler) into the non-corpus base env.
set -u
TAG="$1"
TC=/home/callensxavier_gmail_com/.elan/toolchains/leanprover--lean4---v4.34.0-rc2/bin
A=/home/callensxavier_gmail_com/proposal2/A2
export LEAN_PATH="$(cat $A/logs/lake_LEAN_PATH.txt)"
echo "START $(date -u +%FT%TZ)"
/usr/bin/time -v "$TC/lean" --run $A/lean_scripts/A2Replay.lean $A/audit/replay_corpus_$TAG.txt $A/audit/replay_ext_$TAG.txt
echo "replay rc=$?"
echo "END $(date -u +%FT%TZ)"
