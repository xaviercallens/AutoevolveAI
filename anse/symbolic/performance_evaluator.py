"""
Performance Energy Evaluator: converts :class:`~anse.symbolic.sandbox.ExecutionResult`
into a continuous mathematical computational physics Energy score.

Formal Concept (Use Case 1 — Algorithmic Performance Engineer):
---------------------------------------------------------------
Energy Signal:
    E = w_t * Execution Time (ms) + w_m * Peak RAM Usage (MB)
    Crash / Syntax Error / Incorrect Output = E = ∞ (or penalty 1e6)

Monotonicity Property:
    If code is functionally correct and executes faster or uses less RAM,
    Energy drops continuously. High energy acts as a latent 'pain signal'
    inducing System 2 pondering and dynamic LoRA weight updates.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from anse.config import PerformanceConfig, get_config
from anse.symbolic.sandbox import ExecutionResult


# ─── Categories ──────────────────────────────────────────────────────────────

class PerformanceCategory(str, Enum):
    SYNTAX_ERROR = "syntax_error"
    CRASH = "crash"
    TIMEOUT = "timeout"
    TEST_FAILURE = "test_failure"
    WRONG_OUTPUT = "wrong_output"
    INEFFICIENT = "inefficient"
    MODERATE = "moderate"
    OPTIMIZED = "optimized"
    VECTORIZED = "vectorized"


@dataclass
class PerformanceEnergyResult:
    """Outcome of evaluating computational performance energy."""

    score: float
    """The continuous energy value E ∈ [0, ∞). Lower is faster and leaner."""

    category: PerformanceCategory
    """Qualitative categorization of the execution."""

    is_valid: bool
    """Whether the code executed cleanly and satisfied all correctness criteria."""

    duration_ms: float
    """Wall-clock execution duration in milliseconds."""

    peak_ram_mb: float
    """Peak RAM consumption in Megabytes."""

    execution: ExecutionResult
    """Underlying sandbox execution result."""

    pain_signal: str
    """Pain/reward diagnostic feedback for System 2 pondering or prompt injection."""

    speedup_factor: Optional[float] = None
    """Speedup relative to baseline: T_baseline / T_cand."""

    memory_reduction_ratio: Optional[float] = None
    """Fractional memory saved relative to baseline: 1.0 - (RAM_cand / RAM_baseline)."""

    energy_delta: Optional[float] = None
    """Change in energy: E_baseline - E_cand. Positive indicates improvement."""

    relative_energy: Optional[float] = None
    """Normalized energy relative to baseline: (T / T_base) + (M / M_base)."""


# ─── Evaluator ───────────────────────────────────────────────────────────────

class PerformanceEnergyEvaluator:
    """
    Evaluates candidate code in terms of continuous computational physics:
    Execution Time (ms) + Peak RAM Usage (MB).
    """

    def __init__(self, config: Optional[PerformanceConfig] = None) -> None:
        self.config = config or get_config().performance

    def evaluate(
        self,
        result: ExecutionResult,
        baseline_result: Optional[ExecutionResult] = None,
        expected_output: Optional[str] = None,
        code: Optional[str] = None,
    ) -> PerformanceEnergyResult:
        """
        Evaluate *result* and compute the continuous energy score.

        Parameters
        ----------
        result:
            Output from :class:`~anse.symbolic.sandbox.SandboxExecutor`.
        baseline_result:
            Optional baseline execution result (e.g. naive unvectorized code)
            used to compute relative speedup and energy reduction.
        expected_output:
            Optional expected stdout for output validation.
        code:
            Optional source code string.
        """
        stderr = result.stderr or ""
        stdout = result.stdout or ""

        # 1. Correctness Gate: Any fatal failure spikes energy to infinity (penalty)
        if result.timed_out:
            return self._build_failure_result(
                result=result,
                category=PerformanceCategory.TIMEOUT,
                pain_signal=(
                    f"COMPUTATIONAL CRASH (TIMEOUT): Execution exceeded time limit.\n"
                    f"Stderr:\n{stderr[-1000:]}"
                ),
            )

        if re.search(r"SyntaxError", stderr, re.IGNORECASE):
            return self._build_failure_result(
                result=result,
                category=PerformanceCategory.SYNTAX_ERROR,
                pain_signal=(
                    f"COMPUTATIONAL CRASH (SYNTAX ERROR): Code could not be parsed.\n"
                    f"Traceback:\n{stderr[-1000:]}"
                ),
            )

        if re.search(r"AssertionError", stderr, re.IGNORECASE) or re.search(r"FAILED|FAIL", stdout):
            return self._build_failure_result(
                result=result,
                category=PerformanceCategory.TEST_FAILURE,
                pain_signal=(
                    f"CORRECTNESS FAILURE: Code failed functional verification tests.\n"
                    f"Optimization must strictly preserve algorithmic correctness.\n"
                    f"Stderr:\n{stderr[-1000:]}\nStdout:\n{stdout[-1000:]}"
                ),
            )

        if result.returncode != 0:
            return self._build_failure_result(
                result=result,
                category=PerformanceCategory.CRASH,
                pain_signal=(
                    f"COMPUTATIONAL CRASH: Runtime exception raised (exit code {result.returncode}).\n"
                    f"Traceback:\n{stderr[-1000:]}"
                ),
            )

        if expected_output is not None:
            actual = stdout.strip()
            expected = expected_output.strip()
            if actual != expected:
                return self._build_failure_result(
                    result=result,
                    category=PerformanceCategory.WRONG_OUTPUT,
                    pain_signal=(
                        f"CORRECTNESS FAILURE: Output does not match expected reference.\n"
                        f"Expected:\n{expected[:500]}\n\nActual:\n{actual[:500]}"
                    ),
                )

        # 2. Continuous Physics Calculation
        duration_ms = max(result.duration_ms, 0.001)
        peak_ram_mb = max(result.peak_ram_mb, 0.0)

        raw_energy = (self.config.weight_time_ms * duration_ms) + (
            self.config.weight_peak_ram_mb * peak_ram_mb
        )

        speedup: Optional[float] = None
        mem_red: Optional[float] = None
        energy_delta: Optional[float] = None
        rel_energy: Optional[float] = None

        if baseline_result is not None:
            base_t = max(baseline_result.duration_ms, 0.001)
            base_m = max(baseline_result.peak_ram_mb, 0.001)
            base_energy = (self.config.weight_time_ms * base_t) + (
                self.config.weight_peak_ram_mb * base_m
            )

            speedup = base_t / duration_ms
            mem_red = max(0.0, 1.0 - (peak_ram_mb / base_m))
            energy_delta = base_energy - raw_energy
            rel_energy = (duration_ms / base_t) + (peak_ram_mb / base_m)

        # 3. Categorization based on performance gain
        if speedup is not None:
            if speedup >= 5.0 or (duration_ms < 0.15 * base_t):
                category = PerformanceCategory.VECTORIZED
            elif speedup >= 2.0:
                category = PerformanceCategory.OPTIMIZED
            elif speedup >= 1.1:
                category = PerformanceCategory.MODERATE
            else:
                category = PerformanceCategory.INEFFICIENT
        else:
            category = PerformanceCategory.OPTIMIZED if duration_ms < 50.0 else PerformanceCategory.INEFFICIENT

        # 4. Generate Latent Feedback (Pain vs Reward Signal)
        if category in (PerformanceCategory.VECTORIZED, PerformanceCategory.OPTIMIZED):
            speedup_str = f"{speedup:.1f}x speedup" if speedup else "fast execution"
            pain_signal = (
                f"PERFORMANCE REWARD: Massive Energy Drop! (Energy = {raw_energy:.2f})\n"
                f"- Execution Time: {duration_ms:.2f} ms ({speedup_str})\n"
                f"- Peak RAM: {peak_ram_mb:.2f} MB\n"
                f"- Status: {category.value.upper()} implementation successfully discovered."
            )
        else:
            base_info = ""
            if baseline_result is not None:
                base_info = (
                    f" (Baseline: {baseline_result.duration_ms:.2f} ms, "
                    f"{baseline_result.peak_ram_mb:.2f} MB)"
                )
            pain_signal = (
                f"PERFORMANCE PAIN SIGNAL: High Computational Energy (E = {raw_energy:.2f})\n"
                f"- Execution Time: {duration_ms:.2f} ms{base_info}\n"
                f"- Peak RAM: {peak_ram_mb:.2f} MB\n"
                f"System 2 Pain Diagnosis:\n"
                f"The algorithm is functionally correct but computationally inefficient. "
                f"Nested Python loops and unvectorized allocations create high latency and memory overhead. "
                f"Ponder further: replace sequential for-loops with NumPy array broadcasting, "
                f"contiguous memory layout, or SIMD vectorization to minimize Energy towards zero."
            )

        return PerformanceEnergyResult(
            score=raw_energy,
            category=category,
            is_valid=True,
            duration_ms=duration_ms,
            peak_ram_mb=peak_ram_mb,
            execution=result,
            pain_signal=pain_signal,
            speedup_factor=speedup,
            memory_reduction_ratio=mem_red,
            energy_delta=energy_delta,
            relative_energy=rel_energy,
        )

    def _build_failure_result(
        self,
        result: ExecutionResult,
        category: PerformanceCategory,
        pain_signal: str,
    ) -> PerformanceEnergyResult:
        """Construct infinite energy result for failed execution."""
        return PerformanceEnergyResult(
            score=self.config.penalty_infinite_energy,
            category=category,
            is_valid=False,
            duration_ms=result.duration_ms,
            peak_ram_mb=result.peak_ram_mb,
            execution=result,
            pain_signal=pain_signal,
            speedup_factor=0.0,
            memory_reduction_ratio=0.0,
            energy_delta=-self.config.penalty_infinite_energy,
            relative_energy=float("inf"),
        )
