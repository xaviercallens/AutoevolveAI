#!/usr/bin/env python3
"""Freeze the matrix Lieb-Thirring lab: sha256 of every instrument and document, the controls result, the hypotheses and
the verdict rule, BEFORE any campaign row exists (Elenchus Maieutics: register, then run).  Run once; commit the output."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = REPO / "results" / "openai_math" / "hypotheses" / "lt_matrix" / "preregistration.json"
sys.path.insert(0, str(HERE))
from instrument import sharp_constant  # noqa: E402


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    controls = json.loads((OUT.parent / "controls.json").read_text())
    assert controls["all_pass"], "controls must all pass before preregistration"
    payload = {
        "lab": "matrix-valued sharp 1D Lieb-Thirring (openai/math family 262, matrix and equality-case manuscripts of 2026-10-05)",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "stage": "preregistration: instruments built and controls passed; NO campaign row exists yet",
        "documents": {str(p.relative_to(REPO)): sha(p) for p in (REPO / "docs/OPENAI_MATH_LT_MATRIX.md", REPO / "docs/OPENAI_MATH_SELECTION_2026-10-08.md")},
        "frozen_instruments_sha256": {n: sha(HERE / n) for n in ("instrument.py", "controls.py", "campaign.py")},
        "controls_result_sha256": sha(OUT.parent / "controls.json"),
        "controls_summary": {k: v["pass"] for k, v in controls["controls"].items()},
        "constants": {str(g): sharp_constant(g) for g in (0.75, 1.0, 1.25, 1.4, 1.5, 3.0)},
        "verdict_rule": {
            "VOID": "any control failed",
            "VIOLATION_CERTIFIED": "refined-grid excess > 1e-5 AND finite-difference (Richardson) excess > 5e-6 on the stored parameters",
            "UNDECIDED": "1e-7 < refined-grid excess <= 1e-5, or the two solvers disagree",
            "NO_VIOLATION_FOUND": "every restart excess <= 1e-7 (not a proof; the budget is stated)",
        },
        "hypotheses": {
            "H-LT1": "sup R over m = 2, 3 matrix potentials <= L1(gamma) for gamma in {0.75, 1.0, 1.25, 1.4}; kill: VIOLATION_CERTIFIED with controls passing",
            "H-LT2": "near-maximisers (R >= (1-1e-3) L1) are direct sums of scalar sech^2 solitons in one constant unitary basis; kill: near-maximiser with R >= (1-1e-4) L1 and commutator statistic > 0.05",
            "H-LT3": "embedded scalar extremiser is a local maximum in matrix directions; kill: positive second variation beyond noise confirmed at finite epsilon",
            "H-LT4": "negative controls C5/C7 exceed L1 at gamma = 3; positive controls C1-C4, C6 pass (already satisfied at preregistration)",
            "H-LT5": "dual kinetic form at gamma = 1: Sum ||psi_j'||^2 >= (pi^2/4) int tr rho^3 for orthonormal families of C^m-valued functions; kill: explicit family with quotient < pi^2/4 (1 - 1e-6) after exact re-evaluation",
        },
        "smoke_values_seen_before_registration": {
            "controls": "see controls.json (all pass); scalar search reaches L1 within 4e-6 at gamma=1.0, 1.25 best seed; matrix gamma=3/2 within 2.6e-7; gamma=3 exceeds L1 by +15.9% for m=1 and m=2",
            "no_matrix_search_at_gamma_in_(0.5,1.5)_has_been_run": True,
        },
        "assets": ["Elenchus MAIEUTICS/HYPOTHESES (method)", "Elenchus ledger.py (claims)", "Mensura interval/abstaining verdict style",
                   "LeanMaster Lean environment (statement checks)"],
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
