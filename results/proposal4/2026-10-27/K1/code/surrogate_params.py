"""Extract the stylised-surrogate parameters (q_C, q_N, lam, gamma at T0; T1, T_end of the stored path) for the
Table 2 rows and the scanned sample materials (Tier X inputs to the certified surrogate classification)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cv_gp import CvGP  # noqa: E402
from dac_model import AMU, R, kh_extrapolate, q_ads_inf, t_to_beta  # noqa: E402
from load_data import Dataset, arr  # noqa: E402

T0S = (273.15, 298.15, 313.15)
ALPHA = 400e-6


def params_for(ds: Dataset, name: str, i: int, row=None) -> dict:
    opt = ds.optimized(name)
    rp = opt["Refresh_Path"]
    Ts, Ps = arr(rp["Temperatures"][i]), arr(rp["Pressures"][i])
    kc, kn = ds.kh_co2(name), ds.kh_n2(name)
    k1, _ = kh_extrapolate(np.array([t_to_beta(Ts[0])]), kc, {"cell_density": 1.0 / (AMU * 1e30)})
    rho = float(k1[0]) / arr(rp["Henry_CO2"][i])[0]
    mat = {"cell_density": rho / (AMU * 1e30)}
    cvj = ds.cv(name)
    gp = CvGP(cvj["Temperatures"], cvj["Cv"], cvj["CV_err"])
    out = {"name": name, "solution_index": i, "row": row, "T1": float(Ts[0]), "Tend": float(Ts[-1]),
           "P1": float(Ps[0]), "qC": {}, "qN": {}, "lam": {}, "gamma": {}}
    for T0 in T0S:
        b = np.array([t_to_beta(T0)])
        KC, _ = kh_extrapolate(b, kc, mat)
        KN, _ = kh_extrapolate(b, kn, mat)
        n0 = ALPHA * Ps[0] * float(KC[0]) * 1e-3  # mol/kg
        out["qC"][str(T0)] = float(q_ads_inf(b, kc)[0]) * 1e3
        out["qN"][str(T0)] = float(q_ads_inf(b, kn)[0]) * 1e3
        out["lam"][str(T0)] = (1 - ALPHA) * float(KN[0]) / (ALPHA * float(KC[0]))
        out["gamma"][str(T0)] = float(gp(np.array([T0]))[0]) / (R * n0)
    return out


def main() -> int:
    ds = Dataset(Path(sys.argv[1]))
    pc = json.loads(Path(sys.argv[2]).read_text())
    scan = json.loads(Path(sys.argv[3]).read_text())
    outp = Path(sys.argv[4])
    mats = []
    for r in pc["rows"]:
        mats.append(params_for(ds, r["row"][0].replace(" ", "_"), r["solution_index"], "table2"))
    for x in scan.get("sample", []):
        mats.append(params_for(ds, x["name"], x["solution_index"], "sample"))
    qc = [v for m in mats for v in m["qC"].values()]
    qn = [v for m in mats for v in m["qN"].values()]
    ranges = {"qC": [float(np.floor(min(qc) / 1000) * 1000), float(np.ceil(max(qc) / 1000) * 1000)],
              "qN": [float(np.floor(min(qn) / 1000) * 1000), float(np.ceil(max(qn) / 1000) * 1000)]}
    outp.write_text(json.dumps({"ranges": ranges, "materials": mats}, indent=1))
    print("ranges", ranges, "n", len(mats))
    for m in mats[:14]:
        print(m["name"], "T1", round(m["T1"], 1), "qC", round(m["qC"]["298.15"]), "qN", round(m["qN"]["298.15"]),
              "lam", f"{m['lam']['298.15']:.3g}", "gamma", f"{m['gamma']['298.15']:.3g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
