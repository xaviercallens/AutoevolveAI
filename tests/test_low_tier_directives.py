"""
Unit and integration tests for Low-Tier Model Hardness Directives (D1 - D8).

Verifies the autopoietic self-evolution directives for sub-3B models
(Qwen2.5-Coder-1.5B) under the ANSE Energy framework.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from anse.config import (
    ANSEConfig,
    ModelConfig,
    PromptBudgetPolicy,
    get_model_tier,
    is_small_model,
)
from anse.core.agent_loop import (
    PAIN_PROMPT_TEMPLATE_COMPRESSED,
    AgentLoop,
    compress_failing_code,
)
from anse.core.encoder import HiddenStateExtractor, HiddenStateRecord
from anse.memory.harvester import Harvester, LoopTrace
from anse.memory.lessons import (
    Lesson,
    LessonMemory,
    extract_skeleton,
    format_lessons,
    format_lessons_skeleton,
)
from anse.symbolic.evaluator import EnergyCategory, EnergyEvaluator, EnergyResult
from anse.symbolic.hidden_tests import TestReport
from anse.symbolic.sandbox import ExecutionResult, SandboxExecutor
from antigravity_harness.rl_pipeline.trace_extractor import TraceExtractor


# ─── Directive D1: Context-Budget-Aware Prompt Compression ───────────────────


def test_d1_model_tier_heuristics() -> None:
    assert is_small_model("qwen2.5-coder:1.5b") is True
    assert is_small_model("Qwen/Qwen2.5-Coder-1.5B") is True
    assert is_small_model("qwen2.5-coder:0.5b") is True
    assert is_small_model("qwen2.5-coder:3b") is True
    assert is_small_model("tinyllama:1.1b") is True
    assert is_small_model("qwen2.5-coder:7b") is False
    assert is_small_model("Qwen/Qwen2.5-Coder-7B-Instruct") is False
    assert is_small_model("deepseek-coder:33b") is False

    assert get_model_tier("qwen2.5-coder:1.5b") == "<=3B"
    assert get_model_tier("qwen2.5-coder:7b") == ">3B"


def test_d1_prompt_budget_policy_for_model() -> None:
    small_policy = PromptBudgetPolicy.for_model("qwen2.5-coder:1.5b")
    assert small_policy.max_code_chars == 200
    assert small_policy.max_stderr_chars == 200
    assert small_policy.max_stdout_chars == 0
    assert small_policy.omit_stdout is True
    assert small_policy.compress_code is True
    assert small_policy.energy_monotonic_pruning is True
    assert small_policy.difficulty_triage is True

    large_policy = PromptBudgetPolicy.for_model("qwen2.5-coder:7b")
    assert large_policy.max_code_chars == 4000
    assert large_policy.max_stderr_chars == 1000
    assert large_policy.max_stdout_chars == 1000
    assert large_policy.omit_stdout is False
    assert large_policy.compress_code is False
    assert large_policy.energy_monotonic_pruning is False
    assert large_policy.difficulty_triage is False


def test_d1_compress_failing_code() -> None:
    code = (
        "def compute_fibonacci(n: int) -> int:\n"
        '    """Calculate n-th fibonacci number with memoization."""\n'
        "    if n <= 1:\n"
        "        return n\n"
        "    a, b = 0, 1\n"
        "    for _ in range(2, n + 1):\n"
        "        a, b = b, a + b\n"
        "    return b\n"
    )
    compressed = compress_failing_code(code, max_chars=150)
    assert "def compute_fibonacci(n: int) -> int:" in compressed
    assert "Calculate n-th fibonacci" in compressed
    assert "for _ in range" not in compressed  # implementation details pruned


def test_d1_compressed_pain_prompt_template() -> None:
    prompt = PAIN_PROMPT_TEMPLATE_COMPRESSED.format(
        task="Sort a list",
        energy=50.0,
        category="test_failure",
        test_feedback="AssertionError: [1, 2] != [2, 1]\n",
        code="def sort_list(lst):\n    ...",
        returncode=1,
        stderr="Traceback ...",
    )
    assert "TASK: Sort a list" in prompt
    assert "Failing code summary:" in prompt
    assert "Stdout:" not in prompt  # stdout strictly omitted


# ─── Directive D2: Abolish Adaptive Retry for Sub-3B Models ──────────────────


def test_d2_adaptive_retry_capacity_gating() -> None:
    cfg_small = ANSEConfig(model=ModelConfig(api_model_name="qwen2.5-coder:1.5b"))
    loop_small = AgentLoop(config=cfg_small, adaptive_retry=True)
    assert loop_small.adaptive_retry is False  # disabled for <=3B

    loop_forced = AgentLoop(config=cfg_small, adaptive_retry=True, force_adaptive=True)
    assert loop_forced.adaptive_retry is True  # forced override respected

    cfg_large = ANSEConfig(model=ModelConfig(api_model_name="qwen2.5-coder:7b"))
    loop_large = AgentLoop(config=cfg_large, adaptive_retry=True)
    assert loop_large.adaptive_retry is True  # preserved for >=7B


# ─── Directive D3: Energy-Monotonic Retry Budget Pruning ──────────────────────


def _make_mock_extractor(responses: list[str]) -> MagicMock:
    extractor = MagicMock(spec=HiddenStateExtractor)
    rec = MagicMock(spec=HiddenStateRecord)
    rec.model_id = "test-model"
    rec.to_embedding.return_value = [0.0] * 16

    call_count = 0

    def extract_side_effect(*args, **kwargs):
        nonlocal call_count
        resp = responses[min(call_count, len(responses) - 1)]
        call_count += 1
        return resp, rec

    extractor.extract.side_effect = extract_side_effect
    return extractor


def _make_mock_sandbox(returncode: int = 1, stderr: str = "SyntaxError") -> MagicMock:
    sandbox = MagicMock(spec=SandboxExecutor)
    sandbox._cfg = MagicMock(timeout_seconds=5.0)
    sandbox.execute.return_value = ExecutionResult(
        stdout="",
        stderr=stderr,
        returncode=returncode,
        timed_out=False,
        duration_ms=5.0,
        tier_used=1,
    )
    return sandbox


def test_d3_early_stop_on_catastrophic_e1(tmp_path: Path) -> None:
    cfg = ANSEConfig(model=ModelConfig(api_model_name="qwen2.5-coder:1.5b"))
    extractor = _make_mock_extractor(["```python\ndef broken():\n    return 1\n```"])
    sandbox = _make_mock_sandbox(returncode=1, stderr="SyntaxError: invalid syntax")

    # Evaluator returning E > 60 on iteration 1
    evaluator = MagicMock(spec=EnergyEvaluator)
    res_e1 = EnergyResult(
        score=100.0,
        category=EnergyCategory.SYNTAX_ERROR,
        pain_signal="Syntax error",
        execution=ExecutionResult("", "SyntaxError", 1, False, 5.0, 1),
    )
    evaluator.evaluate.return_value = res_e1

    loop = AgentLoop(
        extractor=extractor,
        sandbox=sandbox,
        evaluator=evaluator,
        config=cfg,
        max_retries=3,
    )

    summary = loop.run("test task")
    assert summary.iterations == 1  # stopped after iteration 1, did not waste retries 2 & 3
    assert summary.traces[0].metadata.get("early_stop_reason") == "E1_catastrophic_failure"


def test_d3_early_stop_on_diverging_e2(tmp_path: Path) -> None:
    cfg = ANSEConfig(model=ModelConfig(api_model_name="qwen2.5-coder:1.5b"))
    extractor = _make_mock_extractor(
        [
            "```python\ndef attempt1():\n    return 1\n```",
            "```python\ndef attempt2():\n    return 2\n```",
        ]
    )
    sandbox = _make_mock_sandbox(returncode=1)

    evaluator = MagicMock(spec=EnergyEvaluator)
    res_e1 = EnergyResult(
        score=35.0,
        category=EnergyCategory.TEST_FAILURE,
        pain_signal="Assert error",
        execution=ExecutionResult("", "", 1, False, 5.0, 1),
    )
    res_e2 = EnergyResult(
        score=55.0,  # Diverged: E2 > E1 and E2 > 40
        category=EnergyCategory.RUNTIME_ERROR,
        pain_signal="Runtime error",
        execution=ExecutionResult("", "", 1, False, 5.0, 1),
    )
    evaluator.evaluate.side_effect = [res_e1, res_e2]

    loop = AgentLoop(
        extractor=extractor,
        sandbox=sandbox,
        evaluator=evaluator,
        config=cfg,
        max_retries=3,
    )

    summary = loop.run("test task")
    assert summary.iterations == 2  # stopped after iteration 2, skipped iteration 3
    assert summary.traces[1].metadata.get("early_stop_reason") == "E2_diverging_energy"


# ─── Directive D4: Skeleton-Only Lesson Injection for Small Models ───────────


def test_d4_skeleton_lesson_formatting() -> None:
    code = (
        "def rotate_list(lst: list, k: int) -> list:\n"
        '    """Rotate a list to the right by k steps."""\n'
        "    k %= len(lst)\n"
        "    return lst[-k:] + lst[:-k]\n"
    )
    lesson = Lesson(task="Rotate a list", code=code, failure="IndexError: out of range")
    lessons = [(0.85, lesson)]

    full = format_lessons(lessons)
    assert "return lst[-k:] + lst[:-k]" in full  # full solution present

    skeleton = format_lessons_skeleton(lessons)
    assert "def rotate_list(lst: list, k: int) -> list:" in skeleton
    assert '"""Rotate a list to the right by k steps."""' in skeleton
    assert "return lst[-k:] + lst[:-k]" not in skeleton  # implementation suppressed
    assert "Avoid previous mistake: IndexError: out of range" in skeleton


# ─── Directive D5: Task Difficulty Estimator (Pre-Retry Triage) ───────────────


def test_d5_difficulty_tier_classification() -> None:
    dummy_exec = ExecutionResult("", "", 0, False, 1.0, 1)

    r_trivial = EnergyResult(0.0, EnergyCategory.PERFECT, "", dummy_exec)
    assert r_trivial.difficulty_tier() == "trivial"

    r_fixable = EnergyResult(25.0, EnergyCategory.WRONG_OUTPUT, "", dummy_exec)
    assert r_fixable.difficulty_tier() == "fixable"

    r_hard_runtime = EnergyResult(60.0, EnergyCategory.RUNTIME_ERROR, "", dummy_exec)
    assert r_hard_runtime.difficulty_tier() == "hard"

    r_hard_syntax = EnergyResult(100.0, EnergyCategory.SYNTAX_ERROR, "", dummy_exec)
    assert r_hard_syntax.difficulty_tier() == "hard"


# ─── Directive D6: DPO Preference Signal from Live Phase 1 Traces ────────────


def test_d6_trace_extractor_from_loop_traces() -> None:
    lt_pass = LoopTrace(
        task="Reverse string",
        prompt="Write reverse_str",
        code="def reverse_str(s): return s[::-1]",
        raw_response="",
        energy=0.0,
        energy_category="perfect",
        converged=True,
        iteration=2,
        duration_ms=10.0,
        returncode=0,
        execution_stdout="",
        execution_stderr="",
        hidden_state=[0.1] * 16,
    )
    lt_fail = LoopTrace(
        task="Reverse string",
        prompt="Write reverse_str",
        code="def reverse_str(s): return s",
        raw_response="",
        energy=50.0,
        energy_category="test_failure",
        converged=False,
        iteration=1,
        duration_ms=10.0,
        returncode=1,
        execution_stdout="",
        execution_stderr="failed",
        hidden_state=[0.2] * 16,
    )

    extractor = TraceExtractor()
    sessions = extractor.extract_from_loop_traces([lt_fail, lt_pass])

    assert len(sessions) == 1
    session = sessions[0]
    assert session.is_dpo_ready is True
    best = session.best_trace()
    worst = session.worst_trace()
    assert best is not None and best.energy == 0.0
    assert worst is not None and worst.energy == 50.0


# ─── Directive D7: Tier-Specific Success Gates G6 - G9 ────────────────────────


def test_d7_tier_specific_gates() -> None:
    from run_phase1_evolution import Bench

    args = MagicMock()
    args.out = "/tmp/test_d7_out"
    args.model = "qwen2.5-coder:1.5b"
    args.seeds = [1, 2, 3]
    args.max_retries = 3
    args.limit = 5
    args.openai_compat = False

    bench = Bench(args)
    # Simulate valid Phase 1 results matching measured numbers
    bench.results["uc1"] = {
        "runs": 20,
        "claimed_converged": 11,
        "verified_pass": 7,
        "false_convergences": 4,
        "false_convergence_rate": 0.36,  # < 0.50 -> G7 PASS
    }
    bench.results["uc2"] = {
        "runs": 60,
        "pass_at_1": 0.383,  # >= 0.30 -> G6 PASS
        "pass_at_n": 0.517,
        "retried_runs": 35,
        "rescued_by_retry": 6,
        "rescued_by_adaptive_retry": 5,  # plain 6 >= adaptive 5 -> G2b PASS (D2)
        "energy_never_increased": 12,  # 12/35 = 0.34 >= 0.30 -> G9 PASS
    }
    bench.results["uc3"] = {
        "failed_first_attempts": 10,
        "without_code": {"fix_rate": 0.222},
        "with_code": {"fix_rate": 0.028},
        "with_compressed_code": {"fix_rate": 0.250},  # >= without_code -> G3 PASS (D1)
    }
    bench.results["uc4"] = {
        "memory_off": {"pass_at_1": 0.333},
        "memory_on": {"pass_at_1": 0.367},
        "gains": 2,
        "regressions": 1,
    }
    bench.results["uc5"] = {
        "crashes": 0,
        "false_convergences": 0,
        "missed_controls": 0,
        "poisoned_memories": 0,
    }

    passed = bench.gate()
    assert passed is True
    checks = bench.results["gate"]
    assert checks["G1 legacy false convergences are exposed (measured, informational)"] is True
    assert checks["G2 plain retry rescues at least one failed first attempt"] is True
    assert checks["G2b plain retry >= adaptive retry for <=3B models (D2 capacity gating)"] is True
    assert checks["G3 fix rate with compressed code >= without code (or with code >= without code)"] is True
    assert checks["G4 memory on: pass@1 >= memory off and no net regression"] is True
    assert checks["G5 zero crashes, false convergences, missed controls, poisoned memories"] is True
    assert checks["G6 low-tier pass@1 >= 0.30"] is True
    assert checks["G7 low-tier false convergence rate < 0.50"] is True
    assert checks["G8 low-tier rescue efficiency >= 0.10"] is True
    assert checks["G9 monotonic energy fraction >= 0.30"] is True


# ─── Directive D8: Autopoietic Prompt Strategy Registry ───────────────────────


def test_d8_prompt_strategy_registry_swap(tmp_path: Path) -> None:
    from anse.autopoiesis.registry import ComponentRegistry

    reg = ComponentRegistry(tmp_path / "registry")
    v1 = reg.ensure_default_prompt_strategy()
    assert v1 == 1
    assert "prompt_strategy" in reg.components()

    mod1 = reg.load_active("prompt_strategy")
    assert hasattr(mod1, "format_pain_prompt")
    prompt1 = mod1.format_pain_prompt(
        task="Reverse",
        code="def rev(): pass",
        energy=50.0,
        category="runtime_error",
        returncode=1,
        stderr="err",
        stdout="",
        model_tier="<=3B",
    )
    assert "TASK: Reverse" in prompt1
    assert "Failing code summary:" in prompt1

    # Promote candidate strategy v2
    custom_strategy = '''"""Evolved prompt strategy v2."""
def format_pain_prompt(task, code, energy, category, returncode, stderr, stdout, model_tier="<=3B", test_feedback=""):
    return f"RETRY_TASK: {task} | E={energy:.1f}"
'''
    v2 = reg.promote(
        "prompt_strategy",
        custom_strategy,
        record={"reason": "test promotion", "active_version": 2},
    )
    assert v2 == 2
    mod2 = reg.load_active("prompt_strategy")
    prompt2 = mod2.format_pain_prompt("Reverse", "", 10.0, "err", 1, "", "")
    assert prompt2 == "RETRY_TASK: Reverse | E=10.0"

    # Rollback to v1
    v_restored = reg.rollback("prompt_strategy", reason="testing rollback")
    assert v_restored == 1
    mod_restored = reg.load_active("prompt_strategy")
    assert "Failing code summary:" in mod_restored.format_pain_prompt(
        "Reverse", "code", 20.0, "err", 1, "", "", model_tier="<=3B"
    )
