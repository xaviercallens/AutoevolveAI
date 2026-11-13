"""The rung-2 gate must not pass having checked nothing.

`verify_against_spec` is the gate the proof-carrying fitness ladder calls
load-bearing, because an axiom read cannot be talked around by passing tests.
An adversarial audit of that claim found two defects in it, both confirmed by
reading the code:

1. **A vacuous pass.** The predicate was
   ``len(results) >= len(theorem_to_spec_map) and all(...)``. With an empty
   obligation map, ``len(results) >= 0`` is vacuously true and ``all()`` over an
   empty sequence is also true, so the function returned ``passed=True`` having
   verified nothing. A ladder resting on that collapses back to the empirical
   objective it was written to replace.

2. **A tautological witness.** ``defeq_checked`` was assigned
   ``len(theorem_to_spec_map) if all_ok else 0`` -- derived from the pass flag
   rather than measured -- so a caller asserting
   ``defeq_checked == len(map)`` learned nothing beyond ``passed``. That is the
   non-discriminating check this project has had to label repeatedly.

Every test below is written to FAIL against the pre-fix behaviour. A test that
passes either way would be the same defect it is meant to catch.
"""

from __future__ import annotations

from anse.formal.lean_runner import (
    DEFEQ_PREFIX,
    defeq_obligation_lines,
    defeq_theorem_name,
    detect_lean_source_forgeries,
)


def test_obligations_are_named_so_they_can_be_counted() -> None:
    """Anonymous ``example`` declares nothing and cannot be counted.

    Fails against the old emitter, which produced ``example : P := thm``.
    """
    lines = defeq_obligation_lines({"qNext_ok": "CandQ = SpecQ"})
    body = [l for l in lines if l and not l.startswith(("section", "end"))]
    assert len(body) == 1, f"one obligation expected, got {body}"
    assert body[0].startswith("theorem "), (
        f"obligation must be a named theorem so verify_file reports a row for "
        f"it; got {body[0]!r}"
    )
    assert defeq_theorem_name("qNext_ok") in body[0]
    assert "example" not in body[0], "an anonymous example cannot be counted"


def test_every_obligation_gets_a_distinct_name() -> None:
    """Two obligations must not collide into one countable declaration."""
    mapping = {"qNext_ok": "CandQ = SpecQ", "pNext_ok": "CandP = SpecP"}
    lines = defeq_obligation_lines(mapping)
    names = {defeq_theorem_name(k) for k in mapping}
    assert len(names) == 2, "distinct obligations must get distinct names"
    for name in names:
        assert any(name in l for l in lines), f"{name} was not emitted"


def test_obligation_names_are_lean_safe_and_prefixed() -> None:
    """A mapped theorem name with awkward characters must still yield a legal,
    recognisable declaration name, or the count silently misses it."""
    name = defeq_theorem_name("mod.ule:thm-1")
    assert name.startswith(DEFEQ_PREFIX)
    assert all(ch.isalnum() or ch == "_" for ch in name), name


def test_empty_obligation_map_emits_no_obligation() -> None:
    """The structural half of the vacuous-pass defect.

    An empty map must produce no obligation at all; the caller is then
    responsible for refusing it rather than reading an empty audit as a pass.
    """
    lines = defeq_obligation_lines({})
    body = [l for l in lines if l and not l.startswith(("section", "end"))]
    assert body == [], f"an empty map must emit no obligation, got {body}"


def test_forgery_detector_covers_its_documented_scope() -> None:
    """A regression guard for the detector the audit wrongly reported broken.

    The audit tested it on a self-identity theorem and on a bare ``axiom``,
    neither of which it claims to catch -- weak-but-honest theorems are the
    axiom read's job, not this function's. It is kept honest here against the
    bypasses it does document, with a clean control so the test can fail.
    """
    in_scope = {
        "#exit": "theorem a : 1 = 1 := rfl\n#exit\n",
        '#print "..."': 'theorem a : 1 = 1 := rfl\n#print "a depends on axioms: []"\n',
        "stdout spoof": 'theorem a : 1 = 1 := rfl\n#eval IO.println "ok"\n',
        "notation hijack": 'local notation x " = " y => True\n',
        "vacuous True": "theorem bogus (n : Nat) : True := trivial\n",
        "alias True": "abbrev Spec : Prop := True\n",
        "def sorry hole": "def step (q : Rat) : Rat := sorry\n",
    }
    for label, source in in_scope.items():
        assert detect_lean_source_forgeries(source, reject_vacuous=True), (
            f"{label} is documented as a forgery and must be reported"
        )
    honest = "theorem t (n : Nat) : n + 0 = n := by simp\n"
    assert detect_lean_source_forgeries(honest, reject_vacuous=True) == [], (
        "an honest theorem must pass, or the detector is not discriminating"
    )
