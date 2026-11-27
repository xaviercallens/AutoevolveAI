"""P3: independent checks of F(tau): mpmath series (50 digits) vs Arb ball; finite-volume MOL (scipy BDF) vs series."""
from __future__ import annotations

import json
import sys

import mpmath as mp
import numpy as np
from flint import arb
from scipy.integrate import solve_ivp
from scipy.sparse import diags

sys.path.insert(0, "results/proposal4/2026-10-27/E2/code")
import spm_cert as S

mp.mp.dps = 50
OUT = "results/proposal4/2026-10-27/E2/data/"
TAUS = [0.05 * 1.25**k for k in range(20)]  # 0.05 .. about 3.4


def f_mp(tau: float) -> mp.mpf:
    t = mp.mpf(repr(tau))
    s = mp.mpf(0)
    n = 1
    while True:
        x0 = (n + mp.mpf(1) / 2) * mp.pi
        a = mp.findroot(lambda x: mp.sin(x) - x * mp.cos(x), x0 - 1 / x0)
        term = mp.e ** (-(a * a) * t) / (a * a)
        s += term
        if term < mp.mpf(10) ** -45 and n > 5:
            break
        n += 1
    return 3 * t + mp.mpf(1) / 5 - 2 * s


def f_mol(taus: list[float], N: int = 400) -> np.ndarray:
    h = 1.0 / N
    r = np.arange(N + 1) * h
    vol = (r[1:] ** 3 - r[:-1] ** 3) / 3.0
    r2 = r**2

    def rhs(_t: float, v: np.ndarray) -> np.ndarray:
        flux = np.zeros(N + 1)  # r^2 v_r at edges
        flux[1:N] = r2[1:N] * (v[1:] - v[:-1]) / h
        flux[N] = 1.0  # v_r(1) = 1 (inward flux, v = (x - x0)/beta)
        flux[0] = 0.0
        return (flux[1:] - flux[:-1]) / vol

    sp = diags([1, 1, 1], [-1, 0, 1], shape=(N, N), format="csc")
    sol = solve_ivp(rhs, (0, max(taus)), np.zeros(N), method="BDF", t_eval=taus, rtol=1e-10, atol=1e-13,
                    jac_sparsity=sp)
    assert sol.success
    return sol.y[-1] + 0.5 * h * 1.0  # surface value from last cell centre + (h/2) v_r


def main() -> None:
    rows = []
    ok_mp = True
    for t in TAUS:
        ball = S.F_ball(arb(repr(t)))
        m = f_mp(t)
        # mpmath value inside the Arb ball (the ball's radius is ~1e-30; the 50-digit mp value agrees to ~1e-40 of itself)
        inside = bool(abs(arb(mp.nstr(m, 45)) - ball.mid()).upper() <= ball.rad() * 4 + arb("1e-30"))
        ok_mp &= inside
        rows.append(dict(tau=t, arb_mid=str(ball.mid()), arb_rad=str(ball.rad()), mp=mp.nstr(m, 30), inside=inside))
    fm = f_mol(TAUS)
    rel = []
    for row, v in zip(rows, fm):
        ref = float(arb(row["arb_mid"]).mid())
        row["mol"] = repr(float(v))
        row["rel_err_mol"] = abs(v - ref) / ref
        rel.append(row["rel_err_mol"])
    out = dict(mpmath_inside_all=ok_mp, max_rel_err_mol=max(rel), mol_ok=bool(max(rel) < 1e-4), rows=rows)
    json.dump(out, open(OUT + "p3_checks.json", "w"), indent=1, default=str)
    print(ok_mp, max(rel))


main()
