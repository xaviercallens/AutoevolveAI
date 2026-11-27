"""Revision 2026-10-27: refine T1 near ambient (T0 = 298.15 K) for the feed-air scenario at r = 1, eps = 0, where the
coarse grid put the optimum in the 298.0 K cell for 11 of 14 rows. New paths: T1 in {294.00, 294.25, ..., 298.00,
298.15} K, dT within +-10 K (step 5) of the best near-ambient path, P_end x {0.7, 1, 1.4}; then the best start in
T1 < T0 and in T1 >= T0 (all paths, coarse + refined) and their ratio.

Usage: python -I rev_refine_ambient.py <DAC_data dir> <positive_control.json> <scan_raw.json> <out.json>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cv_gp import CvGP  # noqa: E402
from load_data import Dataset  # noqa: E402
from rev_scan import cost, evaluate, valid  # noqa: E402
from run_scan import material_inputs  # noqa: E402
from stored import terms_from_stored  # noqa: E402

T0 = 298.15


def main() -> int:
    ds = Dataset(Path(sys.argv[1]))
    pc = json.loads(Path(sys.argv[2]).read_text())
    raw = json.loads(Path(sys.argv[3]).read_text())
    outp = Path(sys.argv[4])
    out = []
    for row, rr in zip(pc["rows"], raw["rows"]):
        name = row["row"][0].replace(" ", "_")
        opt = ds.optimized(name)
        i = row["solution_index"]
        st = terms_from_stored(opt, i)
        mat, sat = material_inputs(ds, name, opt, i)
        cvj = ds.cv(name)
        P1 = float(st.ps[0])
        ctx = {"P1": P1, "kc": ds.kh_co2(name), "kn": ds.kh_n2(name), "mat": mat, "sat": sat,
               "gp": CvGP(cvj["Temperatures"], cvj["Cv"], cvj["CV_err"]), "cache": {}, "xcheck": 0.0}
        pool = [x for x in rr["recs"] if valid(x, P1)]
        near = [x for x in pool if 290.0 <= x["T1"] <= T0 + 1e-9 and cost(x, T0, 1.0, 0.0) > 0]
        c0 = max(near, key=lambda x: x["dnc"] / cost(x, T0, 1.0, 0.0))
        T1s = [float(v) for v in np.arange(294.0, 298.0 + 1e-9, 0.25)] + [T0]
        for T1 in T1s:
            for dT in np.arange(c0["dT"] - 10.0, c0["dT"] + 10.0 + 1e-9, 5.0):
                for f in (0.7, 1.0, 1.4):
                    evaluate(ctx, T1, float(max(dT, 0.0)), float(c0["Pend_req"] * f))
        new = [x for x in ctx["cache"].values() if valid(x, P1)]
        allp = pool + new

        def bestxi(sel: list) -> tuple[float, float]:
            b = max((x for x in sel if cost(x, T0, 1.0, 0.0) > 0), key=lambda x: x["dnc"] / cost(x, T0, 1.0, 0.0))
            return b["dnc"] / cost(b, T0, 1.0, 0.0) * 1e6, b["T1"]
        xc, tc = bestxi([x for x in allp if x["T1"] < T0])
        xw, tw = bestxi([x for x in allp if x["T1"] >= T0])
        xa, ta = bestxi(allp)
        out.append({"row": f"{name} {row['row'][1]}", "n_new": len(new), "T1star": ta, "xi_star": xa,
                    "best_cold_T1": tc, "best_warm_T1": tw, "ratio_v1": xc / xw})
        print(out[-1], flush=True)
    outp.write_text(json.dumps({"T0": T0, "r": 1.0, "eps": 0.0, "rows": out}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
