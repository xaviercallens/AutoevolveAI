"""Tests for MCP guard: critic must fail closed on exception."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def critic_exception_patch():
    """Patch CodeCritic to raise RuntimeError."""
    with patch("anse.guard.critic.CodeCritic") as mock_critic_class:
        mock_instance = MagicMock()
        mock_instance.evaluate.side_effect = RuntimeError("Ollama unreachable")
        mock_critic_class.return_value = mock_instance
        yield mock_critic_class


@pytest.fixture
def critic_rejection_patch():
    """Patch CodeCritic to return a rejecting verdict."""
    from anse.guard.critic import CriticDecision, CriticResult

    with patch("anse.guard.critic.CodeCritic") as mock_critic_class:
        mock_instance = MagicMock()
        mock_instance.evaluate.return_value = CriticResult(
            decision=CriticDecision.REJECT,
            reason="Code contains stubs",
            energy_penalty=10.0,
            duration_ms=5.0,
        )
        mock_critic_class.return_value = mock_instance
        yield mock_critic_class


@pytest.fixture
def critic_accept_patch():
    """Patch CodeCritic to accept code."""
    from anse.guard.critic import CriticDecision, CriticResult

    with patch("anse.guard.critic.CodeCritic") as mock_critic_class:
        mock_instance = MagicMock()
        mock_instance.evaluate.return_value = CriticResult(
            decision=CriticDecision.ACCEPT,
            reason="Code passes all checks",
            energy_penalty=0.0,
            duration_ms=3.0,
        )
        mock_critic_class.return_value = mock_instance
        yield mock_critic_class


def test_critic_fail_closed_on_exception(critic_exception_patch) -> None:
    """Patch CodeCritic to raise RuntimeError; assert tool returns accepted False."""
    from mcp_guard_server import evaluate_code_with_critic

    result = evaluate_code_with_critic(code="def foo(): pass", task_context="test")

    assert result["accepted"] is False
    assert "error" in result
    assert result["error"] == "RuntimeError"


def test_critic_fail_closed_reason_survives_rejection(critic_rejection_patch) -> None:
    """Patch CodeCritic to return rejecting verdict; reason survives."""
    from mcp_guard_server import evaluate_code_with_critic

    result = evaluate_code_with_critic(code="def foo(): pass", task_context="test")

    assert result["accepted"] is False
    assert result["reason"] == "Code contains stubs"
    assert "error" not in result


def test_critic_accept_no_error_key(critic_accept_patch) -> None:
    """Patch CodeCritic to accept; assert accepted True and no error key."""
    from mcp_guard_server import evaluate_code_with_critic

    result = evaluate_code_with_critic(code="def foo(): pass", task_context="test")

    assert result["accepted"] is True
    assert "error" not in result
    assert result["reason"] == "Code passes all checks"
