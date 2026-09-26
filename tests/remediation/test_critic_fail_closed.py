"""Test that the MCP critic guard fails closed on exceptions."""

from unittest.mock import MagicMock, patch

import pytest


def test_critic_raises_exception_returns_accepted_false() -> None:
    """When CodeCritic raises an exception, the tool returns accepted: False with error field."""
    with patch("anse.guard.critic.CodeCritic") as mock_critic_class:
        mock_instance = MagicMock()
        mock_instance.evaluate.side_effect = RuntimeError("Critic connection failed")
        mock_critic_class.return_value = mock_instance

        from mcp_guard_server import evaluate_code_with_critic

        result = evaluate_code_with_critic(code="x = 1", task_context="")

        assert result["accepted"] is False
        assert "error" in result
        assert "RuntimeError" in result["error"]


def test_critic_rejection_preserves_reason() -> None:
    """When CodeCritic rejects code, the original reason is preserved, not replaced."""
    with patch("anse.guard.critic.CodeCritic") as mock_critic_class:
        mock_response = MagicMock()
        mock_response.decision.value = "REJECTED"
        mock_response.is_accepted = False
        mock_response.reason = "Detected stub function"
        mock_response.energy_penalty = 50.0
        mock_response.duration_ms = 125.5

        mock_instance = MagicMock()
        mock_instance.evaluate.return_value = mock_response
        mock_critic_class.return_value = mock_instance

        from mcp_guard_server import evaluate_code_with_critic

        result = evaluate_code_with_critic(code="def foo(): pass", task_context="")

        assert result["accepted"] is False
        assert result["reason"] == "Detected stub function"
        assert "error" not in result


def test_critic_accepts_returns_accepted_true_no_error() -> None:
    """When CodeCritic accepts code, the tool returns accepted: True without error field."""
    with patch("anse.guard.critic.CodeCritic") as mock_critic_class:
        mock_response = MagicMock()
        mock_response.decision.value = "ACCEPTED"
        mock_response.is_accepted = True
        mock_response.reason = "Code quality acceptable"
        mock_response.energy_penalty = 0.0
        mock_response.duration_ms = 95.3

        mock_instance = MagicMock()
        mock_instance.evaluate.return_value = mock_response
        mock_critic_class.return_value = mock_instance

        from mcp_guard_server import evaluate_code_with_critic

        result = evaluate_code_with_critic(code="x = 1 + 1", task_context="")

        assert result["accepted"] is True
        assert "error" not in result
        assert result["reason"] == "Code quality acceptable"
