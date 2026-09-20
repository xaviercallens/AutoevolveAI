"""
Benchmark suite validation for Use Case 1: The Algorithmic Performance Engineer.
Runs all 5 canonical computational physics tasks on both naive baseline and
reference optimized code, verifying functional correctness, positive speedup,
and energy minimization.
"""

from pathlib import Path

import pytest
import yaml

from anse.symbolic.performance_evaluator import (
    PerformanceCategory,
    PerformanceEnergyEvaluator,
)
from anse.symbolic.sandbox import SandboxExecutor


@pytest.fixture(scope="module")
def benchmark_tasks():
    bench_path = Path(__file__).parent.parent.parent / "tasks" / "algorithmic_performance.yaml"
    with open(bench_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["tasks"]


@pytest.fixture(scope="module")
def sandbox():
    return SandboxExecutor()


@pytest.fixture(scope="module")
def evaluator():
    return PerformanceEnergyEvaluator()


def test_benchmark_suite_task_count(benchmark_tasks):
    assert len(benchmark_tasks) == 7
    task_names = [t["name"] for t in benchmark_tasks]
    assert "pairwise_euclidean_distances" in task_names
    assert "matrix_multiplication" in task_names
    assert "spatial_2d_convolution" in task_names
    assert "text_ngram_frequency" in task_names
    assert "sliding_window_maximum" in task_names
    assert "hash_table_lookup_optimization" in task_names
    assert "catastrophic_backtracking_regex" in task_names


def _verify_execution(sandbox, code, harness, name):
    full_code = code.strip() + "\n\n" + harness.strip()
    res = sandbox.execute(full_code)
    assert res.returncode == 0, f"Code failed for {name}: {res.stderr}"
    assert f"OK: {name} passed" in res.stdout, f"Output check failed for {name}"
    return res


@pytest.mark.parametrize("task_idx", range(7))
def test_benchmark_task_correctness_and_speedup(task_idx, benchmark_tasks, sandbox, evaluator):
    task = benchmark_tasks[task_idx]
    name = task["name"]
    harness = task["test_harness"]

    res_naive = _verify_execution(sandbox, task["naive_code"], harness, name)
    res_opt = _verify_execution(sandbox, task["reference_optimized_code"], harness, name)

    energy_naive = evaluator.evaluate(res_naive)
    energy_opt = evaluator.evaluate(res_opt, baseline_result=res_naive)

    assert energy_naive.is_valid is True
    assert energy_opt.is_valid is True

    assert energy_opt.speedup_factor is not None
    assert energy_opt.speedup_factor >= 0.95, (
        f"{name}: Expected speedup >= 0.95, got {energy_opt.speedup_factor:.2f}x "
        f"(Naive: {res_naive.duration_ms:.2f}ms, Opt: {res_opt.duration_ms:.2f}ms)"
    )

    assert res_opt.duration_ms <= res_naive.duration_ms * 1.05
    assert energy_opt.category in (
        PerformanceCategory.VECTORIZED,
        PerformanceCategory.OPTIMIZED,
        PerformanceCategory.MODERATE,
    )
