"""Revision 2026-10-27: analyse the component scan of rev_scan.py (audit items B3, B4, N12).

Scenario families (all at the per-path components stored by rev_scan.py, step-3 right-point rule):
  BASE   : the v1 accounting (heats Carnot-weighted at T0, works at face value, step 3 priced, ideal machines, feed
           air NOT priced), r in {0, 0.5, 1}, T0 in {273.15, 298.15, 313.15} K, purity constraint on/off.
  AIR    : BASE plus the exergy of bringing the contacted feed air from T0 to T1, unrecovered share (1 - eps),
           eps = recuperator effectiveness in [0, 1] (eps = 1 is BASE). n_air = dn_CO2 / x_air (capture fraction
           f = 1, most favourable to a cold start; for f < 1 replace (1 - eps) by (1 - eps)/f).
  AIR-R  : AIR with the refrigerator (sorbent refrigeration and feed-air chilling) at second-law efficiency eta_R,
           heat pump ideal (refrigerator-only degradation; a mixed bookend).
  AIR-S  : AIR with both machines at eta: heat-pump and refrigeration costs divided by eta, reversible credits
           multiplied by eta (symmetric degradation).
  NEG    : H1 negative control: refrigeration (sorbent + air, eps = 0) weighted x M. Warm paths (T1 >= T0) reject
           no heat below T0, so their cost does not depend on M; every cold path pays M x (its step-1 heat removal
           below T0) > 0, so for M large enough cold MUST lose on any finite grid. Reported for M = 100 and 1e4.
  FREE   : sanity check, refrigeration and air free (M = 0): cold must not do worse than in BASE.

Splits of the start temperature (each a pair of half-open T1 intervals; ratio = best xi in COLD / best xi in WARM):
  v1   : COLD T1 < T0,            WARM T1 >= T0 (the definition of v1);
  d10  : COLD T1 <= T0 - 10 K,    WARM T1 > T0 - 10 K (a "materially cold" start against ambient or near-ambient);
  aud  : COLD T1 <= 290 K,        WARM T1 >= 298.15 K (the auditor's 10 K grid has no cell in between; T0 = 298.15 only).
Outcome of a scenario per row: "cold" if T1* <= T0 - 10 K, "near-ambient" if T0 - 10 K < T1* < T0, "warm" if T1* >= T0.

Usage: python -I rev_analyse.py <scan_raw.json> <out.json> [<auditor h1_analysis.json>]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

T0S = (273.15, 298.15, 313.15)
RS = (0.0, 0.5, 1.0)
EPS_GRID = (0.0, 0.5, 0.8, 0.9, 0.95, 0.99, 1.0)
INF = 1e9
TOL = 1e-9


def splits(T0: float) -> dict:
    s = {"v1": ((0.0, T0), (T0, INF)), "d10": ((0.0, T0 - 10.0 + TOL), (T0 - 10.0 + TOL, INF))}
    if abs(T0 - 298.15) < 1e-9:
        s["aud"] = ((0.0, 290.0 + TOL), (298.15, INF))
    return s


def cost(x: dict, T0: float, r: float, eps: float = 1.0, eta_r: float = 1.0, eta_hp: float = 1.0,
         eta_credit: float = 1.0, refr_mult: float | None = None) -> float:
    c = x[str(T0)]
    mr = (1.0 / eta_r) if refr_mult is None else refr_mult
    b = x["W"] + c["hin"] / eta_hp + c["refr"] * mr - r * eta_credit * (c["ccold"] + c["chot"])
    if eps < 1.0:
        b += (1.0 - eps) * c["air"] * (mr if c["air_refr"] else 1.0 / eta_hp)
    return b


def xi_of(x: dict, T0: float | None, r: float, **kw) -> float | None:
    if T0 is None:
        return x["dnc"] / x["E_fv"] * 1e6 if x["E_fv"] > 0 else None
    b = cost(x, T0, r, **kw)
    return x["dnc"] / b * 1e6 if b > 0 else None


def best(recs: list, T0: float | None, r: float, band: tuple, pmin: float | None, **kw) -> dict | None:
    lo, hi = band
    bb = None
    for x in recs:
        if not (lo <= x["T1"] < hi):
            continue
        if pmin is not None and x["purity"] < pmin:
            continue
        v = xi_of(x, T0, r, **kw)
        if v is None:
            continue
        if bb is None or v > bb["xi"]:
            bb = {"xi": v, "T1": x["T1"], "Tend": x["Tend"], "Pend": x["Pend"], "purity": x["purity"]}
    return bb


def ratio(recs: list, T0: float | None, r: float, split: tuple, pmin: float | None = None, **kw):
    c = best(recs, T0, r, split[0], pmin, **kw)
    w = best(recs, T0, r, split[1], pmin, **kw)
    q = (c["xi"] / w["xi"]) if (c and w) else None
    return q, c, w


def outcome(T1: float, T0: float) -> str:
    return "cold" if T1 <= T0 - 10.0 + TOL else ("near-ambient" if T1 < T0 else "warm")


def threshold(recs: list, T0: float, r: float, split: tuple, kw_of, lo: float, hi: float) -> dict:
    """Value p* of a scalar parameter in [lo, hi] at which the cold/warm ratio crosses 1 (bisection after a 100-point
    scan that counts crossings, so a non-monotone dependence is visible)."""
    def f(p: float) -> float | None:
        return ratio(recs, T0, r, split, None, **kw_of(p))[0]
    grid = [lo + (hi - lo) * i / 100.0 for i in range(101)]
    vals = [f(p) for p in grid]
    signs = [None if v is None else (v > 1.0) for v in vals]
    cross = [j for j in range(100) if signs[j] is not None and signs[j + 1] is not None and signs[j] != signs[j + 1]]
    out = {"ratio_at_lo": vals[0], "ratio_at_hi": vals[-1], "crossings": len(cross)}
    if not cross:
        out["p_star"] = None
        out["note"] = "cold wins over the whole range" if signs[0] else "warm wins over the whole range"
        return out
    j = cross[0]
    a, b = grid[j], grid[j + 1]
    sa = signs[j]
    for _ in range(40):
        m = 0.5 * (a + b)
        if (f(m) > 1.0) == sa:
            a = m
        else:
            b = m
    out["p_star"] = 0.5 * (a + b)
    out["note"] = "warm wins below p_star" if not sa else "cold wins below p_star"
    return out


def rnd(v: float | None, n: int = 4) -> float | None:
    return None if v is None else round(v, n)


def main() -> int:
    raw = json.loads(Path(sys.argv[1]).read_text())
    outp = Path(sys.argv[2])
    aud = json.loads(Path(sys.argv[3]).read_text()) if len(sys.argv) > 3 else None
    rows_out = []
    for row in raw["rows"]:
        P1 = row["P1"]
        recs = [x for x in row["recs"] if not (abs(x["Tend"] - x["T1"]) < 1e-9 and abs(x["Pend"] - P1) < 1e-6)
                and x["dnc"] > 1e-6]
        pm = row["purity_min"]
        res = {"name": row["name"], "xi_pub": row["row"][1], "n_paths": len(recs), "purity_min": pm,
               "T1_stored": row["T1_stored"]}
        # ---------------- B4: vacuity of the purity-constrained variants ----------------
        vac = {}
        for T0 in T0S:
            warm = [x for x in recs if x["T1"] >= T0]
            ok = [x for x in warm if x["purity"] >= pm]
            vac[str(T0)] = {"warm_cells": len(warm), "warm_cells_meeting_purity": len(ok), "vacuous": not ok,
                            "best_warm_purity": max((x["purity"] for x in warm), default=None)}
        res["vacuity"] = vac
        # ---------------- BASE: 18 variants ----------------
        t1 = {}
        for cons in (False, True):
            for T0 in T0S:
                for r in RS:
                    b = best(recs, T0, r, (0.0, INF), pm if cons else None)
                    t1[f"{'C' if cons else 'U'}_{T0}_{r}"] = None if b is None else {
                        "T1": rnd(b["T1"], 2), "ge_T0": b["T1"] >= T0, "outcome": outcome(b["T1"], T0),
                        "vacuous": bool(cons and vac[str(T0)]["vacuous"])}
        res["base_T1star"] = t1
        res["fv_T1star"] = best(recs, None, 0.0, (0.0, INF), None)
        sp = splits(298.15)
        res["base_ratio"] = {}
        for lab, T0, r in (("fv", None, 0.0), ("r0", 298.15, 0.0), ("r05", 298.15, 0.5), ("r1", 298.15, 1.0)):
            for sname, s in sp.items():
                q, c, w = ratio(recs, T0, r, s)
                res["base_ratio"][f"{lab}_{sname}"] = {"ratio": q, "cold": c, "warm": w}
        # ---------------- AIR family ----------------
        air = {}
        for T0 in T0S:
            for r in RS:
                for eps in EPS_GRID:
                    b = best(recs, T0, r, (0.0, INF), None, eps=eps)
                    d = {"T1star": b["T1"], "Tend": b["Tend"], "purity": b["purity"], "xi_star": b["xi"],
                         "outcome": outcome(b["T1"], T0)}
                    for sname, s in splits(T0).items():
                        q, c, w = ratio(recs, T0, r, s, eps=eps)
                        d[f"ratio_{sname}"] = q
                        d[f"cold_{sname}"] = c
                        d[f"warm_{sname}"] = w
                    air[f"{T0}_{r}_{eps}"] = d
        res["air"] = air
        res["eps_star"] = {}
        for T0 in T0S:
            for r in RS:
                for sname, s in splits(T0).items():
                    res["eps_star"][f"{T0}_{r}_{sname}"] = threshold(recs, T0, r, s, lambda p: {"eps": p}, 0.0, 1.0)
        # ---------------- machine efficiency sensitivity (T0 = 298.15) ----------------
        res["eta"] = {}
        for mode in ("R", "S"):
            for eps in (1.0, 0.0):
                for r in (0.0, 1.0):
                    for sname in ("d10", "aud"):
                        def kw(p: float, mode: str = mode, eps: float = eps) -> dict:
                            return ({"eps": eps, "eta_r": p} if mode == "R"
                                    else {"eps": eps, "eta_r": p, "eta_hp": p, "eta_credit": p})
                        res["eta"][f"{mode}_eps{eps}_r{r}_{sname}"] = threshold(recs, 298.15, r, sp[sname], kw, 0.01, 1.0)
        res["eps_star_eta0.5"] = {}
        for mode in ("R", "S"):
            for r in RS:
                def kw2(p: float, mode: str = mode) -> dict:
                    return ({"eps": p, "eta_r": 0.5} if mode == "R"
                            else {"eps": p, "eta_r": 0.5, "eta_hp": 0.5, "eta_credit": 0.5})
                res["eps_star_eta0.5"][f"{mode}_{r}_d10"] = threshold(recs, 298.15, r, sp["d10"], kw2, 0.0, 1.0)
        # ---------------- N12: H1 negative control and a sanity control ----------------
        neg = {}
        for M in (100.0, 1e4):
            for r in RS:
                q, c, w = ratio(recs, 298.15, r, sp["v1"], eps=0.0, refr_mult=M)
                b = best(recs, 298.15, r, (0.0, INF), None, eps=0.0, refr_mult=M)
                neg[f"M{M:g}_r{r}"] = {"ratio_v1": q, "T1star": b["T1"],
                                       "detected_warm": bool(q is not None and q < 1.0 and b["T1"] >= 298.15)}
        res["neg_control"] = neg
        free = {}
        for lab, r in (("r0", 0.0), ("r05", 0.5), ("r1", 1.0)):
            q, _, _ = ratio(recs, 298.15, r, sp["v1"], refr_mult=0.0)
            qb = res["base_ratio"][f"{lab}_v1"]["ratio"]
            free[lab] = {"ratio": q, "ratio_base": qb, "not_worse_than_base": bool(q is not None and q >= qb - 1e-12)}
        res["free_refrigeration_sanity"] = free
        rows_out.append(res)
        a0, a1 = air["298.15_0.0_0.0"], air["298.15_1.0_0.0"]
        print(res["name"], res["xi_pub"], "vac298", vac["298.15"]["vacuous"], "T1*U298r0", t1["U_298.15_0.0"]["T1"],
              "| air eps0 r0", rnd(a0["T1star"], 2), rnd(a0["ratio_d10"], 3), "r1", rnd(a1["T1star"], 2), a1["outcome"],
              rnd(a1["ratio_v1"], 4), rnd(a1["ratio_d10"], 3), rnd(a1["ratio_aud"], 3), "eps*d10 r1",
              rnd(res["eps_star"]["298.15_1.0_d10"]["p_star"], 3), "eps*aud r1",
              rnd(res["eps_star"]["298.15_1.0_aud"]["p_star"], 3),
              "neg", [neg[k]["detected_warm"] for k in neg], flush=True)
    # ---------------- aggregates ----------------
    agg: dict = {"n_rows": len(rows_out)}
    agg["base_rows_T1star_ge_T0"] = {k: sum(1 for x in rows_out if x["base_T1star"][k] and x["base_T1star"][k]["ge_T0"])
                                     for k in rows_out[0]["base_T1star"]}
    agg["base_T1star_range_all_18"] = [min(v["T1"] for x in rows_out for v in x["base_T1star"].values() if v),
                                       max(v["T1"] for x in rows_out for v in x["base_T1star"].values() if v)]
    agg["vacuous_row_T0"] = {str(T0): len([x for x in rows_out if x["vacuity"][str(T0)]["vacuous"]]) for T0 in T0S}
    n_vac = sum(3 for x in rows_out for T0 in T0S if x["vacuity"][str(T0)]["vacuous"])
    agg["variants_total"] = len(rows_out) * 18
    agg["constrained_variants_vacuous"] = n_vac
    agg["informative_variants"] = len(rows_out) * 18 - n_vac
    for key in rows_out[0]["base_ratio"]:
        v = [x["base_ratio"][key]["ratio"] for x in rows_out if x["base_ratio"][key]["ratio"] is not None]
        agg[f"base_ratio_{key}_range"] = [min(v), max(v)] if v else None
    for T0 in T0S:
        for r in RS:
            for eps in EPS_GRID:
                k = f"{T0}_{r}_{eps}"
                xs = [x["air"][k] for x in rows_out]
                a = {"outcomes": {o: sum(1 for y in xs if y["outcome"] == o) for o in ("cold", "near-ambient", "warm")},
                     "rows_T1star_ge_T0": sum(1 for y in xs if y["T1star"] >= T0),
                     "T1star_range": [min(y["T1star"] for y in xs), max(y["T1star"] for y in xs)]}
                for sname in splits(T0):
                    v = [y[f"ratio_{sname}"] for y in xs if y[f"ratio_{sname}"] is not None]
                    a[f"ratio_{sname}_range"] = [min(v), max(v)]
                    a[f"rows_warm_wins_{sname}"] = sorted(x["name"] + " " + x["xi_pub"] for x in rows_out
                                                          if x["air"][k][f"ratio_{sname}"] is not None
                                                          and x["air"][k][f"ratio_{sname}"] < 1.0)
                agg[f"air_{k}"] = a
    agg["neg_control_all_rows_detected"] = {k: all(x["neg_control"][k]["detected_warm"] for x in rows_out)
                                            for k in rows_out[0]["neg_control"]}
    agg["neg_control_rows_detected"] = {k: sum(1 for x in rows_out if x["neg_control"][k]["detected_warm"])
                                        for k in rows_out[0]["neg_control"]}
    agg["free_refrigeration_sanity_all_rows"] = {k: all(x["free_refrigeration_sanity"][k]["not_worse_than_base"]
                                                        for x in rows_out) for k in ("r0", "r05", "r1")}
    # ---------------- comparison with the auditor (overlapping rows) ----------------
    if aud:
        target = {"FASJAL_clean": "8.186(69)", "BEVQID_clean": "9.186(66)", "VANNIK_clean": "11.259(38)"}
        comp = []
        for a in aud:
            m = next((x for x in rows_out if x["name"] == a["name"] and x["xi_pub"] == target.get(a["name"])), None)
            if m is None:
                continue
            comp.append({
                "name": a["name"], "xi_pub": m["xi_pub"],
                "base_ratio_fv": [a["ratio_fv"], m["base_ratio"]["fv_v1"]["ratio"]],
                "base_ratio_r0": [a["ratio_r0"], m["base_ratio"]["r0_v1"]["ratio"]],
                "base_ratio_r1": [a["ratio_r1"], m["base_ratio"]["r1_v1"]["ratio"]],
                "air_eps0_r0_T1star": [a["variants_298"]["air_eps0.0_r0.0"]["T1star"], m["air"]["298.15_0.0_0.0"]["T1star"]],
                "air_eps0_r0_ratio_aud": [a["variants_298"]["air_eps0.0_r0.0"]["ratio"], m["air"]["298.15_0.0_0.0"]["ratio_aud"]],
                "air_eps0_r1_ratio_aud": [a["variants_298"]["air_eps0.0_r1.0"]["ratio"], m["air"]["298.15_1.0_0.0"]["ratio_aud"]],
                "eps_star_r1_aud": [a["eps_star_r1"], m["eps_star"]["298.15_1.0_aud"]["p_star"]],
                "eta_star_R_r1_noair_aud": [a["eta_star_r1"], m["eta"]["R_eps1.0_r1.0_aud"]["p_star"]],
                "eta_star_R_r0_noair_aud": [a["eta_star_r0"], m["eta"]["R_eps1.0_r0.0_aud"]["p_star"]],
                "warm_cells_meeting_purity_298": [a["warm_cells_meeting_purity_T0_298"],
                                                  m["vacuity"]["298.15"]["warm_cells_meeting_purity"]]})
        agg["auditor_comparison_[auditor, producer_revision]"] = comp
    outp.write_text(json.dumps({"meta": raw["meta"], "aggregate": agg, "rows": rows_out}, indent=1, default=float))
    print(json.dumps(agg, indent=1, default=float)[:30000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
