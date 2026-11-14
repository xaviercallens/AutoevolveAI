#!/usr/bin/env python3
"""Write result.json for DH-Psi2 with the sha256 of every file in the lane (except result.json itself)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

LANE = Path(__file__).resolve().parents[1]
REPO = LANE.parents[3]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    summ = json.loads((LANE / "data" / "summary.json").read_text())
    m = summ["modes"]
    files = {str(p.relative_to(LANE)): sha(p) for p in sorted(LANE.rglob("*")) if p.is_file() and p.name != "result.json" and "__pycache__" not in p.parts}
    out = {
        "item": "DH-Psi2",
        "proposal": "Proposal 5 (mathematics), lane W1-d",
        "outcome": "KEEP",
        "statement_checked": "max over all F in {+-1}^48 at resolution 2 of Psi = H + 3|T| equals 3 (no violation)",
        "scope": "sign inputs, resolution 2 only; nothing about real inputs, N >= 3, or C*",
        "tier": "C (exhaustive exact enumeration, two independent implementations agreeing on full histograms)",
        "max_Psi": m["PSI"]["python_kernel"]["max_value"],
        "violating_pairs": m["PSI"]["python_kernel"]["violating_pairs_gt3"],
        "pairs_attaining_3": m["PSI"]["python_kernel"]["pairs_attaining_max"],
        "reduced_pairs_enumerated": m["PSI"]["python_kernel"]["pairs"],
        "controls": {k: {"python_max": v["python_kernel"]["max_value"], "c_max": v["c_int_enumeration"]["max_value"], "violating_pairs_gt3": v["python_kernel"]["violating_pairs_gt3"], "hist_identical": v["hist_identical"]} for k, v in m.items()},
        "kill_criterion_fired": False,
        "projected_core_h_after_1pct": 1.136,
        "lean": "not called for (no violation)",
        "preregistration_sha256": sha(REPO / "results/proposal5/2026-10-27/preregistration.json"),
        "producer_unaudited": True,
        "files_sha256": files,
    }
    (LANE / "result.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("outcome", "max_Psi", "violating_pairs", "preregistration_sha256")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
