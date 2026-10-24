"""The three promotion stages must be three different tests.

`AlphaEvolveBiomimeticEngine.run_evolution_with_hardened_gate` scores a champion
through a three-stage hardened loop: search, held-out, replicates. The held-out
and replicate evaluators used to DEFAULT to the search number --
`lambda code: champion.total_energy` and
`lambda code: [E, E * 0.99, E * 1.01]`, whose median is exactly `E` -- while the
loop's `best_heldout_metric` and `best_replicate_median` were both initialised to
the same `baseline_best`. With `_improves` being `candidate < current_best`, all
three stages collapsed to one comparison, so stage 1 passing guaranteed stages 2
and 3. No caller in the repository supplied either function, so that was the only
path taken and every promotion verdict it produced was manufactured.

This is the forced-control defect catalogued in LL.md section 29.2: a control
that cannot fail. The test below fails against the pre-fix behaviour, which
promoted on the strength of the search number alone.
"""

from __future__ import annotations

import inspect

from anse.autopoiesis import alphaevolve_biomimetic as ab


def test_promotion_refuses_without_independent_evaluators() -> None:
    """Absent evaluators must BLOCK, never promote.

    Discriminating: the pre-fix code substituted the search metric and could
    report ``promoted=True`` here.
    """
    engine = ab.AlphaEvolveBiomimeticEngine(
        evaluator_fn=lambda code: {
            "latency_ms": 1.0,
            "memory_mb": 1.0,
            "metabolic_energy": 1.0,
            "invariant_error": 0.0,
            "physical_energy": 1.0,
        },
        seed=7,
    )
    verdict = engine.run_evolution_with_hardened_gate(
        ["def f(x):\n    return x\n"], generations=1
    )

    assert verdict["promoted"] is False, (
        "a promotion without an independent held-out evaluator carries no "
        "evidence and must be refused"
    )
    assert "blocked" in verdict, "the refusal must say why it was refused"
    assert "heldout_eval_fn" in verdict["blocked"]
    assert "replicates_eval_fn" in verdict["blocked"]


def test_the_defaults_that_forced_the_gate_are_gone() -> None:
    """The source must not reinstate a fallback to the search number.

    Guards against the specific regression rather than its symptom: a future
    edit that restores ``heldout_eval_fn or (lambda ...)`` would re-force the
    gate while the behavioural test above might still pass if the fallback
    happened to be pessimistic.
    """
    src = inspect.getsource(ab.AlphaEvolveBiomimeticEngine.run_evolution_with_hardened_gate)
    assert "heldout_eval_fn or (" not in src, (
        "a default held-out evaluator re-forces the gate"
    )
    assert "replicates_eval_fn or (" not in src, (
        "a default replicate evaluator re-forces the gate"
    )


def test_both_evaluators_are_still_honoured_when_supplied() -> None:
    """The fix must not break the real path: supplied evaluators run, and a
    held-out metric that is WORSE than baseline must block promotion."""
    engine = ab.AlphaEvolveBiomimeticEngine(
        evaluator_fn=lambda code: {
            "latency_ms": 1.0,
            "memory_mb": 1.0,
            "metabolic_energy": 1.0,
            "invariant_error": 0.0,
            "physical_energy": 1.0,
        },
        seed=7,
    )
    verdict = engine.run_evolution_with_hardened_gate(
        ["def f(x):\n    return x\n"],
        generations=1,
        heldout_eval_fn=lambda code: 1e9,          # far worse than any baseline
        replicates_eval_fn=lambda code: [1e9, 1e9, 1e9],
    )
    assert "blocked" not in verdict, "supplied evaluators must be used, not refused"
    assert verdict["promoted"] is False, (
        "a champion that fails held-out validation must not be promoted"
    )
