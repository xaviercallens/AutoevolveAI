"""Tests for anse.v2.label_control (card V0-8) and the JEPATrainer label-control hook."""

from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

import pytest
import torch
from hypothesis import given, settings
from hypothesis import strategies as st

from anse.config import JEPAConfig
from anse.jepa.dataset import JEPADataset, train_val_split
from anse.jepa.trainer import LABEL_CONTROL_KEYS, JEPATrainer, shuffled_label_dataset
from anse.jepa.world_model import JEPAWorldModel
from anse.v2.label_control import INFORMATIVE, SATURATED, UNDEFINED, control_report, shuffled_copy

D_INPUT = 16
D_HIDDEN = 24
D_LATENT = 8


# ── shuffled_copy ──────────────────────────────────────────────────────────


def _rows(n: int, seed: int = 0) -> list[dict]:
    rng = random.Random(seed)
    return [{"task": f"t{i}", "energy": float(rng.choice([0.0, 0.0, 0.0, 1.0])), "x": i} for i in range(n)]


def test_shuffled_copy_is_a_bijection_of_the_energies_and_keeps_rows() -> None:
    rows = _rows(40)
    out = shuffled_copy(rows, seed=3)
    assert len(out) == len(rows)
    assert Counter(r["energy"] for r in out) == Counter(r["energy"] for r in rows)
    for original, copied in zip(rows, out, strict=True):
        assert copied["task"] == original["task"]
        assert copied["x"] == original["x"]
    # It is a genuine permutation, not the identity, on rows with mixed labels.
    assert [r["energy"] for r in out] != [r["energy"] for r in rows]


def test_shuffled_copy_leaves_input_untouched() -> None:
    rows = _rows(20)
    snapshot = json.dumps(rows, sort_keys=True)
    out = shuffled_copy(rows, seed=1)
    assert json.dumps(rows, sort_keys=True) == snapshot
    out[0]["energy"] = 99.0
    assert rows[0]["energy"] != 99.0


def test_shuffled_copy_deterministic_per_seed_and_seed_sensitive() -> None:
    rows = _rows(30)
    a = [r["energy"] for r in shuffled_copy(rows, seed=7)]
    b = [r["energy"] for r in shuffled_copy(rows, seed=7)]
    c = [r["energy"] for r in shuffled_copy(rows, seed=8)]
    assert a == b
    assert a != c


def test_shuffled_copy_empty_raises() -> None:
    with pytest.raises(ValueError):
        shuffled_copy([], seed=0)


@settings(max_examples=60, deadline=None)
@given(
    st.lists(st.floats(min_value=0, max_value=100, allow_nan=False), min_size=1, max_size=25),
    st.integers(0, 10_000),
)
def test_shuffled_copy_multiset_preserved_hypothesis(energies: list[float], seed: int) -> None:
    rows = [{"energy": e, "i": i} for i, e in enumerate(energies)]
    out = shuffled_copy(rows, seed)
    assert sorted(r["energy"] for r in out) == sorted(energies)
    assert [r["i"] for r in out] == list(range(len(energies)))


# ── control_report ─────────────────────────────────────────────────────────


def test_control_report_flags_saturated_metric_and_keeps_informative_one() -> None:
    real = {"energy_accuracy": 1.0, "auroc": 0.8, "val_loss": 2.0}
    shuffled = {"energy_accuracy": 1.0, "auroc": 0.5, "val_loss": 2.5}
    report = control_report(real, shuffled, ["energy_accuracy", "auroc", "val_loss"])
    assert report["energy_accuracy"]["status"] == SATURATED
    assert report["energy_accuracy"]["informative"] is False
    assert report["energy_accuracy"]["delta"] == 0.0
    assert report["auroc"]["status"] == INFORMATIVE
    assert report["auroc"]["informative"] is True
    assert report["auroc"]["delta"] == pytest.approx(0.3)
    assert report["auroc"]["real"] == 0.8 and report["auroc"]["shuffled"] == 0.5
    assert report["val_loss"]["delta"] == pytest.approx(-0.5)
    assert report["saturated"] == ["energy_accuracy"]


def test_control_report_undefined_metric_is_not_counted_as_saturated() -> None:
    report = control_report({"auroc": None, "s": 0.2}, {"auroc": 0.5, "s": None}, ["auroc", "s", "missing"])
    for key in ("auroc", "s", "missing"):
        assert report[key]["status"] == UNDEFINED
        assert report[key]["delta"] is None
        assert report[key]["informative"] is False
    assert report["saturated"] == []


# ── trainer hook ───────────────────────────────────────────────────────────


def _write_dataset(path: Path, n_tasks: int, attempts: int, seed: int = 0) -> JEPADataset:
    """Tasks whose energy is a deterministic function of their embedding (learnable)."""
    rng = random.Random(seed)
    with open(path, "w") as f:
        for t in range(n_tasks):
            base = [rng.gauss(0.0, 1.0) for _ in range(D_INPUT)]
            for it in range(attempts):
                hidden = [b + 0.05 * rng.gauss(0.0, 1.0) for b in base]
                energy = 100.0 if sum(hidden) > 0.0 else 0.0
                f.write(json.dumps({
                    "task": f"task_{t}", "iteration": it, "hidden_state": hidden,
                    "energy": energy, "metadata": {"tests_total": 1},
                }) + "\n")
    return JEPADataset(path, hidden_dim=D_INPUT)


def _trainer(tmp_path: Path, init_seed: int = 0) -> JEPATrainer:
    torch.manual_seed(init_seed)
    model = JEPAWorldModel(D_INPUT, D_HIDDEN, D_LATENT)
    return JEPATrainer(
        model=model,
        config=JEPAConfig(latent_dim=D_LATENT, hidden_dim=D_HIDDEN),
        lr=1e-3,
        device="cpu",
        checkpoint_dir=tmp_path / "ckpt",
    )


def test_shuffled_label_dataset_permutes_state_energies_only(tmp_path: Path) -> None:
    ds = _write_dataset(tmp_path / "rows.jsonl", n_tasks=12, attempts=2)
    shuffled = shuffled_label_dataset(ds, seed=4)
    assert len(shuffled) == len(ds)
    assert shuffled.item_tasks == ds.item_tasks
    assert Counter(s.energy for s in shuffled.states) == Counter(s.energy for s in ds.states)
    assert [s.energy for s in shuffled.states] != [s.energy for s in ds.states]
    for (ctx_a, tgt_a, _), (ctx_b, tgt_b, _) in zip(ds, shuffled, strict=True):
        assert torch.equal(ctx_a, ctx_b)
        assert torch.equal(tgt_a, tgt_b)
    # The original dataset is untouched.
    assert [s.energy for s in ds.states] == [s.energy for s in JEPADataset(tmp_path / "rows.jsonl", hidden_dim=D_INPUT).states]


def test_train_default_path_is_unchanged_and_carries_no_control(tmp_path: Path) -> None:
    ds = _write_dataset(tmp_path / "rows.jsonl", n_tasks=12, attempts=2)
    summary = _trainer(tmp_path, init_seed=1).train(ds, epochs=3, batch_size=8, seed=5)
    train_ds, val_ds = train_val_split(ds, 0.2, 5)
    reference = _trainer(tmp_path / "ref", init_seed=1).fit(train_ds, val_ds, epochs=3, batch_size=8, seed=5)
    assert summary.final_train_loss == reference.final_train_loss
    assert summary.final_val_loss == reference.final_val_loss
    assert summary.history[-1]["energy_accuracy"] == reference.history[-1]["energy_accuracy"]
    assert all("label_control" not in record for record in summary.history)


def test_train_with_label_control_reports_both_arms_and_keeps_real_weights(tmp_path: Path) -> None:
    ds = _write_dataset(tmp_path / "rows.jsonl", n_tasks=12, attempts=2)
    plain = _trainer(tmp_path / "plain", init_seed=2)
    plain_summary = plain.train(ds, epochs=3, batch_size=8, seed=5)

    controlled = _trainer(tmp_path / "ctl", init_seed=2)
    summary = controlled.train(ds, epochs=3, batch_size=8, seed=5, label_control_seed=11)

    report = summary.history[-1]["label_control"]
    assert report["seed"] == 11
    assert set(LABEL_CONTROL_KEYS) <= set(report)
    for key in LABEL_CONTROL_KEYS:
        assert set(report[key]) == {"real", "shuffled", "delta", "informative", "status"}
        assert report[key]["status"] in {SATURATED, INFORMATIVE, UNDEFINED}
    assert report["energy_accuracy"]["real"] == plain_summary.history[-1]["energy_accuracy"]
    assert report["val_loss"]["real"] == plain_summary.final_val_loss
    assert report["val_items"] == len(train_val_split(ds, 0.2, 5)[1])
    assert 0 <= report["val_positives"] <= report["val_items"]
    # Only the last record carries the control.
    assert all("label_control" not in record for record in summary.history[:-1])
    # The real fit is what the trainer keeps: identical weights to the plain run.
    for (name, p_ctl), (_, p_plain) in zip(
        controlled.model.state_dict().items(), plain.model.state_dict().items(), strict=True
    ):
        assert torch.equal(p_ctl, p_plain), name
    # The control fit did not overwrite the real checkpoint: byte-equal to the plain run's.
    assert summary.checkpoint_path != plain_summary.checkpoint_path
    ckpt_ctl = torch.load(summary.checkpoint_path, map_location="cpu", weights_only=True)
    ckpt_plain = torch.load(plain_summary.checkpoint_path, map_location="cpu", weights_only=True)
    assert ckpt_ctl.keys() == ckpt_plain.keys()
    for name in ckpt_ctl:
        assert torch.equal(ckpt_ctl[name], ckpt_plain[name]), name


def test_train_with_label_control_shuffled_arm_differs_from_real_arm(tmp_path: Path) -> None:
    ds = _write_dataset(tmp_path / "rows.jsonl", n_tasks=20, attempts=2, seed=3)
    summary = _trainer(tmp_path, init_seed=3).train(ds, epochs=4, batch_size=8, seed=2, label_control_seed=9)
    report = summary.history[-1]["label_control"]
    # Training on permuted labels changes the fit: val_loss cannot be identical to the real arm.
    assert report["val_loss"]["real"] != report["val_loss"]["shuffled"]
    assert report["val_loss"]["status"] == INFORMATIVE
    # Whatever AUROC is, it is either undefined or a probability.
    for arm in ("real", "shuffled"):
        value = report["auroc"][arm]
        assert value is None or 0.0 <= value <= 1.0


def test_train_with_label_control_on_tiny_dataset_uses_full_set_for_both_arms(tmp_path: Path) -> None:
    ds = _write_dataset(tmp_path / "rows.jsonl", n_tasks=2, attempts=1)
    assert len(ds) == 2
    summary = _trainer(tmp_path).train(ds, epochs=2, batch_size=4, seed=1, label_control_seed=0)
    report = summary.history[-1]["label_control"]
    assert report["val_items"] == 2
    assert report["auroc"]["status"] in {UNDEFINED, INFORMATIVE, SATURATED}
    assert report["spearman"]["status"] == UNDEFINED  # < 3 items
