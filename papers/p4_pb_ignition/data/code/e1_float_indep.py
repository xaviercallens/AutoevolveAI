"""Independent float implementation of the E1 model (Tier X). Shares only the coefficient data file.

Written separately from e1_model.py (no import from it): plain floats, scipy quadrature and root finding,
text constants of Wurzel & Hsu (C_B = 5.34e-37 W m^3 keV^-1/2, 1 keV = 1.6e-16 J, m_e c^2 = 511 keV).
Writes ../logs/float_indep.json.
"""
from __future__ import annotations

import json
import math
from typing import Callable
from pathlib import Path

import numpy as np
from scipy import integrate, optimize

HERE = Path(__file__).resolve().parent
FITS = json.loads((HERE.parent / "data" / "fits.json").read_text())
CB = 5.34e-37
KEV = 1.6e-16
MEC2 = 511.0


def f(s: str) -> float:
    if "/" in s:
        p, q = s.split("/")
        return float(p) / float(q)
    return float(s)


def bh_dt(T: float) -> float:
    c = FITS["bosch_hale_DT_reactivity"]
    C = [0.0] + [f(c[f"C{i}"]) for i in range(1, 8)]
    th = T / (1 - T * (C[2] + T * (C[4] + T * C[6])) / (1 + T * (C[3] + T * (C[5] + T * C[7]))))
    xi = (f(c["BG"]) ** 2 / (4 * th)) ** (1 / 3)
    return C[1] * th * math.sqrt(xi / (f(c["mcsquared"]) * T ** 3)) * math.exp(-3 * xi) * 1e-6


def bh_dt_integrated(T: float) -> float:
    """Code 'integrated' path: Maxwellian average of the Bosch-Hale CM cross section (Tier X only)."""
    c = FITS["bosch_hale_DT_cross_section"]
    BG = f(FITS["bosch_hale_DT_reactivity"]["BG"])
    m1, m2 = f(c["m1_keV"]), f(c["m2_keV"])
    mu = m1 * m2 / (m1 + m2)

    def S(E: float) -> float:
        p = c["low"] if E <= 550 else c["high"]
        num = f(p["A1"]) + E * (f(p["A2"]) + E * (f(p["A3"]) + E * (f(p["A4"]) + E * f(p["A5"]))))
        den = 1 + E * (f(p["B1"]) + E * (f(p["B2"]) + E * (f(p["B3"]) + E * f(p["B4"]))))
        return num / den

    def integrand(E: float) -> float:
        sig_mb = S(E) / (E * math.exp(BG / math.sqrt(E)))
        return E * sig_mb * math.exp(-E / T)

    val = integrate.quad(integrand, 0.5, 4700, points=[T, 64.0, 550.0], limit=400)[0]
    c_light = 299792458.0
    return 4 / math.sqrt(2 * math.pi * mu / c_light ** 2) * T ** -1.5 * val * 1e-31


def ns_pb(T: float) -> float:
    c = FITS["nevins_swain_pB11_reactivity_highT"]
    P = [0.0] + [f(c[f"P{i}"]) for i in range(1, 8)]
    th = T / (1 - T * (P[2] + T * (P[4] + T * P[6])) / (1 + T * (P[3] + T * (P[5] + T * P[7]))))
    xi = (f(c["EG_MeV"]) * 1000 / (4 * th)) ** (1 / 3)
    nr = P[1] * th * math.sqrt(xi / (f(c["Mrc2_keV"]) * T ** 3)) * math.exp(-3 * xi)
    return nr + f(c["res_coeff_m3s"]) * T ** -1.5 * math.exp(-f(c["res_E_keV"]) / T)


def wang_S(E: float) -> float:
    w = FITS["wang2026_pB11_S_factor"]
    if E <= 400:
        s = w["seg1"]
        return f(s["C0"]) + f(s["C1"]) * E + f(s["C2"]) * E * E + f(s["AL"]) / ((E - 148) ** 2 + 2.35 ** 2)
    if E <= 700:
        s = w["seg2"]
        x = (E - 400) / 100
        return f(s["D0"]) + f(s["D1"]) * x + f(s["D2"]) * x * x + f(s["D5"]) * x ** 5
    s = w["seg3"]
    return f(s["B"]) + sum(f(a) / ((E - 1000 * f(e)) ** 2 + (1000 * f(d)) ** 2) for a, e, d in zip(s["A"], s["E_MeV"], s["dE_MeV"]))


def wang_pb(T: float) -> float:
    EG = 22589.0
    g = lambda E: 1000 * wang_S(E) * math.exp(-math.sqrt(EG / E) - E / T)  # noqa: E731
    pts = [148, 400, 622.2, 700, 1388, 2492, 3529, 4704]
    val = integrate.quad(g, 1e-3, 10000, points=pts, limit=1000, epsabs=0, epsrel=1e-11)[0]
    mu = 859594.0
    return math.sqrt(8 / math.pi) * 299792458.0 / math.sqrt(mu) * T ** -1.5 * val * 1e-28


def gam(Te: float, z: float) -> float:
    t = Te / MEC2
    return z * (1 + 1.78 * t ** 1.34) + 2.12 * t * (1 + 1.1 * t + t * t - 1.25 * t ** 2.5)


def dt_margin(T: float, rel: bool, sv: Callable[[float], float] = bh_dt, scale: float = 1.0, cbf: float = 1.0) -> float:
    g = gam(T, 1.0) if rel else 1.0
    return 0.25 * 0.2 * scale * sv(T) * 17.6e3 * KEV - cbf * CB * math.sqrt(T) * g


def dt_tp(T: float, rel: bool, sv: Callable[[float], float] = bh_dt, scale: float = 1.0) -> float:
    g = gam(T, 1.0) if rel else 1.0
    D = 0.2 * scale * sv(T) * 17.6e3 / 4 - CB / KEV * math.sqrt(T) * g
    return 3 * T * T / D if D > 0 else math.inf


def pb_R(T: float, th: float, x: float, sv: Callable[[float], float]) -> float:
    Te = th * T
    z = (1 + 24 * x) / (1 + 4 * x)
    return x * (1 - x) * sv(T) * 8.7e3 * KEV / (CB * (1 + 4 * x) ** 2 * math.sqrt(Te) * gam(Te, z))


def theta_c(T: float, x: float, sv: Callable[[float], float]) -> float:
    """Crossing T_e/T_i where R = 1 (R decreasing in theta); 0 if R<1 for all theta in (0,1]."""
    if pb_R(T, 1.0, x, sv) >= 1:
        return 1.0
    if pb_R(T, 1e-4, x, sv) < 1:
        return 0.0
    return optimize.brentq(lambda th: pb_R(T, th, x, sv) - 1, 1e-4, 1.0, xtol=1e-12)


def main() -> None:
    out: dict[str, object] = {}
    for rel in (False, True):
        key = "rel" if rel else "nonrel"
        Tign = optimize.brentq(lambda T: dt_margin(T, rel), 1.0, 20.0, xtol=1e-12)
        r = optimize.minimize_scalar(lambda T: dt_tp(T, rel), bounds=(8, 30), method="bounded", options={"xatol": 1e-9})
        rl = optimize.minimize_scalar(lambda T: dt_tp(T, rel) / T, bounds=(10, 60), method="bounded", options={"xatol": 1e-9})
        out[f"DT_{key}_param"] = {"T_ign": Tign, "TP_Tmin": r.x, "TP_min": r.fun, "LP_Tmin": rl.x, "LP_min": rl.fun}
        Tign_i = optimize.brentq(lambda T: dt_margin(T, rel, sv=bh_dt_integrated), 1.0, 20.0, xtol=1e-10)
        ri = optimize.minimize_scalar(lambda T: dt_tp(T, rel, sv=bh_dt_integrated), bounds=(8, 30), method="bounded", options={"xatol": 1e-7})
        rli = optimize.minimize_scalar(lambda T: dt_tp(T, rel, sv=bh_dt_integrated) / T, bounds=(10, 60), method="bounded", options={"xatol": 1e-7})
        out[f"DT_{key}_integrated"] = {"T_ign": Tign_i, "TP_Tmin": ri.x, "TP_min": ri.fun, "LP_Tmin": rli.x, "LP_min": rli.fun}
    # negative controls (float view)
    out["neg_sv_half"] = {"T_ign": optimize.brentq(lambda T: dt_margin(T, False, scale=0.5), 1.0, 30.0),
                          "TP_min": optimize.minimize_scalar(lambda T: dt_tp(T, False, scale=0.5), bounds=(8, 40), method="bounded").fun}
    out["neg_no_brems_margin_at_0.2keV"] = dt_margin(0.2, False, cbf=0.0)
    Ts = np.geomspace(50, 500, 451)
    xs = np.linspace(0.05, 0.5, 91)
    for name, sv in (("NS", ns_pb), ("Wang", wang_pb)):
        svv = {float(T): sv(float(T)) for T in Ts}
        R1 = max((pb_R(T, 1.0, x, lambda _T: svv[T]), T, x) for T in svv for x in xs)
        thc = max((theta_c(T, x, lambda _T: svv[T]), T, x) for T in svv for x in xs)
        thc_mix = max((theta_c(T, 1 / 6, lambda _T: svv[T]), T) for T in svv)
        out[f"pB_{name}"] = {"maxR_theta1": R1, "theta_c_max_box": thc, "theta_c_max_x1/6": thc_mix,
                             "sv_at": {str(int(T)): svv[float(T)] for T in (50.0, 100.0, 300.0, 500.0) if float(T) in svv}}
    out["wang_over_ns"] = {str(T): wang_pb(T) / ns_pb(T) for T in (50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 500.0)}
    (HERE.parent / "logs").mkdir(exist_ok=True)
    (HERE.parent / "logs" / "float_indep.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
