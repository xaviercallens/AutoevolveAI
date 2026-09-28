#!/usr/bin/env python3
"""Per-file 100 % line+branch check for v2 card acceptance.

Why: pytest-cov 7 / coverage 7.16 collect nothing for ``--cov=anse/v2/<module>`` and the
dotted form ``--cov=anse.v2.<module>`` imports the module inside coverage's process and
segfaults once torch is loaded (reproduced 2026-09-28 in .venv-v2 and .venv). The only
reliable form is directory scope, ``--cov=anse/v2 --cov-report=json:<path>``; this script
then holds the card's OWN files to 100 % from that JSON, so foreign modules in the package
cannot fail (or pass) a card.

Usage:
    python tools/v2_cov_check.py .scratchpad/cov.json anse/v2/metrics.py [anse/v2/other.py ...]
Exit 0 only if every named file is at 100 % lines AND 100 % branches; prints one line per file.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def check(report: dict, files: list[str]) -> list[tuple[str, bool, str]]:
    """Return (file, ok, detail) per requested file; a file absent from the report is not ok."""
    by_path = {Path(p).as_posix(): v for p, v in report.get("files", {}).items()}
    out: list[tuple[str, bool, str]] = []
    for f in files:
        key = Path(f).as_posix()
        entry = next((v for p, v in by_path.items() if p.endswith(key)), None)
        if entry is None:
            out.append((f, False, "not in coverage report (never imported by the tests?)"))
            continue
        s = entry["summary"]
        missing_lines = s.get("missing_lines", 0)
        missing_branches = s.get("missing_branches", 0)
        ok = missing_lines == 0 and missing_branches == 0
        detail = (f"lines {s.get('percent_covered', 0):.1f}% (missing {missing_lines}), "
                  f"branches missing {missing_branches}")
        out.append((f, ok, detail))
    return out


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) < 2:
        print(__doc__)
        return 2
    report = json.loads(Path(args[0]).read_text())
    results = check(report, args[1:])
    for f, ok, detail in results:
        print(f"{'OK  ' if ok else 'FAIL'} {f}: {detail}")
    return 0 if all(ok for _, ok, _ in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
