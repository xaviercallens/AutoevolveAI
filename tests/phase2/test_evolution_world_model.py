"""
Tests for the evolved JEPA world model: bounded predictions, loud dimension
errors, candidate ranking, label alignment of the energy head, and the
single-sample VICReg fix.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest
import torch
import torch.nn.functional as F
from torch.utils.data import Subset

from anse.jepa.dataset import HiddenDimMismatchError, JEPADataset
from anse.jepa.trainer import JEPATrainer
from anse.jepa.world_model import ContextEncoder, JEPAWorldModel, VICRegLoss, l2_normalise

D_IN, D_HID, D_LAT = 24, 16, 8


def _model(seed: int = 0, **kwargs: float) -> JEPAWorldModel:
    torch.manual_seed(seed)
    return JEPAWorldModel(d_input=D_IN, d_hidden=D_HID, d_latent=D_LAT, **kwargs)  # type: ignore[arg-type]


class TestPredictionBounds:
    @pytest.mark.parametrize("scale", [0.0, 1e-6, 1.0, 1e3, 1e6, -1e6])
    def test_scalar_prediction_stays_in_0_100(self, scale: float) -> None:
        model = _model()
        torch.manual_seed(1)
        prediction = model.predict_energy_scalar(torch.randn(D_IN) * scale)

        assert isinstance(prediction, float)
        assert 0.0 <= prediction <= 100.0

    def test_batch_prediction_matches_scalar_and_is_bounded(self) -> None:
        model = _model()
        torch.manual_seed(2)
        batch = torch.randn(9, D_IN) * 50.0
        predictions = model.predict_energy_batch(batch)

        assert predictions.shape == (9,)
        assert bool(((predictions >= 0.0) & (predictions <= 100.0)).all())
        assert predictions[4].item() == pytest.approx(
            model.predict_energy_scalar(batch[4]), abs=1e-4
        )

    def test_saturated_energy_head_cannot_leave_the_interval(self) -> None:
        model = _model()
        with torch.no_grad():
            model.energy_head.head[2].bias.fill_(1e4)  # type: ignore[union-attr, index]
        high = model.predict_energy_scalar(torch.ones(D_IN))
        with torch.no_grad():
            model.energy_head.head[2].bias.fill_(-1e4)  # type: ignore[union-attr, index]
        low = model.predict_energy_scalar(torch.ones(D_IN))

        assert high == pytest.approx(100.0)
        assert low == pytest.approx(0.0)

    def test_non_finite_hidden_state_is_rejected(self) -> None:
        model = _model()
        bad = torch.ones(D_IN)
        bad[5] = float("nan")
        with pytest.raises(ValueError, match="NaN or inf"):
            model.predict_energy_scalar(bad)
        bad[5] = float("inf")
        with pytest.raises(ValueError, match="NaN or inf"):
            model.predict_energy_batch(bad.unsqueeze(0))


class TestDimensionCheck:
    def test_prediction_with_wrong_dimension_raises(self) -> None:
        model = _model()
        with pytest.raises(
            HiddenDimMismatchError,
            match=f"dimension {D_IN + 1} but this world model was built for d_input={D_IN}",
        ):
            model.predict_energy_scalar(torch.zeros(D_IN + 1))
        with pytest.raises(HiddenDimMismatchError, match=f"dimension {D_IN - 1}"):
            model.predict_energy_batch(torch.zeros(3, D_IN - 1))

    def test_training_loss_and_latent_energy_check_both_sides(self) -> None:
        model = _model()
        good, bad = torch.randn(4, D_IN), torch.randn(4, D_IN * 2)
        with pytest.raises(HiddenDimMismatchError, match="h_target has dimension"):
            model.compute_training_loss(good, bad, torch.rand(4))
        with pytest.raises(HiddenDimMismatchError, match="h_context has dimension"):
            model.jepa_energy(bad, good)

    def test_non_positive_input_dimension_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="d_input must be the real embedding dimension"):
            JEPAWorldModel(d_input=0, d_hidden=D_HID, d_latent=D_LAT)
        assert _model().d_input == D_IN


class TestEnergyLabelAlignment:
    def test_transition_items_label_the_target_state(self) -> None:
        """energy_actual is the energy of h_target, so the head must read h_target's encoding."""
        model = _model().eval()
        torch.manual_seed(3)
        h_ctx, h_tgt, energy = torch.randn(6, D_IN), torch.randn(6, D_IN), torch.rand(6)
        _, metrics = model.compute_training_loss(h_ctx, h_tgt, energy)

        with torch.no_grad():
            on_target = F.mse_loss(model.energy_head(model.encode_context(h_tgt)), energy).item()  # type: ignore[misc]
            on_context = F.mse_loss(model.energy_head(model.encode_context(h_ctx)), energy).item()  # type: ignore[misc]
        assert metrics["energy_head_loss"] == pytest.approx(on_target, rel=1e-5)
        assert abs(on_target - on_context) > 1e-6, "fixture must distinguish the two readings"

    def test_energy_weight_scales_only_the_energy_term(self) -> None:
        h, energy = torch.randn(6, D_IN, generator=torch.Generator().manual_seed(4)), torch.rand(6)
        light, heavy = (
            _model(seed=5, energy_weight=1.0).eval(),
            _model(seed=5, energy_weight=11.0).eval(),
        )
        loss_light, m_light = light.compute_training_loss(h, h.clone(), energy)
        loss_heavy, m_heavy = heavy.compute_training_loss(h, h.clone(), energy)

        assert m_light["energy_head_loss"] == pytest.approx(m_heavy["energy_head_loss"], rel=1e-6)
        assert (loss_heavy - loss_light).item() == pytest.approx(
            10.0 * m_light["energy_head_loss"], rel=1e-4
        )


class TestRegularisation:
    def test_input_dropout_is_active_only_in_training(self) -> None:
        torch.manual_seed(6)
        encoder = ContextEncoder(D_IN, D_HID, D_LAT, dropout=0.5)
        h = torch.randn(5, D_IN)
        encoder.eval()
        with torch.no_grad():
            first, second = encoder(h), encoder(h)
        encoder.train()
        noisy_a, noisy_b = encoder(h), encoder(h)

        assert torch.equal(first, second)
        assert not torch.allclose(noisy_a, noisy_b)

    def test_invalid_dropout_is_rejected(self) -> None:
        with pytest.raises(ValueError, match=r"dropout must be in \[0, 1\)"):
            ContextEncoder(D_IN, D_HID, D_LAT, dropout=1.0)
        with pytest.raises(ValueError, match=r"dropout must be in \[0, 1\)"):
            ContextEncoder(D_IN, D_HID, D_LAT, dropout=-0.1)

    def test_vicreg_single_sample_is_zero_not_nan(self) -> None:
        loss, metrics = VICRegLoss()(torch.randn(1, D_LAT, requires_grad=True))

        assert loss.item() == 0.0
        assert metrics == {"std_loss": 0.0, "cov_loss": 0.0}
        two_loss, _ = VICRegLoss()(torch.zeros(2, D_LAT))
        assert two_loss.item() > 0.0, "a collapsed batch of two must still be penalised"

    def test_single_sample_batch_does_not_poison_the_weights(self) -> None:
        model = _model()
        optimiser = torch.optim.SGD([p for p in model.parameters() if p.requires_grad], lr=0.1)
        h = torch.randn(1, D_IN)
        loss, _ = model.compute_training_loss(h, h.clone(), torch.tensor([0.4]))
        loss.backward()
        optimiser.step()

        assert math.isfinite(loss.item())
        assert all(bool(torch.isfinite(p).all()) for p in model.parameters())


def _separable_traces(path: Path, n_tasks: int = 8) -> Path:
    """Failing attempts point along +axis0, passing attempts along -axis0 (plus task noise)."""
    generator = torch.Generator().manual_seed(11)
    lines = []
    for t in range(n_tasks):
        for iteration, energy in ((1, 80.0), (2, 0.0)):
            h = torch.randn(D_IN, generator=generator) * 0.2
            h[0] = 2.0 if energy > 0 else -2.0
            lines.append(
                json.dumps(
                    {
                        "task": f"task-{t}",
                        "iteration": iteration,
                        "energy": energy,
                        "code": f"v{t}-{iteration}",
                        "hidden_state": h.tolist(),
                    }
                )
            )
    path.write_text("\n".join(lines) + "\n")
    return path


class TestRankCandidates:
    def test_ranking_is_a_deterministic_permutation_sorted_by_predicted_energy(self) -> None:
        model = _model()
        candidates = torch.randn(7, D_IN, generator=torch.Generator().manual_seed(8))
        order = model.rank_candidates(candidates)
        energies = model.predict_energy_batch(candidates).tolist()

        assert sorted(order) == list(range(7))
        assert [energies[i] for i in order] == sorted(energies)
        assert order == model.rank_candidates(candidates)

    def test_ties_keep_candidate_order_and_empty_input_is_rejected(self) -> None:
        model = _model()
        same = torch.ones(3, D_IN)
        assert model.rank_candidates(same) == [0, 1, 2]
        with pytest.raises(ValueError, match="non-empty"):
            model.rank_candidates(torch.zeros(0, D_IN))

    def test_trained_model_ranks_the_passing_candidate_of_unseen_tasks_first(
        self, tmp_path: Path
    ) -> None:
        ds = JEPADataset(_separable_traces(tmp_path / "sep.jsonl"))
        held_out = {"task-6", "task-7"}
        train_idx = ds.indices_for_tasks({s.task for s in ds.states} - held_out)
        val_idx = ds.indices_for_tasks(held_out)
        model = _model(seed=9, energy_weight=10.0)
        trainer = JEPATrainer(model, lr=5e-3, checkpoint_dir=tmp_path / "ckpt")
        summary = trainer.fit(
            Subset(ds, train_idx),
            Subset(ds, val_idx),
            epochs=40,
            batch_size=8,
            select_best_on_val=False,
            validate_every=40,
        )

        assert summary.epochs_completed == 40
        assert not (tmp_path / "ckpt").exists(), (
            "select_best_on_val=False must not write checkpoints"
        )
        for task in held_out:
            states = [s for s in ds.states if s.task == task]
            order = model.rank_candidates(torch.stack([s.hidden for s in states]))
            assert states[order[0]].energy == 0.0, (
                f"intuition should run the passing attempt of {task} first"
            )


class TestFitCheckpointing:
    def test_fit_checkpoints_only_when_selection_is_allowed(self, tmp_path: Path) -> None:
        ds = JEPADataset(_separable_traces(tmp_path / "sep.jsonl", n_tasks=4))
        idx = list(range(len(ds)))
        trainer = JEPATrainer(_model(), checkpoint_dir=tmp_path / "select")
        summary = trainer.fit(Subset(ds, idx[:8]), Subset(ds, idx[8:]), epochs=2, batch_size=4)

        assert summary.checkpoint_path == str(tmp_path / "select" / "jepa_best.pt")
        assert (tmp_path / "select" / "jepa_best.pt").exists()
        assert len(summary.history) == 2

    def test_fit_rejects_bad_validate_every_and_handles_empty_train(self, tmp_path: Path) -> None:
        ds = JEPADataset(_separable_traces(tmp_path / "sep.jsonl", n_tasks=2))
        trainer = JEPATrainer(_model(), checkpoint_dir=tmp_path / "c")
        with pytest.raises(ValueError, match="validate_every must be >= 1"):
            trainer.fit(ds, ds, epochs=1, validate_every=0)
        summary = trainer.fit(Subset(ds, []), ds, epochs=3)

        assert summary.epochs_completed == 0
        assert summary.total_steps == 0


class TestInputNormalisationSkew:
    """JEPADataset trains on unit vectors; the agent loop predicts on raw embeddings (norm ~125)."""

    def test_l2_normalise_is_unit_idempotent_and_overflow_safe(self) -> None:
        torch.manual_seed(3)
        h = torch.randn(5, D_IN) * 125.0
        unit = l2_normalise(h)
        huge = l2_normalise(torch.full((D_IN,), 3.0e38))

        assert torch.allclose(unit.norm(dim=-1), torch.ones(5), atol=1e-5)
        assert torch.allclose(l2_normalise(unit), unit, atol=1e-6)
        assert bool(torch.isfinite(huge).all()) and huge.norm().item() == pytest.approx(
            1.0, abs=1e-5
        )
        assert torch.equal(l2_normalise(torch.zeros(D_IN)), torch.zeros(D_IN))

    def test_raw_embedding_predicts_exactly_like_its_normalised_form(self) -> None:
        model = _model(seed=4)
        torch.manual_seed(5)
        raw = torch.randn(7, D_IN) * 125.0
        unit = raw / raw.norm(dim=-1, keepdim=True)

        assert torch.allclose(
            model.predict_energy_batch(raw), model.predict_energy_batch(unit), atol=1e-4
        )
        assert model.predict_energy_scalar(raw[0]) == pytest.approx(
            model.predict_energy_scalar(unit[0]), abs=1e-4
        )
        assert torch.allclose(model.jepa_energy(raw, raw), model.jepa_energy(unit, unit), atol=1e-4)
        assert torch.allclose(model.encode_context(raw), model.encode_context(unit), atol=1e-5)

    def test_without_model_normalisation_the_same_inputs_disagree(self) -> None:
        """The skew is real: this is what the inference API did before the model owned the scaling."""
        model = _model(seed=4, normalise_input=False)
        torch.manual_seed(5)
        raw = torch.randn(7, D_IN) * 125.0
        unit = raw / raw.norm(dim=-1, keepdim=True)
        gap = (
            (model.predict_energy_batch(raw) - model.predict_energy_batch(unit)).abs().max().item()
        )

        assert model.normalise_input is False
        assert gap > 1e-2

    def test_model_trained_on_dataset_states_ranks_raw_scale_candidates_identically(
        self, tmp_path: Path
    ) -> None:
        ds = JEPADataset(_separable_traces(tmp_path / "sep.jsonl"))
        model = _model(seed=9, energy_weight=10.0)
        JEPATrainer(model, lr=5e-3, checkpoint_dir=tmp_path / "ckpt").fit(
            ds, ds, epochs=10, batch_size=8, select_best_on_val=False, validate_every=10
        )
        unit = torch.stack([s.hidden for s in ds.states])
        raw = unit * 125.0

        assert torch.allclose(unit.norm(dim=-1), torch.ones(len(ds.states)), atol=1e-5), (
            "dataset states are unit vectors"
        )
        assert torch.allclose(
            model.predict_energy_batch(raw), model.predict_energy_batch(unit), atol=1e-3
        )
        assert model.rank_candidates(raw) == model.rank_candidates(unit)

    def test_training_loss_is_scale_invariant(self) -> None:
        model = _model(seed=6)
        model.eval()  # no dropout noise between the two calls
        torch.manual_seed(7)
        h, energy = torch.randn(6, D_IN), torch.rand(6)
        loss_unit, _ = model.compute_training_loss(l2_normalise(h), l2_normalise(h), energy)
        loss_raw, metrics = model.compute_training_loss(h * 125.0, h * 125.0, energy)

        assert loss_raw.item() == pytest.approx(loss_unit.item(), rel=1e-4)
        assert metrics["energy_head_loss"] >= 0.0
