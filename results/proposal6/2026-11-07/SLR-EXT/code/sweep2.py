"""usage: sweep2.py logname tlimit J pool N1 N2 ..."""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
logname, tl, J, pool = sys.argv[1:5]
for N in sys.argv[5:]:
    t0 = time.time()
    r = subprocess.run(["taskset", "-c", "1-7", "/home/callensxavier_gmail_com/.cache/slrvenv/bin/python", os.path.join(HERE, "cpsat_rule.py"), N, J, tl,
                        f"sw2_{pool}", "--workers", "7", "--pool", pool], capture_output=True, text=True)
    with open(os.path.join(os.path.dirname(HERE), "logs", logname), "a") as fh:
        fh.write(f"wall={time.time() - t0:.0f}s pool={pool} " + (r.stdout.strip() or r.stderr[-300:]) + "\n")
