"""K1-H1 scan (protocol in logs/h1_operational_test_written_before_run.md, written before this ran).

For each row: hold (T_end, P1, P_end) at the stored path values, scan T1 on a 1 K grid from 200 K to T_end - 1 K
with the code's own linear-path discretisation, evaluate the faithful re-implementation (dac_model.nominal_path,
including both truncations), and pick argmax xi under (a) face value (published convention), (b) exergy no-credit
r = 0, (c) r = 0.5, (d) signed reversible r = 1, at T0 in {273.15, 298.15, 313.15}, with and without the
constraint purity >= the row's stored nominal purity.

Inputs not in the public record and how they are replaced (Deviations): the CSD material files (cell_density,
cell_mass). Density is back-solved from the stored CO2 Henry constant at the first stored path point; the
saturation-truncation cell mass is rho * V_box (box of the saturation GCMC file, tilts ~ 0). Cv off the stored
path comes from the Python GP re-fit (validated to <= 4e-6 relative on the Table 2 paths).
"""

from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cv_gp import CvGP  # noqa: E402
from dac_model import AMU, kh_extrapolate, linear_path, nominal_path, t_to_beta  # noqa: E402
from exergy import build_ledger, exergy_cost, face_value_cost  # noqa: E402
from load_data import Dataset, arr  # noqa: E402
from stored import n_paths, terms_from_stored  # noqa: E402

T0S = (273.15, 298.15, 313.15)
RS = (0.0, 0.5, 1.0)


def material_inputs(ds: Dataset, name: str, opt: dict, i: int) -> tuple[dict, float]:
    rp = opt["Refresh_Path"]
    T0p = arr(rp["Temperatures"][i])[0]
    kh = ds.kh_co2(name)
    k1, _ = kh_extrapolate(np.array([t_to_beta(T0p)]), kh, {"cell_density": 1.0 / (AMU * 1e30)})
    rho = float(k1[0]) / arr(rp["Henry_CO2"][i])[0]
    sat = json.loads((ds.root / f"Saturation/CO2_sat_200K_{name}.json").read_text())
    box = [float(x) for x in str(sat["box"]).strip("[]").split(",")]
    vol = box[0] * box[1] * box[2]  # A^3 (tilts ~ 0 in the files inspected)
    mass_amu = rho * vol * 1e-30 / AMU
    loading = float(sat["isotherm"][str(sat["step_number"])]["loading"])
    return {"cell_density": rho / (AMU * 1e30)}, loading * 1e6 / mass_amu


def scan_row(ds: Dataset, name: str, opt: dict, i: int, purity_min: float, t1_stored: float) -> dict:
    rp = opt["Refresh_Path"]
    Ts, Ps = arr(rp["Temperatures"][i]), arr(rp["Pressures"][i])
    Tend, P1, Pend = float(Ts[-1]), float(Ps[0]), float(Ps[-1])
    material, sat = material_inputs(ds, name, opt, i)
    cvj = ds.cv(name)
    gp = CvGP(cvj["Temperatures"], cvj["Cv"], cvj["CV_err"])
    kc, kn = ds.kh_co2(name), ds.kh_n2(name)
    # self-check: the stored path itself, re-evaluated from raw inputs with the GP Cv and back-solved density
    st = terms_from_stored(opt, i)
    try:
        tchk = nominal_path(Ts.copy(), Ps.copy(), 400e-6, kc, kn, material, sat, gp)
        self_check = {"xi_stored_nominal": st.xi * 1e6, "xi_recomputed": tchk.xi * 1e6,
                      "rel": abs(tchk.xi - st.xi) / st.xi, "npts": [int(Ts.size), int(tchk.ts.size)]}
    except (ValueError, AttributeError) as e:
        self_check = {"error": repr(e)[:200]}
    grid = []
    T1 = 200.0
    while T1 <= Tend - 1.0 + 1e-9:
        ts, ps = linear_path(T1, Tend - T1, P1, Pend - P1)
        try:
            t = nominal_path(ts, ps, 400e-6, kc, kn, material, sat, gp)
        except ValueError:
            t = None
        rec = {"T1_req": T1}
        if t is not None and t.ts.size >= 2 and t.dn_co2 > 0:
            L = build_ledger(t)
            rec.update(T1_eff=float(t.ts[0]), purity=float(t.purity), xi_fv=float(t.dn_co2 / face_value_cost(L) * 1e6))
            for T0 in T0S:
                for r in RS:
                    B = exergy_cost(L, T0, r)
                    rec[f"xi_ex_{T0}_{r}"] = float(t.dn_co2 / B * 1e6) if B > 0 else None
        grid.append(rec)
        T1 += 1.0
    valid = [g for g in grid if "xi_fv" in g]

    def best(key: str, constrained: bool) -> dict | None:
        c = [g for g in valid if g.get(key) is not None and (not constrained or g["purity"] >= purity_min)]
        if not c:
            return None
        g = max(c, key=lambda gg: gg[key])
        return {"T1": g["T1_eff"], "xi": g[key], "purity": g["purity"]}

    out = {"name": name, "solution_index": i, "Tend": Tend, "P1": P1, "Pend": Pend, "T1_stored": t1_stored,
           "purity_min": purity_min, "n_grid": len(grid), "n_valid": len(valid), "self_check": self_check}
    for cons in (True, False):
        tag = "constrained" if cons else "unconstrained"
        out[tag] = {"fv": best("xi_fv", cons)}
        for T0 in T0S:
            for r in RS:
                out[tag][f"ex_{T0}_{r}"] = best(f"xi_ex_{T0}_{r}", cons)
    out["grid_coarse"] = valid[::10]
    return out


def main() -> int:
    ds = Dataset(Path(sys.argv[1]))
    pc = json.loads(Path(sys.argv[2]).read_text())
    outp = Path(sys.argv[3])
    n_sample = int(sys.argv[4])
    t0 = time.time()
    res = {"table2": [], "sample": []}
    for r in pc["rows"]:
        name = r["row"][0].replace(" ", "_")
        opt = ds.optimized(name)
        t = terms_from_stored(opt, r["solution_index"])
        res["table2"].append(scan_row(ds, name, opt, r["solution_index"], t.purity, float(t.ts[0])))
        x = res["table2"][-1]
        print("T2", name, "T1 stored", round(x["T1_stored"], 1), "fv*", x["constrained"]["fv"],
              "ex298 r0*", x["constrained"]["ex_298.15_0.0"], "chk", x["self_check"], round(time.time() - t0), flush=True)
    names = ds.optimized_names()
    rng = random.Random(20261027)
    rng.shuffle(names)
    for name in names:
        if len(res["sample"]) >= n_sample:
            break
        try:
            opt = ds.optimized(name)
            best_i, best_xi = None, -1.0
            for i in range(n_paths(opt)):
                t = terms_from_stored(opt, i)
                if t is not None and np.isfinite(t.xi) and t.xi > best_xi:
                    best_i, best_xi = i, t.xi
            if best_i is None:
                continue
            t = terms_from_stored(opt, best_i)
            res["sample"].append(scan_row(ds, name, opt, best_i, t.purity, float(t.ts[0])))
        except (KeyError, FileNotFoundError, TypeError, ValueError, IndexError) as e:
            res.setdefault("sample_skipped", []).append([name, repr(e)[:200]])
            continue
        if len(res["sample"]) % 10 == 0:
            print("sample", len(res["sample"]), round(time.time() - t0), flush=True)
            outp.write_text(json.dumps(res, default=float))
    res["seed"] = 20261027
    res["seconds"] = round(time.time() - t0, 1)
    outp.write_text(json.dumps(res, default=float))
    print("done", res["seconds"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
