"""Build the preprint and run the Elenchus ledger gate, recording real return codes.

Usage: python -I build.py [--no-tex] [--no-ledger]
Steps: gen_numbers.py, make_listings.py, pdflatex main.tex twice (build1.log, build2.log), then ledger/build_ledger.py
and the Elenchus gate tools/ledger.py ledger.json --evidence-dir evidence (output in ledger/gate_output.txt).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = "/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python"
ELENCHUS = "/mnt/disks/disk-socrateai-local-1/SocrateAI-Scientific-Elenchus/tools/ledger.py"


def run(cmd: list[str], cwd: Path, log: Path | None = None) -> tuple[int, str]:
    p = subprocess.run(["taskset", "-c", "4-7"] + cmd, cwd=cwd, capture_output=True, text=True, errors="replace")
    out = p.stdout + p.stderr
    if log is not None:
        log.write_text(out)
    return p.returncode, out


def main() -> int:
    args = set(sys.argv[1:])
    for s in ("gen_numbers.py", "make_listings.py"):
        rc, out = run([PY, "-I", s], HERE)
        print(s, "rc", rc, out.strip()[-300:])
        if rc:
            return rc
    if "--no-tex" not in args:
        for i in (1, 2):
            rc, out = run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], HERE, HERE / f"build{i}.log")
            print(f"pdflatex pass {i} rc {rc}")
            if rc:
                print(out[-3000:])
                return rc
        log = (HERE / "main.log").read_text(errors="replace")
        for pat in ("undefined", "Rerun", "Unicode", "Error", "Overfull"):
            hits = [l for l in log.splitlines() if re.search(pat, l)]
            print(f"log '{pat}': {len(hits)}", hits[:4])
        rc, out = run(["pdfinfo", "main.pdf"], HERE)
        print([l for l in out.splitlines() if l.startswith("Pages")])
    if "--no-ledger" not in args:
        for p in (HERE / "ledger/evidence").glob("*.json"):  # stale blobs from earlier builds
            p.unlink()
        cc = str(Path(ELENCHUS).with_name("citation_check.py"))
        rc, out = run(["python3", cc, "sources/claim_thm1.json", "sources/waleffe_thm1_source.txt"], HERE / "ledger")
        (HERE / "ledger/sources/citation_check_output.txt").write_text(
            f"$ python3 {cc} sources/claim_thm1.json sources/waleffe_thm1_source.txt   (cwd ledger/)\n{out}\nexit code {rc}\n")
        print("citation_check exit", rc)
        rc, out = run([PY, "-I", "build_ledger.py"], HERE / "ledger")
        print("build_ledger rc", rc, out.strip()[-500:])
        if rc:
            return rc
        rc, out = run(["python3", ELENCHUS, "ledger.json", "--evidence-dir", "evidence"], HERE / "ledger")
        (HERE / "ledger/gate_output.txt").write_text(f"$ python3 {ELENCHUS} ledger.json --evidence-dir evidence\n{out}\nexit code {rc}\n")
        print("elenchus gate exit", rc)
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
