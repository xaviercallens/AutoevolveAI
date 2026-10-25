"""Build main.pdf: pdflatex twice in this directory, then report page count, warnings and undefined refs."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(n: int) -> int:
    p = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=HERE,
                       capture_output=True, text=True)
    (HERE / f"build{n}.log").write_text(p.stdout + p.stderr)
    return p.returncode


def main() -> int:
    rcs = [run(1), run(2)]
    log = (HERE / "main.log").read_text(errors="replace")
    pages = re.search(r"Output written on main\.pdf \((\d+) pages", log)
    undef = re.findall(r"(?:Reference|Citation) `[^']+' .*undefined", log)
    overfull = len(re.findall(r"Overfull \\hbox", log))
    print({"rc": rcs, "pages": int(pages.group(1)) if pages else None, "undefined": undef,
           "overfull_hbox": overfull, "rerun_warning": "Rerun to get" in log})
    return 0 if rcs == [0, 0] and pages and not undef else 1


if __name__ == "__main__":
    sys.exit(main())
