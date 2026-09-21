"""
Unit tests for Symbiotic Developer Reality Engine, 10,000x Speedup Accelerators, and Frontier Domains.
"""

from __future__ import annotations

from pathlib import Path

from anse.core.latent_dreamer import HippocampalReplayEngine, LatentDreamer
from anse.frontier.domains import AutonomousMathematician, CyberImmuneSwarm, SiliconArchitect
from harness_hook import (
    FallbackMockAgent,
    active_inference_copilot,
    evaluate_in_harness,
    shadow_mode_observe,
)


def test_evaluate_in_harness_success(tmp_path: Path) -> None:
    """Verify that a passing test command yields E = 0.0 with proof token."""
    target = tmp_path / "solution.py"
    code = "def add(a, b): return a + b\n"
    # Test command returns 0
    test_cmd = 'python -c "import sys; sys.exit(0)"'

    res = evaluate_in_harness(code, target, test_cmd)
    assert res.is_valid is True
    assert res.energy == 0.0
    assert res.proof_token is not None


def test_evaluate_in_harness_failure(tmp_path: Path) -> None:
    """Verify that a failing test command yields E = 100.0."""
    target = tmp_path / "solution.py"
    code = "def add(a, b): return a + b\n"
    test_cmd = 'python -c "import sys; sys.exit(1)"'

    res = evaluate_in_harness(code, target, test_cmd)
    assert res.is_valid is False
    assert res.energy == 100.0


def test_active_inference_copilot_flow(tmp_path: Path) -> None:
    """Verify that Active Co-Pilot converges and records golden DPO pair."""
    target = tmp_path / "solution.py"
    prompt = "Write solve(nums) that handles empty lists and sums first and last element."
    # Harness test script asserts that empty list returns 0 and [1, 2] returns 3
    test_cmd = f"python -c \"import sys; from pathlib import Path; import importlib.util; spec = importlib.util.spec_from_file_location('mod', r'{target}'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); assert m.solve([]) == 0; assert m.solve([1, 2]) == 3\""

    summary = active_inference_copilot(
        prompt=prompt,
        target_file=target,
        test_command=test_cmd,
        agent=FallbackMockAgent(),
        max_attempts=3,
    )
    assert summary.converged is True
    assert summary.attempts_used == 2
    assert summary.proof_token is not None
    assert summary.dpo_pair_recorded is True


def test_shadow_mode_observe() -> None:
    """Verify that shadow mode calculates surprise energy on human deviation."""
    ai_pred = "def compute(): return 42"
    human_code = "def compute(): return 42  # optimized"
    prompt = "Implement compute()"

    res = shadow_mode_observe(ai_pred, human_code, prompt, "engine.py")
    assert res["is_exact_match"] is False
    assert res["surprise_energy"] > 0.0
    assert res["dpo_pair_logged"] is True


def test_latent_dreamer_grpo_search() -> None:
    """Verify that Latent Dreamer scores 16 branches in latent space and computes GRPO advantage."""
    dreamer = LatentDreamer(latent_dim=32, num_branches=16)
    _ = dreamer.dream_and_search("warmup")
    res = dreamer.dream_and_search("Optimize tensor attention projection")

    assert res.num_candidates == 16
    assert res.latency_ms < 100.0  # Hyper-fast latent matrix evaluation
    assert res.speedup_vs_sandbox > 10.0
    assert res.best_thought.group_advantage >= 0.0
    assert res.best_thought.relative_weight >= 1.0


def test_hippocampal_replay_cycle(tmp_path: Path) -> None:
    """Verify that wake episodes are consolidated in REM sleep to prevent forgetting."""
    memory_file = tmp_path / "hip_test.jsonl"
    engine = HippocampalReplayEngine(memory_file=memory_file)

    engine.log_wake_episode("lean4", "Prove Fermat", "Applied omega tactic", 0.0, is_anchor=True)
    engine.log_wake_episode("cyber", "SQL injection exploit", "Used parameterized query", 0.0)

    sleep_res = engine.execute_sleep_cycle(batch_size=8)
    assert sleep_res["consolidated_traces"] == 2
    assert "lean4" in sleep_res["domains_covered"]
    assert sleep_res["catastrophic_forgetting_prevented"] is True


def test_frontier_mathematician() -> None:
    """Verify Lean 4 theorem prover evaluates proofs and catches sorry gaps."""
    math_prover = AutonomousMathematician()
    valid_proof = "theorem add_comm (n m : Nat) : n + m = m + n := by omega"
    gap_proof = "theorem hard_conjecture : P = NP := by sorry"

    res_valid = math_prover.evaluate_proof("add_comm", valid_proof)
    assert res_valid.is_valid is True
    assert res_valid.energy == 0.0

    res_gap = math_prover.evaluate_proof("hard_conjecture", gap_proof)
    assert res_gap.is_valid is False
    assert res_gap.energy == 1000.0


def test_frontier_cyber_swarm() -> None:
    """Verify cyber immune swarm handles red exploit against blue patch."""
    swarm = CyberImmuneSwarm()
    red_overflow = "A" * 500 + "\x90\x90\xeb\x04"
    blue_def = "def handle(data): if len(data) > 64: raise ValueError(); return data"

    res = swarm.run_engagement(red_overflow, blue_def)
    assert res.exploit_succeeded is False
    assert res.energy == 1000.0
    assert "DEFENSE_SECURE" in res.defense_status


def test_frontier_silicon_architect() -> None:
    """Verify silicon architect calculates latency and power metrics for Verilog AST."""
    silicon = SiliconArchitect()
    verilog = """
    module MacUnit (input clk, input [15:0] a, b, output reg [31:0] acc);
        always @(posedge clk) begin
            acc <= acc + (a * b);
        end
    endmodule
    """
    res = silicon.evaluate_verilog("MacUnit", verilog)
    assert res.is_synthesizable is True
    assert res.latency_ns > 0
    assert res.power_watts > 0
