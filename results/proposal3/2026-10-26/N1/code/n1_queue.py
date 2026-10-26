"""N1 helper: run n1_certify2.py jobs one after another (one job per line of QUEUE: the argument list of
n1_certify2.py after the script name; '#' lines skipped). Inherits the CPU affinity of the caller.

usage: python -I n1_queue.py QUEUE.txt [WAIT_PID]
  WAIT_PID: optionally wait until that process has exited before starting
"""

from __future__ import annotations

import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    if len(sys.argv) > 2:
        pid = int(sys.argv[2])
        while os.path.exists(f"/proc/{pid}"):
            time.sleep(5)
    for line in open(sys.argv[1]).read().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        args = line.split()
        log = args[0].replace(".json", ".log")
        with open(log, "a") as fh:
            subprocess.run([sys.executable, "-I", os.path.join(HERE, "n1_certify2.py")] + args, stdout=fh,
                           stderr=subprocess.STDOUT, check=False)


if __name__ == "__main__":
    main()
