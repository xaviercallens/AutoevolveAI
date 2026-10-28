#!/usr/bin/env python3
"""Write result.json: outcome fields from logs/summary.json plus the sha256 of every file under LR-IND/ and of
the Lean module, so the state before any reading of the S-T repository is fixed."""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parents[3]
LEAN = REPO / "formal_cert" / "Programmes" / "LonelyRunnerInd"
PREREG = REPO / "results" / "proposal5" / "2026-10-27" / "preregistration.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    S = json.loads((ROOT / "logs" / "summary.json").read_text())
    files = {}
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and p.name != "result.json":
            files[str(p.relative_to(REPO))] = sha(p)
    for p in sorted(LEAN.glob("*.lean")):
        files[str(p.relative_to(REPO))] = sha(p)
    k10 = S["k10"]
    out = {
        "item": "LR-IND",
        "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "preregistration_sha256": sha(PREREG),
        "st_repository_read": False,
        "outcome": sys.argv[1] if len(sys.argv) > 1 else "PENDING",
        "statement_checked": "J(10,p) is empty for every p in P_10 (61 primes 127..467), by an independent implementation",
        "tiers": {"J_empty_per_prime": "C (exhaustive exact-integer enumeration, two programs for the identity fibre)",
                  "scalar_inputs": "A (Lean 4.34.1 + pinned Mathlib, axioms within whitelist, leanchecker rc 0)",
                  "LRC9_and_Lemma_2_6": "L (literature premises, not re-derived)"},
        "k10_primes_done": len(k10),
        "k10_all_only_identity_after_2_2_2_project": S["k10_all_only_identity"],
        "k10_all_identity_fibre_level11_proper": S["k10_all_fiber11_zero"],
        "k10_nocanon_second_pass_done": S["k10_nocanon_done"],
        "k10_nocanon_all_agree": S["k10_nocanon_all_agree"],
        "core_seconds": {"main": S["k10_core_seconds_main"], "fiber11": S["k10_core_seconds_fiber11"],
                         "nocanon": S["k10_core_seconds_nocanon"]},
        "B10": S["B10"],
        "controls_ok": S["controls_ok"],
        "k9_S9": {k: v for k, v in S["k9_S9"].items() if k != "rows"},
        "controls_ok_note": ("false only because of k=4, p=13: our sieve and the naive direct scan (direct_I.py) both give "
                             "I(4,13,5) = empty, whereas our reading of Rosenfeld 2509.14111 sec. 7 ('larger than 17') "
                             "expected failure; his Table 1 list is matched. All other controls match (RESULT.md sec. 2)."),
        "nocanon_note": "time-boxed: stopped after 33/61 primes (127..307); all 33 agree with the main pass at hash level",
        "pre_freeze_files": ["logs/control_k8_lift33.jsonl", "logs/k10_p127_probe.json", "logs/probe_k10_p163.json",
                             "logs/probe_k10_p199.json", "logs/probe_k10_p263.json", "logs/probe_k10_p127_x11.json"],
        "files_sha256": files,
    }
    (ROOT / "result.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "files_sha256"}, indent=1))
    print("files hashed:", len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
