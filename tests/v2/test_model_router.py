"""Model x hardness router: sound-first, evidence-ordered, escalates when unearned."""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from anse.v2.model_router import (
    ESCALATE_HUMAN,
    ESCALATE_TOP_TIER,
    Budget,
    CapabilityMatrix,
    Cell,
    record_outcome,
    route,
    summarize,
    with_budget,
)


def _ladder_matrix() -> CapabilityMatrix:
    """The 2026-09-27 baseline numbers (results/hardness/baseline.json)."""
    mx = CapabilityMatrix()
    mx.set("lean", "T0", "deepseek", Cell(10, 6, source="baseline"))
    mx.set("lean", "T0", "goedel", Cell(10, 8, source="baseline"))
    for t in ("T1", "T2", "T3"):
        mx.set("lean", t, "deepseek", Cell(12, 0, false_items=4, false_accepted=0, source="baseline"))
        mx.set("lean", t, "goedel", Cell(12, 0, false_items=4, false_accepted=0, source="baseline"))
    return mx


# ── Cell arithmetic ────────────────────────────────────────────────────────────
def test_wilson_lower_bound_matches_hand_values() -> None:
    assert Cell(10, 8).wilson_low() == pytest.approx(0.4902, abs=2e-3)  # 8/10
    assert Cell(10, 6).wilson_low() == pytest.approx(0.3128, abs=2e-3)  # 6/10
    assert Cell(12, 0).wilson_low() == 0.0
    assert Cell(0, 0).wilson_low() is None and Cell(0, 0).pass_rate is None


def test_one_of_one_never_outranks_eight_of_ten() -> None:
    assert Cell(1, 1).wilson_low() < Cell(10, 8).wilson_low()


def test_cell_rejects_impossible_counts() -> None:
    with pytest.raises(ValueError):
        Cell(1, 2)
    with pytest.raises(ValueError):
        Cell(1, 0, false_items=0, false_accepted=1)
    with pytest.raises(ValueError):
        Cell(-1, 0)


@given(st.integers(0, 200), st.integers(0, 200))
def test_wilson_low_is_a_valid_lower_bound(n: int, k: int) -> None:
    k = min(k, n)
    wl = Cell(n, k).wilson_low()
    if n == 0:
        assert wl is None
    else:
        assert 0.0 <= wl <= k / n + 1e-12


# ── routing ────────────────────────────────────────────────────────────────────
def test_t0_prefers_the_measured_leader_and_does_not_escalate_above_threshold() -> None:
    plan = route("lean", "T0", _ladder_matrix(), ["deepseek", "goedel"], Budget(min_wilson_low=0.4))
    assert [c.model for c in plan.candidates] == ["goedel", "deepseek"]
    assert not plan.escalates
    assert "8/10" in plan.candidates[0].reason


def test_t1_with_zero_passes_escalates_after_the_local_models() -> None:
    plan = route("lean", "T1", _ladder_matrix(), ["deepseek", "goedel"])
    models = [c.model for c in plan.candidates]
    assert models[-1] == ESCALATE_TOP_TIER
    assert set(models[:-1]) == {"deepseek", "goedel"}
    assert "best wilson_low=0.00" in plan.candidates[-1].reason


def test_unsound_model_is_excluded_even_with_a_higher_pass_rate() -> None:
    mx = _ladder_matrix()
    # a model that proves 10/10 true items but also "proves" a false one
    mx.set("lean", "T0", "cheater", Cell(10, 10, false_items=4, false_accepted=1, source="x"))
    plan = route("lean", "T0", mx, ["cheater", "goedel", "deepseek"])
    assert "cheater" not in [c.model for c in plan.candidates]
    assert plan.excluded_unsound == ("cheater",)
    assert plan.candidates[0].model == "goedel"


def test_unmeasured_model_gets_at_most_one_exploration_slot_after_measured_ones() -> None:
    plan = route("lean", "T0", _ladder_matrix(), ["zeta-new", "goedel", "alpha-new", "deepseek"],
                 Budget(max_candidates=4, min_wilson_low=0.4))
    models = [c.model for c in plan.candidates]
    assert models[:2] == ["goedel", "deepseek"]
    assert models[2] == "alpha-new" and "exploration" in plan.candidates[2].reason
    assert "zeta-new" not in models


def test_exploration_can_be_disabled_and_budget_caps_candidates() -> None:
    plan = route("lean", "T0", _ladder_matrix(), ["new", "goedel", "deepseek"],
                 Budget(max_candidates=1, allow_exploration=False, min_wilson_low=0.4))
    assert [c.model for c in plan.candidates] == ["goedel"]


def test_only_unmeasured_models_means_escalation_with_reason() -> None:
    plan = route("physics", "P2", CapabilityMatrix(), ["qwen3:8b"], Budget(next_tier=ESCALATE_HUMAN))
    assert [c.model for c in plan.candidates] == ["qwen3:8b", ESCALATE_HUMAN]
    assert "no measured model" in plan.candidates[-1].reason


def test_route_is_deterministic_under_input_order() -> None:
    mx = _ladder_matrix()
    a = route("lean", "T0", mx, ["deepseek", "goedel"])
    b = route("lean", "T0", mx, ["goedel", "deepseek"])
    assert a == b


def test_route_rejects_empty_availability_and_bad_budget() -> None:
    with pytest.raises(ValueError):
        route("lean", "T0", _ladder_matrix(), [])
    with pytest.raises(ValueError):
        Budget(max_candidates=0)
    with pytest.raises(ValueError):
        Budget(min_wilson_low=1.5)


# ── learning from verdicts ─────────────────────────────────────────────────────
def test_record_outcome_true_item_updates_pass_rate_without_mutating_input() -> None:
    mx = _ladder_matrix()
    before = mx.get("lean", "T1", "goedel")
    new = record_outcome(mx, "lean", "T1", "goedel", passed=True, truth=True, source="retrieval_ab")
    assert mx.get("lean", "T1", "goedel") == before  # pure
    cell = new.get("lean", "T1", "goedel")
    assert (cell.attempts, cell.passes) == (13, 1)
    assert cell.source == "baseline+retrieval_ab"


def test_record_outcome_false_item_accepted_makes_model_unsound_and_unroutable() -> None:
    mx = record_outcome(_ladder_matrix(), "lean", "T0", "goedel", passed=True, truth=False, source="ab")
    assert not mx.get("lean", "T0", "goedel").sound
    plan = route("lean", "T0", mx, ["goedel", "deepseek"])
    assert plan.candidates[0].model == "deepseek" and plan.excluded_unsound == ("goedel",)


def test_record_outcome_unknown_truth_counts_failures_only() -> None:
    mx = record_outcome(CapabilityMatrix(), "lean", "T4", "goedel", passed=True, truth=None, source="s")
    assert mx.get("lean", "T4", "goedel") is None  # an accepted proof of an open statement is not evidence
    mx = record_outcome(mx, "lean", "T4", "goedel", passed=False, truth=None, source="s")
    assert mx.get("lean", "T4", "goedel").attempts == 1


# ── serialisation and reporting ────────────────────────────────────────────────
def test_round_trip_and_summary_rows() -> None:
    mx = _ladder_matrix()
    again = CapabilityMatrix.from_dict(mx.to_dict())
    assert again.cells == mx.cells
    rows = summarize(mx, "lean", ["T0", "T1"], ["deepseek", "goedel"])
    assert rows[0]["best_model"] == "goedel"
    assert rows[0]["best_wilson_low"] == pytest.approx(0.4902, abs=2e-3)
    # Honest consequence of 8/10: the Wilson lower bound (0.49) sits below the default
    # 0.5 threshold, so even the saturated tier T0 is not trusted to a local prover alone.
    assert rows[0]["escalates"] is True
    assert rows[1]["best_wilson_low"] == 0.0 and rows[1]["escalates"] is True


def test_models_lists_only_the_requested_cell_group() -> None:
    mx = _ladder_matrix()
    mx.set("coding", "P1", "qwen3:8b", Cell(20, 16))
    assert mx.models("lean", "T0") == ["deepseek", "goedel"]
    assert mx.models("coding", "P1") == ["qwen3:8b"]
    assert mx.models("lean", "T9") == []


def test_model_shown_only_false_items_and_accepting_one_is_unsound_not_unmeasured() -> None:
    mx = CapabilityMatrix()
    mx.set("lean", "T1", "sloppy", Cell(0, 0, false_items=2, false_accepted=1, source="neg-only"))
    plan = route("lean", "T1", mx, ["sloppy"])
    assert plan.excluded_unsound == ("sloppy",)
    assert [c.model for c in plan.candidates] == [ESCALATE_TOP_TIER]  # not even an exploration slot


def test_with_budget_changes_one_field() -> None:
    b = with_budget(Budget(), min_wilson_low=0.9)
    assert b.min_wilson_low == 0.9 and b.max_candidates == Budget().max_candidates
