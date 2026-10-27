"""K1-H1 joint scan per the 2026-10-27T13:00Z amendment (logs/h1_protocol_amendment_2026-10-27T1300Z.md)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cv_gp import CvGP  # noqa: E402
from dac_model import linear_path, nominal_path  # noqa: E402
from exergy import build_ledger, exergy_cost, face_value_cost  # noqa: E402
from fast_costs import xi_set  # noqa: E402
from load_data import Dataset, arr  # noqa: E402
from run_scan import material_inputs  # noqa: E402
from stored import terms_from_stored  # noqa: E402

T0S = (273.15, 298.15, 313.15)
RS = (0.0, 0.5, 1.0)
KEYS = ["fv"] + [f"ex_{T0}_{r}" for T0 in T0S for r in RS]


def evaluate(ctx: dict, T1: float, dT: float, Pend: float) -> dict | None:
    P1 = ctx["P1"]
    # search domain of the published optimizer: T1 in [200, 400], T_end <= 400 (dT <= 200 not binding here),
    # P_end >= 100 Pa (Delta P lower bound 100 - P1 in Path_optimizer.jl)
    if Pend > P1 or Pend < 100.0 - 1e-9 or T1 + dT > 400.0 + 1e-9 or T1 < 200.0 - 1e-9 or dT < 0:
        return None
    key = (round(T1, 6), round(dT, 6), round(Pend, 3))
    if key in ctx["cache"]:
        return ctx["cache"][key]
    ts, ps = linear_path(T1, dT, P1, Pend - P1)
    rec = None
    if ts.size >= 2:
        try:
            t = nominal_path(ts, ps, 400e-6, ctx["kc"], ctx["kn"], ctx["mat"], ctx["sat"], ctx["gp"])
        except (ValueError, FloatingPointError):
            t = None
        if t is not None and t.ts.size >= 2 and t.dn_co2 > 0 and np.isfinite(t.E):
            rec = {"T1_req": T1, "dT": dT, "Pend": Pend, "T1": float(t.ts[0]), "Tend": float(t.ts[-1]),
                   "purity": float(t.purity), **xi_set(t, T0S, RS)}
    ctx["cache"][key] = rec
    return rec


def best(recs: list, key: str, pmin: float | None) -> dict | None:
    c = [r for r in recs if r and r.get(key) is not None and (pmin is None or r["purity"] >= pmin)]
    return max(c, key=lambda r: r[key]) if c else None


def main() -> int:
    ds = Dataset(Path(sys.argv[1]))
    pc = json.loads(Path(sys.argv[2]).read_text())
    outp = Path(sys.argv[3])
    t0 = time.time()
    rows = []
    xcheck = []
    for row in pc["rows"]:
        name = row["row"][0].replace(" ", "_")
        opt = ds.optimized(name)
        i = row["solution_index"]
        st = terms_from_stored(opt, i)
        # independent-implementation cross-check (fast_costs vs ledger) on the stored path
        L = build_ledger(st)
        xs = xi_set(st, T0S, RS)
        xcheck.append(max([abs(xs["fv"] - st.dn_co2 / face_value_cost(L) * 1e6) / xs["fv"]] +
                          [abs(xs[f"ex_{T0}_{r}"] - st.dn_co2 / exergy_cost(L, T0, r) * 1e6) / xs[f"ex_{T0}_{r}"]
                           for T0 in T0S for r in RS]))
        mat, sat = material_inputs(ds, name, opt, i)
        cvj = ds.cv(name)
        ctx = {"P1": float(st.ps[0]), "kc": ds.kh_co2(name), "kn": ds.kh_n2(name), "mat": mat, "sat": sat,
               "gp": CvGP(cvj["Temperatures"], cvj["Cv"], cvj["CV_err"]), "cache": {}}
        coarse = []
        for T1 in np.arange(200.0, 320.0 + 1e-9, 10.0):
            for dT in np.arange(0.0, 400.0 - T1 + 1e-9, 10.0):
                for Pend in (100.0, 1000.0, 5000.0, 20000.0, 60000.0):
                    coarse.append(evaluate(ctx, float(T1), float(dT), Pend))
        res = {"name": name, "row": row["row"], "P1": ctx["P1"], "purity_min": float(st.purity),
               "T1_stored": float(st.ts[0])}
        for cons in (False, True):
            pmin = float(st.purity) if cons else None
            tag = "constrained" if cons else "unconstrained"
            res[tag] = {}
            for k in KEYS:
                b = best(coarse, k, pmin)
                if b is None:
                    res[tag][k] = None
                    continue
                ref = [b]
                for T1 in np.arange(b["T1_req"] - 10.0, b["T1_req"] + 10.0 + 1e-9, 2.0):
                    for dT in np.arange(b["dT"] - 10.0, b["dT"] + 10.0 + 1e-9, 5.0):
                        for f in (0.5, 0.7, 1.0, 1.4, 2.0):
                            ref.append(evaluate(ctx, float(T1), float(max(dT, 0.0)), b["Pend"] * f))
                bb = best(ref, k, pmin)
                res[tag][k] = {kk: bb[kk] for kk in ("T1", "Tend", "dT", "Pend", "purity", k)}
                # also: value of this accounting at the face-value optimum (for the ratio statement)
        res["n_evaluated"] = len(ctx["cache"])
        rows.append(res)
        u, c = res["unconstrained"], res["constrained"]
        print(name, "fvU", u["fv"] and (round(u["fv"]["T1"], 1), round(u["fv"]["Tend"], 1), u["fv"]["Pend"],
                                         round(u["fv"]["fv"], 3)),
              "| exU298r0", u["ex_298.15_0.0"] and (round(u["ex_298.15_0.0"]["T1"], 1), round(u["ex_298.15_0.0"]["Tend"], 1),
                                                    u["ex_298.15_0.0"]["Pend"], round(u["ex_298.15_0.0"]["purity"], 4),
                                                    round(u["ex_298.15_0.0"]["ex_298.15_0.0"], 2)),
              "| exU298r1", u["ex_298.15_1.0"] and (round(u["ex_298.15_1.0"]["T1"], 1), round(u["ex_298.15_1.0"]["purity"], 4)),
              "| exC298r0", c["ex_298.15_0.0"] and round(c["ex_298.15_0.0"]["T1"], 1),
              "n", res["n_evaluated"], round(time.time() - t0), flush=True)
        outp.write_text(json.dumps({"rows": rows, "xcheck_max_rel": max(xcheck)}, default=float))
    summ = {"xcheck_fast_vs_ledger_max_rel": max(xcheck), "seconds": round(time.time() - t0, 1)}
    for tag in ("unconstrained", "constrained"):
        summ[f"{tag}_fv_T1_below_273"] = sum(1 for r in rows if r[tag]["fv"] and r[tag]["fv"]["T1"] < 273.15)
        for T0 in T0S:
            for rr in RS:
                k = f"ex_{T0}_{rr}"
                summ[f"{tag}_{k}_T1_ge_T0"] = sum(1 for r in rows if r[tag][k] and r[tag][k]["T1"] >= T0)
    outp.write_text(json.dumps({"summary": summ, "rows": rows}, indent=1, default=float))
    print(json.dumps(summ, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
