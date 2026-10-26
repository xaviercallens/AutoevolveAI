"""Paper-stage cross-check of the two independent SCHA implementations (Python b1_lib.SCHA, Rust scha.rs) at several shapes. Writes data/crosscheck.json.

The Rust binary was built from rusty-SUNDIALS commit 9e85e15b23be0c74a665b6a5b74ec02b0bbffc5f (release profile). Same pipeline, not an independent verifier.
Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I scha_crosscheck.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
CODE = PAPER.parents[1] / "results/proposal2/2026-10-26/B1/code"
sys.path.insert(0, str(CODE))
import b1_lib as L  # noqa: E402

BIN = "/home/callensxavier_gmail_com/rusty-target-ar/release/lattice_phonon"
CASES = [(1.0, 0.5, 3 ** 0.5 / 2, 0.1), (1.0, 0.3, 0.96, 0.0942), (0.5, 0.5, 3 ** 0.5 / 2, 0.0877), (0.7, 0.5, 3 ** 0.5 / 2, 0.15), (1.3, 0.46, 1.04, 0.13)]


def main() -> int:
    out = []
    for a, x, y, lam in CASES:
        py = L.SCHA(a, x, y, N=32).solve(lam)
        r = subprocess.run([BIN, "scha", repr(a), repr(x), repr(y), repr(lam), "32"], capture_output=True, text=True)
        ru = json.loads(r.stdout)
        out.append({"a": a, "x": x, "y": y, "lam": lam, "E_python": py["E"], "E_rust": ru["e_scha"], "abs_diff": abs(py["E"] - ru["e_scha"]),
                    "python_status": py["status"], "rust_converged": ru["converged"], "u2_rust": ru["u2"]})
        print(out[-1])
    (PAPER / "data" / "crosscheck.json").write_text(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
