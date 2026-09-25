"""
Unit tests for the PhD-level Multidisciplinary Benchmark Suite:
- Rust numerical computing kernels
- Pure mathematics formal theorems
- Pure physics theoretical invariants
"""

from __future__ import annotations

from anse.benchmark.complex_python_cases import (
    PYTHON_BENCHMARKS,
    run_single_python_benchmark,
)
from anse.benchmark.pure_math_cases import MATH_BENCHMARKS, run_single_math_benchmark
from anse.benchmark.pure_physics_cases import PHYSICS_BENCHMARKS, run_single_physics_benchmark
from anse.benchmark.rust_numeric_cases import RUST_KERNELS, compile_and_run_rust

from antigravity_harness.core.hardened_evaluator import HardenedEvaluator


def test_benchmark_registry_counts() -> None:
    """Verifies that all four domains contain at least 30 benchmarks (120 or 200 total)."""
    assert len(RUST_KERNELS) >= 30, f"Expected 30+ Rust kernels, got {len(RUST_KERNELS)}"
    assert len(MATH_BENCHMARKS) >= 30, f"Expected 30+ Math benchmarks, got {len(MATH_BENCHMARKS)}"
    assert len(PHYSICS_BENCHMARKS) >= 30, f"Expected 30+ Physics benchmarks, got {len(PHYSICS_BENCHMARKS)}"
    assert len(PYTHON_BENCHMARKS) >= 30, f"Expected 30+ Python benchmarks, got {len(PYTHON_BENCHMARKS)}"


def test_rust_kernels_all() -> None:
    """Verifies that all 30 Rust numerical kernels compile with rustc -O and pass invariants."""
    for cid in sorted(RUST_KERNELS.keys()):
        res = compile_and_run_rust(cid)
        assert res.verified, f"Rust kernel {cid} failed verification: {res.error_msg}"
        assert res.latency_ms < 2000.0
        assert res.invariant_error < 0.2


def test_pure_math_benchmarks() -> None:
    """Verifies all 30 pure mathematics formal benchmarks."""
    for cid in sorted(MATH_BENCHMARKS.keys()):
        res = run_single_math_benchmark(cid)
        assert res.verified, f"Math benchmark {cid} failed verification with error {res.invariant_error}"
        assert res.invariant_error < 1e-4


def test_pure_physics_benchmarks() -> None:
    """Verifies all 30 pure physics theoretical benchmarks."""
    for cid in sorted(PHYSICS_BENCHMARKS.keys()):
        res = run_single_physics_benchmark(cid)
        assert res.verified, f"Physics benchmark {cid} failed verification with error {res.invariant_error}"
        assert res.invariant_error < 1e-3


def test_complex_python_benchmarks() -> None:
    """Verifies all 30 complex Python benchmarks."""
    for cid in sorted(PYTHON_BENCHMARKS.keys()):
        res = run_single_python_benchmark(cid)
        assert res.verified, f"Python benchmark {cid} failed verification with error {res.invariant_error}"
        assert res.invariant_error < 1.0


def test_hardened_evaluator_attestation() -> None:
    """Verifies that the HardenedEvaluator rejects AST stubs and mints HMAC tokens on success."""
    evaluator = HardenedEvaluator()

    # Case 1: Rejection of pass stub
    stub_code = "def stub():\n    pass\n"
    clean, violations = evaluator.audit_ast(stub_code)
    assert not clean
    assert any("pass" in v for v in violations)

    # Case 2: Clean code mints token
    token = evaluator.mint_token("TEST-01", 12.34, 1e-8)
    assert len(token) == 32
    assert isinstance(token, str)

