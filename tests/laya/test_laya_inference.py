"""
Tests for LayaInference engine.
"""
import pytest
from anse.laya.inference import LayaInference
from anse.laya.model import LayaDecision


def test_laya_inference_predict():
    engine = LayaInference()
    decision = engine.predict("def add(a, b): return a + b")
    assert isinstance(decision, LayaDecision)
    assert 0.0 <= decision.noul <= 1.0
    assert decision.choice in engine.model.choice_classes
    assert decision.score >= 0.0
    assert decision.latency_ms > 0.0


def test_laya_inference_benchmark():
    engine = LayaInference()
    stats = engine.benchmark(n_warmup=1, n_measure=3)
    assert "p50_ms" in stats
    assert "p95_ms" in stats
    assert "raw_latencies_ms" in stats
    assert len(stats["raw_latencies_ms"]) == 3
