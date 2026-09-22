# Specification: Micro-JEPA Non-Contrastive VICReg Engine (SPEC-ALG-VICREG)

## 1. Mathematical Formulation
VICReg (Variance-Invariance-Covariance Regularization) guarantees non-contrastive self-supervised feature learning without representation collapse:

Given two batches of embeddings $Z, Z' \in \mathbb{R}^{B \times D}$:

1. **Invariance Term:**
   $$s(Z, Z') = \frac{1}{B} \sum_{i=1}^B \|z_i - z'_i\|_2^2$$
2. **Variance Term (Hinge Regularization):**
   For each feature dimension $j \in \{1, \dots, D\}$:
   $$\sigma(z^j) = \sqrt{\frac{1}{B-1} \sum_{i=1}^B (z_{i, j} - \bar{z}_j)^2 + \epsilon}$$
   $$v(Z) = \frac{1}{D} \sum_{j=1}^D \max(0, \gamma - \sigma(z^j))$$
3. **Covariance Term (Decorrelation):**
   $$C(Z) = \frac{1}{B-1} \sum_{i=1}^B (z_i - \bar{z})(z_i - \bar{z})^T$$
   $$c(Z) = \frac{1}{D} \sum_{i \ne j} C_{ij}^2(Z)$$
4. **Total VICReg Loss:**
   $$\mathcal{L}(Z, Z') = \lambda s(Z, Z') + \mu (v(Z) + v(Z')) + \nu (c(Z) + c(Z'))$$

## 2. Formal Invariant Alignment
Directly operationalizes **Theorem B6** from `formal/ANSE/JEPA.lean`:
$$\mathcal{L} = 0 \implies \forall j, \; \sigma(z^j) \ge \gamma$$
proving zero representation collapse.

## 3. API Contract
```python
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class VICRegLossResult:
    total_loss: float
    invariance_loss: float
    variance_loss_z: float
    variance_loss_z_prime: float
    covariance_loss_z: float
    covariance_loss_z_prime: float
    collapse_detected: bool

def compute_vicreg_loss(
    z: np.ndarray,
    z_prime: np.ndarray,
    sim_coeff: float = 25.0,
    std_coeff: float = 25.0,
    cov_coeff: float = 1.0,
    gamma: float = 1.0,
    epsilon: float = 1e-4,
) -> VICRegLossResult:
    ...
```
