"""
Unit and integration tests for Tree of Thoughts (ToT) Deliberate Problem Solving Engine
(Yao et al., NeurIPS 2023, arXiv:2305.10601).
Tests BFS beam search, DFS recursive search with backtracking, and physical energy evaluations.
"""

import pytest

from anse.orchestration.tree_of_thoughts import (
    ThoughtState,
    TreeOfThoughtsEngine,
)


def test_tot_state_initialization_and_serialization():
    state = ThoughtState(
        state_id="root.1",
        problem_input="Formal Banach Contraction Theorem",
        thought_history=["Formal Banach Contraction Theorem"],
        current_thought="Specification & Type Signatures",
        depth=1,
        value=0.88,
        energy_score=1.25,
        is_verified=True,
        proof_token="abcdef123456",
    )

    d = state.to_dict()
    assert d["state_id"] == "root.1"
    assert d["current_thought"] == "Specification & Type Signatures"
    assert d["value"] == 0.88
    assert d["energy_score"] == 1.25
    assert d["is_verified"] is True
    assert d["proof_token"] == "abcdef123456"
    assert "Specification" in state.path_str


def test_tot_dichotomic_proposals():
    tot = TreeOfThoughtsEngine()
    root = ThoughtState(
        state_id="root",
        problem_input="8D Kerr Geodesic Integrator and Symplectic Phase Space",
        depth=0,
    )

    proposals = tot.generate_dichotomic_proposals(root, k=2)
    assert len(proposals) == 2
    assert proposals[0].state_id == "root.1"
    assert proposals[1].state_id == "root.2"
    assert proposals[0].depth == 1
    assert proposals[1].depth == 1
    # Check that proposals reflect orthogonal branches
    assert "Invariants" in proposals[0].current_thought or "Continuous" in proposals[0].current_thought
    assert "Integrator" in proposals[1].current_thought or "Discrete" in proposals[1].current_thought


def test_tot_state_hardness_evaluation_clean_vs_stub():
    tot = TreeOfThoughtsEngine()
    
    # State with clean verifiable code
    clean_state = ThoughtState(
        state_id="s_clean",
        problem_input="Math utility function",
        current_thought="Implement verified math square",
    )
    clean_code = "def square(x):\n    return x * x\n"
    v_clean = tot.evaluate_state_hardness(
        clean_state,
        source_code=clean_code,
        custom_verifier=lambda s: (True, 0.5, {"status": "OK"}),
    )
    assert v_clean > 0.9
    assert clean_state.is_verified
    assert clean_state.proof_token is not None

    # State with stub code: E = 10^6, V(s) = 0.0
    stub_state = ThoughtState(
        state_id="s_stub",
        problem_input="Math utility function",
        current_thought="Implement verified math square",
    )
    stub_code = "def square(x):\n    pass  # TODO: implement later\n"
    v_stub = tot.evaluate_state_hardness(
        stub_state,
        source_code=stub_code,
    )
    assert v_stub == 0.0
    assert stub_state.energy_score == 1e6
    assert not stub_state.is_verified


def test_tot_bfs_search_frontier_and_pruning():
    """Tests Algorithm 1 ToT-BFS level-by-level beam pruning.

    Behavioral contract: the clean candidate (no stub) must win the beam over the
    stub candidate. The engine's sort tiebreaker (non-stub > stub when value equal)
    guarantees this is deterministic even when acceptance commands are unavailable.
    """
    tot = TreeOfThoughtsEngine()

    def mock_code_gen(s: ThoughtState) -> str:
        # Branch .1 has a stub, Branch .2 is clean
        if s.state_id.endswith(".1"):
            return "def f():\n    pass\n"
        return "def f():\n    return 42\n"

    best_state, tree_history = tot.search_bfs(
        problem_input="Formal Banach Contraction Theorem",
        step_limit=1,
        breadth_limit=1,
        candidate_k=2,
        code_generator=mock_code_gen,
    )

    assert len(tree_history) == 2  # Level 0 (root) and Level 1 (pruned frontier)
    assert len(tree_history[1]) == 1  # Beam width pruned to 1
    # Stub candidate (.1) was rejected by STUB_DETECTED; clean candidate (.2) won the beam
    assert best_state is not None
    assert best_state.state_id == "root.2", (
        f"Clean candidate root.2 must beat stub root.1, got {best_state.state_id}"
    )
    # Clean code must have higher value than zero (no stub → energy < 1e6)
    # OR at minimum: stub's value must be 0.0 (barrier penalty enforced)
    stub_in_history = [
        c for step in tree_history for c in step
        if c.state_id == "root.1"
    ]
    # root.1 was generated but pruned — it won't appear in tree_history[1]
    assert all(c.state_id != "root.1" for c in tree_history[1]), (
        "Stub root.1 must be pruned from the frontier"
    )


def test_tot_dfs_search_backtracking_on_stub():
    """Tests Algorithm 2 ToT-DFS depth-first traversal with backtracking when hitting a stub."""
    tot = TreeOfThoughtsEngine()

    def mock_code_gen(s: ThoughtState) -> str:
        # First candidate has stub, causing immediate backtrack
        if s.state_id == "root.1":
            return "def compute():\n    pass\n"
        return "def compute():\n    return 100\n"

    solution, visited = tot.search_dfs(
        problem_input="Systolic Array STA and Real SCM_RIGHTS Hot-Swap",
        step_limit=1,
        value_threshold=0.05,
        candidate_k=2,
        code_generator=mock_code_gen,
    )

    # Must find the verified sibling through backtracking
    assert solution is not None
    assert solution.state_id == "root.2"
    assert solution.is_verified
    assert solution.value > 0.0

    # Search history must record the pruning and backtrack event
    actions = [h.get("action") for h in tot.search_history]
    assert "PRUNED_AND_BACKTRACK" in actions
