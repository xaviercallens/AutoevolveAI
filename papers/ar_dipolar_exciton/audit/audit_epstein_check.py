"""Stage-4 audit (H1): Ewald-free check of the paper's lattice energies via Epstein zeta functions.

For |x| > d the potential U = V/d^2 = 2(1/r - (r^2+d^2)^{-1/2})/d^2 expands as
U = -(2/d^2) sum_{k>=1} binom(-1/2, k) d^{2k} r^{-1-2k}; summing over the lattice gives
e = (1/2) sum' U = -(1/d^2) sum_k binom(-1/2,k) d^{2k} Z(1+2k), Z(s) = sum' |x|^{-s}.
Triangular, unit spacing: sum' |m + n w|^{-2u} = 6 zeta(u) L(u, chi_{-3}); density one rescales by a^{-s},
a = sqrt(2/sqrt 3). Square, unit spacing (density one): 4 zeta(u) beta(u).
Positive control: closed-form Z(5) against a brute-force lattice sum. Negative control: using the square
lattice zeta for the triangular entry must disagree with the paper's triangular value.
"""

from __future__ import annotations

import json
import sys

import mpmath as mp

mp.mp.dps = 30


def chi_m3_L(u: mp.mpf) -> mp.mpf:
    # L(u, chi_{-3}) = 3^{-u} (zeta(u, 1/3) - zeta(u, 2/3))
    return mp.power(3, -u) * (mp.zeta(u, mp.mpf(1) / 3) - mp.zeta(u, mp.mpf(2) / 3))


def beta(u: mp.mpf) -> mp.mpf:
    return mp.power(4, -u) * (mp.zeta(u, mp.mpf(1) / 4) - mp.zeta(u, mp.mpf(3) / 4))


A_TRI = mp.sqrt(2 / mp.sqrt(3))


def z_tri(s: mp.mpf) -> mp.mpf:
    u = s / 2
    return 6 * mp.zeta(u) * chi_m3_L(u) * mp.power(A_TRI, -s)


def z_sq(s: mp.mpf) -> mp.mpf:
    u = s / 2
    return 4 * mp.zeta(u) * beta(u)


def energy(d: float, z, rmin: mp.mpf) -> mp.mpf:
    d = mp.mpf(d)
    assert d < rmin
    tot = mp.mpf(0)
    for k in range(1, 400):
        term = mp.binomial(mp.mpf(-0.5), k) * d ** (2 * k) * z(mp.mpf(1 + 2 * k))
        tot += term
        if abs(term) < mp.mpf(10) ** -25:
            break
    return -tot / d**2


def main() -> int:
    out: dict[str, object] = {}
    out["half_riesz3_tri_density1"] = float(z_tri(mp.mpf(3)) / 2)
    out["half_riesz3_sq_density1"] = float(z_sq(mp.mpf(3)) / 2)
    out["sq_over_tri_minus1_d0"] = float(z_sq(mp.mpf(3)) / z_tri(mp.mpf(3)) - 1)
    rows = []
    for d in (0.0209, 0.066, 0.114, 0.3):
        et = energy(d, z_tri, A_TRI)
        es = energy(d, z_sq, mp.mpf(1))
        rows.append({"d": d, "e_tri": float(et), "e_sq": float(es), "sq_minus_tri": float(es - et),
                     "sq_rel": float(es / et - 1)})
    out["rows"] = rows
    # negative control: swap lattices (must not reproduce the triangular entry)
    out["neg_ctl_tri_entry_from_sq_zeta_d0066"] = float(energy(0.066, z_sq, mp.mpf(1)))
    # physical-unit check of the meV gaps: E = (e^2/4 pi eps0) sqrt(n) d_tilde^2 * delta_e
    e2 = 1.43996448  # eV nm (CODATA e^2/(4 pi eps0))
    meV = []
    for n_cm2, d in ((1e11, 0.0208676), (1e12, 0.0659891), (3e12, 0.1142965)):
        sqrt_n_per_nm = (n_cm2 * 1e-14) ** 0.5
        de = energy(d, z_sq, mp.mpf(1)) - energy(d, z_tri, A_TRI)
        meV.append({"n_cm2": n_cm2, "d_tilde": d, "gap_meV": float(e2 * sqrt_n_per_nm * d * d * de * 1000)})
    out["gap_meV"] = meV
    # positive control: brute-force Z_tri(5), Z_sq(5) over |m|,|n| <= 300 (tail beyond ~ 2 pi/(3 R^3) ~ 1e-7)
    import math
    a = float(A_TRI)
    bt = 0.0
    bs = 0.0
    nmax = 300
    for m in range(-nmax, nmax + 1):
        for n in range(-nmax, nmax + 1):
            if m == 0 and n == 0:
                continue
            x = a * (m + 0.5 * n)
            y = a * (math.sqrt(3) / 2) * n
            bt += (x * x + y * y) ** -2.5
            bs += (m * m + n * n) ** -2.5
    out["pos_ctl_Z5_tri_closed_vs_brute"] = [float(z_tri(mp.mpf(5))), bt]
    out["pos_ctl_Z5_sq_closed_vs_brute"] = [float(z_sq(mp.mpf(5))), bs]
    json.dump(out, sys.stdout, indent=1)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
