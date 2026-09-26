"""Test that anse.core.red_team refuses to audit rather than fabricate a verdict."""

from unittest.mock import MagicMock, patch

import pytest
import requests

import anse.core.red_team as red_team
from anse.core.red_team import (
    LeanScanUnparseableError,
    SimulationRefusedError,
    call_local_r1_model,
    scan_lean_declaration_heuristically,
)


def test_call_local_r1_model_refuses_when_ollama_unreachable() -> None:
    """A ConnectionError from the Ollama client must raise SimulationRefusedError naming the endpoint."""
    with patch("anse.core.red_team.requests.post", side_effect=requests.exceptions.ConnectionError("boom")):
        with pytest.raises(SimulationRefusedError, match=red_team.OLLAMA_GENERATE_URL) as exc_info:
            call_local_r1_model("some prompt")
    assert "boom" in str(exc_info.value)


def test_call_local_r1_model_refuses_on_non_200_response() -> None:
    """A non-200 HTTP response must also raise SimulationRefusedError, not a fabricated PASS/REJECT string."""
    mock_response = MagicMock()
    mock_response.status_code = 503
    with patch("anse.core.red_team.requests.post", return_value=mock_response):
        with pytest.raises(SimulationRefusedError, match=red_team.OLLAMA_GENERATE_URL):
            call_local_r1_model("some prompt")


def test_mock_coder_auto_correction_removed_from_module() -> None:
    """The fabricated 'auto-correction' node must not exist anywhere on the module."""
    assert not hasattr(red_team, "mock_coder_auto_correction")
    assert not hasattr(red_team.DeepThinkAuditor, "mock_coder_auto_correction")


def test_scan_lean_declaration_heuristically_raises_on_unparseable_input() -> None:
    """Input with no recognizable Lean declaration must raise, not return a fake AST-shaped dict/string."""
    with pytest.raises(LeanScanUnparseableError, match="no recognizable Lean declaration"):
        scan_lean_declaration_heuristically("this is not lean code at all, just prose")

    with pytest.raises(LeanScanUnparseableError, match="empty"):
        scan_lean_declaration_heuristically("   ")


def test_scan_lean_declaration_heuristically_scans_real_declaration() -> None:
    """A real theorem declaration still produces the heuristic scan string, not an AST."""
    result = scan_lean_declaration_heuristically("theorem foo : 1 + 1 = 2 := by ring")
    assert result.startswith("HEURISTIC_SCAN:")
    assert "AST" not in result


def test_final_judgment_reports_confidence_and_marks_heuristic() -> None:
    """final_judgment must return a confidence field, and its docstring must flag the logic as heuristic."""
    auditor = red_team.DeepThinkAuditor.__new__(red_team.DeepThinkAuditor)
    state: dict = {"thoughts": ["<think>cheating detected</think> reject", "<think>fine</think> ok"]}

    result = auditor.final_judgment(state)

    assert "REJECT" in result["verdict"]
    assert "confidence" in result
    assert 0.0 < result["confidence"] <= 1.0
    assert "heuristic" in red_team.DeepThinkAuditor.final_judgment.__doc__.lower()
