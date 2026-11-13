"""Batched rung-2 verification: does it amortise, and does bisection isolate?

`results/lean_batching.json` measured that 97% of a single verification is fixed
per-invocation overhead, so eight candidates in one Lean invocation cost a
median 6.35 s against 45.47 s for eight -- a 7.16x saving at a 1.02x same-input
spread. `verify_batch_against_spec` exploits that.

The hard part is not the saving, it is ATOMICITY. A Lean compile is
all-or-nothing, so a batch containing one false obligation fails whole and yields
no per-candidate verdict. The implementation bisects to name the culprits, and
these tests check that it names the RIGHT ones and that it costs fewer
invocations than running everyone individually. A batch verifier that reported
"someone failed" without saying who, or that silently passed a bad candidate,
would be worse than no batching at all.

The toolchain is apparatus: if Lean is unavailable these SKIP with a reason that
says BLOCKED, so a missing toolchain is never mistaken for a passing gate.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import pytest

from anse.formal.lean_runner import LeanKernelVerifier

REPO = Path(__file__).resolve().parents[2]
FORMAL = REPO / "formal"
SPEC = FORMAL / "ANSE" / "VerletSymplectic.lean"


def _toolchain_available() -> tuple[bool, str]:
    if not SPEC.exists():
        return False, f"spec missing: {SPEC}"
    try:
        done = subprocess.run(
            ["lake", "env", "lean", "--version"],
            cwd=str(FORMAL), capture_output=True, text=True, timeout=180,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"lake env lean unavailable: {type(exc).__name__}"
    return (done.returncode == 0), done.stdout.strip()[:60]


@pytest.fixture(scope="module")
def verifier() -> LeanKernelVerifier:
    ok, detail = _toolchain_available()
    if not ok:
        pytest.skip(f"BLOCKED: apparatus unavailable, not a passing gate ({detail})")
    return LeanKernelVerifier(formal_dir=FORMAL)


def _source(ns: str, coeff: int) -> str:
    """One candidate. coeff=2 is the true Verlet step; anything else is false."""
    return f"""import Mathlib.Tactic.Ring
import ANSE.VerletSymplectic

namespace {ns}

def candQ (h w q p : Rat) : Rat := q + h * p - (h ^ 2 * w ^ 2 / {coeff}) * q

theorem {ns}_matches (h w q p : Rat) : candQ h w q p = ANSE.Verlet.qNext h w q p := by
  unfold candQ ANSE.Verlet.qNext; ring

end {ns}

#print axioms {ns}.{ns}_matches
"""


def _entry(tmp: Path, ns: str, coeff: int):
    path = tmp / f"{ns}.lean"
    path.write_text(_source(ns, coeff), encoding="utf-8")
    obligations = {
        f"{ns}.{ns}_matches":
            f"∀ h w q p : Rat, {ns}.candQ h w q p = ANSE.Verlet.qNext h w q p"
    }
    return (ns, path, obligations)


def test_all_honest_candidates_pass_in_one_invocation(verifier) -> None:
    """The amortisation case: four candidates, one compile."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        batch = [_entry(tmp, f"BatchOk{i}", 2) for i in range(1, 5)]
        out = verifier.verify_batch_against_spec(batch, SPEC, timeout_s=1800.0)
    assert out["passed"] is True, f"all four are true: {out}"
    assert out["verdicts"] == {f"BatchOk{i}": True for i in range(1, 5)}
    assert out["invocations"] == 1, (
        f"four honest candidates must cost ONE invocation, not "
        f"{out['invocations']}; otherwise there is no amortisation"
    )
    assert out["invocations"] < out["invocations_if_run_individually"]
    assert "none needed" in str(out["isolation_strategy"]).lower()


def test_the_single_culprit_is_named_in_one_invocation(verifier) -> None:
    """The culprit is named by the kernel, so nothing has to be isolated.

    This file twice encoded a worse strategy. First a bisection, measured worse
    than a flat re-run (11 and 15 invocations against 9 at n=8, because ~97% of
    an invocation is fixed cost so every branch re-pays a near-whole
    verification). Then the flat re-run itself, 1+n. BOTH were solving a problem
    the wrapper had invented: `verify_file` returned one aggregate failure as soon
    as the compile exited nonzero, discarding the per-declaration axiom lines Lean
    had already printed. A failed tactic proof is admitted as `sorryAx` and named,
    so one invocation yields every verdict. See
    results/lean_atomicity_is_the_wrapper.json.
    """
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        batch = [
            _entry(tmp, "BisA", 2),
            _entry(tmp, "BisB", 2),
            _entry(tmp, "BisC", 3),   # false
            _entry(tmp, "BisD", 2),
        ]
        out = verifier.verify_batch_against_spec(batch, SPEC, timeout_s=1800.0)
    assert out["passed"] is False
    assert out["failed"] == ["BisC"], f"exactly BisC is false, got {out['failed']}"
    assert out["verdicts"]["BisA"] is True
    assert out["verdicts"]["BisB"] is True
    assert out["verdicts"]["BisD"] is True
    assert out["invocations"] == 1, (
        f"one invocation must name the culprit, got {out['invocations']}; any more "
        "means the wrapper is re-running work the kernel already reported"
    )


def test_two_culprits_are_both_named(verifier) -> None:
    """More than one failure must not hide behind the first."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        batch = [
            _entry(tmp, "TwoA", 3),   # false
            _entry(tmp, "TwoB", 2),
            _entry(tmp, "TwoC", 2),
            _entry(tmp, "TwoD", 5),   # false
        ]
        out = verifier.verify_batch_against_spec(batch, SPEC, timeout_s=1800.0)
    assert out["passed"] is False
    assert out["failed"] == ["TwoA", "TwoD"], f"both culprits, got {out['failed']}"
    assert out["verdicts"]["TwoB"] is True
    assert out["verdicts"]["TwoC"] is True
    # The property that matters: cost is ONE invocation whatever the failure
    # count, so the batching break-even condition (1-p)^b > 1/b does not apply.
    assert out["invocations"] == 1, (
        f"two failures must still cost one invocation, got {out['invocations']}"
    )


def test_name_collisions_are_refused_before_compiling(verifier) -> None:
    """Colliding declarations fail as unverified, which is safe but opaque.

    _lookup_axioms resolves a namespace-relative name by UNIQUE suffix and
    returns None on ambiguity, so a collision would surface as a mysterious
    verification failure. It is reported as a collision instead, and costs zero
    invocations.
    """
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        a = _entry(tmp, "Clash", 2)
        dup = tmp / "Clash_dup.lean"
        dup.write_text(_source("Clash", 2), encoding="utf-8")
        b = ("ClashDup", dup, a[2])
        out = verifier.verify_batch_against_spec([a, b], SPEC, timeout_s=1800.0)
    assert out["passed"] is False
    assert "collision" in str(out.get("blocked", "")).lower(), out
    assert out["invocations"] == 0, "a collision must be caught before compiling"


def test_an_empty_obligation_map_blocks_the_batch(verifier) -> None:
    """A vacuous audit verifies nothing and must not ride along in a batch."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        good = _entry(tmp, "EmptyOk", 2)
        bad = _entry(tmp, "EmptyBad", 2)
        out = verifier.verify_batch_against_spec(
            [good, (bad[0], bad[1], {})], SPEC, timeout_s=1800.0
        )
    assert out["passed"] is False
    assert "empty obligation map" in str(out.get("blocked", "")).lower(), out
    assert out["invocations"] == 0
