"""
Unit tests for the local Code Critic SLM module.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from anse.config import CriticConfig
from anse.guard.critic import CodeCritic, CriticDecision


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
