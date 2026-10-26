"""Post-process generated Lean files: `def` -> `noncomputable def` (literal-carrying generated files only; never the
Core templates). Usage: make_noncomputable.py FILE_OR_DIR ..."""
from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    n = 0
    for a in sys.argv[1:]:
        p = Path(a)
        files = sorted(p.glob("*.lean")) if p.is_dir() else [p]
        for f in files:
            if f.name == "Core.lean":
                continue
            s = f.read_text()
            t = re.sub(r"^def ", "noncomputable def ", s, flags=re.M)
            if t != s:
                f.write_text(t)
                n += 1
    print(f"rewrote {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
