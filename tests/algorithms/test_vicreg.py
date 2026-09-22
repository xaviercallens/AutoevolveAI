"""
Tests for Micro-JEPA Non-Contrastive VICReg Loss Engine.

Validates invariance MSE, variance hinge, covariance decorrelation,
and collapse detection matching formal Lean 4 specifications.
"""

from __future__ import annotations

import math
import numpy as np
import pytest

from anse.algorithms.vicreg import compute_vicreg_loss, VICRegLossResult


class TestVICRegLoss:
    """Test suite for VICReg loss calculation and collapse detection."""

    def test_shape_mismatch_raises(self) -> None:
        z = np.zeros((10, 4))
        z_prime = np.zeros((10, 5))
        with pytest.raises(ValueError, match="Shape mismatch"):
            compute_vicreg_loss(z, z_prime)

    def test_batch_size_under_two_raises(self) -> None:
        z = np.zeros((1, 4))
        with pytest.raises(ValueError, match="Batch size must be at least 2"):
            compute_vicreg_loss(z, z)

    def test_collapse_detection_on_constant_embeddings(self) -> None:
        # All embeddings identical (constant zero vector) -> complete representation collapse
        z = np.zeros((16, 8))
        res = compute_vicreg_loss(z, z)
        assert res.invariance_loss == 0.0
        # Variance loss should be near gamma (1.0) because std is ~0
        assert res.variance_loss_z > 0.98
        assert res.collapse_detected is True
        assert res.total_loss > 0.0

    def test_ideal_uncorrelated_standard_normal(self) -> None:
        # Generate independent standard normal vectors (large batch)
        np.random.seed(42)
        b, d = 2000, 4
        # Orthogonal components scaled to unit variance
        q, _ = np.linalg.qr(np.random.randn(b, d))
        z = q * math.sqrt(b - 1)
        z_prime = z.copy()

        res = compute_vicreg_loss(z, z_prime, gamma=1.0)
        # Invariance should be exactly 0
        assert math.isclose(res.invariance_loss, 0.0, abs_tol=1e-6)
        # Variance loss should be ~0 because each column has std ~ 1.0
        assert res.variance_loss_z < 0.05
        # Covariance loss should be ~0 because columns are orthogonal
        assert res.covariance_loss_z < 0.05
        assert res.collapse_detected is False

    def test_nonnegativity_invariants(self) -> None:
        # For arbitrary representations, all components must be non-negative
        np.random.seed(123)
        z = np.random.randn(32, 16)
        z_prime = np.random.randn(32, 16)

        res = compute_vicreg_loss(z, z_prime)
        assert res.invariance_loss >= 0.0
        assert res.variance_loss_z >= 0.0
        assert res.variance_loss_z_prime >= 0.0
        assert res.covariance_loss_z >= 0.0
        assert res.covariance_loss_z_prime >= 0.0
        assert res.total_loss >= 0.0
