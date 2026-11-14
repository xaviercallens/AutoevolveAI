"""Block (sleeping, no CPU work) until a log file contains a marker string, or a timeout passes.

Usage: python -I wait_for_text.py <file> <marker> <timeout_s>
"""

from __future__ import annotations

import sys
import time
from pathlib import Path


def main() -> int:
    p, marker, tmax = Path(sys.argv[1]), sys.argv[2], float(sys.argv[3])
    t0 = time.time()
    while time.time() - t0 < tmax:
        if p.exists() and marker in p.read_text(errors="replace"):
            print("found", marker, "after", round(time.time() - t0), "s")
            return 0
        time.sleep(15)
    print("timeout")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
