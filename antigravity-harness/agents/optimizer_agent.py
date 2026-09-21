"""
Optimizer Agent: Computational physics profiling and algorithmic refactoring.
Measures physical energy E = w_t * Duration (ms) + w_m * Peak RAM (MB).
Audits algorithms for O(N^2) quadratic patterns and enforces the thermodynamic
improvement contract: Delta E = E_child - E_parent < 0.
"""

from __future__ import annotations

import ast
import time
import tracemalloc
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class PhysicalEnergy:
    """Energy measurement under the ANSE computational physics model."""

    duration_ms: float
    peak_ram_mb: float
    weight_time: float = 1.0
    weight_ram: float = 0.1

    @property
    def total_energy(self) -> float:
        return (self.weight_time * self.duration_ms) + (self.weight_ram * self.peak_ram_mb)


@dataclass
class OptimizationProposal:
    """Result of an optimization analysis and profiling run."""

    baseline_energy: PhysicalEnergy
    candidate_energy: PhysicalEnergy
    delta_energy: float  # E_candidate - E_baseline
    speedup_ratio: float
    is_thermodynamically_favorable: bool
    bottlenecks_detected: list[str]


class OptimizerAgent:
    """Profiles computational targets and analyzes algorithmic complexity."""

    def __init__(self, weight_time: float = 1.0, weight_ram: float = 0.1) -> None:
        self.weight_time = weight_time
        self.weight_ram = weight_ram

    def profile_callable(
        self,
        target_fn: Callable[..., Any],
        *args: Any,
        warmup_runs: int = 1,
        benchmark_runs: int = 3,
        **kwargs: Any,
    ) -> PhysicalEnergy:
        """
        Profiles execution duration and peak resident memory allocations using tracemalloc.
        """
        # Warmup
        for _ in range(warmup_runs):
            try:
                target_fn(*args, **kwargs)
            except Exception:
                pass

        tracemalloc.start()
        start_time = time.perf_counter()

        for _ in range(benchmark_runs):
            target_fn(*args, **kwargs)

        end_time = time.perf_counter()
        _current_ram, peak_ram = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        duration_ms = ((end_time - start_time) / max(1, benchmark_runs)) * 1000.0
        peak_ram_mb = peak_ram / (1024.0 * 1024.0)

        return PhysicalEnergy(
            duration_ms=duration_ms,
            peak_ram_mb=peak_ram_mb,
            weight_time=self.weight_time,
            weight_ram=self.weight_ram,
        )

    def detect_algorithmic_bottlenecks(self, source_code: str) -> list[str]:
        """Scans AST for known algorithmic anti-patterns."""
        bottlenecks: list[str] = []
        try:
            tree = ast.parse(source_code)
        except Exception:
            return ["Syntax error prevents static complexity analysis."]

        # Check for nested loops: potential O(N^2)
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if child is not node and isinstance(child, (ast.For, ast.While)):
                        bottlenecks.append(
                            f"Line {node.lineno}: Nested loop detected (potential O(N^2) complexity)."
                        )
                        break

            # Check for linear search in list inside loop: `if x in list_var`
            if isinstance(node, ast.Compare):
                for op in node.ops:
                    if isinstance(op, ast.In):
                        # Potential unindexed membership test
                        bottlenecks.append(
                            f"Line {node.lineno}: 'in' membership check inside expression (consider set/dict hash lookup)."
                        )

        return bottlenecks

    def compare_and_evaluate(
        self,
        baseline_fn: Callable[..., Any],
        candidate_fn: Callable[..., Any],
        candidate_source: str,
        *args: Any,
        **kwargs: Any,
    ) -> OptimizationProposal:
        """
        Runs both functions and evaluates Delta E = E_candidate - E_baseline.
        Thermodynamically favorable if Delta E < 0.
        """
        base_e = self.profile_callable(baseline_fn, *args, **kwargs)
        cand_e = self.profile_callable(candidate_fn, *args, **kwargs)

        delta_e = cand_e.total_energy - base_e.total_energy
        speedup = base_e.duration_ms / max(0.001, cand_e.duration_ms)
        favorable = delta_e < 0.0

        bottlenecks = self.detect_algorithmic_bottlenecks(candidate_source)

        return OptimizationProposal(
            baseline_energy=base_e,
            candidate_energy=cand_e,
            delta_energy=delta_e,
            speedup_ratio=speedup,
            is_thermodynamically_favorable=favorable,
            bottlenecks_detected=bottlenecks,
        )
