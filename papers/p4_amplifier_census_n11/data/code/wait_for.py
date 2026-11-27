"""Block until a text file contains a marker string or a timeout passes. Usage: wait_for.py <file> <marker> <timeout_s>"""

from __future__ import annotations

import sys
import time
from pathlib import Path


def main() -> None:
    path, marker, timeout = Path(sys.argv[1]), sys.argv[2], float(sys.argv[3])
    t0 = time.time()
    while time.time() - t0 < timeout:
        text = path.read_text(errors="replace") if path.exists() else ""
        hit = [mk for mk in marker.split("|") if mk and mk in text]
        if hit:
            print("found", hit, "after", round(time.time() - t0), "s")
            return
        time.sleep(10)
    print("timeout")


if __name__ == "__main__":
    main()
