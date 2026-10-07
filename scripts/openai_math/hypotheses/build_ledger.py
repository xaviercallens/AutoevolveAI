#!/usr/bin/env python3
"""Build the Elenchus claim ledger for the openai_math hypothesis lab and check it.

Every claim is filed at the tier its evidence kind allows (Elenchus KIND_CAP): exact rational
arithmetic -> B, citations -> L, numerical/solver readings -> X. Evidence digests are the sha256 of
the committed result files. Copies the blobs into ledger/evidence/ so the gate can verify them.

Run:
    python3 scripts/openai_math/hypotheses/build_ledger.py
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RES = REPO / "results" / "openai_math"
LEDGER_DIR = RES / "hypotheses" / "ledger"
ELENCHUS = Path("/mnt/disks/disk-socrateai-local-1/SocrateAI-Scientific-Elenchus/tools/ledger.py")


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def claim(cid: str, statement: str, tier: str, kind: str, evidence: Path, deps: list[str] | None = None) -> dict[str, object]:
    return {
        "schema_version": 1,
        "id": cid,
        "statement": statement,
        "tier": tier,
        "kind": kind,
        "depends_on": deps or [],
        "evidence": digest(evidence),
        "audit": None,
        "_evidence_path": str(evidence.relative_to(REPO)),
    }


def main() -> int:
    h = RES / "hypotheses"
    claims = [
        claim("OMH-X-1", "Static scan: the import closure of upstream OAI.NumberTheory.DirichletL.Nonvanishing (2924 local files), OAI.NumberTheory.SiegelZeros.Main and OAI.Analysis.LienardCycles.Main contains no sorry/admit/axiom outside comments. Not a compile.", "X", "numeric", RES / "solution_scan_riemann_hilbert.json"),
        claim("OMH-L-2", "H1/H3: a zero-free half-plane Re s > theta implies psi(x) - x = O(x^theta log^2 x) and the analogue in progressions (von Koch/Ingham; Littlewood for M(x)). Conditional on upstream family 003, which is not verified here.", "L", "citation", h / "preregistration.json"),
        claim("OMH-X-3", "H2(b): for all 3,039,632 fundamental D < 0 with |D| <= 1e7 and |D| >= 7, L(1,chi_D) log log|D| >= 0.40060 (min at D = -163); holdout min 0.53577 at D = -2383747. PARI qfbclassno, controls passed.", "X", "numeric", h / "H2" / "result.json"),
        claim("OMH-B-4", "H5: the dyadic triangular Hilbert ratio of the N=4 +-1 witness equals exactly 5/2; hence the best constant C* >= 5/2.", "B", "exact_harness", h / "H5" / "best_inputs_N4.npz"),
        claim("OMH-X-5", "H5': Hoelder-ascent searches at N = 2..7 (fresh seeds for N = 6, 7) found no ratio above 5/2 + 1e-9. Numerical; cannot prove C* <= 5/2.", "X", "numeric", h / "H5" / "result_H5prime_N7.json", ["OMH-B-4"]),
    ]
    h4_files = sorted((h / "H4").glob("result_seed*.json"))
    if h4_files:
        claims.append(claim("OMH-X-6", f"H4: {len(h4_files)} seeds of random and averaging-structured classical Lienard search found at most 2 confirmed limit cycles at degree 5 and at degree 6. Low power; does not reach the canard regime.", "X", "numeric", h4_files[0]))
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    evidence_dir = LEDGER_DIR / "evidence"
    evidence_dir.mkdir(exist_ok=True)
    for c in claims:
        src = REPO / str(c.pop("_evidence_path"))
        shutil.copyfile(src, evidence_dir / (str(c["evidence"]).split(":", 1)[1] + ".json"))
    ledger = {"schema_version": 1, "claims": claims}
    path = LEDGER_DIR / "ledger.json"
    path.write_text(json.dumps(ledger, indent=2) + "\n")
    proc = subprocess.run([sys.executable, str(ELENCHUS), str(path), "--evidence-dir", str(evidence_dir)],
                          capture_output=True, text=True)
    (LEDGER_DIR / "gate_check.txt").write_text(f"exit={proc.returncode}\n{proc.stdout}{proc.stderr}")
    print(f"exit={proc.returncode}")
    print(proc.stdout[-3000:], proc.stderr[-2000:])
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
