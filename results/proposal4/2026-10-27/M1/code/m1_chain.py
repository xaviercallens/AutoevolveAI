"""Wait until the driver's JOBSET_A has finished (its status JSON ends with {"done": true}), then run JOBSET_B
in this process's turn (one certifier process at a time). usage: python -I m1_chain.py M1_DIR JOBSET_A JOBSET_B"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time


def main() -> None:
    m1, a, b = sys.argv[1], sys.argv[2], sys.argv[3]
    st = os.path.join(m1, "logs", f"driver_{a}.json")
    while True:
        try:
            with open(st) as fh:
                rows = json.load(fh)
            if rows and rows[-1].get("done"):
                break
        except (OSError, ValueError):
            pass
        time.sleep(30)
    subprocess.run([sys.executable, "-I", os.path.join(m1, "code", "m1_driver.py"), m1, b], check=False)
    print("chain done", b)


if __name__ == "__main__":
    main()
