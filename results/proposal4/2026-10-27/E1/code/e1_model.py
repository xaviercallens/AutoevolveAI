"""E1 model in Arb ball arithmetic (python-flint 0.6.0).

0-D ideal-ignition power balance of Wurzel & Hsu (arXiv 2105.10954, eqs 6-8, 16, 22, 41, D1-D5),
bremsstrahlung with the relativistic fit (W-H eq D2 = Ochs-Fisch eq 14, x^2 term included).

All functions take Arb balls (intervals) and return Arb balls that contain every value of the
function over the input balls (standard interval semantics of Arb). Coefficients come from
../data/fits.json (verbatim decimal strings).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/.scratchpad/b2_pylib")
from flint import arb, acb, ctx  # noqa: E402

ctx.prec = 128

HERE = Path(__file__).resolve().parent
FITS = json.loads((HERE.parent / "data" / "fits.json").read_text())


def A(s: str) -> arb:
    """Arb ball containing the exact decimal (or rational 'p/q') string s."""
    if "/" in s:
        p, q = s.split("/")
        return arb(p) / arb(q)
    return arb(s)


def hull(*xs: arb) -> arb:
    lo = min(x.lower() for x in xs)
    hi = max(x.upper() for x in xs)
    return iv(lo, hi)


def iv(lo: arb | float | str, hi: arb | float | str) -> arb:
    """Arb ball containing the closed interval [lo, hi]."""
    lo_b = arb(lo) if not isinstance(lo, arb) else lo
    hi_b = arb(hi) if not isinstance(hi, arb) else hi
    a = lo_b.lower()
    b = hi_b.upper()
    if a > b:
        raise ValueError("empty interval")
    return a.union(b)


# ---------------------------------------------------------------- constants (intervals)
def K_const() -> arb:
    """K = (J per keV) / C_B  [keV^-1/2 ... units cancel in S_c/S_B]; hull of text, code and Ochs-Fisch values."""
    k_text = A("1.6e-16") / A("5.34e-37")
    cb_code_w = A("1.69e-38") * arb(1000).sqrt()
    k_code_fig6 = (A("1000") / A("6.242e18")) / cb_code_w
    k_code_tables = (arb(1000).sqrt()) / (A("1.69e-38") * A("6.24e18"))  # 1/Cbr_keV, Cbr_keV = 1.69e-38*6.24e18/sqrt(1000)
    k_codata_text = A("1.602176634e-16") / A("5.34e-37")
    k_of = A("511").sqrt() / (A("7.56e-11") * A("1e-9"))  # eq 14: 7.56e-11 eV cm^3/s * sqrt(T/511keV)
    k_of2 = A("510.99895").sqrt() / (A("7.56e-11") * A("1e-9"))
    return hull(k_text, k_code_fig6, k_code_tables, k_codata_text, k_of, k_of2)


ME_C2 = hull(A("510.99895"), A("511"))


# ---------------------------------------------------------------- bremsstrahlung factor
def gamma_rel(Te: arb, zeff: arb, me_c2: arb = ME_C2) -> arb:
    """W-H eq D2 / Ochs-Fisch eq 14 bracket: Zeff(1+1.78 t^1.34) + 2.12 t (1 + 1.1 t + t^2 - 1.25 t^2.5)."""
    t = Te / me_c2
    return zeff * (1 + A("1.78") * t ** A("1.34")) + A("2.12") * t * (1 + A("1.1") * t + t * t - A("1.25") * t ** A("2.5"))


# ---------------------------------------------------------------- D-T reactivity (Bosch-Hale form)
def sv_bosch_hale_dt(T: arb, scale: arb | None = None) -> arb:
    c = FITS["bosch_hale_DT_reactivity"]
    C = [None] + [A(c[f"C{i}"]) for i in range(1, 8)]
    BG, mc2 = A(c["BG"]), A(c["mcsquared"])
    theta = T / (1 - (T * (C[2] + T * (C[4] + T * C[6]))) / (1 + T * (C[3] + T * (C[5] + T * C[7]))))
    xi = (BG * BG / (4 * theta)) ** (arb(1) / 3)
    r = C[1] * theta * (xi / (mc2 * T ** 3)).sqrt() * (-3 * xi).exp() * A("1e-6")
    return r if scale is None else r * scale


# ---------------------------------------------------------------- p-11B reactivity, Nevins-Swain high-T fit
def sv_nevins_swain(T: arb, scale: arb | None = None) -> arb:
    c = FITS["nevins_swain_pB11_reactivity_highT"]
    P = [None] + [A(c[f"P{i}"]) for i in range(1, 8)]
    EG = A(c["EG_MeV"]) * 1000
    M = A(c["Mrc2_keV"])
    theta = T / (1 - (T * (P[2] + T * (P[4] + T * P[6]))) / (1 + T * (P[3] + T * (P[5] + T * P[7]))))
    xi = (EG / (4 * theta)) ** (arb(1) / 3)
    nr = P[1] * theta * (xi / (M * T ** 3)).sqrt() * (-3 * xi).exp()
    res = A(c["res_coeff_m3s"]) * T ** A("-1.5") * (-A(c["res_E_keV"]) / T).exp()
    r = nr + res
    return r if scale is None else r * scale


# ---------------------------------------------------------------- D-T power balance (W-H eqs 8, 16, 22)
def dt_gamma(T: arb, variant: str) -> arb:
    if variant == "text":       # eq (7)-(8), Z = 1, non-relativistic
        return arb(1)
    if variant == "code":       # code tables: Putvinski relativistic correction, Zeff = 1
        return gamma_rel(T, arb(1))
    raise ValueError(variant)


def dt_fc(variant: str) -> arb:
    c = FITS["bosch_hale_DT_reactivity"]
    return hull(A(c["f_charged_code"]), A(c["f_charged_text"]))


def dt_ignition_margin(T: arb, variant: str, sv: Callable[[arb], arb], K: arb, cb_factor: arb, fc: arb) -> arb:
    """sign(S_c - S_B) = sign(fc sv E K/4 - cb_factor sqrt(T) gamma)   (equimolar D-T, n_e = n_i)."""
    E = A(FITS["bosch_hale_DT_reactivity"]["E_total_keV"])
    return fc * sv(T) * E * K / 4 - cb_factor * T.sqrt() * dt_gamma(T, variant)


def dt_triple_product(T: arb, variant: str, sv: Callable[[arb], arb], K: arb, cb_factor: arb, fc: arb, Qinv: arb = arb(0)) -> tuple[arb, arb]:
    """(numerator, denominator) of eq (22): n T tau_E = 3 T^2 / ((fc + 1/Q) sv E / 4 - sqrt(T) gamma / K)."""
    E = A(FITS["bosch_hale_DT_reactivity"]["E_total_keV"])
    D = (fc + Qinv) * sv(T) * E / 4 - cb_factor * T.sqrt() * dt_gamma(T, variant) / K
    return 3 * T * T, D


def dt_lawson(T: arb, variant: str, sv: Callable[[arb], arb], K: arb, cb_factor: arb, fc: arb) -> tuple[arb, arb]:
    num, D = dt_triple_product(T, variant, sv, K, cb_factor, fc)
    return num / T, D


# ---------------------------------------------------------------- p-11B power ratio
def pb_ratio(T: arb, theta: arb, x: arb, sv: Callable[[arb], arb], K: arb, E_keV: arb, cb_factor: arb) -> arb:
    """R = S_c / S_B for a p-11B plasma with boron fraction x = n_B/n_i, T_e = theta T_i, f_c = 1.

    S_c = n_p n_B <sv> E,  S_B = C_B n_e^2 sqrt(Te) gamma(Zeff),  n_p = (1-x) n_i, n_e = (1+4x) n_i,
    Zeff = (1+24x)/(1+4x).  R does not depend on density.
    """
    Te = theta * T
    zeff = (1 + 24 * x) / (1 + 4 * x)
    num = x * (1 - x) * sv(T) * E_keV * K
    den = cb_factor * (1 + 4 * x) ** 2 * Te.sqrt() * gamma_rel(Te, zeff)
    return num / den


def pb_E_keV() -> arb:
    e = FITS["pB11_energy"]["E_MeV_interval"]
    return hull(A(e[0]), A(e[1])) * 1000


# ---------------------------------------------------------------- Wang et al. 2026 S-factor and certified reactivity
def _wang_S(E: acb, seg: int) -> acb:
    """S(E) in keV b for E in keV (complex-analytic on each segment)."""
    w = FITS["wang2026_pB11_S_factor"]
    if seg == 1:
        s = w["seg1"]
        S = A(s["C0"]) + A(s["C1"]) * E + A(s["C2"]) * E * E + A(s["AL"]) / ((E - A(s["EL_keV"])) ** 2 + A(s["dEL_keV"]) ** 2)
    elif seg == 2:
        s = w["seg2"]
        x = (E - A(w["E1_MeV"]) * 1000) / 100
        S = A(s["D0"]) + A(s["D1"]) * x + A(s["D2"]) * x ** 2 + A(s["D5"]) * x ** 5
    else:
        s = w["seg3"]
        S = acb(A(s["B"]))
        for Ak, Ek, dk in zip(s["A"], s["E_MeV"], s["dE_MeV"]):
            S = S + A(Ak) / ((E - A(Ek) * 1000) ** 2 + (A(dk) * 1000) ** 2)
    return S * 1000  # MeV b -> keV b


def wang_S_real(E: arb) -> arb:
    w = FITS["wang2026_pB11_S_factor"]
    e1, e2 = A(w["E1_MeV"]) * 1000, A(w["E2_MeV"]) * 1000
    seg = 1 if E.upper() <= e1.lower() else (2 if E.upper() <= e2.lower() else 3)
    return _wang_S(acb(E), seg).real


MU_PB = hull(A("859500"), A("859650"))  # p-11B reduced mass c^2 in keV (NS 859526; AME nuclear masses ~859594)
C_LIGHT = arb(299792458)


def wang_reactivity(T: arb, prec_goal: int = 40) -> arb:
    """Certified <sigma v>(T) in m^3/s of the Wang 2026 S-factor model (sigma = 0 above 10 MeV) at a POINT T.

    int_0^10MeV S(E) exp(-sqrt(EG/E) - E/T) dE  (keV^2 b), split at 1 keV (rigorous tail bound below),
    400 keV and 700 keV segment boundaries; Arb rigorous integration on each analytic segment.
    """
    w = FITS["wang2026_pB11_S_factor"]
    EG = A(w["EG_MeV"]) * 1000
    Tc = acb(T)

    def mk(seg: int) -> Callable[[acb, bool], acb]:
        def f(z: acb, analytic: bool) -> acb:
            return _wang_S(z, seg) * (-(acb(EG) / z).sqrt(analytic=analytic) - z / Tc).exp()
        return f

    total = arb(0)
    bounds = [(arb(1), A(w["E1_MeV"]) * 1000, 1), (A(w["E1_MeV"]) * 1000, A(w["E2_MeV"]) * 1000, 2), (A(w["E2_MeV"]) * 1000, A(w["E3_MeV"]) * 1000, 3)]
    for a, b, seg in bounds:
        # subdivide segment 1 finely around the narrow 148 keV resonance to help the integrator
        pts = [a]
        if seg == 1:
            pts += [arb(100), arb(140), arb(146), arb(150), arb(156), arb(200), arb(300)]
        elif seg == 3:
            pts += [arb(1000), arb(1500), arb(2500), arb(3500), arb(4700), arb(6000)]
        pts.append(b)
        for p, q in zip(pts[:-1], pts[1:]):
            val = acb.integral(mk(seg), acb(p), acb(q), rel_tol=arb(2) ** (-prec_goal), eval_limit=10 ** 6)
            total = total + val.real
    # (0, 1 keV]: S1 <= C0 + C1 + C2 + AL/((148-1)^2) on (0,1], exp(-sqrt(EG/E)) <= exp(-sqrt(EG)), exp(-E/T) <= 1
    s1 = w["seg1"]
    smax = A(s1["C0"]) + A(s1["C1"]) + A(s1["C2"]) + A(s1["AL"]) / (A(s1["EL_keV"]) - 1) ** 2
    tail0 = smax * 1000 * (-(EG.sqrt())).exp()
    total = total + iv(arb(0), tail0)
    # <sigma v> = sqrt(8/pi) c (mu c^2)^-1/2 T^-3/2 * integral(sigma E e^-E/T dE) ; sigma E = S exp(-sqrt(EG/E)); b -> m^2
    pref = (arb(8) / arb.pi()).sqrt() * C_LIGHT / MU_PB.sqrt() * T ** A("-1.5") * A("1e-28")
    return pref * total


def wang_reactivity_interval(Ta: arb, Tb: arb, sv_a: arb, sv_b: arb) -> arb:
    """Rigorous enclosure of <sigma v>(T) for T in [Ta, Tb] from point enclosures at the endpoints.

    For T in [a,b]: T^-3/2 e^{-E/T} <= a^-3/2 e^{-E/b} and >= b^-3/2 e^{-E/a}, hence
    sv(a) (a/b)^{3/2} <= sv(T) <= sv(b) (b/a)^{3/2}.
    """
    lo = (sv_a * (Ta / Tb) ** A("1.5")).lower()
    hi = (sv_b * (Tb / Ta) ** A("1.5")).upper()
    return iv(lo, hi)


# ---------------------------------------------------------------- D-T reactivity, 'integrated' code path (Bosch-Hale cross section)
def _bh_S(E: acb, part: str) -> acb:
    p = FITS["bosch_hale_DT_cross_section"][part]
    num = A(p["A1"]) + E * (A(p["A2"]) + E * (A(p["A3"]) + E * (A(p["A4"]) + E * A(p["A5"]))))
    den = 1 + E * (A(p["B1"]) + E * (A(p["B2"]) + E * (A(p["B3"]) + E * A(p["B4"]))))
    return num / den


def bh_integrated_reactivity(T: arb, prec_goal: int = 40) -> arb:
    """Certified <sigma v>(T) in m^3/s of the Wurzel-Hsu 'integrated' path at a POINT T:
    Maxwellian average of the Bosch-Hale CM cross section sigma = S/(E exp(BG/sqrt E)) [mb], integrated over
    E in [0.5, 4700] keV exactly as lib/reactivity.py does (sigma := 0 outside), split at 550 keV."""
    c = FITS["bosch_hale_DT_cross_section"]
    BG = A(FITS["bosch_hale_DT_reactivity"]["BG"])
    m1, m2 = A(c["m1_keV"]), A(c["m2_keV"])
    mu = m1 * m2 / (m1 + m2)
    Tc = acb(T)

    def mk(part: str) -> Callable[[acb, bool], acb]:
        def f(z: acb, analytic: bool) -> acb:
            return _bh_S(z, part) * (-(acb(BG) / z.sqrt(analytic=analytic)) - z / Tc).exp()
        return f

    total = arb(0)
    for a, b, part in ((A(c["low"]["E_min"]), A("550"), "low"), (A("550"), A(c["high"]["E_max"]), "high")):
        pts = [a]
        if part == "low":
            pts += [arb(2), arb(10), arb(30), arb(64), arb(100), arb(200)]
        pts.append(b)
        for p, q in zip(pts[:-1], pts[1:]):
            total = total + acb.integral(mk(part), acb(p), acb(q), rel_tol=arb(2) ** (-prec_goal), eval_limit=10 ** 6).real
    pref = (arb(8) / arb.pi()).sqrt() * C_LIGHT / mu.sqrt() * T ** A("-1.5") * A("1e-31")
    return pref * total


class GridSV:
    """sv enclosure over a T-ball from certified point integrals on a fixed geometric grid g_0 < ... < g_n.

    For T in [a,b] with g_i <= a and b <= g_j: sv(g_i)(g_i/g_j)^{3/2} <= sv(T) <= sv(g_j)(g_j/g_i)^{3/2}
    (same monotonicity bound as wang_reactivity_interval, valid because sigma >= 0)."""

    def __init__(self, point_fn: Callable[[arb], arb], lo: str, hi: str, ratio: str) -> None:
        self.nodes: list[arb] = []
        t, top, r = arb(lo), arb(hi), arb(ratio)
        while t < top:
            self.nodes.append(t)
            t = (t * r).mid()
        self.nodes.append(top)
        self.vals = [point_fn(g) for g in self.nodes]
        self.flo = [float(g.mid()) for g in self.nodes]

    def __call__(self, T: arb) -> arb:
        import bisect
        a, b = T.lower(), T.upper()
        if a < self.nodes[0] or b > self.nodes[-1]:
            raise ValueError("T outside grid")
        i = max(0, bisect.bisect_right(self.flo, float(a)) - 1)
        while self.nodes[i] > a:
            i -= 1
        j = min(len(self.nodes) - 1, bisect.bisect_left(self.flo, float(b)))
        while self.nodes[j] < b:
            j += 1
        if i == j:
            return self.vals[i]
        return wang_reactivity_interval(self.nodes[i], self.nodes[j], self.vals[i], self.vals[j])


class CachedPointSV:
    """sv enclosure over a T-ball [a,b] from certified point integrals at a and b (cached)."""

    def __init__(self, point_fn: Callable[[arb], arb]) -> None:
        self.point_fn = point_fn
        self.cache: dict[str, arb] = {}

    def at(self, t: arb) -> arb:
        k = t.mid().str(30, radius=False)
        if k not in self.cache:
            self.cache[k] = self.point_fn(t.mid())
        return self.cache[k]

    def __call__(self, T: arb) -> arb:
        a, b = T.lower(), T.upper()
        if a == b:
            return self.at(a)
        return wang_reactivity_interval(a, b, self.at(a), self.at(b))
