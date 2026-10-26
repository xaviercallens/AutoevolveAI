"""Insert the `(winStart off)` argument into grid-stage chunk files generated before the atStart fix."""
from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    n = 0
    for a in sys.argv[1:]:
        for f in sorted(Path(a).glob("*.lean")):
            s = f.read_text()
            t = re.sub(r"\(winC (\d+) (\d+)\) \(winEnd", r"(winC \1 \2) (winStart \1) (winEnd", s)
            if t != s:
                f.write_text(t)
                n += 1
    print("fixed", n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
