"""Build papers/ar_yukawa_crystal/main.pdf: pdflatex twice, keep logs as build1.log/build2.log, remove aux files.

Usage: python -I build_pdf_stage5.py PAPER_DIR
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path


def main(paper_dir: str) -> int:
    d = Path(paper_dir)
    for i in (1, 2):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=d,
                           capture_output=True, text=True)
        (d / f"build{i}.log").write_text(r.stdout + r.stderr)
        print(f"pass {i}: rc {r.returncode}")
        if r.returncode != 0:
            print(r.stdout[-3000:])
            return r.returncode
    log = (d / "main.log").read_text(errors="replace")
    for pat in ("undefined", "Rerun", "Overfull", "Warning"):
        hits = [l for l in log.splitlines() if pat in l]
        print(f"{pat}: {len(hits)}")
        for h in hits[:8]:
            print("   ", h)
    pages = subprocess.run(["pdfinfo", "main.pdf"], cwd=d, capture_output=True, text=True).stdout
    m = re.search(r"Pages:\s+(\d+)", pages)
    print("pages", m.group(1) if m else "?")
    for ext in ("aux", "log", "out", "toc"):
        p = d / f"main.{ext}"
        if p.exists():
            p.unlink()
    shutil.disk_usage(d)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
