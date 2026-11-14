"""Rebuild everything in order: gen_inputs -> ledger -> gate -> gen_inputs (picks up ledger/gate numbers) -> figures -> pdf."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = ["gen_inputs.py", "ledger/build_ledger.py", "ledger/run_gate.py", "gen_inputs.py", "make_figures.py", "build_pdf.py"]


def main() -> int:
    for s in STEPS:
        res = subprocess.run([sys.executable, "-I", str(HERE / s)], capture_output=True, text=True)
        print(f"== {s} rc={res.returncode}\n{res.stdout[-600:]}{res.stderr[-600:]}")
        if res.returncode != 0:
            return res.returncode
    json.loads((HERE / "publication_meta.json").read_text())
    print("publication_meta.json parses")
    return 0


if __name__ == "__main__":
    sys.exit(main())
