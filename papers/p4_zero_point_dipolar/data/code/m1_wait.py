"""Wait until a file exists (or a timeout in seconds passes); prints the outcome. usage: python -I m1_wait.py PATH TIMEOUT"""
from __future__ import annotations

import os
import sys
import time


def main() -> None:
    path, timeout = sys.argv[1], float(sys.argv[2])
    t0 = time.time()
    while not os.path.exists(path) and time.time() - t0 < timeout:
        time.sleep(15)
    print("exists" if os.path.exists(path) else "timeout", round(time.time() - t0), path)


if __name__ == "__main__":
    main()
