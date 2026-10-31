"""K2: certified eta = dDIC/dTA at fixed fCO2 (carbonate system), interval arithmetic with mpmath.iv.

Constants: Dickson, Sabine, Christian (eds) 2007, Guide to Best Practices for Ocean CO2 Measurements, Ch.5 sec.7
(Weiss 1974 K0; Lueker et al. 2000 K1, K2; Dickson 1990 KB; Millero 1995 KW; Uppstrom 1974 boron). Total pH scale,
mol/kg-solution. Sulfate, fluoride, phosphate, silicate are not included.
"""
from __future__ import annotations

import math

import mpmath
from mpmath import iv, mp

iv.dps = 30
mp.dps = 30

Interval = "mpmath.ctx_iv.ivmpf"

# sigma of the pK values (OEDG18, as shipped in PyCO2SYS.uncertainty; secondary source)
SIGMA_PK = {"K0": 0.002, "K1": 0.0075, "K2": 0.015, "KB": 0.01, "KW": 0.01}
LN10 = mpmath.log(10)


def _pm(x: float) -> object:
    """Symmetric interval [-x, x]."""
    return iv.mpf([-x, x])


def _logs(t_c: object, s: object, corrupt: dict) -> tuple:
    """Interval enclosures of (ln K0, log10 K1, log10 K2, ln KB, ln KW) for T-interval t_c (deg C), S-interval s."""
    T = t_c + iv.mpf("273.15")
    k1_a = 3633.86 + corrupt.get("k1_coef_shift", 0.0)
    ln_k0 = (
        93.4517 * (100 / T) - 60.2409 + 23.3585 * iv.log(T / 100)
        + s * (iv.mpf("0.023517") - iv.mpf("0.023656") * (T / 100) + iv.mpf("0.0047036") * (T / 100) ** 2)
    )
    log10_k1 = -k1_a / T + iv.mpf("61.2172") - iv.mpf("9.67770") * iv.log(T) + iv.mpf("0.011555") * s - iv.mpf("0.0001152") * s**2
    log10_k2 = -iv.mpf("471.78") / T - iv.mpf("25.9290") + iv.mpf("3.16967") * iv.log(T) + iv.mpf("0.01781") * s - iv.mpf("0.0001122") * s**2
    sq = iv.sqrt(s)
    # ln KB regrouped by powers of q = sqrt(S) (algebraically identical to Guide eq. 37)
    lt = iv.log(T)
    g0 = -iv.mpf("8966.90") / T + iv.mpf("148.0248") - iv.mpf("24.4344") * lt
    g1 = -iv.mpf("2890.53") / T + iv.mpf("137.1942") - iv.mpf("25.085") * lt + iv.mpf("0.053105") * T
    g2 = -iv.mpf("77.942") / T + iv.mpf("1.62142") - iv.mpf("0.2474") * lt
    g3 = iv.mpf("1.728") / T
    g4 = -iv.mpf("0.0996") / T
    ln_kb = g0 + sq * (g1 + sq * (g2 + sq * (g3 + sq * g4)))
    ln_kw = (
        -iv.mpf("13847.26") / T + iv.mpf("148.9652") - iv.mpf("23.6521") * lt
        + (iv.mpf("118.67") / T - iv.mpf("5.977") + iv.mpf("1.0495") * lt) * sq - iv.mpf("0.01615") * s
    )
    return ln_k0, log10_k1, log10_k2, ln_kb, ln_kw


def _hull(vals: list) -> object:
    lo = min(v.a for v in vals)
    hi = max(v.b for v in vals)
    return iv.mpf([lo, hi])


def constants(t_c: object, s: object, nsigma: float = 0.0, corrupt: dict | None = None, nsub: tuple = (1, 1)) -> dict:
    """Interval constants over the box t_c x s (iv intervals). nsub = (n_T, n_S) inner subdivisions whose hull is
    taken, to cut the interval-dependency overestimate of the large cancelling terms (still a rigorous enclosure)."""
    corrupt = corrupt or {}
    nt, ns = nsub
    parts = []
    for i in range(nt):
        ti = iv.mpf([t_c.a + (t_c.b - t_c.a) * i / nt, t_c.a + (t_c.b - t_c.a) * (i + 1) / nt]) if nt > 1 else t_c
        for j in range(ns):
            sj = iv.mpf([s.a + (s.b - s.a) * j / ns, s.a + (s.b - s.a) * (j + 1) / ns]) if ns > 1 else s
            parts.append(_logs(ti, sj, corrupt))
    ln_k0, log10_k1, log10_k2, ln_kb, ln_kw = (_hull([p[k] for p in parts]) for k in range(5))
    d = lambda name: _pm(nsigma * SIGMA_PK[name]) if nsigma else iv.mpf(0)
    k0 = iv.exp(ln_k0) * iv.exp(d("K0") * LN10)
    k1 = iv.mpf(10) ** (log10_k1 + d("K1"))
    k2 = iv.mpf(10) ** (log10_k2 + d("K2"))
    kb = iv.exp(ln_kb) * iv.exp(d("KB") * LN10)
    kw = iv.exp(ln_kw) * iv.exp(d("KW") * LN10)
    bt = iv.mpf("0.000416") * s / 35
    if corrupt.get("swap_k1k2"):
        k1, k2 = k2, k1
    return {"K0": k0, "K1": k1, "K2": k2, "KB": kb, "KW": kw, "BT": bt}


def ta_minus(h: object, c: dict, f_uatm: object, ta: object, corrupt: dict | None = None) -> object:
    """F(h) = TA_model(h) - TA, all mol/kg. f_uatm in micro-atm."""
    corrupt = corrupt or {}
    C = c["K0"] * f_uatm * iv.mpf("1e-6")
    sign_b = -1 if corrupt.get("flip_borate_sign") else 1
    return (
        C * (c["K1"] / h + 2 * c["K1"] * c["K2"] / h**2)
        + sign_b * c["BT"] * c["KB"] / (c["KB"] + h)
        + c["KW"] / h - h - ta
    )


def eta_at(h: object, c: dict, f_uatm: object, corrupt: dict | None = None) -> object:
    """eta = (h+2K2) / ((h+4K2) + h^3 R/(C K1)), algebraically identical to N/D (C and K1 occur once)."""
    corrupt = corrupt or {}
    C = c["K0"] * f_uatm * iv.mpf("1e-6")
    k1, k2, kb, kw, bt = c["K1"], c["K2"], c["KB"], c["KW"], c["BT"]
    sign_b = -1 if corrupt.get("flip_borate_sign") else 1
    r = sign_b * bt * kb / (kb + h) ** 2 + kw / h**2 + 1
    return (h + 2 * k2) / ((h + 4 * k2) + h**3 * r / (C * k1))


def _mid(x: object) -> mpmath.mpf:
    return mpmath.mpf(x.mid.a) if hasattr(x.mid, "a") else mpmath.mpf(x.mid)


def eta_increasing_in_h(h: object, c: dict, f_uatm: object) -> bool:
    """True if d eta/dh > 0 is certified over h x parameter intervals.

    With A = C K1 h^-4, R = BT KB/(KB+h)^2 + KW/h^2 + 1, N = A h (h+2 K2), D = A h (h+4 K2) + R one finds
    N'D - N D' = A (2 A h^2 K2 + Q) with Q = -[R_B (2hK2+2hKB+6 K2 KB)/(KB+h) + 2 K2 R_W + 2h + 6 K2] < 0
    (R_B the borate and R_W the water term of R). We certify 2 C K1 K2/h^2 > |Q|.
    """
    C = c["K0"] * f_uatm * iv.mpf("1e-6")
    k1, k2, kb, kw, bt = c["K1"], c["K2"], c["KB"], c["KW"], c["BT"]
    r_b = bt * kb / (kb + h) ** 2
    r_w = kw / h**2
    absq = r_b * (2 * h * k2 + 2 * h * kb + 6 * k2 * kb) / (kb + h) + 2 * k2 * r_w + 2 * h + 6 * k2
    return (2 * C * k1 * k2 / h**2 - absq).a > 0


def float_root(t_c: float, s: float, f: float, ta: float, nsigma: float = 0.0, corrupt: dict | None = None) -> float:
    """Float (mp) solve of TA(h)=TA at a point, constants at nominal (nsigma=0)."""
    c = constants(iv.mpf(t_c), iv.mpf(s), 0.0, corrupt)
    cm = {k: mpmath.mpf(v.a) for k, v in c.items()}
    C = cm["K0"] * f * mpmath.mpf("1e-6")
    sb = -1 if (corrupt or {}).get("flip_borate_sign") else 1

    def F(lh: mpmath.mpf) -> mpmath.mpf:
        h = mpmath.e ** lh
        return C * (cm["K1"] / h + 2 * cm["K1"] * cm["K2"] / h**2) + sb * cm["BT"] * cm["KB"] / (cm["KB"] + h) + cm["KW"] / h - h - ta

    lo, hi = mpmath.log(mpmath.mpf("1e-12")), mpmath.log(mpmath.mpf("1e-3"))
    flo, fhi = F(lo), F(hi)
    if flo * fhi >= 0:
        return float("nan")
    for _ in range(120):  # bisection on log h
        mid = (lo + hi) / 2
        fm = F(mid)
        if fm * flo > 0:
            lo, flo = mid, fm
        else:
            hi = mid
    return float(mpmath.e ** ((lo + hi) / 2))


def eta_box(t_rng, s_rng, f_rng, ta_rng, nsigma: float = 0.0, corrupt: dict | None = None, nsub: tuple = (1, 1), cache: dict | None = None) -> tuple[float, float, dict]:
    """Rigorous enclosure of eta over a sub-box (ranges are (lo, hi) floats; TA in mol/kg).

    Returns (eta_lo, eta_hi, info). Raises RuntimeError if the root cannot be bracketed.
    """
    corrupt = corrupt or {}
    t = iv.mpf(t_rng)
    s = iv.mpf(s_rng)
    f = iv.mpf(f_rng)
    ta = iv.mpf(ta_rng)
    key = (t_rng, s_rng, nsigma, nsub, tuple(sorted(corrupt.items())))
    if cache is not None and key in cache:
        c = cache[key]
    else:
        c = constants(t, s, nsigma, corrupt, nsub)
        if cache is not None:
            cache[key] = c
    # h for bracketing: corner/midpoint float root to seed
    tm, sm, fm, tam = [(r[0] + r[1]) / 2 for r in (t_rng, s_rng, f_rng, ta_rng)]
    h0 = float_root(tm, sm, fm, tam, 0.0, corrupt)
    if h0 != h0:
        raise RuntimeError("no float root")
    # bracket: find outer verified bounds by doubling, then tighten each side by bisection (verified by iv signs)
    delta = 1e-4
    ok = False
    for _ in range(40):
        l0, u0 = h0 * math.exp(-delta), h0 * math.exp(delta)
        if ta_minus(iv.mpf(l0), c, f, ta, corrupt).a > 0 and ta_minus(iv.mpf(u0), c, f, ta, corrupt).b < 0:
            ok = True
            break
        delta *= 2
        if delta >= 4.0:
            break
    if not ok:
        raise RuntimeError("bracketing failed")
    lo_v, lo_bad = l0, h0  # lo_v verified (F_lower > 0); lo_bad candidate toward h0
    for _ in range(40):
        mid = 0.5 * (lo_v + lo_bad)
        if ta_minus(iv.mpf(mid), c, f, ta, corrupt).a > 0:
            lo_v = mid
        else:
            lo_bad = mid
    hi_v, hi_bad = u0, h0
    for _ in range(40):
        mid = 0.5 * (hi_v + hi_bad)
        if ta_minus(iv.mpf(mid), c, f, ta, corrupt).b < 0:
            hi_v = mid
        else:
            hi_bad = mid
    # split the verified h bracket geometrically into pieces; on each piece use the certified monotone endpoint form
    # when the interval sign test passes, else the naive interval evaluation. The hull of the pieces covers the bracket.
    npieces = 1 if (not corrupt and eta_increasing_in_h(iv.mpf([lo_v, hi_v]), c, f)) else 24
    ratio = (hi_v / lo_v) ** (1.0 / npieces)
    lo_e, hi_e = 1e300, -1e300
    mono = True
    for k in range(npieces):
        a_k = lo_v * ratio**k if k > 0 else lo_v
        b_k = lo_v * ratio ** (k + 1) if k < npieces - 1 else hi_v
        hp = iv.mpf([a_k, b_k])
        if not corrupt and eta_increasing_in_h(hp, c, f):
            e0 = eta_at(iv.mpf(a_k), c, f)
            e1 = eta_at(iv.mpf(b_k), c, f)
            lo_k, hi_k = e0.a, e1.b
        else:
            e = eta_at(hp, c, f, corrupt)
            lo_k, hi_k = e.a, e.b
            mono = False
        lo_e = min(lo_e, float(lo_k))
        hi_e = max(hi_e, float(hi_k))
    return float(lo_e), float(hi_e), {"h_lo": lo_v, "h_hi": hi_v, "monotone_used": mono}

