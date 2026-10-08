"""Tests for scripts/openai_math/lt_matrix/kinetic_dual.py (H-LT5 dual kinetic instrument)."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "openai_math" / "lt_matrix"))
from kinetic_dual import (PI2_3, PI2_4, evaluate_numpy, kinetic_and_cubic, orthonormal_coefficients,  # noqa: E402
                          padded_to_larger_basis, project_sech_half, quotient, run_search)


def _random_raw(m: int, K: int, N: int, seed: int) -> torch.Tensor:
    g = torch.Generator().manual_seed(seed)
    return torch.complex(torch.randn(m * K, N, generator=g, dtype=torch.float64),
                         torch.randn(m * K, N, generator=g, dtype=torch.float64))


def test_qr_gives_orthonormal_columns_and_unit_norm_functions() -> None:
    q = orthonormal_coefficients(_random_raw(2, 12, 3, 1))
    gram = (q.conj().T @ q).detach().numpy()
    assert np.abs(gram - np.eye(3)).max() < 1e-12
    # sum_j int tr rho = N (each function has unit L2 norm): check through the exact grid on M > 6K
    m, K, L, M = 2, 12, 3.0, 6 * 12 + 8
    from kinetic_dual import sine_values
    psi = sine_values(q.reshape(m, K, 3).permute(0, 2, 1), M) / math.sqrt(L)
    mass = (2 * L / M) * (psi.abs() ** 2).sum()
    assert float(mass) == pytest.approx(3.0, rel=1e-12)


def test_cubic_integral_is_exact_and_matches_independent_numpy_path() -> None:
    m, K, N, L = 2, 10, 3, 4.0
    raw = _random_raw(m, K, N, 2)
    j_small = float(quotient(raw, m, K, L, 6 * K + 4))
    j_big = float(quotient(raw, m, K, L, 8 * (6 * K + 4)))
    assert j_small == pytest.approx(j_big, rel=1e-12)
    q = orthonormal_coefficients(raw).detach().numpy()
    assert evaluate_numpy(q, m, K, L, 4096)["J"] == pytest.approx(j_big, rel=1e-10)
    with pytest.raises(ValueError):
        quotient(raw, m, K, L, 6 * K)  # a non-exact grid is refused


def test_unitary_mixing_of_components_leaves_quotient_invariant_and_basis_padding_too() -> None:
    m, K, N, L = 2, 8, 2, 3.0
    q = orthonormal_coefficients(_random_raw(m, K, N, 3)).detach()
    j0 = float(quotient(q, m, K, L, 6 * K + 8))
    th = 0.7
    U = torch.tensor([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]], dtype=torch.complex128)
    mixed = torch.einsum("ab,bkn->akn", U, q.reshape(m, K, N)).reshape(m * K, N)
    assert float(quotient(mixed, m, K, L, 6 * K + 8)) == pytest.approx(j0, rel=1e-12)
    q2 = padded_to_larger_basis(q, m, K, 2 * K)
    assert float(quotient(q2, m, 2 * K, L, 6 * 2 * K + 8)) == pytest.approx(j0, rel=1e-12)


def test_sech_half_projection_is_above_pi2_over_4_and_close() -> None:
    K, L = 256, 60.0
    c = project_sech_half(K, L)
    c = c / torch.linalg.vector_norm(c)
    kin, cub = kinetic_and_cubic(c.reshape(K, 1), 1, K, L, 2048)
    j = float(kin / cub)
    assert j >= PI2_4 * (1 - 1e-12)
    assert j == pytest.approx(PI2_4, rel=1e-3)


def test_free_fermion_limit_is_above_pi2_over_4_and_near_pi2_over_3() -> None:
    N, K = 30, 48
    q = torch.eye(K, dtype=torch.complex128)[:, :N]
    kin, cub = kinetic_and_cubic(q, 1, K, 1.0, 512)
    j = float(kin / cub)
    assert j > PI2_4
    assert j == pytest.approx(PI2_3, rel=0.1)


def test_negative_control_wrong_constant_is_violated_immediately() -> None:
    wrong = 0.99 * PI2_3
    j, _ = run_search(1, 1, 48, 20.0, 512, 3004, adam_steps=100, target=wrong)
    assert j < wrong
    assert j >= PI2_4 * (1 - 1e-9)  # but never below the claimed sharp constant


def test_direct_gauss_legendre_evaluation_agrees_with_fft_paths() -> None:
    from kinetic_dual import evaluate_direct

    m, K, N, L = 2, 12, 2, 4.0
    q = orthonormal_coefficients(_random_raw(m, K, N, 5)).detach().numpy()
    direct = evaluate_direct(q, m, K, L, panels=2000, pts=8)
    fft = evaluate_numpy(q, m, K, L, 1024)
    assert direct["J"] == pytest.approx(fft["J"], rel=1e-10)
    assert direct["kinetic"] == pytest.approx(fft["kinetic"], rel=1e-12)
