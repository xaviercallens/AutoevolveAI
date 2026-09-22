"""
Physical Invariant and Symplectic Conservation Test Suite.

Verifies:
1. Symplectic energy conservation: |Delta H / H_0| < 1e-3.
2. Time-reversibility of the Velocity-Verlet flow.
3. Equivalence between Rust C-ABI kernel and Python reference.
4. Poincaré section hyperplane crossing calculations.
5. Non-symplectic explicit Euler violation (DPO alignment ground truth).
"""

from __future__ import annotations

import math
import pytest

from anse.algorithms.symplectic import (
    POTENTIAL_DOUBLE_WELL,
    POTENTIAL_HARMONIC,
    POTENTIAL_HENON_HEILES,
    SymplecticResult,
    compute_poincare_section,
    estimate_lyapunov_exponent,
    explicit_euler_integrate,
    solve_symplectic_orbit,
)


class TestSymplecticHarmonicOscillator:
    """Harmonic oscillator tests for exact energy conservation and reversibility."""

    def test_harmonic_energy_conservation_rust(self) -> None:
        res = solve_symplectic_orbit(
            potential="harmonic",
            q0=[1.0],
            p0=[0.0],
            dt=0.01,
            steps=1000,
            prefer_rust=True,
        )
        assert res.is_symplectic
        assert res.energy_drift < 1e-3
        assert len(res.trajectory_q) == 1000
        assert len(res.energy_h) == 1000

    def test_harmonic_energy_conservation_python_fallback(self) -> None:
        res = solve_symplectic_orbit(
            potential="harmonic",
            q0=[1.0],
            p0=[0.0],
            dt=0.01,
            steps=1000,
            prefer_rust=False,
        )
        assert res.backend == "python_pure"
        assert res.is_symplectic
        assert res.energy_drift < 1e-3
        assert len(res.trajectory_q) == 1001

    def test_rust_python_numeric_equivalence(self) -> None:
        steps = 200
        res_rust = solve_symplectic_orbit("harmonic", [1.5], [0.5], dt=0.005, steps=steps, prefer_rust=True)
        res_py = solve_symplectic_orbit("harmonic", [1.5], [0.5], dt=0.005, steps=steps, prefer_rust=False)

        # Both backends must match initial energy and final energy within numerical epsilon
        assert abs(res_rust.energy_h[0] - res_py.energy_h[0]) < 1e-10
        assert abs(res_rust.energy_h[-1] - res_py.energy_h[steps - 1]) < 1e-7

    def test_time_reversibility_invariant(self) -> None:
        """Integrating forward N steps and backward -N steps must invert phase space."""
        q0 = [1.2]
        p0 = [0.8]
        dt = 0.01
        steps = 300

        # Step forward
        forward = solve_symplectic_orbit("harmonic", q0, p0, dt=dt, steps=steps, prefer_rust=False)
        q_final = forward.trajectory_q[-1]
        p_final = forward.trajectory_p[-1]

        # Reverse momentum and integrate forward (equivalent to backward in time)
        p_reversed = [-x for x in p_final]
        backward = solve_symplectic_orbit("harmonic", q_final, p_reversed, dt=dt, steps=steps, prefer_rust=False)

        # Reconstructed initial position must equal q0
        q_recon = backward.trajectory_q[-1]
        assert abs(q_recon[0] - q0[0]) < 1e-4


class TestNonlinearPotentials:
    """Tests for anharmonic, double-well, and Hénon-Heiles chaotic potentials."""

    def test_double_well_bounded_drift(self) -> None:
        res = solve_symplectic_orbit(
            potential="double_well",
            q0=[0.5],
            p0=[0.2],
            dt=0.005,
            steps=1500,
            prefer_rust=True,
        )
        assert res.is_symplectic
        assert res.energy_drift < 1e-3

    def test_henon_heiles_poincare_crossings(self) -> None:
        # Standard Hénon-Heiles quasi-periodic initial conditions
        q0 = [0.0, 0.2]
        p0 = [0.3, 0.0]
        res = solve_symplectic_orbit(
            potential="henon_heiles",
            q0=q0,
            p0=p0,
            dt=0.01,
            steps=2000,
            prefer_rust=True,
            compute_aux=True,
        )
        assert res.is_symplectic
        assert len(res.poincare_crossings) > 0

    def test_lyapunov_exponent_estimation(self) -> None:
        lyap = estimate_lyapunov_exponent(
            potential="henon_heiles",
            q0=[0.0, 0.2],
            p0=[0.3, 0.0],
            dt=0.01,
            steps=500,
        )
        assert lyap >= 0.0


class TestDPOPhysicalPreferenceViolation:
    """Verifies that non-symplectic Euler creates a high energy drift violation."""

    def test_euler_fails_symplectic_bound(self) -> None:
        dt = 0.02
        steps = 1000
        res_euler = explicit_euler_integrate("harmonic", [1.0], [0.0], dt=dt, steps=steps)
        res_symp = solve_symplectic_orbit("harmonic", [1.0], [0.0], dt=dt, steps=steps)

        # Explicit Euler must drift drastically
        assert not res_euler.is_symplectic
        assert res_euler.energy_drift > 0.05  # > 5% energy error

        # Symplectic Velocity-Verlet must remain stable
        assert res_symp.is_symplectic
        assert res_symp.energy_drift < 1e-3

        # Ratio of drift must be at least two orders of magnitude
        assert res_euler.energy_drift / res_symp.energy_drift > 100.0
