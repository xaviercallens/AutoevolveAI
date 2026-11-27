"""Best path restricted to a warm start (T1 >= T0 = 298.15 K) under each accounting, per Table 2 row, on the same
grid family as run_joint.py (T1 in {300, 310, 320}, dT step 10 incl. 0, P_end in {100, 1000, 5000, 20000, 60000},
then the same refinement with T1 kept >= 298.15 K). Quantifies the size of the 'start cold' benefit
xi*(cold, joint) / xi*(warm) under face value and exergy."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cv_gp import CvGP  # noqa: E402
from load_data import Dataset  # noqa: E402
from run_joint import best, evaluate  # noqa: E402
from run_scan import material_inputs  # noqa: E402
from stored import terms_from_stored  # noqa: E402

TW = 298.15


def main() -> int:
    ds = Dataset(Path(sys.argv[1]))
    pc = json.loads(Path(sys.argv[2]).read_text())
    joint = json.loads(Path(sys.argv[3]).read_text())
    outp = Path(sys.argv[4])
    t0 = time.time()
    out = []
    for row, jr in zip(pc["rows"], joint["rows"]):
        name = row["row"][0].replace(" ", "_")
        opt = ds.optimized(name)
        i = row["solution_index"]
        st = terms_from_stored(opt, i)
        mat, sat = material_inputs(ds, name, opt, i)
        cvj = ds.cv(name)
        ctx = {"P1": float(st.ps[0]), "kc": ds.kh_co2(name), "kn": ds.kh_n2(name), "mat": mat, "sat": sat,
               "gp": CvGP(cvj["Temperatures"], cvj["Cv"], cvj["CV_err"]), "cache": {}}
        coarse = []
        for T1 in (300.0, 310.0, 320.0):
            for dT in np.arange(0.0, 400.0 - T1 + 1e-9, 10.0):
                for Pend in (100.0, 1000.0, 5000.0, 20000.0, 60000.0):
                    coarse.append(evaluate(ctx, T1, float(dT), Pend))
        res = {"name": name, "row": row["row"]}
        for k in ("fv", "ex_298.15_0.0", "ex_298.15_0.5", "ex_298.15_1.0"):
            b = best([c for c in coarse if c and c["T1"] >= TW], k, None)
            if b is None:
                res[k] = None
                continue
            ref = [b]
            for T1 in np.arange(max(TW + 0.01, b["T1_req"] - 10.0), b["T1_req"] + 10.0 + 1e-9, 2.0):
                for dT in np.arange(b["dT"] - 10.0, b["dT"] + 10.0 + 1e-9, 5.0):
                    for f in (0.5, 0.7, 1.0, 1.4, 2.0):
                        ref.append(evaluate(ctx, float(T1), float(max(dT, 0.0)), b["Pend"] * f))
            bb = best([c for c in ref if c and c["T1"] >= TW], k, None)
            cold = jr["unconstrained"][k][k]
            res[k] = {"warm": {kk: bb[kk] for kk in ("T1", "Tend", "Pend", "purity", k)}, "cold_joint_xi": cold,
                      "benefit_ratio_cold_over_warm": cold / bb[k]}
        out.append(res)
        print(name, {k: (None if res[k] is None else (round(res[k]["warm"]["T1"], 1), round(res[k]["warm"]["Tend"], 1),
                                                      res[k]["warm"]["Pend"], round(res[k]["warm"]["purity"], 4),
                                                      round(res[k]["benefit_ratio_cold_over_warm"], 2)))
                     for k in ("fv", "ex_298.15_0.0", "ex_298.15_1.0")}, round(time.time() - t0), flush=True)
    outp.write_text(json.dumps({"rows": out}, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
