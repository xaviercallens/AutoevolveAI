import pytest
from anse.symbolic.lean_mcts_prover import LeanMCTSProver, MCTSProofNode


def test_mcts_node_ucb1_scoring():
    parent = MCTSProofNode(tactic_sequence=[], visits=10, total_value=5.0)
    child1 = MCTSProofNode(tactic_sequence=["simp"], parent=parent, visits=2, total_value=2.0)
    child2 = MCTSProofNode(tactic_sequence=["linarith"], parent=parent, visits=5, total_value=1.0)

    # Q(child1) = 2.0 / 2 = 1.0; Q(child2) = 1.0 / 5 = 0.2
    assert child1.q_value == 1.0
    assert child2.q_value == 0.2
    assert child1.ucb1_score() > child2.ucb1_score()


def test_mcts_prover_prunes_epistemic_cheat():
    prover = LeanMCTSProver(work_dir="formal")
    # Evaluate a cheat tactic
    is_proven, is_cheat, value, goals, msg = prover.evaluate_tactic_sequence(
        theorem_name="test_cheat_pruning",
        theorem_signature=": 1 = 1",
        required_imports=["Mathlib.Data.Real.Basic"],
        tactic_sequence=["sorry"],
    )
    assert is_proven is False
    assert is_cheat is True
    assert value == -100.0
    assert "REJECT" in msg


def test_mcts_prover_successful_search():
    prover = LeanMCTSProver(work_dir="formal")
    res = prover.search(
        theorem_name="mcts_test_linarith",
        theorem_signature="(a b : ℝ) (h1 : a ≤ b) (h2 : b ≤ a) : a = b",
        required_imports=["Mathlib.Data.Real.Basic", "Mathlib.Tactic.Linarith"],
        max_iterations=10,
        max_depth=2,
    )
    assert res["success"] is True
    assert res["status"] == "VERIFIED_SOUND"
    assert "linarith" in res["proof_tactics"]
    assert res["terminal_q"] > 0.0
