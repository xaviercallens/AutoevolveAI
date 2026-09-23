import pytest
from anse.core.red_team import AdversarialRedTeam

def test_adversarial_red_team_accepts():
    """Verify that the red team passes through a valid solution."""
    call_count = 0
    def mock_llm(prompt: str, sys_prompt: str, temp: float) -> str:
        nonlocal call_count
        call_count += 1
        if "physics" in sys_prompt.lower():
            return "No physical anomalies found."
        if "epistemic" in sys_prompt.lower():
            return "No logical contradictions found."
        if "judge" in sys_prompt.lower():
            return "ACCEPT. The code is logically and physically sound."
        return ""
    
    red_team = AdversarialRedTeam(mock_llm)
    verdict = red_team.evaluate("def simple_func(): return 1")
    
    assert "ACCEPT" in verdict
    assert call_count == 3


def test_adversarial_red_team_rejects():
    """Verify that the red team correctly rejects impossible code based on hidden thoughts."""
    def mock_llm(prompt: str, sys_prompt: str, temp: float) -> str:
        if "physics" in sys_prompt.lower():
            return "O(N^2) operation is claimed to run in O(1) time."
        if "epistemic" in sys_prompt.lower():
            return "Contradiction: claims exact proof but uses floats."
        if "judge" in sys_prompt.lower():
            return "REJECT. Code violates physical and logical bounds."
        return ""
    
    red_team = AdversarialRedTeam(mock_llm)
    verdict = red_team.evaluate("def magic_sort(): pass")
    
    assert "REJECT" in verdict
