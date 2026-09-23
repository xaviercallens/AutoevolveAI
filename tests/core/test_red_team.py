import pytest
from unittest.mock import patch
from anse.core.red_team import DeepThinkAuditor

class MockExtractor:
    def __init__(self, reject: bool = False):
        self.reject = reject
        self.call_count = 0
        
    def extract(self, prompt: str, system_prompt: str, temperature: float = 0.2):
        self.call_count += 1
        if "epistemic" in system_prompt.lower():
            if self.reject:
                return "<think>Junk values found.</think> missing bounds.", None
            return "<think>All logical steps check out.</think> It's clean.", None
        if "physics" in system_prompt.lower():
            if self.reject:
                return "<think>Needs fuzzing, tautology.</think> Fuzzing required.", None
            return "<think>Physics constraints respected.</think> No anomalies.", None
        return "", None

@patch("anse.core.red_team.call_local_r1_model")
def test_deep_think_auditor_accepts(mock_call_local):
    """Verify that the deep think auditor passes through a valid solution."""
    mock_call_local.return_value = "<think>Valid topological structure detected.</think> PASS"
    mock_extractor = MockExtractor(reject=False)
    auditor = DeepThinkAuditor(extractor=mock_extractor)
    
    result = auditor.invoke({
        "math_problem": "Test Problem",
        "lean_code": "def valid(): pass",
        "python_metrics": {"error": 0.0, "latency_ms": 1.0},
        "thoughts": []
    })
    
    assert "ACCEPT" in result['verdict']
    assert mock_extractor.call_count == 1
    mock_call_local.assert_called_once()

@patch("anse.core.red_team.call_local_r1_model")
def test_deep_think_auditor_rejects(mock_call_local):
    """Verify that the deep think auditor correctly rejects impossible code."""
    mock_call_local.side_effect = [
        "<think>Algebraic tautology found.</think> REJECT",
        "<think>Valid topological structure detected.</think> PASS"
    ]
    mock_extractor = MockExtractor(reject=True)
    auditor = DeepThinkAuditor(extractor=mock_extractor)
    
    result = auditor.invoke({
        "math_problem": "Test Problem",
        "lean_code": "def invalid(): pass",
        "python_metrics": {"error": 0.0, "latency_ms": 1.0},
        "thoughts": []
    })
    
    assert "ACCEPT" in result.get('verdict', '') or "REJECT" in result.get('verdict', '')
    # The graph will backtrack to coder, coder changes status to RETRY, then epistemic returns PASS.
    # Then it goes to physics which rejects it (mock_extractor(reject=True)), so final judgment is REJECT.
    assert "REJECT" in result['verdict']
    assert mock_call_local.call_count == 2
