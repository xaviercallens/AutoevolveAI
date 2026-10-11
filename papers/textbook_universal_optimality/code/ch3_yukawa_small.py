"""Chapter 3 companion (Tier X): relax a small periodic Yukawa system with L-BFGS and compare with the lattice.

Model as in rusty-SUNDIALS qf-yukawa-crystal: V(r) = exp(-kappa r)/r, shifted-force cutoff rc, periodic box that
holds n x 2n triangular sites (N = 2 n^2) at density 1. L-BFGS is a minimiser, not the CVODE gradient flow.
Usage: python ch3_yukawa_small.py [n] [kappa] [rc]
"""
from __future__ import annotations
import sys
import numpy as np
from scipy.optimize import minimize
n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
KAPPA = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
RC = float(sys.argv[3]) if len(sys.argv) > 3 else 6.0
A = np.sqrt(2.0 / np.sqrt(3.0))                      # triangular spacing at density 1
L = np.array([n * A, n * np.sqrt(3.0) * A])          # box n a x n sqrt(3) a, area N
N = 2 * n * n
v = lambda r: np.exp(-KAPPA * r) / r                  # noqa: E731
dv = lambda r: -np.exp(-KAPPA * r) * (KAPPA * r + 1.0) / r**2  # noqa: E731
VC, DVC = v(RC), dv(RC)
M = np.ceil(RC / L + 0.5).astype(int)                # image shells needed beyond the minimum image
SHIFTS = np.array([(i * L[0], j * L[1]) for i in range(-M[0], M[0] + 1) for j in range(-M[1], M[1] + 1)])

def energy_grad(flat: np.ndarray) -> tuple[float, np.ndarray]:
    """E = (1/2) sum_{i,j,images} V_sf(r) and its gradient (sum over all images inside rc)."""
    x = flat.reshape(N, 2)
    d = x[:, None, :] - x[None, :, :]
    d = d - L * np.round(d / L)
    d = d[:, :, None, :] + SHIFTS[None, None, :, :]
    r = np.linalg.norm(d, axis=-1)
    inside = (r < RC) & (r > 1e-12)
    rs = np.where(inside, r, RC)
    e = np.where(inside, v(rs) - VC - (rs - RC) * DVC, 0.0)
    g = np.where(inside, dv(rs) - DVC, 0.0)
    return 0.5 * float(e.sum()), ((g / rs)[..., None] * d).sum(axis=(1, 2)).ravel()

def triangular() -> np.ndarray:
    return np.array([((i + 0.5 * (j % 2) + 0.25) * A, (j + 0.5) * A * np.sqrt(3.0) / 2.0)
                     for j in range(2 * n) for i in range(n)])

def lattice_sum() -> float:
    """Direct sum (1/2) sum_{v != 0} V_sf(|v|) over the infinite triangular lattice."""
    m = int(RC / (A * np.sqrt(3.0) / 2.0)) + 3
    tot = 0.0
    for i in range(-m, m + 1):
        for j in range(-m, m + 1):
            r = np.hypot(i * A + 0.5 * j * A, j * A * np.sqrt(3.0) / 2.0)
            if 0.0 < r < RC:
                tot += v(r) - VC - (r - RC) * DVC
    return 0.5 * tot

def defects(x: np.ndarray) -> int:
    d = x[:, None, :] - x[None, :, :]
    r = np.linalg.norm(d - L * np.round(d / L), axis=-1) + np.eye(N) * 1e9
    return int(((r < 1.35 * np.median(r.min(axis=1))).sum(axis=1) != 6).sum())

def random_start(rng: np.random.Generator, dmin: float) -> np.ndarray:
    pts: list[np.ndarray] = []
    while len(pts) < N:
        p = rng.uniform(0.0, 1.0, 2) * L
        if all(np.linalg.norm((p - q) - L * np.round((p - q) / L)) >= dmin for q in pts):
            pts.append(p)
    return np.array(pts)

def relax(x0: np.ndarray) -> tuple[float, float, int, np.ndarray]:
    res = minimize(energy_grad, x0.ravel(), jac=True, method="L-BFGS-B",
                   options={"maxiter": 50000, "gtol": 1e-10, "ftol": 1e-15})
    return res.fun / N, float(np.abs(res.jac).max()), res.nit, res.x.reshape(N, 2) % L

lat = triangular()
e_box = energy_grad(lat.ravel())[0] / N
print(f"N={N} kappa={KAPPA} rc={RC} box={L[0]:.6f}x{L[1]:.6f}")
print(f"e_tri box sum = {e_box:.12f}  direct lattice sum = {lattice_sum():.12f}")
rng = np.random.default_rng(0)
starts = [("perturbed lattice 0.1a", lat + 0.1 * A * rng.normal(size=lat.shape))]
starts += [(f"random start seed {s}", random_start(np.random.default_rng(s), 0.5 * A)) for s in range(1, 6)]
for name, x0 in starts:
    e, gmax, nit, x = relax(x0)
    print(f"{name:24s} e-e_tri = {e - e_box: .3e}  max|grad| = {gmax:.1e}  iters = {nit:5d}  defects = {defects(x)}")
