"""Card C-7: held-out pass@k, Wilson interval, promotion compare, ladder loader, GATE wiring."""

from __future__ import annotations

import importlib.util
import json
import logging
import sys
from math import comb
from pathlib import Path
from types import ModuleType

import pytest
from hypothesis import given
from hypothesis import strategies as st

from anse.v2.heldout_eval import (
    LadderVerdicts,
    build_heldout_baseline,
    compare,
    load_ladder_verdicts,
    pass_at_k,
    score,
    score_by_tier,
    wilson_interval,
)

REPO = Path(__file__).resolve().parents[2]


# ── pass@k estimator ──────────────────────────────────────────────────────────
def test_pass_at_k_hand_values() -> None:
    # n=5, c=2, k=3: 1 - C(3,3)/C(5,3) = 1 - 1/10
    assert pass_at_k(5, 2, 3) == pytest.approx(0.9)
    # n=5, c=2, k=1: plain pass rate
    assert pass_at_k(5, 2, 1) == pytest.approx(0.4)
    # n=10, c=3, k=2: 1 - C(7,2)/C(10,2) = 1 - 21/45
    assert pass_at_k(10, 3, 2) == pytest.approx(1 - 21 / 45)
    assert pass_at_k(4, 0, 2) == 0.0
    assert pass_at_k(4, 4, 2) == 1.0
    assert pass_at_k(5, 3, 3) == 1.0  # n - c < k: some correct sample is always drawn


def test_pass_at_k_rejects_bad_arguments() -> None:
    with pytest.raises(ValueError, match="k="):
        pass_at_k(2, 1, 3)
    with pytest.raises(ValueError, match="k must be"):
        pass_at_k(2, 1, 0)
    with pytest.raises(ValueError, match="c="):
        pass_at_k(2, 3, 1)


@given(n=st.integers(1, 12), c=st.integers(0, 12), k=st.integers(1, 12))
def test_pass_at_k_is_a_probability_monotone_in_c_and_k(n: int, c: int, k: int) -> None:
    if c > n or k > n:
        with pytest.raises(ValueError):
            pass_at_k(n, c, k)
        return
    p = pass_at_k(n, c, k)
    assert 0.0 <= p <= 1.0
    assert p == pytest.approx(1 - comb(n - c, k) / comb(n, k))
    if c < n:
        assert pass_at_k(n, c + 1, k) >= p
    if k < n:
        assert pass_at_k(n, c, k + 1) >= p


# ── Wilson interval ───────────────────────────────────────────────────────────
def test_wilson_matches_hand_values() -> None:
    assert wilson_interval(8, 10) == pytest.approx((0.4902, 0.9433), abs=2e-4)
    assert wilson_interval(6, 10) == pytest.approx((0.3127, 0.8318), abs=2e-4)
    assert wilson_interval(0, 12) == pytest.approx((0.0, 0.2425), abs=2e-4)
    assert wilson_interval(12, 12) == pytest.approx((0.7576, 1.0), abs=2e-4)
    with pytest.raises(ValueError, match="at least one"):
        wilson_interval(0, 0)
    with pytest.raises(ValueError, match="successes="):
        wilson_interval(3.5, 3)


@given(n=st.integers(1, 200), frac=st.floats(0.0, 1.0))
def test_wilson_brackets_the_point_estimate(n: int, frac: float) -> None:
    successes = frac * n
    low, high = wilson_interval(successes, n)
    assert 0.0 <= low <= successes / n + 1e-12
    assert successes / n - 1e-12 <= high <= 1.0


# ── score / score_by_tier ─────────────────────────────────────────────────────
def test_score_averages_per_item_pass_at_k_and_reports_interval() -> None:
    verdicts = {"a": [True, False, False, False, False], "b": [False] * 5, "c": [True] * 5}
    out = score(verdicts, k=3)
    # per item: a = 1 - C(4,3)/C(5,3) = 0.6 ; b = 0 ; c = 1
    assert out["pass_at_k"] == pytest.approx((0.6 + 0.0 + 1.0) / 3)
    assert out["n_items"] == 3 and out["k"] == 3
    low, high = wilson_interval(1.6, 3)
    assert (out["ci_low"], out["ci_high"]) == pytest.approx((low, high))
    assert out["ci_low"] < out["pass_at_k"] < out["ci_high"]


def test_score_raises_when_an_item_has_fewer_than_k_samples() -> None:
    with pytest.raises(ValueError, match="item 'short'"):
        score({"ok": [True, True, False], "short": [True, False]}, k=3)
    with pytest.raises(ValueError, match="no items"):
        score({}, k=1)


def test_score_by_tier_breaks_down_and_requires_tier_metadata() -> None:
    verdicts = {"x": [True], "y": [False], "z": [True]}
    tiers = {"x": "T0", "y": "T1", "z": "T0"}
    out = score_by_tier(verdicts, tiers, k=1)
    assert out["pass_at_k"] == pytest.approx(2 / 3)
    assert out["tiers"]["T0"]["pass_at_k"] == 1.0 and out["tiers"]["T0"]["n_items"] == 2
    assert out["tiers"]["T1"]["pass_at_k"] == 0.0
    with pytest.raises(ValueError, match=r"without a tier: \['z'\]"):
        score_by_tier(verdicts, {"x": "T0", "y": "T1"}, k=1)


# ── compare ───────────────────────────────────────────────────────────────────
def _scored(overall: float, tiers: dict[str, float], k: int = 1, n: int = 46) -> dict:
    return {
        "k": k,
        "pass_at_k": overall,
        "n_items": n,
        "tiers": {t: {"pass_at_k": p, "n_items": 10} for t, p in tiers.items()},
    }


def test_compare_promotes_on_clear_gain_without_regression() -> None:
    base = _scored(0.13, {"T0": 0.6, "T1": 0.0, "T2": 0.0})
    cand = _scored(0.20, {"T0": 0.6, "T1": 0.1, "T2": 0.1})
    out = compare(base, cand)
    assert out["promote"] is True
    assert out["gain"] == pytest.approx(0.07)
    assert out["reasons"] == ["gain clears min_gain and no tier regresses"]


def test_compare_refuses_when_gain_is_below_min_gain() -> None:
    base = _scored(0.13, {"T0": 0.6})
    cand = _scored(0.16, {"T0": 0.7})
    out = compare(base, cand)
    assert out["promote"] is False
    assert any("below min_gain" in r for r in out["reasons"])
    assert compare(base, cand, min_gain=0.02)["promote"] is True


def test_tier_regression_blocks_a_net_gain() -> None:
    # T0 loses 0.2 while T1/T2 rise enough for +0.10 overall: net gain, still refused.
    base = _scored(0.20, {"T0": 0.6, "T1": 0.0, "T2": 0.0})
    cand = _scored(0.30, {"T0": 0.4, "T1": 0.25, "T2": 0.25})
    out = compare(base, cand)
    assert out["promote"] is False
    assert out["reasons"] == ["tier T0 regressed -0.2000 (limit -0.0200)"]
    assert compare(base, cand, max_tier_regression=0.25)["promote"] is True


def test_compare_refuses_k_mismatch_missing_tier_small_n_and_unsound_candidate() -> None:
    base = _scored(0.10, {"T0": 0.5, "T1": 0.0})
    cand = _scored(0.30, {"T0": 0.5}, k=3, n=12)
    cand["false_accepted"] = 1
    out = compare(base, cand)
    assert out["promote"] is False
    joined = " | ".join(out["reasons"])
    assert "k mismatch" in joined
    assert "12 item(s), need >= 30" in joined
    assert "accepted 1 FALSE item" in joined
    assert "tier T1 missing" in joined
    assert len(out["reasons"]) == 4


# ── loader on a tmp baseline.json with the real schema ────────────────────────
def _run(model: str, item: str, tier: str, truth: bool | None, clean: bool) -> dict:
    """One record in the shape scripts/hardness/run_ladder.py writes to baseline.json."""
    return {"model": model, "id": item, "tier": tier, "truth": truth, "gen_s": 1.0,
            "extracted": True, "clean": clean, "axioms": ["propext"] if clean else
            ["propext", "sorryAx"], "compile_s": 2.0}


@pytest.fixture
def ladder_files(tmp_path: Path) -> dict[str, Path]:
    frozen = [{"id": i, "tier": t, "prop": f"p_{i}", "sha": "0" * 16}
              for i, t in (("t0_a", "T0"), ("t0_b", "T0"), ("t1_a", "T1"), ("t1_F", "T1"),
                           ("t4_bsd", "T4"))]
    runs = [
        _run("deepseek", "t0_a", "T0", True, True),
        _run("deepseek", "t0_b", "T0", True, False),
        _run("deepseek", "t1_a", "T1", True, False),
        _run("deepseek", "t1_F", "T1", False, True),     # FALSE item accepted: unsound
        _run("deepseek", "t4_bsd", "T4", None, False),   # open problem: unknown truth
        _run("deepseek", "leak", "T1", True, True),      # not in the frozen split
        _run("goedel", "t0_a", "T0", True, True),
        _run("goedel", "t0_b", "T0", True, True),
        _run("goedel", "t1_a", "T1", True, False),
        _run("goedel", "t1_F", "T1", False, False),
    ]
    ab_runs = [dict(_run("deepseek", "t0_a", "T0", True, True), arm="k5", k=5),
               dict(_run("deepseek", "t0_a", "T0", True, False), arm="k5", k=5)]
    paths = {
        "baseline": tmp_path / "baseline.json",
        "ab": tmp_path / "retrieval_ab.json",
        "frozen": tmp_path / "frozen_split.json",
    }
    paths["baseline"].write_text(json.dumps({"started": "x", "n_items": 5, "runs": runs,
                                             "summary": {}, "finished": "y"}))
    paths["ab"].write_text(json.dumps({"started": "x", "k": 5, "runs": ab_runs, "hits": {}}))
    paths["frozen"].write_text(json.dumps(frozen))
    return paths


def test_loader_groups_true_items_flags_false_acceptance_and_drops_off_split(
    ladder_files: dict[str, Path],
) -> None:
    arms = load_ladder_verdicts(ladder_files["baseline"], ladder_files["ab"], ladder_files["frozen"])
    assert set(arms) == {"deepseek", "goedel", "deepseek+premises"}
    ds = arms["deepseek"]
    assert ds.verdicts == {"t0_a": [True], "t0_b": [False], "t1_a": [False]}
    assert ds.tiers == {"t0_a": "T0", "t0_b": "T0", "t1_a": "T1"}
    assert (ds.false_n, ds.false_accepted) == (1, 1)
    assert ds.unknown_truth == ["t4_bsd"] and ds.dropped_off_split == ["leak"]
    assert arms["goedel"].false_accepted == 0
    # two retrieval-arm records for the same item become n=2 samples
    assert arms["deepseek+premises"].verdicts == {"t0_a": [True, False]}
    # without a frozen split nothing is dropped
    assert load_ladder_verdicts(ladder_files["baseline"])["deepseek"].dropped_off_split == []
    # a missing retrieval file is simply absent
    assert set(load_ladder_verdicts(ladder_files["baseline"],
                                    ladder_files["ab"].with_name("nope.json"))) == {
        "deepseek", "goedel"}


def test_loader_rejects_a_file_without_runs(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps([1, 2, 3]))
    with pytest.raises(ValueError, match="'runs' list"):
        load_ladder_verdicts(bad)


def test_build_heldout_baseline_scores_per_arm_with_provenance(
    ladder_files: dict[str, Path],
) -> None:
    doc = build_heldout_baseline(ladder_files["baseline"], ladder_files["ab"],
                                 ladder_files["frozen"], k=1)
    assert doc["k"] == 1 and doc["n_frozen_items"] == 5
    assert set(doc["sha256"]) == {"baseline", "frozen_split", "retrieval_ab"}
    ds = doc["models"]["deepseek"]
    assert ds["pass_at_k"] == pytest.approx(1 / 3)
    assert ds["tiers"]["T0"]["pass_at_k"] == 0.5 and ds["tiers"]["T1"]["pass_at_k"] == 0.0
    assert ds["false_accepted"] == 1 and ds["unknown_truth"] == ["t4_bsd"]
    assert doc["models"]["goedel"]["tiers"]["T0"]["pass_at_k"] == 1.0
    assert doc["models"]["deepseek+premises"]["pass_at_k"] == 0.5
    assert doc["skipped"] == {}
    # k=2: the greedy arms have n=1 < k and are skipped with the reason; the n=2 arm scores
    doc2 = build_heldout_baseline(ladder_files["baseline"], None, ladder_files["frozen"], k=2)
    assert set(doc2["skipped"]) == {"deepseek", "goedel"}
    assert "k=2" in doc2["skipped"]["deepseek"] and "retrieval_ab" not in doc2["sources"]
    doc3 = build_heldout_baseline(ladder_files["baseline"], ladder_files["ab"],
                                  ladder_files["frozen"], k=2)
    assert doc3["models"]["deepseek+premises"]["pass_at_k"] == 1.0


def test_ladder_verdicts_scored_raises_below_k() -> None:
    lv = LadderVerdicts(model="m")
    lv.add_run(_run("m", "i", "T0", True, True), None)
    with pytest.raises(ValueError, match="k=2"):
        lv.scored(2)


# ── the real frozen ladder: numbers LL.md §4c reports ─────────────────────────
@pytest.mark.skipif(not (REPO / "results/hardness/baseline.json").exists(),
                    reason="real ladder results not checked out")
def test_real_baseline_reproduces_ll_md_4c() -> None:
    doc = build_heldout_baseline(REPO / "results/hardness/baseline.json", None,
                                 REPO / "results/hardness/frozen_split.json", k=1)
    ds, gd = doc["models"]["deepseek"], doc["models"]["goedel"]
    assert ds["tiers"]["T0"]["pass_at_k"] == pytest.approx(0.6)
    assert gd["tiers"]["T0"]["pass_at_k"] == pytest.approx(0.8)
    for t in ("T1", "T2", "T3"):
        assert ds["tiers"][t] == pytest.approx(gd["tiers"][t])
        assert ds["tiers"][t]["pass_at_k"] == 0.0 and ds["tiers"][t]["n_items"] == 12
    assert ds["false_accepted"] == 0 and gd["false_accepted"] == 0 and ds["false_n"] == 12
    assert ds["unknown_truth"] == ["t4_bsd_rank"]


# ── GATE wiring in scripts/night_training_workflow.py ─────────────────────────
def _load_workflow() -> ModuleType:
    path = REPO / "scripts/night_training_workflow.py"
    spec = importlib.util.spec_from_file_location("night_training_workflow_under_test", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    try:
        spec.loader.exec_module(mod)
    except ModuleNotFoundError as exc:
        pytest.skip(f"night_training_workflow.py dependency unavailable: {exc}")
    return mod


@pytest.fixture
def wf(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    mod = _load_workflow()
    monkeypatch.setattr(mod, "JOURNALS", tmp_path / "journals")
    monkeypatch.setattr(mod, "HELDOUT_BASELINE", tmp_path / "v2" / "heldout_baseline.json")
    # The trainer bits: no disk 2, no GPU, no torch. Each upstream step is mocked to succeed.
    monkeypatch.setattr(mod, "step_artifact", lambda model, journal: True)
    monkeypatch.setattr(mod, "step_data", lambda model, journal, smoke: [{"prompt": "p"}])
    adapter_dir = tmp_path / "candidates" / "m"
    adapter_dir.mkdir(parents=True)
    fit = {"weights_written": True, "loss_first": 2.0, "loss_last": 1.0,
           "adapter_dir": str(adapter_dir)}
    monkeypatch.setattr(mod, "step_fit", lambda model, journal, rows, smoke: dict(fit))
    monkeypatch.setattr(mod, "step_eval", lambda model, journal, fit: {
        "improved": True, "loss_change_pct": -50.0})
    mod._test_adapter_dir = adapter_dir  # type: ignore[attr-defined]
    return mod


def _gate(journal) -> object:
    recs = [s for s in journal.steps if s.step == "GATE"]
    assert len(recs) == 1
    return recs[0]


def test_gate_is_blocked_naming_the_missing_baseline_file(wf: ModuleType) -> None:
    journal = wf.run_model("m", smoke=False)
    rec = _gate(journal)
    assert rec.outcome == wf.Outcome.BLOCKED
    assert str(wf.HELDOUT_BASELINE) in rec.detail
    assert rec.data["missing_file"] == str(wf.HELDOUT_BASELINE)
    assert rec.data["promoted"] is False
    written = json.loads((wf.JOURNALS / "m.json").read_text())
    assert written["steps"][-1]["outcome"] == "BLOCKED"


def test_gate_with_baseline_but_no_candidate_eval_is_blocked_naming_it(wf: ModuleType) -> None:
    wf.HELDOUT_BASELINE.parent.mkdir(parents=True)
    wf.HELDOUT_BASELINE.write_text(json.dumps({"k": 1, "models": {"deepseek": _scored(0.1, {})}}))
    rec = _gate(wf.run_model("m", smoke=False))
    assert rec.outcome == wf.Outcome.BLOCKED
    assert rec.data["missing_file"].endswith("heldout_eval.json")
    assert "candidate heldout eval missing" in rec.data["reason"]


def test_gate_calls_compare_and_records_promote_and_reasons(
    wf: ModuleType, monkeypatch: pytest.MonkeyPatch,
) -> None:
    wf.HELDOUT_BASELINE.parent.mkdir(parents=True)
    base = _scored(0.13, {"T0": 0.6, "T1": 0.0})
    wf.HELDOUT_BASELINE.write_text(json.dumps({"k": 1, "models": {"deepseek": base}}))
    cand = _scored(0.25, {"T0": 0.6, "T1": 0.15})
    cand["prover"] = "deepseek"
    (wf._test_adapter_dir / "heldout_eval.json").write_text(json.dumps(cand))
    calls: list[tuple[dict, dict]] = []
    real_compare = wf.heldout_eval.compare

    def spy(b: dict, c: dict, **kw: object) -> dict:
        calls.append((b, c))
        return real_compare(b, c, **kw)

    monkeypatch.setattr(wf.heldout_eval, "compare", spy)
    rec = _gate(wf.run_model("m", smoke=False))
    assert calls and calls[0][0]["pass_at_k"] == 0.13 and calls[0][1]["prover"] == "deepseek"
    assert rec.outcome == wf.Outcome.OK
    assert rec.data["promoted"] is True and rec.detail.startswith("PROMOTE")
    assert rec.data["reasons"] == ["gain clears min_gain and no tier regresses"]

    # a regressing candidate is recorded as rejected with the reason, not BLOCKED
    cand["tiers"]["T0"]["pass_at_k"] = 0.3
    (wf._test_adapter_dir / "heldout_eval.json").write_text(json.dumps(cand))
    rec2 = _gate(wf.run_model("m", smoke=False))
    assert rec2.outcome == wf.Outcome.OK and rec2.data["promoted"] is False
    assert rec2.data["reasons"] == ["tier T0 regressed -0.3000 (limit -0.0200)"]


def test_gate_blocks_when_candidate_prover_is_not_in_baseline(wf: ModuleType) -> None:
    wf.HELDOUT_BASELINE.parent.mkdir(parents=True)
    wf.HELDOUT_BASELINE.write_text(json.dumps({"k": 1, "models": {"deepseek": _scored(0.1, {})}}))
    cand = _scored(0.9, {})
    cand["prover"] = "qwen_lora"
    (wf._test_adapter_dir / "heldout_eval.json").write_text(json.dumps(cand))
    rec = _gate(wf.run_model("m", smoke=False))
    assert rec.outcome == wf.Outcome.BLOCKED
    assert "'qwen_lora'" in rec.detail and "['deepseek']" in rec.detail


def test_write_heldout_baseline_flag_builds_the_file_from_the_ladder(
    wf: ModuleType, ladder_files: dict[str, Path], monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr(wf, "HARDNESS_DIR", ladder_files["baseline"].parent)
    with caplog.at_level(logging.INFO, logger="night_train"):
        assert wf.main(["--write-heldout-baseline"]) == 0
    doc = json.loads(wf.HELDOUT_BASELINE.read_text())
    assert set(doc["models"]) == {"deepseek", "goedel", "deepseek+premises"}
    assert doc["models"]["goedel"]["tiers"]["T0"]["pass_at_k"] == 1.0
    assert "written" in doc
    assert any("T0 1/2" in r.message for r in caplog.records)  # deepseek T0
    # k=3 on greedy data: arms are skipped and said so, not silently scored
    with caplog.at_level(logging.INFO, logger="night_train"):
        doc3 = wf.write_heldout_baseline(wf.HELDOUT_BASELINE, k=3)
    assert set(doc3["skipped"]) == {"deepseek", "goedel", "deepseek+premises"}
    assert any("SKIPPED" in r.message for r in caplog.records)
    assert json.loads(wf.HELDOUT_BASELINE.read_text())["k"] == 3
