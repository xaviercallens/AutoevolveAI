"""The rung-2 gate at more than one obligation.

Every stored control had been recorded at `obligations_requested: 1`, so the
multi-obligation path had never been exercised -- guard G9 says validate at
the real size rather than a convenient one.

The second test also records a corrected prediction. I expected a partial
count (1 of 2) and argued it would prove `defeq_checked` measured rather than
derived. That was WRONG: a Lean compile is atomic, so one failing obligation
fails the audit file, `verify_file` returns a single file-level row, and no
obligation rows exist to count. The value is 0 or len(map) and nothing
between. What naming the obligations actually buys is that each one's axiom
footprint is read at all -- the previous anonymous `example : P := thm`
declared nothing, so it was never axiom-checked.

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


def _pair(ns: str, q_coeff: int, p_coeff: int) -> str:
    return f"""import Mathlib.Tactic.Ring
import ANSE.VerletSymplectic

namespace {ns}

def candQ (h w q p : Rat) : Rat := q + h * p - (h ^ 2 * w ^ 2 / {q_coeff}) * q

def candP (h w q p : Rat) : Rat :=
  p - h * w ^ 2 * q - (h ^ 2 * w ^ 2 / {p_coeff}) * p + (h ^ 3 * w ^ 4 / 4) * q

theorem candQ_matches (h w q p : Rat) : candQ h w q p = ANSE.Verlet.qNext h w q p := by
  unfold candQ ANSE.Verlet.qNext; ring

theorem candP_matches (h w q p : Rat) : candP h w q p = ANSE.Verlet.pNext h w q p := by
  unfold candP ANSE.Verlet.pNext; ring

end {ns}

#print axioms {ns}.candQ_matches
#print axioms {ns}.candP_matches
"""


def _two_obligations(ns: str) -> dict[str, str]:
    return {
        f"{ns}.candQ_matches":
            f"∀ h w q p : Rat, {ns}.candQ h w q p = ANSE.Verlet.qNext h w q p",
        f"{ns}.candP_matches":
            f"∀ h w q p : Rat, {ns}.candP h w q p = ANSE.Verlet.pNext h w q p",
    }


def test_two_honest_obligations_both_count(verifier) -> None:
    out = _run(verifier, _pair("TwoHonest", 2, 2), _two_obligations("TwoHonest"))
    assert out["passed"] is True, f"both obligations are true: {out.get('results')}"
    assert out["obligations_requested"] == 2
    assert out["defeq_checked"] == 2, "both obligations must be counted"


def test_one_false_obligation_fails_the_whole_audit(verifier) -> None:
    """Atomicity: the count is 0, not a partial 1. See the module docstring."""
    out = _run(verifier, _pair("OneWrong", 2, 3), _two_obligations("OneWrong"))
    assert out["passed"] is False
    assert out["obligations_requested"] == 2
    assert out["defeq_checked"] == 0, (
        "a Lean compile is atomic, so a failed obligation yields no obligation "
        "rows at all and the count is 0 rather than a partial tally"
    )
