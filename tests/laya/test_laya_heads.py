"""
Unit tests for Laya decision heads (NoulHead, ChoiceHead, ScoreHead).
"""
import torch
import pytest

from anse.laya.heads import NoulHead, ChoiceHead, ScoreHead


def test_noul_head_forward():
    batch_size = 4
    hidden_size = 768
    head = NoulHead(hidden_size=hidden_size)
    x = torch.randn(batch_size, hidden_size)
    out = head(x)
    assert out.shape == (batch_size,)
    assert (out >= 0.0).all() and (out <= 1.0).all(), "Noul outputs must be probabilities in [0, 1]"


def test_choice_head_forward_and_predict():
    batch_size = 3
    hidden_size = 768
    classes = ["omega", "linarith", "ring", "simp"]
    head = ChoiceHead(hidden_size=hidden_size, num_classes=len(classes), class_names=classes)
    x = torch.randn(batch_size, hidden_size)
    logits = head(x)
    assert logits.shape == (batch_size, len(classes))
    preds = head.predict(x)
    assert len(preds) == batch_size
    for p in preds:
        assert p in classes


def test_score_head_forward():
    batch_size = 5
    hidden_size = 768
    head = ScoreHead(hidden_size=hidden_size)
    x = torch.randn(batch_size, hidden_size)
    out = head(x)
    assert out.shape == (batch_size,)
    assert (out >= 0.0).all(), "Score outputs must be non-negative (ReLU)"
