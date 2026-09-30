"""
tests/autoresearch/test_policy_value_sandbox.py
================================================
Unit tests for AR-H5 Policy, Value, and Sandbox components.
All tests run on CPU without any GPU, model downloads, or ONNX file.
"""

import pytest
from anse.autoresearch.policy import MockQwenPolicy
from anse.autoresearch.value import MockLayaValue
from anse.autoresearch.sandbox import AR_H5_Sandbox
from anse.autoresearch.ar_h5_orchestrator import AR_H5_Orchestrator


def test_mock_policy_branches():
    """MockQwenPolicy returns exactly k branches of valid Python code."""
    policy = MockQwenPolicy()
    branches = policy.generate_branches("state", "prompt", k=3)
    assert len(branches) == 3
    # Branches should be valid Python (contain 'def' or 'print')
    for b in branches:
        assert isinstance(b, str)
        assert len(b) > 10


def test_mock_policy_exact_k():
    """MockQwenPolicy honours k=1 and k=5."""
    policy = MockQwenPolicy()
    assert len(policy.generate_branches("", "p", k=1)) == 1
    assert len(policy.generate_branches("", "p", k=5)) == 5


def test_mock_value_gate():
    """Gate polarity: noul >= tau_noul → PASS; noul < tau_noul → KILL.

    AR-H5 convention (matching anse/laya/model.py LayaDecision.is_blocked):
      is_blocked = noul < threshold  →  KILL
      NOT blocked = noul >= threshold  →  PASS
    """
    # noul=0.85 >= tau=0.3 → all branches PASS
    value_high = MockLayaValue(fixed_noul=0.85)
    nouls, passed = value_high.gate_batch(["text1", "text2"])
    assert nouls == [0.85, 0.85]
    assert passed == [True, True], "High-quality branches (noul=0.85) should PASS the gate"

    # noul=0.1 < tau=0.3 → all branches KILLED
    value_low = MockLayaValue(fixed_noul=0.1)
    nouls, passed = value_low.gate_batch(["text1", "text2"])
    assert nouls == [0.1, 0.1]
    assert passed == [False, False], "Low-quality branches (noul=0.1) should be KILLED"


def test_sandbox_python_clean():
    """Clean Python code → is_error=False, stdout captured."""
    sandbox = AR_H5_Sandbox()
    result = sandbox.run_python("print('hello')")
    assert not result.is_error
    assert "hello" in result.stdout


def test_sandbox_python_error():
    """Division by zero → is_error=True, error_type=runtime."""
    sandbox = AR_H5_Sandbox()
    result = sandbox.run_python("1/0")
    assert result.is_error
    assert result.error_type == "runtime"


def test_sandbox_python_timeout():
    """Long sleep with short timeout → is_error=True, error_type=timeout."""
    sandbox = AR_H5_Sandbox(python_timeout_s=0.2)
    result = sandbox.run_python("import time\ntime.sleep(5)")
    assert result.is_error
    assert result.error_type == "timeout"


def test_sandbox_extract_code_block():
    """Markdown code block extraction strips the triple-backtick fences."""
    sandbox = AR_H5_Sandbox()
    text = "Here is code:\n```python\nprint('extracted')\n```\nDone."
    code = sandbox._extract_code(text)
    assert code == "print('extracted')"


def test_orchestrator_mock():
    """Full orchestrator run with Mock components.

    policy branches are valid Python → sandbox passes → MCTS expands → success.
    Uses noul=0.85 (above tau=0.3) so Laya does NOT kill any branches.
    """
    policy = MockQwenPolicy()
    # noul=0.85 → all branches pass the gate
    value = MockLayaValue(fixed_noul=0.85)
    sandbox = AR_H5_Sandbox()
    orchestrator = AR_H5_Orchestrator(
        policy, value, sandbox, max_depth=2, k=2, timeout_s=10.0
    )

    res = orchestrator.run("Write a hello world function")

    assert res.success, (
        f"Orchestrator should succeed with valid branches and passing gate. "
        f"Got: nodes={res.tree_nodes}, killed={res.branches_killed}, "
        f"sandbox_errors={res.sandbox_errors}, answer={res.answer!r}"
    )
    assert res.laya_calls > 0, "Laya should have been called at least once"
    assert res.branches_killed == 0, "No branches should be killed with noul=0.85"
    assert res.tree_nodes > 1, "MCTS should have explored more than the root node"
