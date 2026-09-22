"""
Unit tests for the local Code Critic SLM module.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from anse.config import CriticConfig
from anse.guard.critic import CodeCritic, CriticDecision, NeuralEnergyCritic


def test_critic_disabled_by_default() -> None:
    config = CriticConfig(enabled=False)
    critic = CodeCritic(config)
    res = critic.evaluate("def foo(): return 42")
    assert res.decision == CriticDecision.SKIPPED
    assert res.energy_penalty == 0.0


def test_critic_accept_response() -> None:
    config = CriticConfig(enabled=True)
    critic = CodeCritic(config)

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"response": json.dumps({"status": "ACCEPT"})}
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.Client.post", return_value=mock_resp):
        res = critic.evaluate("def add(a, b): return a + b")
        assert res.decision == CriticDecision.ACCEPT
        assert res.is_accepted is True
        assert res.energy_penalty == 0.0


def test_critic_reject_response() -> None:
    config = CriticConfig(enabled=True, rejection_penalty=1e6)
    critic = CodeCritic(config)

    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "response": json.dumps({"status": "REJECT", "reason": "Stub 'pass' detected."})
    }
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.Client.post", return_value=mock_resp):
        res = critic.evaluate("def add(a, b): pass")
        assert res.decision == CriticDecision.REJECT
        assert res.is_accepted is False
        assert res.energy_penalty == 1e6
        assert "Stub 'pass'" in res.reason


def test_critic_service_down_fallback_open() -> None:
    config = CriticConfig(enabled=True, fallback_policy="allow_with_warning")
    critic = CodeCritic(config)

    with patch("httpx.Client.post", side_effect=ConnectionError("Ollama offline")):
        res = critic.evaluate("def add(a, b): return a + b")
        assert res.decision == CriticDecision.SKIPPED
        assert res.energy_penalty == 0.0
        assert "CRITIC_FALLBACK_OPEN" in res.reason


def test_critic_service_down_fallback_closed() -> None:
    config = CriticConfig(enabled=True, fallback_policy="deny", rejection_penalty=1e6)
    critic = CodeCritic(config)

    with patch("httpx.Client.post", side_effect=ConnectionError("Ollama offline")):
        res = critic.evaluate("def add(a, b): return a + b")
        assert res.decision == CriticDecision.REJECT
        assert res.energy_penalty == 1e6
        assert "CRITIC_UNAVAILABLE" in res.reason


def test_neural_energy_critic_in_memory() -> None:
    critic = NeuralEnergyCritic(model_path=None, device="cpu")
    reward = critic.predict_reward("Optimize array search", "def search(arr, val): return val in arr")
    assert isinstance(reward, float)

    res = critic.evaluate("def search(arr, val): return val in arr")
    assert res.is_accepted is True


def test_neural_energy_critic_threshold_rejection() -> None:
    critic = NeuralEnergyCritic(model_path=None, device="cpu")
    # Setting an impossibly high minimum threshold should reject
    res = critic.evaluate("def foo(): pass", min_acceptable_reward=1e9)
    assert res.decision == CriticDecision.REJECT
    assert "below threshold" in res.reason


def test_neural_energy_critic_trained_checkpoint_preference() -> None:
    checkpoint_path = Path("results/rl_nightly/anse_critic_final.pt")
    if not checkpoint_path.exists():
        return

    critic = NeuralEnergyCritic(model_path=checkpoint_path, device="cpu")
    r_working = critic.predict_reward(
        "Sort an array in ascending order",
        "def sort_array(nums):\n    return sorted(nums)\n"
    )
    r_stub = critic.predict_reward(
        "Sort an array in ascending order",
        "def sort_array(nums):\n    pass\n"
    )
    assert r_working > r_stub, f"Working code reward {r_working} must exceed stub reward {r_stub}"

