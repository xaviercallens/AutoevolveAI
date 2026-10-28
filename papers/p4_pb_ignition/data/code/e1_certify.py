"""E1 certified computations (Arb ball arithmetic, python-flint 0.6.0). Tier C under the proposal's interval rule.

Usage: python -I e1_certify.py   (writes ../logs/certify.json and ../logs/certify.log)
"""
from __future__ import annotations

import heapq
import json
import sys
import time
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1_model import (A, CachedPointSV, GridSV, FITS, K_const, arb, bh_integrated_reactivity, dt_ignition_margin,  # noqa: E402
                      dt_lawson, dt_triple_product, gamma_rel, hull, iv, pb_E_keV, pb_ratio, sv_bosch_hale_dt,
                      sv_nevins_swain, wang_reactivity, _bh_S, wang_S_real)
from e1_gate import gate  # noqa: E402

HERE = Path(__file__).resolve().parent
LOG: list[str] = []


def log(msg: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    LOG.append(line)


def F(x: arb) -> float:
    return float(x.mid())


def enc(x: arb) -> list[float]:
    return [float(x.lower()), float(x.upper())]


def gmid(a: arb, b: arb) -> arb:
    return (a * b).sqrt().mid()


# ------------------------------------------------------------------ constants
def K_variants() -> dict[str, arb]:
    cb_code_w = A("1.69e-38") * arb(1000).sqrt()
    return {
        "code_fig6": (A("1000") / A("6.242e18")) / cb_code_w,
        "code_tables": arb(1000).sqrt() / (A("1.69e-38") * A("6.24e18")),
        "text": A("1.6e-16") / A("5.34e-37"),
        "hull": K_const(),
    }


FC_CODE = A("0.2")
FC_HULL = hull(A("0.2"), A("3.5") / A("17.6"))


# ------------------------------------------------------------------ 1-D adaptive sign certification
def certify_sign_1d(fcell: Callable[[arb, arb], arb], a: arb, b: arb, want: int, max_leaves: int = 200000) -> tuple[bool, int]:
    """True iff want*f > 0 is certified on every cell of [a,b] (geometric bisection)."""
    stack = [(a, b, 0)]
    leaves = 0
    while stack:
        lo, hi, d = stack.pop()
        v = fcell(lo, hi)
        ok = (v.lower() > 0) if want > 0 else (v.upper() < 0)
        if ok:
            leaves += 1
            continue
        if d > 45 or leaves > max_leaves:
            return False, leaves
        m = gmid(lo, hi)
        stack.append((lo, m, d + 1))
        stack.append((m, hi, d + 1))
    return True, leaves


def root_bisect(fpoint: Callable[[arb], arb], a: arb, b: arb, iters: int = 80) -> arb | None:
    fa, fb = F(fpoint(a)), F(fpoint(b))
    if fa * fb > 0:
        return None
    for _ in range(iters):
        m = gmid(a, b)
        fm = F(fpoint(m))
        if (fm > 0) == (fa > 0):
            a, fa = m, fm
        else:
            b = m
    return gmid(a, b)


# ------------------------------------------------------------------ D-T: ideal ignition temperature
def certify_T_ign(variant: str, sv: Callable[[arb], arb], K: arb, fc: arb, cbf: arb, Tmin: str = "0.2", Tmax: str = "100") -> list[float] | None:
    marg = lambda T: dt_ignition_margin(T, variant, sv, K, cbf, fc)  # noqa: E731
    lo_d, hi_d = arb(Tmin), arb(Tmax)
    r = root_bisect(marg, lo_d, arb(20))
    if r is None:
        return None
    for eps in ("1e-7", "1e-6", "1e-5", "1e-4", "1e-3", "1e-2"):
        lo, hi = (r * (1 - arb(eps))).mid(), (r * (1 + arb(eps))).mid()
        ok1, n1 = certify_sign_1d(lambda a, b: marg(iv(a, b)), lo_d, lo, -1)
        ok2, n2 = certify_sign_1d(lambda a, b: marg(iv(a, b)), hi, hi_d, +1)
        if ok1 and ok2:
            log(f"  T_ign certified in [{F(lo)}, {F(hi)}] (leaves {n1}+{n2}, eps {eps})")
            return [float(lo.lower()), float(hi.upper())]
    return None


# ------------------------------------------------------------------ D-T: minimum of h(T) = num/D
def certify_min(hfun: Callable[[arb], tuple[arb, arb]], Tmin: arb, Tmax: arb, guess: tuple[float, float]) -> dict[str, Any] | None:
    def h_lower(T: arb) -> arb:
        num, D = hfun(T)
        if D.upper() <= 0:
            return arb("inf")
        return (num.lower() / D.upper()).lower()

    def h_point(T: arb) -> float:
        num, D = hfun(T)
        return F(num / D) if D.lower() > 0 else float("inf")

    # golden-section search on point values
    a, b = arb(str(guess[0])), arb(str(guess[1]))
    g = (arb(5).sqrt() - 1) / 2
    for _ in range(90):
        c = (b - g * (b - a)).mid()
        d = (a + g * (b - a)).mid()
        if h_point(c) < h_point(d):
            b = d
        else:
            a = c
    T0 = ((a + b) / 2).mid()
    num, D = hfun(T0)
    if not D.lower() > 0:
        return None
    U = (num / D).upper()
    # bracket {h <= U}: walk outwards until point value clearly exceeds U, then certify h > U outside
    # bracket edges chosen by a VALUE margin (the minimum is flat): h(edge) >= U (1 + margin), margin >> enclosure width
    for margin in ("1e-4", "5e-5", "2e-4"):
        target = F(U) * (1 + float(margin))

        def edge(direction: int) -> arb:
            step = arb("1e-3")
            for k in range(1, 400):
                T = (T0 * (1 + direction * step * k)).mid()
                if h_point(T) >= target:
                    return T
            return (T0 * (1 + direction * arb("0.4"))).mid()

        aa, bb = edge(-1), edge(+1)
        fcell = lambda x, y: h_lower(iv(x, y)) - U  # noqa: E731
        ok1, n1 = certify_sign_1d(fcell, Tmin, aa, +1, max_leaves=20000)
        ok2, n2 = certify_sign_1d(fcell, bb, Tmax, +1, max_leaves=20000)
        if ok1 and ok2:
            # lower bound of the minimum over [aa, bb]
            L = None
            cells = [(aa, bb)]
            for _ in range(8):
                nxt = []
                for x, y in cells:
                    m = gmid(x, y)
                    nxt += [(x, m), (m, y)]
                cells = nxt
            L = min(float(h_lower(iv(x, y))) for x, y in cells)
            log(f"  min certified: argmin in [{F(aa)}, {F(bb)}], min in [{L:.6e}, {float(U):.6e}] (leaves {n1}+{n2})")
            return {"Tmin": [float(aa.lower()), float(bb.upper())], "min": [L, float(U)]}
    return None


def run_dt(variant: str, sv: Callable[[arb], arb], K: arb, fc: arb, cbf: arb, with_tign: bool) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if with_tign:
        out["T_ign"] = certify_T_ign(variant, sv, K, fc, cbf)
    tp = certify_min(lambda T: dt_triple_product(T, variant, sv, K, cbf, fc), arb(1), arb(100), (8.0, 30.0))
    lp = certify_min(lambda T: dt_lawson(T, variant, sv, K, cbf, fc), arb(1), arb(100), (12.0, 60.0))
    out["TP_Tmin"], out["TP_min"] = (tp["Tmin"], tp["min"]) if tp else (None, None)
    out["LP_Tmin"], out["LP_min"] = (lp["Tmin"], lp["min"]) if lp else (None, None)
    return out


# ------------------------------------------------------------------ p-11B: 2-D branch and bound for max R over (T, x)
def max_R(theta: arb, sv: Callable[[arb], arb], K: arb, E: arb, cbf: arb, Tbox: tuple[str, str], xbox: tuple[str, str],
          rtol: float = 1e-4, max_iter: int = 400000, decide: bool = False, min_rel: float = 1e-6) -> dict[str, Any]:
    """Certified enclosure [L, U] of max_{T in Tbox, x in xbox} R(T, theta, x)."""
    def cellR(Ta: arb, Tb: arb, xa: arb, xb: arb) -> arb:
        return pb_ratio(iv(Ta, Tb), theta, iv(xa, xb), sv, K, E, cbf)

    def pointR(T: arb, x: arb) -> arb:
        return pb_ratio(T, theta, x, sv, K, E, cbf)

    T0, T1 = arb(Tbox[0]), arb(Tbox[1])
    x0, x1 = arb(xbox[0]), arb(xbox[1])
    heap: list[tuple[float, int, tuple[arb, arb, arb, arb]]] = []
    cnt = 0
    r = cellR(T0, T1, x0, x1)
    heapq.heappush(heap, (-(float(r.upper()) * (1 + 1e-15)) if r.is_finite() else -float("inf"), cnt, (T0, T1, x0, x1)))
    best_L, best_pt = -1.0, None
    stuck_U = -1.0  # upper bounds of cells too small to split further (kept, never dropped)
    it = 0
    while heap:
        it += 1
        negU, _, (Ta, Tb, xa, xb) = heapq.heappop(heap)
        U = -negU
        Tm, xm = gmid(Ta, Tb), ((xa + xb) / 2).mid()
        pv = pointR(Tm, xm)
        if not pv.is_finite():
            return {"L": None, "U": None, "certified_below_1": False, "witness_above_1": False, "argmax": None,
                    "iters": it, "note": "non-finite point value (e.g. zero bremsstrahlung)"}
        if float(pv.lower()) > best_L:
            best_L, best_pt = float(pv.lower()), (F(Tm), F(xm))
        if U - best_L <= rtol * best_L or it > max_iter or (decide and (best_L > 1.0 or max(U, stuck_U) < 1.0)):
            heapq.heappush(heap, (negU, -1, (Ta, Tb, xa, xb)))
            break
        # split along the larger relative extent
        relT = F((Tb - Ta) / Tm)
        relx = F((xb - xa) / xm)
        if max(relT, relx) < min_rel:
            stuck_U = max(stuck_U, U)
            continue
        if relT >= relx:
            kids = [(Ta, Tm, xa, xb), (Tm, Tb, xa, xb)]
        else:
            kids = [(Ta, Tb, xa, xm), (Ta, Tb, xm, xb)]
        for kd in kids:
            rv = cellR(*kd)
            ub = float(rv.upper()) * (1 + 1e-15) if rv.is_finite() else float("inf")
            if ub >= best_L:
                cnt += 1
                heapq.heappush(heap, (-ub, cnt, kd))
    U_glob = max(-heap[0][0] if heap else best_L, stuck_U)
    return {"L": best_L, "U": U_glob, "certified_below_1": U_glob < 1.0, "witness_above_1": best_L > 1.0,
            "argmax": best_pt, "iters": it}


def theta_threshold(sv: Callable[[arb], arb], K: arb, E: arb, cbf: arb, Tbox: tuple[str, str], xbox: tuple[str, str], label: str, min_rel: float = 1e-6) -> dict[str, Any]:
    """Two-sided certified threshold: at theta_hi, max R < 1 (certified); at theta_lo, a point with R > 1 (certified)."""
    lo, hi = 0.05, 1.0
    for _ in range(20):
        m = 0.5 * (lo + hi)
        res = max_R(arb(str(m)), sv, K, E, cbf, Tbox, xbox, rtol=1e-3, decide=True, min_rel=min_rel)
        if res["L"] is not None and res["L"] > 1.0:
            lo = m
        else:
            hi = m
    for d in ("1e-4", "3e-4", "1e-3", "3e-3", "1e-2"):
        th_hi = arb(str(hi)) * (1 + arb(d))
        th_lo = arb(str(lo)) * (1 - arb(d))
        th_hi, th_lo = th_hi.mid(), th_lo.mid()
        rh = max_R(th_hi, sv, K, E, cbf, Tbox, xbox, rtol=float(d) / 4, decide=True, min_rel=min_rel)
        rl = max_R(th_lo, sv, K, E, cbf, Tbox, xbox, rtol=float(d) / 4, decide=True, min_rel=min_rel)
        if rh["certified_below_1"] and rl["witness_above_1"]:
            log(f"  [{label}] theta* in [{F(th_lo)}, {F(th_hi)}]: maxR(theta_hi) <= {rh['U']:.6f}; R(witness {rl['argmax']}, theta_lo) >= {rl['L']:.6f}")
            return {"theta_lo": F(th_lo), "theta_hi": F(th_hi), "maxR_at_theta_hi": [rh["L"], rh["U"]],
                    "witness_at_theta_lo": {"T_x": rl["argmax"], "R_lower": rl["L"]}, "argmax_at_theta_hi": rh["argmax"]}
    return {"theta_lo": None, "theta_hi": None, "note": "not separated"}


# ------------------------------------------------------------------ auxiliary certified facts
def certify_gamma_monotone() -> bool:
    """d/dt[t(1+1.1t+t^2-1.25t^2.5)] = 1+2.2t+3t^2-4.375t^2.5 > 0 on t in [0, 1]; the Zeff term is increasing."""
    def f(a: arb, b: arb) -> arb:
        t = iv(a, b)
        return 1 + A("2.2") * t + 3 * t * t - A("4.375") * t ** A("2.5")
    ok, n = certify_sign_1d(lambda a, b: f(a, b), arb("1e-30"), arb(1), +1)
    ok0 = True  # at t = 0 the derivative is exactly 1
    log(f"  gamma monotone in t on (0,1]: {ok} ({n} leaves)")
    return ok and ok0


def certify_S_nonneg() -> dict[str, bool]:
    res = {}
    for part, a, b in (("low", "0.5", "550"), ("high", "550", "4700")):
        ok, n = certify_sign_1d(lambda x, y: _bh_S_real(iv(x, y), part), arb(a), arb(b), +1)
        res[f"BH_S_{part}_positive"] = ok
    w = FITS["wang2026_pB11_S_factor"]
    for a, b in (("1e-9", "400"), ("400", "700"), ("700", "10000")):
        ok, n = certify_sign_1d(lambda x, y: wang_S_real(iv(x, y)), arb(a), arb(b), +1)
        res[f"Wang_S_{a}_{b}_positive"] = ok
    log(f"  S-factor positivity: {res}")
    return res


def _bh_S_real(E: arb, part: str) -> arb:
    p = FITS["bosch_hale_DT_cross_section"][part]
    num = A(p["A1"]) + E * (A(p["A2"]) + E * (A(p["A3"]) + E * (A(p["A4"]) + E * A(p["A5"]))))
    den = 1 + E * (A(p["B1"]) + E * (A(p["B2"]) + E * (A(p["B3"]) + E * A(p["B4"]))))
    return num / den


# ------------------------------------------------------------------ pipeline used by the gate and the negative controls
def run_pipeline(sv_scale: str, cbf_s: str, bh_int: CachedPointSV, label: str) -> dict[str, Any]:
    s, cbf = arb(sv_scale), arb(cbf_s)
    Kv = K_variants()
    log(f"pipeline '{label}': sv x {sv_scale}, bremsstrahlung x {cbf_s}")
    sv_par = lambda T: sv_bosch_hale_dt(T) * s  # noqa: E731
    sv_int = lambda T: bh_int(T) * s  # noqa: E731
    res: dict[str, Any] = {}
    res["T_ign"] = certify_T_ign("text", sv_par, Kv["code_fig6"], FC_CODE, cbf)          # Fig 6 / eq (8) path
    dt = run_dt("code", sv_int, Kv["code_tables"], FC_CODE, cbf, with_tign=False)         # Table II/III code path
    res.update({k: dt[k] for k in ("TP_Tmin", "TP_min", "LP_Tmin", "LP_min")})
    # constant hull: TP and LP = num/D with D increasing in fc and in K (sv > 0, sqrt(T) gamma / K > 0), so
    # min_T TP is decreasing in (fc, K); the hull's min-value range is spanned by the two corners.
    hull_res: dict[str, Any] = {"T_ign": certify_T_ign("text", sv_par, Kv["hull"], FC_HULL, cbf)}
    lo_c = run_dt("code", sv_int, arb(Kv["hull"].upper()), arb(FC_HULL.upper()), cbf, with_tign=False)
    hi_c = run_dt("code", sv_int, arb(Kv["hull"].lower()), arb(FC_HULL.lower()), cbf, with_tign=False)
    for k in ("TP_min", "LP_min"):
        hull_res[k] = [lo_c[k][0], hi_c[k][1]] if (lo_c[k] and hi_c[k]) else None
    hull_res["corners"] = {"K_hi_fc_hi": lo_c, "K_lo_fc_lo": hi_c}
    res["hull"] = hull_res
    sv_ns = lambda T: sv_nevins_swain(T) * s  # noqa: E731
    m = max_R(arb(1), sv_ns, Kv["code_tables"], A("8.7e3"), cbf, ("50", "500"), ("0.16666666666666666", "0.16666666666666667"), rtol=1e-4)
    res["pB_NS_WHmix_theta1"] = m
    res["pB_NS_WHmix_theta1_certified_below_1"] = bool(m["certified_below_1"])
    log(f"  result: {json.dumps({k: v for k, v in res.items() if k != 'pB_NS_WHmix_theta1'})}")
    return res


def main() -> None:
    t_start = time.time()
    out: dict[str, Any] = {}
    float_ref = json.loads((HERE.parent / "logs" / "float_indep.json").read_text())
    fr = {"T_ign": float_ref["DT_nonrel_param"]["T_ign"], "TP_min": float_ref["DT_rel_integrated"]["TP_min"],
          "LP_min": float_ref["DT_rel_integrated"]["LP_min"]}
    bh_int = CachedPointSV(bh_integrated_reactivity)

    only_pb = "pb" in sys.argv[1:]
    if only_pb:
        out["note"] = "stage run: p-11B and D-T variants only; gates are in certify_gates.json"
    log("== auxiliary certified facts")
    out["gamma_monotone"] = certify_gamma_monotone()
    out["S_nonneg"] = certify_S_nonneg()

    if not only_pb:
        log("== E1a positive control through the gate")
        pos = run_pipeline("1", "1", bh_int, "positive")
        out["positive"] = pos
        out["gate_positive"] = gate(pos, fr)
        log(f"  GATE positive: {out['gate_positive']}")

        log("== negative control NC1: reactivity x 0.5")
        nc1 = run_pipeline("0.5", "1", bh_int, "NC1_sv_half")
        out["NC1"] = nc1
        out["gate_NC1"] = gate(nc1, fr)
        log(f"  GATE NC1: {out['gate_NC1']}")

        log("== negative control NC2: bremsstrahlung removed")
        nc2 = run_pipeline("1", "0", bh_int, "NC2_no_brems")
        out["NC2"] = nc2
        out["gate_NC2"] = gate(nc2, fr)
        log(f"  GATE NC2: {out['gate_NC2']}")
        (HERE.parent / "logs" / ("certify_pb.json" if only_pb else "certify.json")).write_text(json.dumps(out, indent=1, default=str) + "\n")

        (HERE.parent / "logs" / ("certify_pb.json" if only_pb else "certify.json")).write_text(json.dumps(out, indent=1, default=str) + "\n")
    log("== E1b/E1c p-11B")
    Kv = K_variants()
    E = pb_E_keV()
    K = Kv["hull"]
    pb: dict[str, Any] = {}
    log("  building certified Wang reactivity grid on [50,500] keV, ratio 1.0005")
    sv_w = GridSV(wang_reactivity, "49.999999", "500.000001", "1.0005")
    log(f"  grid built: {len(sv_w.nodes)} certified integrals")
    for fit, sv in (("NS", sv_nevins_swain), ("Wang2026", sv_w)):
        if fit == "NS" and "wangonly" in sys.argv[1:]:
            prev = json.loads((HERE.parent / "logs" / "certify_pb_NS.json").read_text())["pB11"]
            pb.update({k: v for k, v in prev.items() if k.startswith("NS_")})
            log("  NS results loaded from logs/certify_pb_NS.json (same code, previous stage run)")
            continue
        mr = 1e-6 if fit == "NS" else 2e-4
        log(f" fit {fit}: max R at T_e = T_i over T in [50,500], x in [0.05,0.5]")
        rt = 1e-4 if fit == "NS" else 1e-3
        pb[f"{fit}_theta1_box"] = max_R(arb(1), sv, K, E, arb(1), ("50", "500"), ("0.05", "0.5"), rtol=rt, max_iter=100000, min_rel=mr)
        log(f"   {pb[f'{fit}_theta1_box']}")
        pb[f"{fit}_theta1_WHmix"] = max_R(arb(1), sv, K, E, arb(1), ("50", "500"), ("0.16666666666666666", "0.16666666666666667"), rtol=rt, max_iter=100000, min_rel=mr)
        log(f"   WH mix: {pb[f'{fit}_theta1_WHmix']}")
        pb[f"{fit}_theta_star_box"] = theta_threshold(sv, K, E, arb(1), ("50", "500"), ("0.05", "0.5"), f"{fit} box", min_rel=mr)
        pb[f"{fit}_theta_star_WHmix"] = theta_threshold(sv, K, E, arb(1), ("50", "500"), ("0.16666666666666666", "0.16666666666666667"), f"{fit} WH mix", min_rel=mr)
        out["pB11"] = pb
        (HERE.parent / "logs" / ("certify_pb.json" if only_pb else "certify.json")).write_text(json.dumps(out, indent=1, default=str) + "\n")
    # certified ratio Wang/NS at nodes (point enclosures)
    ratio = {}
    for T in ("50", "100", "150", "200", "250", "300", "350", "400", "450", "500"):
        r = wang_reactivity(arb(T)) / sv_nevins_swain(arb(T))
        ratio[T] = enc(r)
    pb["Wang_over_NS_points"] = ratio
    # m*: reactivity multiplier needed for any window at T_e = T_i
    for fit in ("NS", "Wang2026"):
        U = pb[f"{fit}_theta1_box"]["U"]
        L = pb[f"{fit}_theta1_box"]["L"]
        pb[f"{fit}_m_star"] = [1.0 / U, 1.0 / L]
    log(f"  m*: NS {pb['NS_m_star']}, Wang {pb['Wang2026_m_star']}; Wang/NS {ratio}")
    out["pB11"] = pb
    (HERE.parent / "logs" / ("certify_pb.json" if only_pb else "certify.json")).write_text(json.dumps(out, indent=1, default=str) + "\n")
    log("== E1a sensitivity: other D-T model variants (code constants and constant hull)")
    Kv = K_variants()
    sv_par = sv_bosch_hale_dt
    var: dict[str, Any] = {}
    for name, variant, sv in (("param_nonrel", "text", sv_par), ("param_rel", "code", sv_par),
                              ("integrated_nonrel", "text", bh_int), ("integrated_rel", "code", bh_int)):
        for kname, K, fc in ((("text", Kv["text"], FC_CODE),) if variant == "text" else (("code_tables", Kv["code_tables"], FC_CODE),)):
            if name == "integrated_rel":
                continue  # identical to the positive-control pipeline above
            log(f" variant {name} / K={kname}")
            var[f"{name}|{kname}"] = run_dt(variant, sv, K, fc, arb(1), with_tign=(name.startswith("param")))
    out["dt_variants"] = var

    out["n_wang_integrals"] = len(sv_w.nodes)
    out["n_bh_integrals"] = len(bh_int.cache)
    out["wall_seconds"] = round(time.time() - t_start, 1)
    (HERE.parent / "logs" / ("certify_pb.json" if only_pb else "certify.json")).write_text(json.dumps(out, indent=1, default=str) + "\n")
    (HERE.parent / "logs" / ("certify_pb.log" if only_pb else "certify.log")).write_text("\n".join(LOG) + "\n")
    log(f"done in {out['wall_seconds']} s")


if __name__ == "__main__":
    main()
