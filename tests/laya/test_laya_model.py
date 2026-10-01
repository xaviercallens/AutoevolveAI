"""
Unit tests for LayaCodingCompanion model.
"""
import pytest
import torch

from anse.laya.model import LayaCodingCompanion, LayaDecision


def test_laya_model_init_lightweight():
    model = LayaCodingCompanion(load_pretrained=False)
    assert model.encoder is None
    assert model.noul_head is not None
    assert model.choice_head is not None
    assert model.score_head is not None
    assert hasattr(model, 'quality_gate_head')


def test_laya_model_forward_lightweight():
    model = LayaCodingCompanion(load_pretrained=False)
    input_ids = torch.randint(0, 1000, (2, 16))
    attention_mask = torch.ones((2, 16))
    
    noul, choice, score, gate = model(input_ids, attention_mask)
    assert noul.shape == (2,)
    assert choice.shape[0] == 2
    assert choice.shape[1] == len(model.choice_classes)
    assert score.shape == (2,)
    assert gate.shape == (2,)


def test_laya_decision_dataclass():
    decision = LayaDecision(
        noul=0.15,
        choice="vulnerable",
        choice_probs={"vulnerable": 0.95, "safe": 0.05},
        score=25.0,
        latency_ms=12.5,
        barrier_penalty=1e6,
    )
    assert decision.is_blocked(threshold=0.3) is True
    assert decision.anse_energy() >= 1e6
