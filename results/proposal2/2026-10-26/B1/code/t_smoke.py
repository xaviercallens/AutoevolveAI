"""Smoke test of b1_lib against P2 reference values (E_zp gauss:1 at rho and at 0.5+0.966i, Lap E_static, c_zp)."""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b1_lib as L  # noqa: E402

t = time.time()
for N in (32, 48, 64, 96):
    print(N, L.e_zp(1, 0.5, L.S3 / 2, N), L.e_zp(1, 0.5, 0.966025403784, N), L.u2_harmonic_per_lam(1, 0.5, L.S3 / 2, N))
print("t", time.time() - t)
print("lapS exact", L.lap_static_exact(1.0))
print("lapS stencil", L.lap_stencil(lambda x, y: L.e_static(1.0, x, y), *L.RHO))
t = time.time()
z = L.lap_stencil(lambda x, y: L.e_zp(1.0, x, y, 48), *L.RHO)
print("lapZ", z, "c_zp", z["lap"] / 4, time.time() - t)
print(L.quick_stable(1, 0.5, L.S3 / 2), L.quick_stable(1, 0, 1))
for lam in (0.0, 1e-3, 0.05, 0.124):
    t = time.time()
    s = L.SCHA(1.0, 0.5, L.S3 / 2, N=32)
    r = s.solve(lam)
    print("SCHA", lam, r["E"], r["status"], r["iters"], r["u2"], "harm", L.harmonic_energy(1.0, 0.5, L.S3 / 2, lam, 32), time.time() - t)
