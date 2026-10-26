"""Build « Le journal des découvertes »: generated back matter, then pdflatex three times, then a log report.

The report separates problems in the frame (main.tex, cadre/, gen/) from problems in the contribution chapters
(chapters/cNN.tex, written by other agents), lists every error and every overfull box above the threshold,
counts the pages, and says which chapters are present and which are still placeholders.
Usage: python -I code/build.py [--threshold 15]   (any working directory)
Exit code: 0 if there is no LaTeX error and no frame overfull above the threshold, 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]
PY = sys.executable


def run_pdflatex(passes: int) -> list[int]:
    """Run pdflatex `passes` times in the book directory; return the exit codes."""
    codes = []
    for _ in range(passes):
        proc = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
            cwd=BOOK, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
        )
        codes.append(proc.returncode)
        if proc.returncode != 0:
            break
    return codes


def attribute(log: str) -> list[tuple[str, str]]:
    """Walk the log, tracking the file stack from '(' and ')' tokens, and attribute each problem line to a file."""
    events: list[tuple[str, str]] = []
    stack: list[str] = []
    file_re = re.compile(r"\((\./[^\s()]+|/[^\s()]+)")
    lines = log.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("!") or re.match(r"(Overfull|Underfull) \\[hv]box", line) or "LaTeX Warning: Reference" in line:
            current = next((f for f in reversed(stack) if f.endswith(".tex")), "main.tex")
            detail = line if not line.startswith("!") else line + " | " + " ".join(lines[i + 1:i + 3])
            events.append((current, detail))
        pos = 0
        while pos < len(line):
            ch = line[pos]
            if ch == "(":
                m = file_re.match(line, pos)
                if m:
                    stack.append(m.group(1))
                    pos = m.end()
                    continue
                stack.append("")
            elif ch == ")" and stack:
                stack.pop()
            pos += 1
    return events


def page_count() -> int:
    out = subprocess.run(["pdfinfo", str(BOOK / "main.pdf")], capture_output=True, text=True, check=False).stdout
    m = re.search(r"Pages:\s+(\d+)", out)
    return int(m.group(1)) if m else -1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=15.0)
    args = ap.parse_args()
    gen = subprocess.run([PY, "-I", str(BOOK / "code" / "make_backmatter.py")], capture_output=True, text=True)
    if gen.returncode != 0:
        print(gen.stdout, gen.stderr)
        return 1
    codes = run_pdflatex(3)
    log = (BOOK / "main.log").read_text(errors="replace")
    events = attribute(log)
    errors = [(f, d) for f, d in events if d.startswith("!")]
    overfull = []
    for f, d in events:
        m = re.match(r"Overfull \\[hv]box \(([\d.]+)pt too (wide|high)\)(.*)", d)
        if m and float(m.group(1)) > args.threshold:
            overfull.append((f, float(m.group(1)), d.strip()))
    undefined = sorted({d for _, d in events if "Reference" in d and "undefined" in d})
    frame = lambda f: "/chapters/" not in f  # noqa: E731
    present = sorted(p.stem for p in (BOOK / "chapters").glob("c[0-2][0-9].tex"))
    report = {
        "pdflatex_exit_codes": codes,
        "pages": page_count(),
        "errors_frame": [e for e in errors if frame(e[0])],
        "errors_chapters": [e for e in errors if not frame(e[0])],
        "overfull_over_threshold_frame": [o for o in overfull if frame(o[0])],
        "overfull_over_threshold_chapters": [o for o in overfull if not frame(o[0])],
        "undefined_references": undefined,
        "chapters_present": present,
        "chapters_pending": [f"c{i:02d}" for i in range(1, 21) if f"c{i:02d}" not in present],
    }
    (BOOK / "build_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    ok = all(c == 0 for c in codes) and not report["errors_frame"] and not report["errors_chapters"] \
        and not report["overfull_over_threshold_frame"]
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
