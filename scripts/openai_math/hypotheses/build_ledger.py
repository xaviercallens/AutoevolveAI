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


def night_2026_10_07(n: Path) -> list[dict[str, object]]:
    """Claims from the night run 2026-10-07 lanes, worded with the adversarial verifiers' corrections."""
    return [
        claim("OMHN-B-1", "H5': the +-1 input kron(w4, w4) at N=8 (w4 = sign of the N=4 witness) has dyadic triangular Hilbert ratio exactly 23/8 (ratio^3 = 12167/512 by the integer certifier; h5_exact and an independent implementation both give 23/8). Hence C* >= 23/8 > 5/2 and the preregistered H5' (C* = 5/2) is refuted.", "B", "exact_harness", n / "H5" / "chunks" / "W_N8_witness_x_witness.json", ["OMH-B-4"]),
        claim("OMHN-B-2", "H5: over +-1 inputs the maximum ratio is exactly 1 at N=1 and exactly 2 at N=2 (exhaustive enumeration, exact arithmetic, every argmax rechecked).", "B", "exact_harness", n / "H5" / "summary.json"),
        claim("OMHN-C-3", "H5 (exploratory, not preregistered): product rule R(f (x) g) = H(g) + |T(g)| R(f) for +-1 f, g, proved on paper in NOTE.md (not Lean-checked, reviewed only by the lane verifier); with the N=2 maximiser g2 (R=2, H=3/2, T=1/2) its tensor powers give 3 - 2^(1-r), so C* >= 3. Novelty unchecked.", "C", "argument", n / "H5" / "NOTE.md", ["OMHN-B-1", "OMHN-B-2"]),
        claim("OMHN-C-4", "H5 (exploratory): Hoelder-marginal upper bounds over all real inputs B_1 = 1, B_2 = 2, B_3 = 5/2, giving C_1 = 1, C_2 = 2 and 2 <= C_3 <= 5/2. The reduction is a paper argument; B_1, B_2 were recomputed independently, B_3 rests on holder_bound.py alone.", "C", "argument", n / "H5" / "holder_bound.json"),
        claim("OMHN-X-5", "H5': 18 preregistered Hoelder-ascent chunks at N = 5..8 reached per-chunk best ratios between 2.4999186 and 2.4999999999, never above 5/2; Walsh lifts of the N=4 witness max 5/2. Local ascent misses the tensor extremisers. 7 walsh_top chunks BLOCKED by a code bug.", "X", "numeric", n / "H5" / "result.json", ["OMHN-B-1"]),
        claim("OMHN-X-6", "H2(b): for all 27,356,753 fundamental D < 0 with 1e7 < |D| <= 1e8, L(1,chi_D) log log|D| >= 0.567741 (min at D = -10560643, h = 211). PARI qfbclassno (relies on PARI's documented correctness); 11,700 D rechecked with GRH-conditional quadclassunit; positive and negative controls passed. Finite check, not a proof.", "X", "numeric", n / "H2" / "result.json", ["OMH-X-3"]),
        claim("OMHN-X-7", "H4: the h4_v2 instrument passes C1-C3 and N1, but the reconstructed De Maesschalck-Dumortier degree-6 family gives at most 1 confirmed cycle at eps = 0.003 (the only one of 6 preregistered eps run), so positive control P4 (>= 4) was not reproduced; N2 incomplete. Lane PARTIAL: no claim about H4.", "X", "numeric", n / "H4" / "result.json"),
        claim("OMHN-X-8", "D1: a frozen token comparison of the 45 Comparator definition-hole bodies (9 configs, upstream adc7f124) gives 37 MATCHES, 6 DIFFERS, 2 SORRIED_IN_CHALLENGE; controls 98/98. Unelaborated (no Lean run).", "X", "numeric", n / "D1" / "definition_holes.json"),
        claim("OMHN-X-9", "D1: by reading, the 6 mechanical DIFFERS are equivalent, so 43 of 45 holes reproduce the challenge's definition at the token level or by reading (unelaborated; 8 MATCHES have differing open/instance context pinned by reading only; sobolevOddPower's pin is conditional on sobolevProduct). sobolevProduct and elementaryPositivityWitness are sorried in the challenge and stay unpinned. Filed at X because the 37 MATCHES come from the mechanical comparison.", "X", "numeric", n / "D1" / "eye_review.json", ["OMHN-X-8"]),
    ]


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
    claims.extend(night_2026_10_07(h / "night_2026-10-07"))
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
