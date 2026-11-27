"""Tests for scripts/openai_math/lt_matrix/structure_lt2.py (H-LT2 commutator statistic)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("torch")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "openai_math" / "lt_matrix"))
from structure_lt2 import commutator_statistic  # noqa: E402


def _solitons(n: int = 801) -> tuple[np.ndarray, np.ndarray]:
    x = np.linspace(-12, 12, n)
    return x, 1.0 / np.cosh(x) ** 2


def test_direct_sum_of_scalar_solitons_has_zero_commutator_statistic() -> None:
    x, s = _solitons()
    W = np.zeros((len(x), 2, 2), dtype=complex)
    W[:, 0, 0] = s
    W[:, 1, 1] = 0.5 / np.cosh(2 * (x - 3)) ** 2
    st = commutator_statistic(W)
    assert st["C"] < 1e-12
    assert st["n_eig_max"] == 2


def test_negative_control_position_dependent_rotation_has_large_statistic() -> None:
    x, s = _solitons()
    th = 0.5 * x
    W = np.zeros((len(x), 2, 2), dtype=complex)
    for i in range(len(x)):
        U = np.array([[np.cos(th[i]), -np.sin(th[i])], [np.sin(th[i]), np.cos(th[i])]])
        W[i] = U @ np.diag([s[i], 0.2 * s[i]]) @ U.T
    st = commutator_statistic(W)
    assert st["C"] > 0.05
    assert st["region_points_used"] > 10


def test_constant_unitary_conjugation_keeps_statistic_zero() -> None:
    x, s = _solitons()
    D = np.zeros((len(x), 2, 2), dtype=complex)
    D[:, 0, 0], D[:, 1, 1] = s, 0.3 * s
    U = np.array([[1, 1j], [1j, 1]]) / np.sqrt(2)
    W = U @ D @ U.conj().T
    assert commutator_statistic(W)["C"] < 1e-12
    assert commutator_statistic(W)["n_eig_min"] == 2
