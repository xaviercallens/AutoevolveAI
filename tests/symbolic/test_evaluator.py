import pytest
from anse.symbolic.evaluator import EnergyResult, EnergyCategory
from anse.symbolic.sandbox import ExecutionResult

def test_difficulty_tier():
    # Trivial: E == 0.0
    res = EnergyResult(score=0.0, category=EnergyCategory.PERFECT, pain_signal="", execution=ExecutionResult(returncode=0, stdout="", stderr="", duration_ms=10.0, timed_out=False, tier_used=1, dangerous_imports=False))
    assert res.difficulty_tier() == "trivial"

    # Fixable: 0.0 < E < 20.0
    res.score = 15.0
    assert res.difficulty_tier() == "fixable"

    # Hard: 20.0 <= E < 50.0
    res.score = 30.0
    assert res.difficulty_tier() == "hard"

    res.score = 49.9
    assert res.difficulty_tier() == "hard"

    # PhD: E >= 50.0
    res.score = 50.0
    assert res.difficulty_tier() == "phd"

    res.score = 100.0
    assert res.difficulty_tier() == "phd"
