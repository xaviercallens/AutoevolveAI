---
name: computational-physics-engine
description: High-fidelity computational physics code generation across symplectic mechanics, general relativity, quantum field theory, lattice QCD, and topological quantum error correction. Use this skill when modeling physical systems, asserting conservation laws, or implementing numerical PDE/ODE physics simulations.
---

# Computational Physics Engine Skill

This skill governs the generation and verification of physical simulation engines in AutoevolveAI / ANSE, enforcing the **Physics of Computation** paradigm: every physical model must satisfy exact physical conservation laws and thermodynamic invariants.

---

## 1. Physical Domains & Conservation Invariants

| Physics Domain | Invariant Condition | Failure Criteria ($E = 10^6$) |
| :--- | :--- | :--- |
| **Symplectic Hamiltonian Mechanics** | Energy Drift: $\left\|\frac{H(t) - H(0)}{H(0)}\right\| < 10^{-4}$; Symplectic 2-form: $\omega = \sum dq_i \wedge dp_i$ preserved. | Non-symplectic drift $\Delta H / H_0 > 10^{-3}$; Phase-space volume contraction/expansion. |
| **Relativistic Kerr Black Hole Geodesics** | Carter Constant: $\left\|\frac{K(\tau) - K(0)}{K(0)}\right\| < 10^{-10}$; Rest mass invariant: $g_{\mu\nu} u^\mu u^\nu = -\mu^2$. | Unbounded Carter drift; Geodesic violation of horizon boundary conditions. |
| **Relativistic QED & Gauge Invariance** | Ward-Takahashi Identity: $k_\mu M^\mu = 0.00$ ($|k \cdot M| < 10^{-12}$); Mandelstam relation: $s + t + u = \sum m_i^2$. | Longitudinal photon polarization coupling; Lorentz non-invariance. |
| **Non-Abelian Lattice Gauge Theory (QCD)** | Wilson Plaquette Gauge Invariance: $\mathrm{Tr}(U_{\mu\nu}) = \mathrm{Tr}(g_x U_{\mu\nu} g_x^\dagger)$; Mass gap $\Delta m > 0$. | Plaquette trace violation; Gauge symmetry breaking on spatial links. |
| **Topological Quantum Error Correction** | Commuting Stabilizer Group: $[S_i, S_j] = 0$; Logical error suppression: $P_L \propto p^{(d+1)/2}$. | Non-commuting syndrome checks; Unsuppressed fault propagation. |
| **Cosmology & Singularity Congruence** | Raychaudhuri Focal Singularity: $\tau_{\text{focus}} = \frac{3}{\|\theta_0\|}$; Ricci curvature focusing $R_{\mu\nu} k^\mu k^\nu \ge 0$. | Defocusing under attractive gravity; Riccati integration divergence error $> 10^{-6}$. |

---

## 2. Core Operational Protocols

1. **Symplectic Integration Protocol:**
   - Never use standard explicit Euler or generic Runge-Kutta for long-term orbital or Hamiltonian dynamics.
   - Use **Velocity-Verlet** (2nd-order) or **Yoshida 4th-order** symplectic integrators to guarantee zero secular energy drift.
2. **C-ABI / SIMD Acceleration Protocol:**
   - Inner loop physics kernels must leverage vectorized NumPy, PyTorch C-ABI, or Rust SIMD (`anse/physics/`, `libanse_physics.so`).
   - Profile performance to guarantee low physical latency and minimal memory footprint ($E = \text{duration\_ms} + 0.1 \times \text{peak\_ram\_mb}$).
3. **Formal Theorem Grounding:**
   - Anchor relativistic conservation and error correction properties in Lean 4 specifications in `formal/ANSE/` (`KerrSymplectic.lean`, `StabilizerCode.lean`, `GaussBonnet.lean`).

---

## 3. Reference Implementation: 4th-Order Yoshida Symplectic Integrator

```python
"""4th-Order Yoshida Symplectic Integrator for Hamiltonian Systems H(q, p) = T(p) + V(q)."""
from __future__ import annotations
import numpy as np

# Yoshida 4th-order integration coefficients
_CR3 = 2.0 ** (1.0 / 3.0)
_W0 = -_CR3 / (2.0 - _CR3)
_W1 = 1.0 / (2.0 - _CR3)
_C = np.array([_W1 / 2.0, (_W0 + _W1) / 2.0, (_W0 + _W1) / 2.0, _W1 / 2.0])
_D = np.array([_W1, _W0, _W1])

def yoshida4_step(
    q: np.ndarray,
    p: np.ndarray,
    grad_v_fn: Any,
    inv_mass: float | np.ndarray,
    dt: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Advances (q, p) by dt preserving the symplectic 2-form dq ^ dp."""
    q_curr = q.copy()
    p_curr = p.copy()
    
    # 4 stages
    for step in range(4):
        # Drift q
        q_curr += _C[step] * dt * (p_curr * inv_mass)
        # Kick p (for first 3 stages)
        if step < 3:
            grad_v = grad_v_fn(q_curr)
            p_curr -= _D[step] * dt * grad_v
            
    return q_curr, p_curr

def simulate_henon_heiles_orbit(
    q0: np.ndarray,
    p0: np.ndarray,
    dt: float = 0.01,
    steps: int = 10000,
) -> tuple[float, float]:
    """Simulates Henon-Heiles non-linear potential and returns max relative energy drift."""
    def grad_v(q: np.ndarray) -> np.ndarray:
        x, y = q[0], q[1]
        return np.array([x + 2.0 * x * y, y + (x**2 - y**2)])
    
    def hamiltonian(q: np.ndarray, p: np.ndarray) -> float:
        x, y = q[0], q[1]
        kinetic = 0.5 * np.sum(p**2)
        potential = 0.5 * (x**2 + y**2) + (x**2 * y - (y**3) / 3.0)
        return float(kinetic + potential)
    
    h0 = hamiltonian(q0, p0)
    q, p = q0.copy(), p0.copy()
    max_drift = 0.0
    
    for _ in range(steps):
        q, p = yoshida4_step(q, p, grad_v, 1.0, dt)
        h_t = hamiltonian(q, p)
        drift = abs(h_t - h0) / abs(h0)
        if drift > max_drift:
            max_drift = drift
            
    assert max_drift < 1e-4, f"Symplectic energy drift exceeded bound: {max_drift:.3e} >= 1e-4"
    return max_drift, h0
```

---

## 4. Verification Commands

```bash
# 1. Run full 10-problem pure physics benchmark suite
uv run python -m anse.benchmark.pure_physics_cases

# 2. Run relativistic Kerr orbit & lattice instanton verification
uv run pytest tests/test_symplectic_physics_profile.py -v

# 3. Audit anti-stub compliance across physics modules
uv run python -m antigravity_harness audit anse/physics/
```
