#!/bin/bash
# EG-CB68: arbitrary-root certificate at cap CAP streamed through a FIFO into the Python checker (producer + checker on core 3).
set -u
cd "$(dirname "$0")/.."
cap=$1
F=/home/callensxavier_gmail_com/EG-CB68_scratch/fifo_Rpy$cap
rm -f "$F"; mkfifo "$F"
taskset -c 3 code/cb_search $cap 0 A -cert "$F" > data/main/R_cap${cap}_A_certrun_py.json &
taskset -c 3 tee >(sha256sum > logs/main/R_cap${cap}_stream_py_sha256.txt) < "$F" | taskset -c 3 python3 -I code/cb_check.py - --json data/main/R_cap${cap}_check_py.json > /dev/null
wait
sleep 5
rm -f "$F"
echo rcert-py-done $cap
