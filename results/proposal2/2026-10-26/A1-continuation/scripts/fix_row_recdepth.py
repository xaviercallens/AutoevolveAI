"""Insert `set_option maxRecDepth 100000 in` before every `theorem row_<j>` (row conjunctions of 100+ segments hit the
default recursion depth during elaboration). Idempotent. Usage: fix_row_recdepth.py DIR ..."""
from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    n = 0
    for a in sys.argv[1:]:
        for f in sorted(Path(a).glob("R*.lean")):
            s = f.read_text()
            t = re.sub(r"(?<!in\n)^theorem row_", "set_option maxRecDepth 100000 in\ntheorem row_", s, flags=re.M)
            if t != s:
                f.write_text(t)
                n += 1
    print("fixed", n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
