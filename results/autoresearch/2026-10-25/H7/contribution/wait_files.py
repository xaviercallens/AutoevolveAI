"""Wait until every listed file exists (or timeout seconds pass), printing one line per file as it appears."""
import os
import sys
import time

timeout = float(sys.argv[1])
pending = list(sys.argv[2:])
t0 = time.time()
while pending and time.time() - t0 < timeout:
    for p in list(pending):
        if os.path.exists(p):
            print("ready", p, round(time.time() - t0), flush=True)
            pending.remove(p)
    time.sleep(5)
for p in pending:
    print("timeout", p, flush=True)
