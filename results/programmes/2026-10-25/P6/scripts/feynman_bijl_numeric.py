"""Tier X float check of the Lean Feynman-Bijl statements (P6, programmes 2026-10-25).

Never supports a claim on its own; it only cross-checks the Lean theorems on random instances and
shows that the controls behave as expected.

Checks
  POS-1  double-commutator identity  <psi|[r^+,[H,r]]|psi> = A(r) + A(r^+)  (random H, random r)
  POS-2  symmetric r (r = r^+): A(r) = f/2, trial excess = f/(2 N S), and the lowest eigenvalue
         in the sector excited by r is <= E0 + f/(2 N S)
  POS-3  Bogoliubov: hbar^2 k^2/(2 m S_B) = eps_B and S_B <= sqrt(k/(2 k*))
  NEG-1  2x2 raising operator (Lean symmetry_needed): A(r) = 1, f/2 = 0.5
  NEG-2  random non-symmetric r: |A(r) - f/2| / |f| is nonzero (reported min and median), i.e.
         without the symmetry hypothesis A(r) = f/2 does not hold
  NEG-3  planted false claim A(r) = f must fail on POS-2 instances
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np


def herm(rng: np.random.Generator, n: int) -> np.ndarray:
    a = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
    return (a + a.conj().T) / 2


def comm(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a @ b - b @ a


def excess(h: np.ndarray, e0: float, psi: np.ndarray, x: np.ndarray) -> complex:
    v = x @ psi
    return complex(np.vdot(v, h @ v) - e0 * np.vdot(v, v))


def main() -> int:
    rng = np.random.default_rng(20261025)
    out: dict[str, object] = {}
    n, trials = 12, 200
    res1, res2a, res2b, sector_ok, neg2, neg3_caught = [], [], [], 0, [], 0
    for _ in range(trials):
        h = herm(rng, n)
        w, v = np.linalg.eigh(h)
        e0, psi = float(w[0]), v[:, 0]
        r = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
        f = complex(np.vdot(psi, comm(r.conj().T, comm(h, r)) @ psi))
        res1.append(abs(f - (excess(h, e0, psi, r) + excess(h, e0, psi, r.conj().T))) / abs(f))
        neg2.append(abs(excess(h, e0, psi, r) - f / 2) / abs(f))
        rs = herm(rng, n)
        fs = complex(np.vdot(psi, comm(rs, comm(h, rs)) @ psi)).real
        a = excess(h, e0, psi, rs).real
        nS = float(np.vdot(rs @ psi, rs @ psi).real)  # N S = ||r psi||^2
        res2a.append(abs(a - fs / 2) / abs(fs))
        phi = rs @ psi / np.sqrt(nS)
        res2b.append(abs((np.vdot(phi, h @ phi).real - e0) - fs / (2 * nS)) / abs(fs))
        overlaps = np.abs(v.conj().T @ (rs @ psi))
        sector = w[overlaps > 1e-9 * overlaps.max()]
        if sector.min() - e0 <= fs / (2 * nS) + 1e-10:
            sector_ok += 1
        if abs(a - fs) > 1e-6 * abs(fs):
            neg3_caught += 1
    out["POS-1_max_rel_residual"] = max(res1)
    out["POS-2_max_rel_residual_A_eq_f_half"] = max(res2a)
    out["POS-2_max_rel_residual_trial_energy"] = max(res2b)
    out["POS-2_sector_bound_holds"] = f"{sector_ok}/{trials}"
    out["NEG-2_rel_gap_A_minus_f_half_min_median"] = [float(np.min(neg2)), float(np.median(neg2))]
    out["NEG-3_planted_A_eq_f_caught"] = f"{neg3_caught}/{trials}"
    # NEG-1: H = |e1><e1|, psi = e0, r = |e1><e0|
    h2 = np.array([[0, 0], [0, 1]], dtype=complex)
    r2 = np.array([[0, 0], [1, 0]], dtype=complex)
    psi2 = np.array([1, 0], dtype=complex)
    f2 = complex(np.vdot(psi2, comm(r2.conj().T, comm(h2, r2)) @ psi2))
    out["NEG-1_A_rho"] = excess(h2, 0.0, psi2, r2).real
    out["NEG-1_A_rho_dag"] = excess(h2, 0.0, psi2, r2.conj().T).real
    out["NEG-1_f"] = f2.real
    # POS-3 Bogoliubov, hbar = m = c = 1 (ks = 2)
    ks, ok_eq, ok_h8 = 2.0, 0.0, 0
    ks_grid = np.linspace(0.01, 20, 2000)
    for k in ks_grid:
        e0f = k**2 / ks
        eb = np.sqrt(k**2 + (k**2 / ks) ** 2)
        sb = e0f / eb
        ok_eq = max(ok_eq, abs(k**2 / (2 * sb) - eb) / eb)
        ok_h8 += int(sb <= np.sqrt(k / (2 * ks)) + 1e-15)
    out["POS-3_max_rel_resid_feynman_eq_epsB"] = ok_eq
    out["POS-3_H8_bound_holds"] = f"{ok_h8}/{len(ks_grid)}"
    dest = Path(sys.argv[1])
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
