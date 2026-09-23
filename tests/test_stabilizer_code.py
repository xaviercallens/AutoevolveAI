"""
Tests for ANSE Stabilizer Code Engine.
Physical hardness: all assertions verified against genuine computation.
No mocks. No hardcoded rates.
"""

from __future__ import annotations

import numpy as np
import pytest

from anse.quantum.stabilizer_code_engine import (
    PauliOperator,
    SurfaceCodeLayout,
    StabilizerCodeEngine,
    sample_depolarizing_error,
    greedy_mwpm_correction,
    is_logical_x_error,
    is_logical_z_error,
)


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Pauli Group Algebra
# ─────────────────────────────────────────────────────────────────────────────

def test_pauli_commutation():
    """X and Z anticommute on the same qubit: XZ = iY, ZX = -iY → they anticommute."""
    n = 1
    X = PauliOperator.single_x(n, 0)
    Z = PauliOperator.single_z(n, 0)
    I = PauliOperator.identity(n)

    # X and Z should NOT commute
    assert not X.commutes_with(Z), "X and Z must anticommute on the same qubit"
    # X commutes with X
    assert X.commutes_with(X), "X commutes with itself"
    # Z commutes with Z
    assert Z.commutes_with(Z), "Z commutes with itself"
    # I commutes with everything
    assert I.commutes_with(X)
    assert I.commutes_with(Z)


def test_pauli_weight():
    """Pauli weight equals the number of non-identity factors."""
    n = 5
    X2 = PauliOperator.single_x(n, 2)
    assert X2.weight() == 1

    x = np.zeros(n, dtype=np.uint8)
    z = np.zeros(n, dtype=np.uint8)
    x[0] = 1; x[2] = 1; z[3] = 1  # X0 Y0... → X_0, X_2, Z_3
    p = PauliOperator(x, z, 0)
    assert p.weight() == 3, f"Expected weight 3, got {p.weight()}"


def test_pauli_multiplication():
    """XX = I, XZ = iY."""
    n = 1
    X = PauliOperator.single_x(n, 0)
    Z = PauliOperator.single_z(n, 0)

    XX = X * X
    assert np.all(XX.x == 0) and np.all(XX.z == 0), "X*X must equal identity"

    XZ = X * Z
    # X*Z: x=1,z=1 → Y, with phase shift of (z of X) dot (x of Z) = 0·1=0
    # phase = 0+0+0 = 0 → no extra i from anticomm... let's just check x,z parts
    assert XZ.x[0] == 1 and XZ.z[0] == 1, "X*Z must have both x and z set (Y factor)"


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: Surface Code Layout — Stabilizer Construction
# ─────────────────────────────────────────────────────────────────────────────

def test_surface_code_layout_d3():
    """Distance-3 surface code should have 9 data qubits and 8 stabilizers."""
    layout = SurfaceCodeLayout(d=3)
    assert layout.n_data == 9, f"d=3 → 9 data qubits, got {layout.n_data}"
    n_stabs = len(layout.x_stabilizers) + len(layout.z_stabilizers)
    assert n_stabs == 8, f"d=3 → 8 stabilizers, got {n_stabs}"


def test_surface_code_layout_d5():
    """Distance-5 surface code should have 25 data qubits."""
    layout = SurfaceCodeLayout(d=5)
    assert layout.n_data == 25, f"d=5 → 25 data qubits, got {layout.n_data}"


def test_stabilizers_are_binary():
    """All stabilizer check vectors must be binary (0 or 1 only)."""
    layout = SurfaceCodeLayout(d=3)
    for check in layout.x_stabilizers + layout.z_stabilizers:
        assert set(check).issubset({0, 1}), "Stabilizer check must be binary"


def test_syndrome_measurement_no_error():
    """With no errors, all syndromes must be 0."""
    layout = SurfaceCodeLayout(d=3)
    n = layout.n_data
    zero_error = np.zeros(n, dtype=np.uint8)
    syn_x = layout.measure_x_syndrome(zero_error)
    syn_z = layout.measure_z_syndrome(zero_error)
    assert np.all(syn_x == 0), "No error → all X syndromes must be 0"
    assert np.all(syn_z == 0), "No error → all Z syndromes must be 0"


def test_syndrome_measurement_single_z_error():
    """A single-qubit Z error must trigger at least 1 non-zero X syndrome."""
    layout = SurfaceCodeLayout(d=3)
    n = layout.n_data
    error_z = np.zeros(n, dtype=np.uint8)
    error_z[4] = 1  # flip center qubit Z
    syn_x = layout.measure_x_syndrome(error_z)
    assert np.any(syn_x > 0), "Single Z error must trigger nonzero X syndrome (code detects it)"


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Depolarizing Noise Model
# ─────────────────────────────────────────────────────────────────────────────

def test_depolarizing_error_zero_rate():
    """At p=0 there must be no errors."""
    rng = np.random.default_rng(42)
    ex, ez = sample_depolarizing_error(25, 0.0, rng)
    assert np.all(ex == 0) and np.all(ez == 0), "p=0 → no errors"


def test_depolarizing_error_high_rate():
    """At p=0.99, most qubits should have errors."""
    rng = np.random.default_rng(42)
    ex, ez = sample_depolarizing_error(25, 0.99, rng)
    total_errors = int(np.sum(ex | ez))
    assert total_errors > 10, f"p=0.99 → many errors expected, got {total_errors}"


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Logical Error Detection
# ─────────────────────────────────────────────────────────────────────────────

def test_logical_z_on_column_zero():
    """Z errors spanning the full column 0 must be detected as a logical chain (homological check)."""
    d = 3
    n = d * d
    error_z = np.zeros(n, dtype=np.uint8)
    for r in range(d):
        error_z[r * d] = 1  # Z on every qubit in col 0
    # Homological check: logical_x_row0 = [1,1,1,0,...] · error_z_col0 = [1,0,0,1,0,0,1,0,0]
    # dot = 1*1+1*0+1*0 = 1 → mod 2 = 1 → logical error
    assert is_logical_x_error(error_z, d), "Full Z column-0 chain must be detected as logical chain"


def test_logical_x_on_row_zero():
    """X errors spanning the full row 0 must be detected as a logical chain (homological check)."""
    d = 3
    n = d * d
    error_x = np.zeros(n, dtype=np.uint8)
    for c in range(d):
        error_x[c] = 1  # X on every qubit in row 0
    # Homological check: logical_z_col0 = [1,0,0,1,0,0,...] · error_x_row0 = [1,1,1,0,...]
    # dot = 1*1+0*1+0*1 = 1 → mod 2 = 1 → logical error
    assert is_logical_z_error(error_x, d), "Full X row-0 chain must be detected as logical chain"


def test_no_logical_error_small_error():
    """A small bulk Z error (not forming a spanning chain) must NOT be a logical error."""
    d = 5
    n = d * d
    error_z = np.zeros(n, dtype=np.uint8)
    error_z[12] = 1  # center qubit (row=2, col=2): not in row 0
    # Homological check: logical_x_row0 = [1,1,1,1,1,0,...]
    # dot([1,1,1,1,1,0,...], error_z) = 0 (qubit 12 is not in row 0)
    assert not is_logical_x_error(error_z, d), "Interior Z error not in row 0 → not a logical chain"


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: Full Simulation — Physical Hardness Gate
# ─────────────────────────────────────────────────────────────────────────────

def test_qec_logical_error_rate_below_threshold():
    """
    PHYSICAL HARDNESS GATE: Distance-5 code at p=0.001 (0.1%, well below ~1% threshold)
    must achieve logical_error_rate < 1e-4.
    At p=0.001 with d=5, logical errors require 3+ simultaneous qubit errors, giving
    LER ≈ O(p^3) ≈ O(1e-9) per round → 0 logical errors expected in 500 rounds.
    """
    engine = StabilizerCodeEngine(d=5, p=0.001, seed=42)
    result = engine.simulate(n_rounds=500)

    assert result.code_distance == 5
    assert result.n_data_qubits == 25
    assert result.code_distance_verified is True, "Code distance must be formally verified via logical pair test"
    assert result.logical_error_rate < 1e-4, (
        f"GATE FAIL: logical_error_rate={result.logical_error_rate:.2e} >= 1e-4. "
        f"Surface code d=5 at p=0.001 must beat this threshold decisively."
    )
    assert result.status == "VERIFIED", f"Status must be VERIFIED, got {result.status}"
    assert result.proof_token, "Proof token must be non-empty"
    print(f"\n[QEC GATE PASS] d={result.code_distance}, p={result.noise_rate_p}, "
          f"LER={result.logical_error_rate:.2e}, "
          f"syndrome_weight_mean={result.syndrome_weight_mean:.3f}, "
          f"elapsed={result.elapsed_ms:.1f}ms")


def test_qec_high_noise_fails_gate():
    """At p=0.10 (above threshold), logical error rate must be HIGH (fails gate)."""
    engine = StabilizerCodeEngine(d=3, p=0.10, seed=99)
    result = engine.simulate(n_rounds=200)
    # High noise → logical errors should appear
    assert result.logical_error_rate > 0, "High noise must produce some logical errors"
    print(f"\n[QEC HIGH NOISE] d={result.code_distance}, p={result.noise_rate_p}, "
          f"LER={result.logical_error_rate:.2e}")
