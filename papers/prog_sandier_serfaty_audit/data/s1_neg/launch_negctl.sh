#!/bin/bash
# Launches the S1-neg negative-control certificate copy on cores 4-5 with 2 OpenMP threads.
export OMP_NUM_THREADS=2
exec taskset -c 4-5 /usr/bin/python3 -I -B /home/callensxavier_gmail_com/programmes-2026-10-25/P1/negctl/verification/run-certificate.py --output-dir /home/callensxavier_gmail_com/programmes-2026-10-25/P1/negctl/run > /home/callensxavier_gmail_com/programmes-2026-10-25/P1/negctl/wrapper.log 2>&1
