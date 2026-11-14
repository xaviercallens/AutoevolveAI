#!/bin/bash
# EG-CB68: arbitrary-root certificate at cap CAP streamed through a FIFO (too large to store) into
#   - cb_check_fast (C, core 2, together with the producer) and, if MODE=both, also
#   - cb_check.py (Python, core 3).
# The stream's sha256 is recorded on the fly. usage: run_rcert.sh CAP [fast|both]
set -u
cd "$(dirname "$0")/.."
cap=$1
mode=${2:-fast}
F=/home/callensxavier_gmail_com/EG-CB68_scratch/fifo_R$cap
rm -f "$F"; mkfifo "$F"
taskset -c 2 code/cb_search $cap 0 A -cert "$F" > data/main/R_cap${cap}_A_certrun.json &
if [ "$mode" = both ]; then
  taskset -c 2 tee >(sha256sum > logs/main/R_cap${cap}_stream_sha256.txt) >(taskset -c 2 code/cb_check_fast > data/main/R_cap${cap}_checkfast.json) < "$F" \
    | taskset -c 3 python3 -I code/cb_check.py - --json data/main/R_cap${cap}_check.json > /dev/null
else
  taskset -c 2 tee >(sha256sum > logs/main/R_cap${cap}_stream_sha256.txt) < "$F" | taskset -c 2 code/cb_check_fast > data/main/R_cap${cap}_checkfast.json
fi
wait
sleep 5
rm -f "$F"
echo rcert-done $cap
