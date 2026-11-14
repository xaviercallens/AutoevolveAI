"""Paper-stage rerun of the four Feynman-Bijl Lean compiles (same AI pipeline; NOT producer != verifier).

Basic.lean is re-elaborated from source WITHOUT writing an olean (so the stage-1 olean is untouched); the other three
files import the stage-1 Programmes.FeynmanBijl.Basic olean, as in stage 1. Output: rerun/compile_*.json.
Run:  taskset -c 4-7 /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I rerun_lean.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = HERE.parents[1]
SRC = W / "formal_cert/Programmes/FeynmanBijl"
LEAN = W / "scripts/certified_numerics/lean_pinned.py"
OUT = HERE / "rerun"


def main() -> int:
    OUT.mkdir(exist_ok=True)
    summary = {}
    for name, tag in [("Basic", "basic"), ("NegativeControls", "negctl"), ("PositiveControls", "posctl"), ("Controls", "controls")]:
        out = OUT / f"compile_{tag}.json"
        res = subprocess.run(["taskset", "-c", "4-7", "python3", str(LEAN), "compile", str(SRC / f"{name}.lean"), "--json-out", str(out)],
                             capture_output=True, text=True, cwd=str(W))
        d = json.loads(out.read_text()) if out.exists() else {}
        summary[name] = {"driver_rc": res.returncode, "rc": d.get("rc"), "seconds": d.get("seconds")}
        print(name, summary[name], flush=True)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
