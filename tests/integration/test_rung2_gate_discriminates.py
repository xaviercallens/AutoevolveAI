"""The rung-2 gate must discriminate, not merely refuse.

Four controls against the frozen spec formal/ANSE/VerletSymplectic.lean
(namespace ANSE.Verlet, a computable Stormer-Verlet step over the rationals
whose theorems close by `ring`). The POSITIVE case is what makes the three
negatives mean anything: a gate that refuses everything refuses the bad
cases too, so three refusals on their own are not evidence.

A NOTE ON WHY THIS FILE IS SHAPED LIKE THIS. It was first committed as a script
with a `main()` and no pytest test function, under a `test_*.py` name. pytest
collected ZERO tests from it, so the suite reported nothing while appearing to
cover the gate -- a file shaped like a check that cannot fail, which is the
defect this project has had to label repeatedly. It is now real tests.

The Lean toolchain is apparatus, not data. If it is absent the tests SKIP with a
reason that says BLOCKED and names what is missing, so a missing toolchain can
never be mistaken for a passing gate. The probe is a real invocation, not a
swallowed exception.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import pytest

from anse.formal.lean_runner import LeanKernelVerifier

REPO = Path(__file__).resolve().parents[2]
FORMAL = REPO / "formal"
SPEC = FORMAL / "ANSE" / "VerletSymplectic.lean"


def _toolchain_available() -> tuple[bool, str]:
    """Probe the Lean toolchain. A failure here is an apparatus failure."""
    if not SPEC.exists():
        return False, f"spec missing: {SPEC}"
    try:
        done = subprocess.run(
            ["lake", "env", "lean", "--version"],
            cwd=str(FORMAL), capture_output=True, text=True, timeout=180,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"lake env lean unavailable: {type(exc).__name__}"
    if done.returncode != 0:
        return False, f"lake env lean exited {done.returncode}"
    return True, done.stdout.strip()[:60]


@pytest.fixture(scope="module")
def verifier() -> LeanKernelVerifier:
    ok, detail = _toolchain_available()
    if not ok:
        pytest.skip(f"BLOCKED: apparatus unavailable, not a passing gate ({detail})")
    return LeanKernelVerifier(formal_dir=FORMAL)


def _run(verifier: LeanKernelVerifier, source: str, mapping: dict) -> dict:
    with tempfile.TemporaryDirectory() as td:
        cand = Path(td) / "Candidate.lean"
        cand.write_text(source, encoding="utf-8")
        return verifier.verify_against_spec(cand, SPEC, mapping, timeout_s=1200.0)


def _candidate(ns: str, q_coeff: int, proof: str) -> str:
    return f"""import Mathlib.Tactic.Ring
import ANSE.VerletSymplectic

namespace {ns}

def candQ (h w q p : Rat) : Rat := q + h * p - (h ^ 2 * w ^ 2 / {q_coeff}) * q

theorem candQ_matches (h w q p : Rat) : candQ h w q p = ANSE.Verlet.qNext h w q p := by
  {proof}

end {ns}

#print axioms {ns}.candQ_matches
"""


def _obligation(ns: str) -> dict[str, str]:
    return {
        f"{ns}.candQ_matches":
            f"∀ h w q p : Rat, {ns}.candQ h w q p = ANSE.Verlet.qNext h w q p"
    }


def test_honest_candidate_passes_and_counts_its_obligation(verifier) -> None:
    """The positive control. Without it the negatives below are vacuous."""
    out = _run(verifier, _candidate("CtlHonest", 2, "unfold candQ ANSE.Verlet.qNext; ring"),
               _obligation("CtlHonest"))
    assert out["passed"] is True, f"honest candidate must pass: {out.get('results')}"
    assert out["defeq_checked"] == 1, "the obligation must be counted as checked"
    assert out["obligations_requested"] == 1


def test_wrong_coefficient_is_refused(verifier) -> None:
    out = _run(verifier, _candidate("CtlWrong", 3, "unfold candQ ANSE.Verlet.qNext; ring"),
               _obligation("CtlWrong"))
    assert out["passed"] is False, "a false equality must not discharge an obligation"
    assert out["defeq_checked"] == 0


def test_a_true_claim_proved_by_sorry_is_refused(verifier) -> None:
    """`sorry` exits zero, which is why the axiom read rather than the exit code
    is the gate."""
    out = _run(verifier, _candidate("CtlSorry", 2, "sorry"), _obligation("CtlSorry"))
    assert out["passed"] is False, "sorry must be refused even when the claim is true"


def test_an_empty_obligation_map_is_refused(verifier) -> None:
    """The vacuous pass this gate used to return.

    The old predicate was `len(results) >= len(map) and all(...)`; with an empty
    map the first conjunct is vacuously true and `all()` over an empty sequence
    is also true, so the gate passed having verified nothing.
    """
    out = _run(verifier, _candidate("CtlEmpty", 2, "unfold candQ ANSE.Verlet.qNext; ring"), {})
    assert out["passed"] is False, "an empty obligation set must never pass"
    assert out["obligations_requested"] == 0
