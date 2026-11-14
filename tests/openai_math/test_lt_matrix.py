"""Tests for scripts/openai_math/lt_matrix/instrument.py (matrix Lieb-Thirring lab)."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "openai_math" / "lt_matrix"))
from instrument import (Blobs, Grid, equality_potential, numerator_denominator, ratio, semiclassical_constant,  # noqa: E402
                        sharp_constant, verdict)


def test_known_constants() -> None:
    assert sharp_constant(1.5) == pytest.approx(3 / 16, rel=1e-12)  # Lieb-Thirring / KdV endpoint
    assert sharp_constant(0.5) == pytest.approx(0.5, rel=1e-12)  # Hundertmark-Lieb-Thomas endpoint
    assert semiclassical_constant(1.5) == pytest.approx(3 / 16, rel=1e-12)
    # dual kinetic constant at gamma = 1: 4 / (27 L1^2) = pi^2 / 4
    assert 4 / (27 * sharp_constant(1.0) ** 2) == pytest.approx(math.pi**2 / 4, rel=1e-5)
    # one-bound-state constant is above the semiclassical one below 3/2 and below it above 3/2
    assert sharp_constant(1.0) > semiclassical_constant(1.0)
    assert sharp_constant(3.0) < semiclassical_constant(3.0)


def test_equality_potential_has_one_bound_state_at_minus_one() -> None:
    g = Grid(24.0, 160, 1200)
    for gamma in (1.0, 1.25):
        num, den, neg = numerator_denominator(equality_potential(gamma, g), gamma, g)
        assert neg.numel() == 1
        assert float(neg.max()) == pytest.approx(1.0, abs=1e-5)
        excess = float(num / den) / sharp_constant(gamma) - 1.0
        assert abs(excess) < 2e-6
        assert excess < 1e-9  # one-sided: the discretisation can only lose


def test_rayleigh_ritz_numerator_is_monotone_in_basis_size() -> None:
    gamma = 1.0
    nums = []
    for M in (64, 96, 128):
        g = Grid(24.0, M, 1500)
        nums.append(float(numerator_denominator(equality_potential(gamma, g), gamma, g)[0]))
    assert nums[0] <= nums[1] + 1e-9 <= nums[2] + 2e-9
    assert nums[2] < 1.0 + 1e-9  # the true numerator (one eigenvalue -1) is an upper limit


def test_matrix_embedding_and_constant_unitary_invariance() -> None:
    g = Grid(24.0, 128, 1000)
    gamma = 1.0
    base = equality_potential(gamma, g)
    for m in (2, 3):
        W = torch.zeros(g.Q, m, m, dtype=torch.complex128)
        W[:, 0, 0] = base[:, 0, 0]
        U = torch.linalg.qr(torch.randn(m, m, dtype=torch.complex128, generator=torch.Generator().manual_seed(m)))[0]
        r_scalar, r_embed, r_dressed = ratio(base, gamma, g), ratio(W, gamma, g), ratio(U @ W @ U.conj().T, gamma, g)
        assert r_embed == pytest.approx(r_scalar, abs=1e-12)
        assert r_dressed == pytest.approx(r_embed, abs=1e-12)


def test_x_dependent_rotation_is_not_a_symmetry() -> None:
    """A position-dependent rotation changes the ratio, so the matrix problem is genuinely different from the scalar one."""
    g = Grid(24.0, 128, 1000)
    gamma = 1.0
    w = equality_potential(gamma, g)[:, 0, 0].real
    theta = 0.8 * torch.tanh(g.x)
    c, s = torch.cos(theta), torch.sin(theta)
    u = torch.stack([c, s], dim=1).to(torch.complex128)  # unit vector u(x)
    W_rot = w[:, None, None].to(torch.complex128) * (u[:, :, None] * u[:, None, :].conj())
    W_fix = torch.zeros_like(W_rot)
    W_fix[:, 0, 0] = w
    assert abs(ratio(W_rot, gamma, g) - ratio(W_fix, gamma, g)) > 1e-6
    # both stay below the claimed bound (this is the claim under test; failure here would be a discovery)
    assert ratio(W_rot, gamma, g) <= sharp_constant(gamma) * (1 + 1e-6)


def test_blobs_contains_the_exact_scalar_optimiser() -> None:
    g = Grid(24.0, 64, 600)
    gamma = 1.25
    r = 1.0 / (gamma - 0.5)
    mdl = Blobs(1, 1, 4, 0)
    with torch.no_grad():
        mdl.cr.zero_(); mdl.ci.zero_(); mdl.x0.zero_()
        mdl.logk.fill_(math.log(r)); mdl.cr[0, 0, 0, 0] = math.sqrt(r + 1)
        W = mdl.W(g.x)
    assert float((W - equality_potential(gamma, g)).abs().max()) < 1e-12
    assert W.shape == (g.Q, 1, 1)


def test_verdict_is_interval_style_and_abstaining() -> None:
    L1 = 0.245
    assert verdict(L1 * (1 + 1e-4), L1) == "CANDIDATE_VIOLATION"
    assert verdict(L1 * (1 + 1e-8), L1) == "WITHIN_TOLERANCE"
    assert verdict(L1 * (1 - 1e-3), L1) == "BELOW"
