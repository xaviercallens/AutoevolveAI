#!/bin/bash
# Dose-response variants of S1-neg. A: midpoint constant 1/24 -> 1/12 on cores 4-5. B: Lipschitz allowance x2 on cores 6-7.
export OMP_NUM_THREADS=2
B=/home/callensxavier_gmail_com/programmes-2026-10-25/P1
taskset -c 4-5 /usr/bin/python3 -I -B $B/negctl_A_x2/run-certificate.py --output-dir $B/negctl_A_x2_run > $B/negctl_A_x2.wrapper.log 2>&1 &
taskset -c 6-7 /usr/bin/python3 -I -B $B/negctl_B_lip/run-certificate.py --output-dir $B/negctl_B_lip_run > $B/negctl_B_lip.wrapper.log 2>&1 &
wait
