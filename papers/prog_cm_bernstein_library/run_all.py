"""Regenerate everything for the P3 preprint in dependency order: inputs, ledger, gate, inputs again (gate macros), ledger, gate.

Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I run_all.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = ["gen_inputs.py", "ledger/build_ledger.py", "ledger/run_gate.py", "gen_inputs.py", "ledger/build_ledger.py",
         "ledger/run_gate.py"]


def main() -> int:
    for s in STEPS:
        res = subprocess.run([sys.executable, "-I", str(HERE / s)], capture_output=True, text=True, cwd=HERE)
        tail = [l for l in (res.stdout + res.stderr).splitlines() if "UNAUDITED" not in l][-4:]
        print(f"== {s} rc={res.returncode}")
        print("\n".join(tail))
        if res.returncode != 0:
            return res.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
