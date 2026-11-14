"""Clean build of main.pdf: remove aux files, run pdflatex twice in this directory, report warnings and page count."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    for ext in ("aux", "log", "out", "toc"):
        p = HERE / f"main.{ext}"
        if p.exists():
            p.unlink()
    for i in (1, 2):
        res = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=HERE,
                             capture_output=True, text=True, errors="replace")
        (HERE / f"build{i}.log").write_text(res.stdout + res.stderr)
        if res.returncode != 0:
            print(f"pass {i} failed rc {res.returncode}")
            print(res.stdout[-3000:])
            return 1
    log = (HERE / "main.log").read_text(errors="replace")
    undef = re.findall(r"(?:Reference|Citation) `[^']+' .*undefined", log)
    over = len(re.findall(r"Overfull \\hbox", log))
    warn = re.findall(r"LaTeX Warning: [^\n]*", log)
    pages = re.search(r"Output written on main\.pdf \((\d+) pages", log)
    print(f"pages {pages.group(1) if pages else '?'}; undefined refs {len(undef)} {undef[:5]}; overfull hbox {over}; warnings {len(warn)}")
    for w in warn[:10]:
        print(w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
