"""Replace the generated-table blocks of main.tex with the current bodies written by rev_tables.py.

A block is either the line '\\input{NAME.tex}\\bottomrule' (first run) or the lines between
'%BEGIN-GENERATED NAME.tex' and '%END-GENERATED NAME.tex' (later runs), so the script can be re-run after the tables
are regenerated.

Usage: python -I inline_tables.py <main.tex> <table_base.tex> <table_air.tex>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    tex = Path(sys.argv[1])
    s = tex.read_text()
    for f in sys.argv[2:]:
        p = Path(f)
        body = p.read_text().rstrip("\n")
        block = f"%BEGIN-GENERATED {p.name}\n{body}\n%END-GENERATED {p.name}\n\\bottomrule"
        first = f"\\input{{{p.name}}}\\bottomrule"
        if first in s:
            s = s.replace(first, block)
        else:
            pat = re.compile(rf"%BEGIN-GENERATED {re.escape(p.name)}\n.*?%END-GENERATED {re.escape(p.name)}\n\\bottomrule",
                             re.S)
            s, n = pat.subn(lambda m: block, s)
            if n != 1:
                raise SystemExit(f"block for {p.name} not found exactly once ({n})")
    tex.write_text(s)
    print("inlined", len(sys.argv) - 2, "tables")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
