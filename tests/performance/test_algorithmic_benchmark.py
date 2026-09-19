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
    with open(bench_path, "r", encoding="utf-8") as f:
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


@pytest.mark.parametrize("task_idx", range(7))
def test_benchmark_task_correctness_and_speedup(task_idx, benchmark_tasks, sandbox, evaluator):
    task = benchmark_tasks[task_idx]
    name = task["name"]
    naive_full = task["naive_code"].strip() + "\n\n" + task["test_harness"].strip()
    opt_full = task["reference_optimized_code"].strip() + "\n\n" + task["test_harness"].strip()

    # 1. Execute naive baseline
    res_naive = sandbox.execute(naive_full)
    assert res_naive.returncode == 0, f"Naive code failed for {name}: {res_naive.stderr}"
    assert f"OK: {name} passed" in res_naive.stdout

    # 2. Execute reference optimized
    res_opt = sandbox.execute(opt_full)
    assert res_opt.returncode == 0, f"Optimized code failed for {name}: {res_opt.stderr}"
    assert f"OK: {name} passed" in res_opt.stdout

    # 3. Evaluate Computational Physics Energy
    energy_naive = evaluator.evaluate(res_naive)
    energy_opt = evaluator.evaluate(res_opt, baseline_result=res_naive)

    assert energy_naive.is_valid is True
    assert energy_opt.is_valid is True

    # 4. Verify physical speedup and energy reduction
    assert energy_opt.speedup_factor is not None
    assert energy_opt.speedup_factor >= 1.0, (
        f"{name}: Expected speedup >= 1.0, got {energy_opt.speedup_factor:.2f}x "
        f"(Naive: {res_naive.duration_ms:.2f}ms, Opt: {res_opt.duration_ms:.2f}ms)"
    )

    # Execution duration of optimized code must be strictly faster or equal
    assert res_opt.duration_ms <= res_naive.duration_ms * 1.05
    assert energy_opt.category in (
        PerformanceCategory.VECTORIZED,
        PerformanceCategory.OPTIMIZED,
        PerformanceCategory.MODERATE,
    )
