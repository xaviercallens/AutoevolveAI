"""
Tests for Banach Fixed-Point Contraction Engine.

Validates geometric convergence, Lipschitz constant estimation,
and Dottie number / linear system convergence against analytical solutions.
"""

from __future__ import annotations

import math
import numpy as np
import pytest

from anse.algorithms.fixed_point import solve_banach_fixed_point, estimate_lipschitz_constant, FixedPointResult


class TestFixedPoint:
    """Test suite for Banach fixed point contraction solver."""

    def test_dottie_number_cosine_fixed_point(self) -> None:
        # Scalar operator Phi(x) = cos(x) on [0, 1] is a contraction with L = sin(1) ~ 0.841
        def op(x: np.ndarray) -> np.ndarray:
            return np.cos(x)

        x0 = np.array([0.5])
        res = solve_banach_fixed_point(op, x0, tol=1e-7, max_iter=100)

        assert res.converged is True
        # Dottie number is approximately 0.7390851332
        dottie = 0.7390851332
        assert math.isclose(float(res.fixed_point[0]), dottie, abs_tol=1e-5)
        assert res.residual < 1e-7
        assert res.estimated_lipschitz < 1.0

    def test_affine_contraction_linear_system(self) -> None:
        # Phi(x) = A x + b with ||A||_2 < 1.
        # Fixed point x* = (I - A)^(-1) b.
        a = np.array([[0.2, 0.1], [0.1, 0.3]])
        b = np.array([1.0, 2.0])

        def op(x: np.ndarray) -> np.ndarray:
            return a @ x + b

        # Analytical solution
        expected_x = np.linalg.inv(np.eye(2) - a) @ b

        x0 = np.zeros(2)
        res = solve_banach_fixed_point(op, x0, tol=1e-8, max_iter=50)

        assert res.converged is True
        np.testing.assert_allclose(res.fixed_point, expected_x, rtol=1e-5, atol=1e-5)
        # Residuals must contract monotonically
        for k in range(len(res.history) - 1):
            assert res.history[k + 1] < res.history[k]

    def test_lipschitz_constant_estimation(self) -> None:
        # Phi(x) = 0.5 * x has Lipschitz L = 0.5
        def op(x: np.ndarray) -> np.ndarray:
            return 0.5 * x

        pairs = [
            (np.array([1.0, 2.0]), np.array([3.0, 4.0])),
            (np.array([0.0, 0.0]), np.array([10.0, 10.0])),
        ]
        l_est = estimate_lipschitz_constant(op, pairs)
        assert math.isclose(l_est, 0.5, abs_tol=1e-6)

    def test_divergence_detection(self) -> None:
        # Diverging linear system Phi(x) = 2.0 * x + 1.0
        def op(x: np.ndarray) -> np.ndarray:
            return 2.0 * x + 1.0

        x0 = np.array([1.0])
        res = solve_banach_fixed_point(op, x0, tol=1e-6, max_iter=10)
        # Should not converge within max_iter
        assert res.converged is False
        assert res.residual > 1.0
