"""Interval-certified sign of the 'start cold' benefit in a stylised two-component (CO2 + N2) van 't Hoff Henry
temperature-swing model with sensible heat. Tier C under the proposal's interval rule (mpmath outward-rounded
interval arithmetic, not replayed in Lean; Lean holds the exact algebra in formal_cert/Programmes/DacExergy).

Model (per kg sorbent; a stated surrogate of the published model, NOT the published model itself):
  f_i(T1) = exp(q_i/R (1/T1 - 1/T0)) - exp(q_i/R (1/Th - 1/T0)),   i in {C (CO2), N (N2)}
  dn_C = n0 f_C(T1),  dn_N = n0 lam f_N(T1),  lam = (N2 loading)/(CO2 loading) at the inlet at T0
  c = gamma R n0 (sorbent heat capacity), heat-recovery fraction r in [0, 1] on the sensible heat
  per mol of species i (T1 <= T0 <= Th):
    face value  a_i = 2 q_i + R (T1 + Th)                     (Eq. 1 heat + RT1 work; desorption heat + RT work)
    exergy      a_i = q_i (T0/T1 - 1) + q_i (1 - T0/Th) + R (T1 + Th)   (works kept at face value)
  sensible per kg: face value (1-r) c (Th - T1);  exergy (1-r) c S(T1, Th),  S(a,b) = int_a^b |1 - T0/T| dT
  cost per mol CO2  C(T1) = a_C + lam (f_N/f_C) a_N + (1-r) gamma R s(T1)/f_C(T1)
Benefit of starting at Tc < T0 instead of T0 (same Th): beta = C(T0) - C(Tc) = A + lam B + (1-r) gamma R D,
  A_ex = -(T0 - Tc)(q_C/Tc - R) < 0 (for q_C > R Tc),   A_fv = R (T0 - Tc) > 0,
  B = (f_N/f_C)(T0) a_N(T0) - (f_N/f_C)(Tc) a_N(Tc),     D = s(T0)/f_C(T0) - s(Tc)/f_C(Tc).
Consequences used below:
  * beta is affine in r with slope -gamma R D, so if D >= 0 the full-recovery case r = 1 is the worst case for
    'start cold': beta(r) >= beta(1) for every r in [0, 1].
  * at r = 1, exergy: cold wins  <=>  lam B > -A_ex,  i.e. (B > 0 and) lam > lam* = (T0 - Tc)(q_C/Tc - R) / B.
  * at r = 1, face value: cold wins whenever B >= 0 (A_fv > 0).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from mpmath import iv, mpf

iv.prec = 80
R_EXACT = mpf("1.380649e-23") * mpf("6.02214076e23")
RI = iv.mpf([R_EXACT, R_EXACT])


def I(a: float, b: float | None = None):
    return iv.mpf([mpf(a), mpf(a if b is None else b)])


def S_full(T1, Th, T0):
    """S(T1, Th) for T1 <= T0 <= Th."""
    return (T0 * iv.log(T0 / T1) - (T0 - T1)) + ((Th - T0) - T0 * iv.log(Th / T0))


def f(T1, Th, T0, q):
    return iv.exp(q / RI * (1 / T1 - 1 / T0)) - iv.exp(q / RI * (1 / Th - 1 / T0))


def f0(Th, T0, q):
    """f at T1 = T0 (exact form 1 - exp(...))."""
    return 1 - iv.exp(q / RI * (1 / Th - 1 / T0))


def a_ex(T1, Th, T0, q, at_T0: bool):
    base = q * (1 - T0 / Th) + RI * (T1 + Th)
    return base if at_T0 else base + q * (T0 / T1 - 1)


def a_fv(T1, Th, q):
    return 2 * q + RI * (T1 + Th)


def ABD(Tc, Th, T0, qC, qN, kind: str):
    fC_c, fN_c = f(Tc, Th, T0, qC), f(Tc, Th, T0, qN)
    fC_0, fN_0 = f0(Th, T0, qC), f0(Th, T0, qN)
    if kind == "ex":
        A = -((T0 - Tc) * (qC / Tc - RI))
        B = (fN_0 / fC_0) * a_ex(T0, Th, T0, qN, True) - (fN_c / fC_c) * a_ex(Tc, Th, T0, qN, False)
        D = ((Th - T0) - T0 * iv.log(Th / T0)) / fC_0 - S_full(Tc, Th, T0) / fC_c
    else:
        A = RI * (T0 - Tc)
        B = (fN_0 / fC_0) * a_fv(T0, Th, qN) - (fN_c / fC_c) * a_fv(Tc, Th, qN)
        D = (Th - T0) / fC_0 - (Th - Tc) / fC_c
    return A, B, D


def sgn(x) -> int:
    return 1 if x.a > 0 else (-1 if x.b < 0 else 0)


def bisect(fn, box: dict, maxdepth: int) -> dict:
    keys = list(box)
    full = {k: box[k][1] - box[k][0] for k in keys}
    acc = {1: 0.0, -1: 0.0, 0: 0.0}
    und = []
    stack = [(dict(box), 0)]
    n = 0
    while stack:
        b, d = stack.pop()
        n += 1
        s = sgn(fn(*(I(*b[k]) for k in keys)))
        vol = 1.0
        for k in keys:
            vol *= (b[k][1] - b[k][0]) / full[k] if full[k] > 0 else 1.0
        if s != 0 or d >= maxdepth:
            acc[s] += vol
            if s == 0:
                und.append(b)
            continue
        k = max(keys, key=lambda kk: ((b[kk][1] - b[kk][0]) / full[kk]) if full[kk] > 0 else -1.0)
        lo, hi = b[k]
        m = 0.5 * (lo + hi)
        for a, c in ((lo, m), (m, hi)):
            nb = dict(b); nb[k] = (a, c)
            stack.append((nb, d + 1))
    return {"box": box, "maxdepth": maxdepth, "evals": n, "frac_positive": acc[1], "frac_negative": acc[-1],
            "frac_undecided": acc[0], "undecided_sample": und[:8]}


def lam_star(Tc: float, Th: float, T0: float, qC: tuple, qN: tuple) -> dict:
    """Enclosure of lam* at r = 1 (exergy) on q-cells; plus face-value B sign."""
    A, B, D = ABD(I(Tc), I(Th), I(T0), I(*qC), I(*qN), "ex")
    _, Bf, Df = ABD(I(Tc), I(Th), I(T0), I(*qC), I(*qN), "fv")
    out = {"Tc": Tc, "Th": Th, "T0": T0, "qC": list(qC), "qN": list(qN), "B_ex": [float(B.a), float(B.b)],
           "D_ex": [float(D.a), float(D.b)], "B_fv": [float(Bf.a), float(Bf.b)], "D_fv": [float(Df.a), float(Df.b)]}
    if B.a > 0:
        ls = -A / B
        out.update(status="threshold", lam_star=[float(ls.a), float(ls.b)])
    elif B.b < 0:
        out.update(status="never_for_any_lam")
    else:
        out.update(status="undecided")
    return out


def float_beta(Tc: float, Th: float, T0: float, qC: float, qN: float, lam: float, gam: float, r: float,
               kind: str) -> float:
    """Independent plain-float implementation (numpy-free math, written separately from the interval code)."""
    import math
    Rf = 1.380649e-23 * 6.02214076e23
    fC = lambda T: math.exp(qC / Rf * (1 / T - 1 / T0)) - math.exp(qC / Rf * (1 / Th - 1 / T0))
    fN = lambda T: math.exp(qN / Rf * (1 / T - 1 / T0)) - math.exp(qN / Rf * (1 / Th - 1 / T0))
    if kind == "ex":
        aN = lambda T: qN * max(0.0, T0 / T - 1) + qN * (1 - T0 / Th) + Rf * (T + Th)
        aC = lambda T: qC * max(0.0, T0 / T - 1) + qC * (1 - T0 / Th) + Rf * (T + Th)
        s = lambda T: (T0 * math.log(T0 / T) - (T0 - T)) + ((Th - T0) - T0 * math.log(Th / T0))
    else:
        aN = lambda T: 2 * qN + Rf * (T + Th)
        aC = lambda T: 2 * qC + Rf * (T + Th)
        s = lambda T: Th - T
    C = lambda T: aC(T) + lam * fN(T) / fC(T) * aN(T) + (1 - r) * gam * Rf * s(T) / fC(T)
    return C(T0) - C(Tc)


def classify(Tc: float, Th: float, T0: float, qC: float, qN: float, lam: float, gam: float, r: float) -> dict:
    """Certified sign of beta_ex and beta_fv at one parameter point (point intervals, outward rounding)."""
    res = {}
    for kind in ("ex", "fv"):
        A, B, D = ABD(I(Tc), I(Th), I(T0), I(qC), I(qN), kind)
        beta = A + I(lam) * B + (1 - I(r)) * I(gam) * RI * D
        fb = float_beta(Tc, Th, T0, qC, qN, lam, gam, r, kind)
        tol = 1e-9 * max(abs(fb), 1.0)
        res[kind] = {"beta": [float(beta.a), float(beta.b)], "sign": sgn(beta),
                     "A": float(A.mid), "B": float(B.mid), "D": float(D.mid), "beta_float": fb,
                     "float_inside_enclosure": bool(float(beta.a) - tol <= fb <= float(beta.b) + tol)}
    return res


def main() -> int:
    outdir = Path(sys.argv[1])
    params = json.loads(Path(sys.argv[2]).read_text())  # per-material surrogate parameters (from the dataset)
    t = time.time()
    qC_lo, qC_hi = params["ranges"]["qC"]
    qN_lo, qN_hi = params["ranges"]["qN"]
    res: dict = {"param_ranges": params["ranges"]}
    box = {"Tc": (200.0, 272.0), "Th": (315.0, 400.0), "T0": (273.0, 313.0), "qC": (qC_lo, qC_hi)}
    # (1) exergy A < 0 on the whole box (q_C > R Tc there); face-value A > 0 (trivial).
    res["A_ex_negative"] = bisect(lambda Tc, Th, T0, qC: (T0 - Tc) * (qC / Tc - RI), box, 10)
    # (2) sign of D_ex and of B (exergy, face value) over the full box
    box2 = dict(box); box2["qN"] = (qN_lo, qN_hi)
    res["D_ex_sign"] = bisect(lambda Tc, Th, T0, qC, qN: ABD(Tc, Th, T0, qC, qN, "ex")[2], box2, 16)
    res["B_ex_sign"] = bisect(lambda Tc, Th, T0, qC, qN: ABD(Tc, Th, T0, qC, qN, "ex")[1], box2, 16)
    res["B_fv_sign"] = bisect(lambda Tc, Th, T0, qC, qN: ABD(Tc, Th, T0, qC, qN, "fv")[1], box2, 16)
    # (3) lam* enclosures on a grid
    grid = []
    step_c = (qC_hi - qC_lo) / 8
    step_n = (qN_hi - qN_lo) / 4
    for T0 in (273.15, 298.15, 313.15):
        for Tc in [200.0 + 10.0 * k for k in range(12) if 200.0 + 10.0 * k < T0 - 1]:
            for Th in (320.0, 340.0, 360.0, 380.0, 400.0):
                for jc in range(8):
                    for jn in range(4):
                        grid.append(lam_star(Tc, Th, T0, (qC_lo + jc * step_c, qC_lo + (jc + 1) * step_c),
                                             (qN_lo + jn * step_n, qN_lo + (jn + 1) * step_n)))
    res["lam_star_grid_r1"] = grid
    # (4) per-material certified classification at the surrogate parameters
    cls = []
    for m in params["materials"]:
        for r in (0.0, 0.5, 1.0):
            for T0 in (273.15, 298.15, 313.15):
                if m["T1"] >= T0:
                    continue
                c = classify(m["T1"], m["Tend"], T0, m["qC"][str(T0)], m["qN"][str(T0)], m["lam"][str(T0)],
                             m["gamma"][str(T0)], r)
                cls.append({"name": m["name"], "row": m.get("row"), "T0": T0, "r": r, **c})
    res["classification"] = cls
    res["independent_float_check_failures"] = sum(1 for c in cls for k in ("ex", "fv")
                                                  if not c[k]["float_inside_enclosure"])
    print("independent float check failures", res["independent_float_check_failures"], "of", 2 * len(cls))
    res["seconds"] = round(time.time() - t, 1)
    (outdir / "cert_sign.json").write_text(json.dumps(res, indent=1))
    for k in ("A_ex_negative", "D_ex_sign", "B_ex_sign", "B_fv_sign"):
        x = res[k]
        print(k, "pos", round(x["frac_positive"], 6), "neg", round(x["frac_negative"], 6), "und",
              round(x["frac_undecided"], 6), "evals", x["evals"])
    st: dict[str, int] = {}
    for g in grid:
        st[g["status"]] = st.get(g["status"], 0) + 1
    print("lam* grid", st)
    agg: dict[str, list[int]] = {}
    for c in cls:
        key = f"T0={c['T0']} r={c['r']}"
        a = agg.setdefault(key, [0, 0, 0, 0, 0])
        a[0] += 1
        a[1] += c["ex"]["sign"] == 1
        a[2] += c["ex"]["sign"] == -1
        a[3] += c["fv"]["sign"] == 1
        a[4] += c["fv"]["sign"] == -1
    print("classification [n, ex+, ex-, fv+, fv-]", json.dumps(agg))
    print("seconds", res["seconds"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
