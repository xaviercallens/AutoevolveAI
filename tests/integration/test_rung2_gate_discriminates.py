"""End-to-end test of the rung-2 gate on a REAL Lean spec, with controls.

This is the gate the proof-carrying fitness ladder calls load-bearing, and it
was just changed (it used to pass on an empty obligation map, and its
`defeq_checked` witness used to be derived from the pass flag rather than
measured). Unit tests on the emitter are not enough: the gate has to be
exercised against a real spec through a real Lean kernel, with a positive case
and negatives that must fail.

Spec: formal/ANSE/VerletSymplectic.lean -- computable one-step Stormer-Verlet
map over the rationals, whose theorems close by `ring`.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "/home/xavkal/xdev/AutoevolveAI")
from anse.formal.lean_runner import LeanKernelVerifier  # noqa: E402

REPO = Path("/home/xavkal/xdev/AutoevolveAI")
FORMAL = REPO / "formal"
SPEC = FORMAL / "ANSE" / "VerletSymplectic.lean"

# A candidate that re-derives the same step under its own names and asserts it
# equals the frozen spec. This is the honest positive case.
HONEST = """import Mathlib.Tactic.Ring
import ANSE.VerletSymplectic

namespace CandidateHonest

def candQ (h w q p : Rat) : Rat := q + h * p - (h ^ 2 * w ^ 2 / 2) * q

theorem candQ_matches (h w q p : Rat) : candQ h w q p = ANSE.Verlet.qNext h w q p := by
  unfold candQ ANSE.Verlet.qNext; ring

end CandidateHonest

#print axioms CandidateHonest.candQ_matches
"""

# Same shape, but the equality is false: a wrong coefficient.
WRONG = """import Mathlib.Tactic.Ring
import ANSE.VerletSymplectic

namespace CandidateWrong

def candQ (h w q p : Rat) : Rat := q + h * p - (h ^ 2 * w ^ 2 / 3) * q

theorem candQ_matches (h w q p : Rat) : candQ h w q p = ANSE.Verlet.qNext h w q p := by
  unfold candQ ANSE.Verlet.qNext; ring

end CandidateWrong

#print axioms CandidateWrong.candQ_matches
"""

# The claim is true but discharged by `sorry`: must be refused by the axiom read.
SORRIED = """import Mathlib.Tactic.Ring
import ANSE.VerletSymplectic

namespace CandidateSorry

def candQ (h w q p : Rat) : Rat := q + h * p - (h ^ 2 * w ^ 2 / 2) * q

theorem candQ_matches (h w q p : Rat) : candQ h w q p = ANSE.Verlet.qNext h w q p := by
  sorry

end CandidateSorry

#print axioms CandidateSorry.candQ_matches
"""

CASES = [
    ("POSITIVE honest candidate", HONEST, {"CandidateHonest.candQ_matches": "∀ h w q p : Rat, CandidateHonest.candQ h w q p = ANSE.Verlet.qNext h w q p"}, True),
    ("NEGATIVE wrong coefficient", WRONG, {"CandidateWrong.candQ_matches": "∀ h w q p : Rat, CandidateWrong.candQ h w q p = ANSE.Verlet.qNext h w q p"}, False),
    ("NEGATIVE sorry proof", SORRIED, {"CandidateSorry.candQ_matches": "∀ h w q p : Rat, CandidateSorry.candQ h w q p = ANSE.Verlet.qNext h w q p"}, False),
    ("NEGATIVE empty obligation map", HONEST, {}, False),
]

def main() -> int:
    runner = LeanKernelVerifier(formal_dir=FORMAL)
    rows = []
    for label, source, mapping, expect_pass in CASES:
        with tempfile.TemporaryDirectory() as td:
            cand = Path(td) / "Candidate.lean"
            cand.write_text(source, encoding="utf-8")
            try:
                out = runner.verify_against_spec(cand, SPEC, mapping, timeout_s=900.0)
            except Exception as exc:  # noqa: BLE001
                out = {"passed": False, "error": f"{type(exc).__name__}: {exc}"}
        agrees = bool(out.get("passed")) == expect_pass
        rows.append({
            "case": label,
            "expected_pass": expect_pass,
            "passed": bool(out.get("passed")),
            "obligations_requested": out.get("obligations_requested"),
            "defeq_checked": out.get("defeq_checked"),
            "every_result_clean": out.get("every_result_clean"),
            "forgeries": out.get("forgeries"),
            "error": out.get("error"),
            "as_expected": agrees,
        })
        mark = "OK " if agrees else "!! "
        print(f"{mark}{label:<34} passed={bool(out.get('passed'))!s:<5} "
              f"obligations={out.get('obligations_requested')} "
              f"defeq_checked={out.get('defeq_checked')}"
              + (f" err={out.get('error')[:60]}" if out.get("error") else ""))
    Path("/home/xavkal/.claude/jobs/6eb13034/tmp/rung2_result.json").write_text(
        json.dumps(rows, indent=2) + "\n")
    agreed = sum(1 for r in rows if r["as_expected"])
    print(f"\n{agreed}/{len(rows)} cases behaved as the gate requires")
    return 0 if agreed == len(rows) else 1

if __name__ == "__main__":
    raise SystemExit(main())
