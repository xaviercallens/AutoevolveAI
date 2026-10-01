"""
End-to-End Integration tests for Laya with ANSE dispatcher.
"""
import pytest
from anse.laya.integration import LayaANSEDispatcher, ANSERole, ANSEAction


def test_anse_dispatcher_dispatch():
    dispatcher = LayaANSEDispatcher()
    action = dispatcher.dispatch("def compute_matrix_product(A, B):\n    return A @ B")
    assert isinstance(action, ANSEAction)
    assert isinstance(action.blocked, bool)
    assert isinstance(action.role, ANSERole)
    assert action.energy >= 0.0
    assert len(action.reasoning) > 0


def test_anse_dispatcher_blocked_energy():
    dispatcher = LayaANSEDispatcher(noul_threshold=0.99) # Force gating on standard sample
    action = dispatcher.dispatch("def stub(): pass")
    # If blocked, energy should be at maximum barrier 1e6
    if action.blocked:
        assert action.energy >= 1e6
        assert "BLOCKED" in action.reasoning
    else:
        assert action.energy < 1e6
