import pytest
from anse.symbolic.lean_rag_dojo import (
    MathlibPremiseRetriever,
    LeanCompilerREPL,
    InteractiveFormalProver
)

def test_mathlib_premise_retriever_fallback():
    retriever = MathlibPremiseRetriever(db_path="./test_mathlib_rag_db")
    context = retriever.retrieve_mathlib_premises("Dense (⋂ n, U n)")
    assert "USEFUL MATHLIB PREMISES" in context
    assert "import" in context

def test_lean_compiler_repl_success():
    repl = LeanCompilerREPL(work_dir="formal")
    imports = ["Mathlib.Data.Real.Basic", "Mathlib.Tactic.Linarith"]
    code = "theorem test_linarith (a b : ℝ) (h1 : a ≤ b) (h2 : b ≤ a) : a = b := by\n  linarith\n"
    success, msg, goals = repl.run_proof_attempt(imports, code)
    assert success is True
    assert len(goals) == 0

def test_lean_compiler_repl_failure_gives_goals():
    repl = LeanCompilerREPL(work_dir="formal")
    imports = ["Mathlib.Data.Real.Basic"]
    # Missing linarith tactic import and step
    code = "theorem test_fail (a b : ℝ) (h1 : a ≤ b) (h2 : b ≤ a) : a = b := by\n  skip\n"
    success, msg, goals = repl.run_proof_attempt(imports, code)
    assert success is False
    assert len(goals) > 0 or "unsolved goals" in msg

def test_interactive_prover_anti_cheat():
    prover = InteractiveFormalProver()
    res = prover.prove_step_by_step(
        theorem_name="cheat_thm",
        theorem_signature=": 1 = 1",
        candidate_tactics=["sorry"],
        required_imports=["Mathlib.Data.Real.Basic"]
    )
    assert res["success"] is False
    assert res["is_epistemic_cheat"] is True
    assert "REJECT" in res["status"]
