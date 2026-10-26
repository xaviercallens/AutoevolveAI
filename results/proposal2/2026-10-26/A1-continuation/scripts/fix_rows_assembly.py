"""Rewrite `theorem <stage>_rows : row_0 ∧ row_1 ...` (generated before the fix) into the `type_of%` form.
Idempotent. Usage: fix_rows_assembly.py Assemble.lean ..."""
from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    for a in sys.argv[1:]:
        f = Path(a)
        s = f.read_text()
        m = re.search(r"theorem (\w+)_rows : (.*?) :=", s, flags=re.S)
        if not m or "type_of%" in m.group(2):
            print(f, "unchanged")
            continue
        names = [x.strip() for x in m.group(2).split("∧")]
        new = f"theorem {m.group(1)}_rows : " + " ∧\n    ".join(f"(type_of% {x})" for x in names) + " :="
        f.write_text(s[:m.start()] + new + s[m.end():])
        print(f, len(names), "rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
