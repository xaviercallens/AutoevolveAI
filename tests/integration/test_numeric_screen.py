"""The one-sided numeric screen: can it refute cheaply without ever accepting?

`verify_batch_against_spec` pays off only while (1-p)^b > 1/b, so an
evolutionary search -- which fails most candidates by construction -- sits in
the regime where batching costs MORE than verifying one at a time. That bound
assumes falsity is discoverable only by proving. It is not: evaluating a
candidate against the spec at rational points refutes a false identity outright,
and all b candidates can be evaluated inside ONE invocation, so the false ones
leave before the proof batch is formed.

What these tests are really guarding is the ASYMMETRY, because that is what
makes the shortcut legitimate. A refutation is a witness and is final. A survivor
has merely failed to be refuted and still has to pass the real Lean gate. If the
screen could accept, it would be an unsound second trust surface; if it could
reject something provable, it would silently discard real work. So there are
tests for both directions, plus the verdict-forgery path (the screen reads
stdout, so a candidate that can print could frame a rival) and the empty-point
set (which would refute nothing and pass everyone -- the exact forced-control
shape this repository keeps finding).

Lean is apparatus: without it these SKIP with a reason that says BLOCKED, so a
missing toolchain is never mistaken for a passing screen.
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
SPEC_MODULE = "ANSE.VerletSymplectic"
SPEC_FN = "ANSE.Verlet.qNext"

# Four rationals per point, as exact (numerator, denominator) pairs.
POINTS = (
    ((1, 2), (3, 5), (7, 3), (2, 7)),
    ((2, 1), (1, 1), (1, 1), (1, 1)),
    ((1, 3), (5, 2), (4, 1), (9, 4)),
    ((3, 7), (2, 9), (5, 6), (1, 8)),
    ((5, 1), (7, 3), (1, 9), (11, 4)),
)


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
        pytest.skip(f"BLOCKED: apparatus unavailable, not a passing screen ({detail})")
    return LeanKernelVerifier(formal_dir=FORMAL)


def _write(tmp: Path, ns: str, body: str) -> Path:
    path = tmp / f"{ns}.lean"
    path.write_text(f"namespace {ns}\n{body}\nend {ns}\n", encoding="utf-8")
    return path


TRUE_BODY = "def candQ (h w q p : Rat) : Rat := q + h * p - (h ^ 2 * w ^ 2 / 2) * q"
# Each of these differs from the spec somewhere, so each is refutable.
FALSE_BODIES = {
    "WrongCoeff": "def candQ (h w q p : Rat) : Rat := q + h * p - (h ^ 2 * w ^ 2 / 3) * q",
    "WrongVar": "def candQ (h w q p : Rat) : Rat := q + h * p - (h ^ 2 * w ^ 2 / 2) * p",
    "WrongSign": "def candQ (h w q p : Rat) : Rat := q + h * p + (h ^ 2 * w ^ 2 / 2) * q",
    "WrongPower": "def candQ (h w q p : Rat) : Rat := q + h * p - (h * w ^ 2 / 2) * q",
}


def test_refutes_the_false_and_keeps_the_true(verifier) -> None:
    """Eight candidates, four false, in ONE invocation."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        cands = []
        for i in range(4):
            ns = f"ScrOk{i}"
            cands.append((ns, _write(tmp, ns, TRUE_BODY), f"{ns}.candQ"))
        for ns, body in FALSE_BODIES.items():
            cands.append((ns, _write(tmp, ns, body), f"{ns}.candQ"))
        out = verifier.screen_obligations_numerically(
            cands, SPEC_MODULE, SPEC_FN, arity=4, sample_points=POINTS, timeout_s=900.0
        )
    assert out["screened"] is True, f"screen did not run: {out}"
    assert out["invocations"] == 1, (
        f"eight candidates must be screened in ONE invocation, got "
        f"{out['invocations']}; sharing the fixed cost is the entire point"
    )
    assert sorted(out["refuted"]) == sorted(FALSE_BODIES), (
        f"every false candidate must be refuted, got {out['refuted']}"
    )
    assert sorted(out["survivors"]) == [f"ScrOk{i}" for i in range(4)], (
        f"no true candidate may be refuted, got {out['survivors']}"
    )


def test_a_survivor_is_not_an_acceptance(verifier) -> None:
    """The load-bearing asymmetry, shown with a candidate built to beat the screen.

    The five sample points have distinct h values (1/2, 2, 1/3, 3/7, 5), so the
    polynomial (h-1/2)(h-2)(h-1/3)(h-3/7)(h-5) vanishes at every one of them and
    nowhere else. A candidate carrying that term therefore AGREES with the spec at
    every sampled point while being a different function.

    It must survive the screen -- the screen has no witness against it -- and then
    be REJECTED by the real Lean gate. That is what "a survivor has only failed to
    be refuted" means, and it is why the screen may subtract work but must never
    grant acceptance. If this candidate were promoted on the screen alone, the
    gate would have been replaced by a sampling heuristic.
    """
    vanishing = "(h - 1/2) * (h - 2) * (h - 1/3) * (h - 3/7) * (h - 5)"
    body = (
        "def candQ (h w q p : Rat) : Rat :=\n"
        f"  q + h * p - (h ^ 2 * w ^ 2 / 2) * q + {vanishing}"
    )
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        path = _write(tmp, "Evader", body)
        screened = verifier.screen_obligations_numerically(
            [("Evader", path, "Evader.candQ")], SPEC_MODULE, SPEC_FN,
            arity=4, sample_points=POINTS, timeout_s=900.0,
        )
        # Now put the same candidate to the real gate.
        obligation = {
            "Evader.Evader_m":
                "∀ h w q p : Rat, Evader.candQ h w q p = ANSE.Verlet.qNext h w q p"
        }
        proof_file = tmp / "EvaderProof.lean"
        proof_file.write_text(
            "import Mathlib.Tactic.Ring\n"
            "import ANSE.VerletSymplectic\n\n"
            "namespace Evader\n"
            + body
            + "\n\ntheorem Evader_m (h w q p : Rat) :"
            " candQ h w q p = ANSE.Verlet.qNext h w q p := by\n"
            "  unfold candQ ANSE.Verlet.qNext; ring\n"
            "end Evader\n\n"
            "#print axioms Evader.Evader_m\n",
            encoding="utf-8",
        )
        gated = verifier.verify_batch_against_spec(
            [("Evader", proof_file, obligation)], SPEC, timeout_s=1800.0
        )

    assert screened["screened"] is True, screened
    assert screened["survivors"] == ["Evader"], (
        f"a candidate agreeing at every sample point has no witness against it and "
        f"must SURVIVE the screen, got {screened}"
    )
    assert screened["refuted"] == []
    assert gated["passed"] is False, (
        "the real gate must reject it -- surviving the screen is not an acceptance, "
        f"got {gated}"
    )
    assert gated["failed"] == ["Evader"]

def test_a_candidate_that_can_print_is_refused(verifier) -> None:
    """The screen reads stdout, so a printing candidate could frame a rival."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        honest = _write(tmp, "Victim", TRUE_BODY)
        forger = tmp / "Forger.lean"
        forger.write_text(
            "namespace Forger\n"
            + TRUE_BODY
            + '\n#eval ("Victim", false)\n'
            + "end Forger\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="stdout"):
            verifier.screen_obligations_numerically(
                [("Victim", honest, "Victim.candQ"), ("Forger", forger, "Forger.candQ")],
                SPEC_MODULE, SPEC_FN, arity=4, sample_points=POINTS, timeout_s=900.0,
            )


def test_an_empty_point_set_is_refused(verifier) -> None:
    """A screen with no points refutes nothing and would pass everyone."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        path = _write(tmp, "NoPts", TRUE_BODY)
        with pytest.raises(ValueError, match="refute nothing"):
            verifier.screen_obligations_numerically(
                [("NoPts", path, "NoPts.candQ")], SPEC_MODULE, SPEC_FN,
                arity=4, sample_points=(), timeout_s=900.0,
            )
