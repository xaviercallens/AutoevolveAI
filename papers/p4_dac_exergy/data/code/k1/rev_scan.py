"""Revision 2026-10-27 (audit items B1, B3, B4, N4): joint grid over the 14 Table 2 rows that stores, for every
evaluated path, the separate exergy cost COMPONENTS, so that every accounting scenario (heat recovery r, feed-air
chilling with recuperator effectiveness eps, machine second-law efficiencies, purity constraint, ambient T0) can be
evaluated afterwards on the same set of paths (rev_analyse.py).

Model: the producer's re-implementation of the published evaluator (dac_model.nominal_path, unchanged), step-3 return
with the right-point rule of the published step 2 (exergy.step3_quadrature "right", the revised convention).

Grid (a choice, stated in the paper): T1 in {200, 210, ..., 400} U {205, 215, 225, 235, 245} U {270, 272, ..., 298}
U {273.15, 298.15, 313.15} K; dT in {0, 10, ...} with T_end <= 400 K (the C_V training range; the published
optimiser allows T_end up to 600 K); P_end in {100, 1000, 5000, 20000, 60000, P1} Pa (P_end <= P1, >= 100 Pa).
Then a refinement (T1 +-10 K step 2, dT +-10 K step 5, P_end x {0.5, 0.7, 1, 1.4, 2} clipped to [100, P1]) around
the best overall / best cold / best warm / best purity-constrained cells of each of these accountings: baseline
(no feed-air pricing) at T0 in {273.15, 298.15, 313.15} K and r in {0, 0.5, 1}; feed air priced with eps = 0 at
T0 = 298.15 K and r in {0, 0.5, 1}.

Components per path and T0 (J/kg sorbent; heats signed as in exergy.py):
  hin   = sum over heat IN at T > T0 of Q (1 - T0/T)            (heat-pump cost)
  refr  = sum over heat OUT at T < T0 of Q (T0/T - 1)           (refrigeration cost)
  ccold = sum over heat IN at T <= T0 of Q (T0/T - 1)           (reversible credit)
  chot  = sum over heat OUT at T >= T0 of Q (1 - T0/T)          (reversible credit)
  air   = ideal exergy to bring the contacted feed air from T0 to T1 and NOT recover it:
          n_air c_p [T0 ln(T0/T1) - (T0 - T1)] (refrigeration, T1 < T0) or n_air c_p [(T1 - T0) - T0 ln(T1/T0)]
          (heat pump, T1 > T0), n_air = dn_CO2 / x_air (capture fraction f = 1, the case most favourable to a cold
          start), x_air = 400e-6 (alpha in run_optimize_intrinsic_dac.jl:15), c_p = 7/2 R.
  W     = works at face value (W_ads + W_des + E_P); WEP = E_P only.
Self-check: hin + refr and ccold + chot reproduce fast_costs.costs (an independent implementation) nc and credit.

Usage: python -I rev_scan.py <DAC_data dir> <positive_control.json> <out_raw.json>
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cv_gp import CvGP  # noqa: E402
from dac_model import R, Terms, linear_path, nominal_path  # noqa: E402
from exergy import step3_quadrature  # noqa: E402
from fast_costs import costs as fast_costs_costs  # noqa: E402
from load_data import Dataset  # noqa: E402
from run_scan import material_inputs  # noqa: E402
from stored import terms_from_stored  # noqa: E402

T0S = (273.15, 298.15, 313.15)
X_AIR = 400e-6
CP_AIR = 3.5 * R
T_END_MAX = 400.0


def components(t: Terms, T0: float) -> dict:
    ts = t.ts
    tm = 0.5 * (ts[1:] + ts[:-1])
    q1_out = t.Q_ads_co2 + t.Q_ads_n2
    qin2 = (t.Q_des_co2 + t.Q_des_n2 + t.E_heat_co2 + t.E_heat_n2 + t.E_heat_sorb)[1:]
    gas_c = 4.5 * R * t.n_co2[-1] + 3.5 * R * t.n_n2[-1]
    q3_out = step3_quadrature(np.asarray(t.cv, dtype=float) + gas_c, ts, "right")
    Tq = np.concatenate([[ts[0]], tm, tm])
    qin = np.concatenate([[-q1_out], qin2, -q3_out])
    ok = np.isfinite(qin) & (qin != 0.0)
    Tq, qin = Tq[ok], qin[ok]
    m_hin = (qin > 0) & (Tq > T0)
    m_ccold = (qin > 0) & (Tq <= T0)
    m_refr = (qin < 0) & (Tq < T0)
    m_chot = (qin < 0) & (Tq >= T0)
    T1 = float(ts[0])
    n_air = t.dn_co2 / X_AIR
    if T1 < T0:
        air = n_air * CP_AIR * (T0 * math.log(T0 / T1) - (T0 - T1))
        air_refr = 1
    else:
        air = n_air * CP_AIR * ((T1 - T0) - T0 * math.log(T1 / T0))
        air_refr = 0
    return {"hin": float(np.sum(qin[m_hin] * (1.0 - T0 / Tq[m_hin]))),
            "refr": float(np.sum(-qin[m_refr] * (T0 / Tq[m_refr] - 1.0))),
            "ccold": float(np.sum(qin[m_ccold] * (T0 / Tq[m_ccold] - 1.0))),
            "chot": float(np.sum(-qin[m_chot] * (1.0 - T0 / Tq[m_chot]))),
            "air": float(air), "air_refr": air_refr}


def works(t: Terms) -> tuple[float, float]:
    ep = float(np.nansum(t.E_P))
    return float(t.W_ads_co2 + t.W_ads_n2 + np.nansum(t.W_des_co2 + t.W_des_n2)) + ep, ep


def evaluate(ctx: dict, T1: float, dT: float, Pend: float) -> dict | None:
    P1 = ctx["P1"]
    Pend = min(max(Pend, 100.0), P1)
    if T1 < 200.0 - 1e-9 or T1 > 400.0 + 1e-9 or dT < 0 or T1 + dT > T_END_MAX + 1e-9:
        return None
    key = (round(T1, 6), round(dT, 6), round(Pend, 3))
    if key in ctx["cache"]:
        return ctx["cache"][key]
    rec = None
    ts, ps = linear_path(T1, dT, P1, Pend - P1)
    if ts.size >= 2:
        try:
            t = nominal_path(ts, ps, X_AIR, ctx["kc"], ctx["kn"], ctx["mat"], ctx["sat"], ctx["gp"])
        except (ValueError, FloatingPointError, ZeroDivisionError):
            t = None
        if t is not None and t.ts.size >= 2 and t.dn_co2 > 0 and np.isfinite(t.E) and t.E > 0:
            W, WEP = works(t)
            rec = {"T1_req": T1, "dT": dT, "Pend_req": Pend, "T1": float(t.ts[0]), "Tend": float(t.ts[-1]),
                   "Pend": float(t.ps[-1]), "dnc": float(t.dn_co2), "purity": float(t.purity), "E_fv": float(t.E),
                   "W": W, "WEP": WEP}
            for T0 in T0S:
                c = components(t, T0)
                rec[str(T0)] = c
                f = fast_costs_costs(t, T0, "right")
                for a, b in ((c["hin"] + c["refr"], f["nc"]), (c["ccold"] + c["chot"], f["credit"]), (W, f["works"])):
                    ctx["xcheck"] = max(ctx["xcheck"], abs(a - b) / max(abs(b), 1e-30))
    ctx["cache"][key] = rec
    return rec


def cost(rec: dict, T0: float, r: float, eps: float | None) -> float:
    c = rec[str(T0)]
    b = rec["W"] + c["hin"] + c["refr"] - r * (c["ccold"] + c["chot"])
    if eps is not None:
        b += (1.0 - eps) * c["air"]
    return b


def valid(rec: dict | None, P1: float) -> bool:
    if rec is None:
        return False
    no_swing = abs(rec["Tend"] - rec["T1"]) < 1e-9 and abs(rec["Pend"] - P1) < 1e-6
    return (not no_swing) and rec["dnc"] > 1e-6


def best(recs: list, T0: float, r: float, eps: float | None, side: str, pmin: float | None) -> dict | None:
    bb, bv = None, -1.0
    for x in recs:
        if side == "cold" and not x["T1"] < T0:
            continue
        if side == "warm" and not x["T1"] >= T0:
            continue
        if pmin is not None and x["purity"] < pmin:
            continue
        b = cost(x, T0, r, eps)
        if b <= 0:
            continue
        v = x["dnc"] / b
        if v > bv:
            bb, bv = x, v
    return bb


def main() -> int:
    ds = Dataset(Path(sys.argv[1]))
    pc = json.loads(Path(sys.argv[2]).read_text())
    outp = Path(sys.argv[3])
    t0 = time.time()
    T1_grid = sorted(set([float(x) for x in np.arange(200.0, 400.0 + 1e-9, 10.0)] + [205.0, 215.0, 225.0, 235.0, 245.0]
                         + [float(x) for x in np.arange(270.0, 298.0 + 1e-9, 2.0)] + list(T0S)))
    rows = []
    xcheck_all = 0.0
    for row in pc["rows"]:
        name = row["row"][0].replace(" ", "_")
        opt = ds.optimized(name)
        i = row["solution_index"]
        st = terms_from_stored(opt, i)
        mat, sat = material_inputs(ds, name, opt, i)
        cvj = ds.cv(name)
        P1 = float(st.ps[0])
        ctx = {"P1": P1, "kc": ds.kh_co2(name), "kn": ds.kh_n2(name), "mat": mat, "sat": sat,
               "gp": CvGP(cvj["Temperatures"], cvj["Cv"], cvj["CV_err"]), "cache": {}, "xcheck": 0.0}
        for T1 in T1_grid:
            for dT in np.arange(0.0, T_END_MAX - T1 + 1e-9, 10.0):
                for Pend in (100.0, 1000.0, 5000.0, 20000.0, 60000.0, P1):
                    evaluate(ctx, float(T1), float(dT), float(Pend))
        pmin = float(st.purity)
        scen = [(T0, r, None) for T0 in T0S for r in (0.0, 0.5, 1.0)] + [(298.15, r, 0.0) for r in (0.0, 0.5, 1.0)]
        centres = set()
        pool = [x for x in ctx["cache"].values() if valid(x, P1)]
        for T0, r, eps in scen:
            for side, pm in (("all", None), ("cold", None), ("warm", None), ("all", pmin)):
                b = best(pool, T0, r, eps, side, pm)
                if b is not None:
                    centres.add((b["T1_req"], b["dT"], b["Pend_req"]))
        for T1c, dTc, Pc in sorted(centres):
            for T1 in np.arange(T1c - 10.0, T1c + 10.0 + 1e-9, 2.0):
                for dT in np.arange(dTc - 10.0, dTc + 10.0 + 1e-9, 5.0):
                    for f in (0.5, 0.7, 1.0, 1.4, 2.0):
                        evaluate(ctx, float(T1), float(max(dT, 0.0)), float(Pc * f))
        recs = [x for x in ctx["cache"].values() if x is not None]
        xcheck_all = max(xcheck_all, ctx["xcheck"])
        rows.append({"name": name, "row": row["row"], "solution_index": i, "P1": P1, "purity_min": pmin,
                     "T1_stored": float(st.ts[0]), "n_evaluated": len(ctx["cache"]), "n_paths": len(recs),
                     "n_refinement_centres": len(centres), "recs": recs})
        print(name, "paths", len(recs), "centres", len(centres), "xcheck", f"{ctx['xcheck']:.2e}",
              round(time.time() - t0), flush=True)
    meta = {"T0s": list(T0S), "x_air": X_AIR, "cp_air_J_per_molK": CP_AIR, "T_end_max": T_END_MAX,
            "T1_grid": T1_grid, "step3_rule": "right", "xcheck_components_vs_fast_costs_max_rel": xcheck_all,
            "seconds": round(time.time() - t0, 1)}
    outp.write_text(json.dumps({"meta": meta, "rows": rows}, default=float))
    print(json.dumps(meta, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
