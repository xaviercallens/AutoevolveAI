"""Rebuild the ledger, prune orphan evidence blobs, run the Elenchus ledger gate, record stdout/stderr/rc.

Run: .venv/bin/python -I ledger/run_gate.py   -> writes ledger/gate_output.txt (verbatim gate output plus exit code)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = "/mnt/disks/disk-socrateai-local-1/SocrateAI-Scientific-Elenchus/tools/ledger.py"


def main() -> int:
    b = subprocess.run([sys.executable, "-I", str(HERE / "build_ledger.py")], capture_output=True, text=True)
    if b.returncode != 0:
        print(b.stdout, b.stderr)
        return b.returncode
    used = {c["evidence"].split(":")[1] for c in json.loads((HERE / "ledger.json").read_text())["claims"]}
    pruned = []
    for f in sorted((HERE / "evidence").glob("*.json")):
        if f.stem not in used:
            f.unlink()
            pruned.append(f.name)
    p = subprocess.run(["python3", "-I", GATE, str(HERE / "ledger.json"), "--evidence-dir", str(HERE / "evidence")],
                       capture_output=True, text=True)
    text = (f"$ python3 -I {GATE} ledger/ledger.json --evidence-dir ledger/evidence\n"
            f"--- stdout ---\n{p.stdout}--- stderr ---\n{p.stderr}--- exit code: {p.returncode} ---\n"
            f"build: {b.stdout.strip()}; orphan blobs pruned: {pruned}\n")
    (HERE / "gate_output.txt").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
