"""verify_theorem_axioms: a rejection must say which clause bound, and not collide.

Two defects found by sweeping the verifier after discovering that its sibling
function reported a limit of its own making.

FIRST, ATTRIBUTION. On a nonzero exit this returned `has_sorry=True`. That fails
closed, which is right, but it mislabels the reason: a module that does not build
or a misspelled theorem name is not a proof that cheated. These results are
serialised into artifacts and into training rows, where "the proof used sorry"
and "the module did not compile" are different facts, and the first is a far
stronger claim about the candidate. Every caller gates on
`compiled_successfully` before reading `has_sorry`, so correcting the
attribution changes no verdict.

SECOND, COLLISION. The temp file was the fixed `.tmp_axiom_check.lean` in the
shared `formal/` directory, and the cleanup unlinks it, so two concurrent calls
would clobber each other and one could delete the file another was compiling. No
caller runs this concurrently today, so the hazard was latent; it has seven call
sites and nothing stops the eighth from being threaded.

Lean is apparatus: without it these SKIP with a reason that says BLOCKED.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from anse.formal.lean_runner import TRUSTED_AXIOMS, LeanKernelVerifier

REPO = Path(__file__).resolve().parents[2]
FORMAL = REPO / "formal"
MODULE = "ANSE.VerletSymplectic"
REAL_THEOREM = "ANSE.Verlet.det_eq_one"


def _toolchain_available() -> tuple[bool, str]:
    if not (FORMAL / "ANSE" / "VerletSymplectic.lean").exists():
        return False, "spec module missing"
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
        pytest.skip(f"BLOCKED: apparatus unavailable, not a passing check ({detail})")
    return LeanKernelVerifier(formal_dir=FORMAL)


def test_a_real_theorem_passes_with_only_whitelisted_axioms(verifier) -> None:
    """The positive control: without it, every rejection below is uninformative."""
    result = verifier.verify_theorem_axioms(MODULE, REAL_THEOREM)
    assert result.compiled_successfully is True, result.output
    assert result.has_sorry is False
    assert result.axioms, "a verified theorem must report its axioms"
    assert all(a in TRUSTED_AXIOMS for a in result.axioms), result.axioms


def test_a_missing_name_is_not_reported_as_a_sorry(verifier) -> None:
    """The attribution fix: rejected, but not for having used `sorry`."""
    result = verifier.verify_theorem_axioms(MODULE, "ANSE.Verlet.no_such_theorem")
    assert result.compiled_successfully is False, "a missing name must be rejected"
    assert result.has_sorry is False, (
        "a failed compile means the kernel reported nothing about the proof; "
        "calling that a sorry finding is a stronger claim than the evidence"
    )
    assert result.axioms == []
    assert "REJECTED" in result.output and "not a sorry finding" in result.output, (
        f"the output must name the clause that bound: {result.output[:200]!r}"
    )


def test_two_calls_do_not_share_a_temp_file(verifier) -> None:
    """The collision fix, asserted on the artifact rather than on the code.

    Each call must use its own temp file and leave none behind. Checking the
    directory before and after is what makes this a measurement rather than a
    reading of the source.
    """
    leftovers_before = sorted(p.name for p in FORMAL.glob(".tmp_axiom_check*"))
    first = verifier.verify_theorem_axioms(MODULE, REAL_THEOREM)
    second = verifier.verify_theorem_axioms(MODULE, "ANSE.Verlet.trace_eq")
    leftovers_after = sorted(p.name for p in FORMAL.glob(".tmp_axiom_check*"))
    assert first.compiled_successfully is True, first.output
    assert second.compiled_successfully is True, second.output
    assert leftovers_after == leftovers_before, (
        f"temp files left behind: {set(leftovers_after) - set(leftovers_before)}"
    )
    # The fixed name is what two concurrent calls would have fought over.
    assert not (FORMAL / ".tmp_axiom_check.lean").exists()
