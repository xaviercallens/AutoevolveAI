"""Sweep cpsat_rule.py over N downward. usage: sweep.py Nhi Nlo J tlimit logname [--p5]  (7 workers on cores 1-7)"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
hi, lo, J, tl, logname = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
extra = sys.argv[6:]
log = os.path.join(os.path.dirname(HERE), "logs", logname)
for N in range(hi, lo - 1, -1):
    t0 = time.time()
    r = subprocess.run(["taskset", "-c", "1-7", "/home/callensxavier_gmail_com/.cache/slrvenv/bin/python", os.path.join(HERE, "cpsat_rule.py"), str(N), J, tl,
                        f"sweep{J}", "--workers", "7"] + extra, capture_output=True, text=True)
    with open(log, "a") as fh:
        fh.write(f"wall={time.time() - t0:.0f}s args={extra} " + (r.stdout.strip() or r.stderr[-300:]) + "\n")
