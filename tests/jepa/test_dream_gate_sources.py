"""Source-separation tests for the dream-predictor gate: a pass must come from signal, not source identity."""

from __future__ import annotations

from typing import Any

from anse.jepa.dream_predictor_trainer import evaluate_gate
from tests.jepa.test_dream_predictor_trainer import _rows


def _tagged(rows: list[dict[str, Any]], source: str) -> list[dict[str, Any]]:
    """Give rows a source tag and make their task names unique to that source."""
    return [{**row, "task": f"{source}:{row['task']}", "metadata": {"source": source}} for row in rows]


def test_gate_refuses_a_pass_that_only_comes_from_source_identity() -> None:
    # Source A fails 80% of the time and source B passes 80%. A probe can separate the two
    # sources by their text style without learning anything about correctness, and neither
    # source carries real signal inside it.
    lean_like = _tagged(_rows(n_tasks=12, per_task=20, seed=5, signal=False), "lean")
    cosmo_like = _tagged(_rows(n_tasks=12, per_task=20, seed=6, signal=False), "cosmo")
    for i, row in enumerate(lean_like):
        row["energy"] = 0.0 if i % 5 == 0 else 1.0
    for i, row in enumerate(cosmo_like):
        row["energy"] = 1.0 if i % 5 == 0 else 0.0

    gate = evaluate_gate(lean_like + cosmo_like, seeds=(0, 1))

    assert gate.status == "BLOCKED"
    assert any("does not beat" in reason for reason in gate.reasons)


def test_gate_passes_only_when_every_source_has_real_signal() -> None:
    first = _tagged(_rows(n_tasks=12, per_task=10, seed=7, signal=True), "alpha")
    second = _tagged(_rows(n_tasks=12, per_task=10, seed=8, signal=True), "beta")

    gate = evaluate_gate(first + second, seeds=(0, 1))

    assert gate.status == "PASS", gate.reasons
    assert set(gate.real_folds) == {"alpha", "beta"}


def test_gate_blocks_an_empty_pool() -> None:
    gate = evaluate_gate([], seeds=(0,))

    assert gate.status == "BLOCKED"
    assert gate.reasons == ["no rows in the verified pool"]
