"""SCHA checks: Lam^2 scaling of E_SCHA - E_harm, convergence in N and widen, variational minimality in Deff."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import b1_lib as L  # noqa: E402

x, y = L.RHO
for lam in (1e-3, 2e-3, 4e-3, 1e-2, 2e-2, 5e-2):
    r = L.SCHA(1.0, x, y, N=32).solve(lam)
    d = r["E"] - L.harmonic_energy(1.0, x, y, lam, 32)
    print("lam", lam, "dE", d, "dE/lam^2", d / lam**2, r["status"], r["iters"])
for N, wd in ((24, 4.0), (32, 4.0), (48, 4.0), (32, 9.0)):
    r = L.SCHA(1.0, x, y, N=N, widen=wd).solve(0.1)
    print("N", N, "widen", wd, r["E"], r["status"])
s = L.SCHA(1.0, x, y, N=32)
r = s.solve(0.1)
D = r["D"]


def energy_of(Dt: np.ndarray, lam: float) -> float:
    inv, trs, lo = L.mat_sqrt_inv_and_sqrt(Dt)
    C = lam * ((s.w[:, None] * s.oneminuscos).T @ inv)
    Vc, _ = s.smoothed(C)
    return lam / 4 * float((s.w * trs).sum()) + 0.5 * float(Vc.sum())


print("E*", energy_of(D, 0.1))
rng = np.random.default_rng(1)
for scale in (0.97, 1.03):
    print("scaled", scale, energy_of(D * scale, 0.1) - energy_of(D, 0.1))
D0 = s.pg.D(s.Kappa)
for t in (0.5, 0.9):
    print("toward bare D", t, energy_of(t * D + (1 - t) * D0, 0.1) - energy_of(D, 0.1))
