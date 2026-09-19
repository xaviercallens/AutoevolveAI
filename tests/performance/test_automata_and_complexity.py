"""
Targeted tests for:
1. Algorithmic Complexity Explorer (Hash Map / Set O(1) vs O(N) lookup)
2. Catastrophic Backtracking Parser (Automata Physics & Exponential Time Explosion)

Verifies continuous energy minimization and strict timeout enforcement ($E = 10^6$).
"""

import pytest

from anse.config import SandboxConfig
from anse.symbolic.performance_evaluator import (
    PerformanceCategory,
    PerformanceEnergyEvaluator,
)
from anse.symbolic.sandbox import SandboxExecutor


@pytest.fixture(scope="module")
def evaluator():
    return PerformanceEnergyEvaluator()


def test_hash_table_complexity_energy_reduction(evaluator):
    """
    Validates that replacing O(N * M) list linear search with an O(N + M)
    hash set lookup drastically reduces physical energy and achieves high speedup.
    """
    sandbox = SandboxExecutor()

    naive_code = """
def filter_present_keys(keys, query_batch):
    found = []
    for q in query_batch:
        if q in keys:
            found.append(q)
    return found

import random
random.seed(42)
keys = [f"key_{i:06d}" for i in range(12000)]
query_batch = [f"key_{random.randint(0, 24000):06d}" for _ in range(600)]
res = filter_present_keys(keys, query_batch)
assert len(res) > 0
print("OK")
"""

    opt_code = """
def filter_present_keys(keys, query_batch):
    key_set = set(keys)
    return [q for q in query_batch if q in key_set]

import random
random.seed(42)
keys = [f"key_{i:06d}" for i in range(12000)]
query_batch = [f"key_{random.randint(0, 24000):06d}" for _ in range(600)]
res = filter_present_keys(keys, query_batch)
assert len(res) > 0
print("OK")
"""

    res_naive = sandbox.execute(naive_code)
    res_opt = sandbox.execute(opt_code)

    assert res_naive.returncode == 0
    assert res_opt.returncode == 0

    energy_naive = evaluator.evaluate(res_naive)
    energy_opt = evaluator.evaluate(res_opt, baseline_result=res_naive)

    assert energy_naive.is_valid is True
    assert energy_opt.is_valid is True
    assert energy_opt.speedup_factor is not None
    assert energy_opt.speedup_factor > 5.0, f"Expected speedup > 5x, got {energy_opt.speedup_factor:.2f}x"
    assert energy_opt.score < energy_naive.score


def test_catastrophic_backtracking_triggers_timeout_penalty(evaluator):
    """
    Validates that a naive regex with nested ambiguous quantifiers suffers from
    catastrophic backtracking O(2^N) when processing an adversarial input,
    triggering the sandbox timeout and spiking energy to 1e6 (Maximum Pain).
    """
    # Use a tight 1.0s timeout to quickly trap the exponential hang
    cfg = SandboxConfig(timeout_seconds=1.0)
    sandbox = SandboxExecutor(config=cfg)

    # 28 repetitions produces 2^28 operations in backtracking engine
    naive_code = """
import re

PATTERN = re.compile(r"^(\\[EVENT:([a-zA-Z0-9]+_?)+:(SUCCESS|FAILED|PENDING)\\])+$")

# Adversarial input with length 10 mismatch at the end
adversarial_entry = "[" + "EVENT:" + ("node_" * 10) + ":UNKNOWN]"
PATTERN.match(adversarial_entry)
print("COMPLETED")
"""

    res_naive = sandbox.execute(naive_code)
    assert res_naive.timed_out is True
    assert res_naive.returncode != 0

    energy_naive = evaluator.evaluate(res_naive)
    assert energy_naive.is_valid is False
    assert energy_naive.category == PerformanceCategory.TIMEOUT
    assert energy_naive.score == 1_000_000.0
    assert "COMPUTATIONAL CRASH (TIMEOUT)" in energy_naive.pain_signal


def test_optimized_parser_handles_adversarial_input(evaluator):
    """
    Validates that the refactored, linear-time deterministic regex executes
    cleanly on the EXACT SAME adversarial string without exponential explosion,
    satisfying is_valid=True with negligible latency.
    """
    cfg = SandboxConfig(timeout_seconds=1.0)
    sandbox = SandboxExecutor(config=cfg)

    opt_code = """
import re

PATTERN = re.compile(r"^\\[EVENT:[a-zA-Z0-9_]+:(?:SUCCESS|FAILED|PENDING)\\]$")

adversarial_entry = "[" + "EVENT:" + ("node_" * 10) + ":UNKNOWN]"
match = PATTERN.match(adversarial_entry)
assert match is None
print("OK: Linear parse succeeded")
"""

    res_opt = sandbox.execute(opt_code)
    assert res_opt.timed_out is False
    assert res_opt.returncode == 0
    assert "OK: Linear parse succeeded" in res_opt.stdout

    energy_opt = evaluator.evaluate(res_opt)
    assert energy_opt.is_valid is True
    assert energy_opt.score < 1_000.0
    assert res_opt.duration_ms < 200.0
