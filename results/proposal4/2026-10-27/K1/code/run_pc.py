"""K1 positive control.

PC-a  dataset -> paper: every Table 2 row is located in the optimized-cycle JSON of its material by its path
      end-points, and the stored posterior mean/std of xi, x_end, dn_CO2, dn_N2 and the path end-points are rounded
      to the printed digits and compared with the printed strings.
PC-b  independent recompute of the nominal path from the raw GCMC inputs (Kh coefficients, saturation, density)
      with the stored Cv, through code/dac_model.py: Henry constants, q, loadings, every step-1/step-2 term,
      E1, E2, Total_E, nominal xi must match the stored arrays to 1e-9 relative.
PC-c  gap between the nominal xi and the stored posterior mean (the printed value).
PC-d  Python re-fit of the Cv GP against the stored Cv arrays (tolerance logged; used only off the stored paths).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cv_gp import CvGP  # noqa: E402
from dac_model import AMU, kh_extrapolate, nominal_path, t_to_beta  # noqa: E402
from load_data import Dataset, arr  # noqa: E402
from table2 import TABLE2, parse_pm  # noqa: E402


def rel(a: np.ndarray, b: np.ndarray) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = np.isfinite(a) & np.isfinite(b)
    if (np.isfinite(a) != np.isfinite(b)).any():
        return float("inf")
    # normalised max deviation: max|a-b| / max|b| (per-element relative error is meaningless at entries ~0)
    if not m.any():
        return 0.0
    return float(np.abs(a[m] - b[m]).max() / max(np.abs(b[m]).max(), 1e-300))


def density_from_first_point(kh: dict, T: float, kh_stored: float) -> dict:
    """Material dict whose cell_density reproduces the stored CO2 Henry constant at the first path point."""
    b = np.array([t_to_beta(T)])
    k1, _ = kh_extrapolate(b, kh, {"cell_density": 1.0 / (AMU * 1e30)})  # rho = 1 kg/m^3
    rho = float(k1[0]) / kh_stored
    return {"cell_density": rho / (AMU * 1e30), "rho_kg_m3_backsolved": rho}


def printed_match(value: float, std: float | None, s: str, scale: float = 1.0) -> dict:
    v, dec, unc = parse_pm(s)
    ok_v = round(value * scale, dec) == round(v, dec)
    ok_u = True if unc is None or std is None else round(std * scale, dec) == round(unc, dec)
    return {"printed": s, "stored_value": value * scale, "stored_std": None if std is None else std * scale,
            "value_ok": bool(ok_v), "unc_ok": bool(ok_u)}


def main() -> int:
    ds = Dataset(Path(sys.argv[1]))
    out_path = Path(sys.argv[2])
    rows = []
    gp_dev = []
    for row in TABLE2:
        name = row[0].replace(" ", "_")
        opt = ds.optimized(name)
        rp, eb = opt["Refresh_Path"], opt["E_Balance"]
        T1p, Tep, P1p, Pep = (parse_pm(row[k])[0] for k in (5, 6, 7, 8))
        best, bi = None, None
        for i, Ts in enumerate(rp["Temperatures"]):
            if Ts is None:
                continue
            Ts = arr(Ts); Ps = arr(rp["Pressures"][i])
            d = abs(Ts[0] - T1p) / 0.05 + abs(Ts[-1] - Tep) / 0.05 + abs(Ps[0] - P1p) / 0.5 + abs(Ps[-1] - Pep) / 0.5
            if best is None or d < best:
                best, bi = d, i
        i = bi
        Ts = arr(rp["Temperatures"][i]); Ps = arr(rp["Pressures"][i])
        cmp = {
            "xi": printed_match(opt["Intrinsic_capture_efficiency"][i], opt["Intrinsic_capture_efficiency_std"][i],
                                row[1], 1e6),
            "x_end": printed_match(opt["Purity_captured_CO2"][i], opt["Purity_captured_CO2_std"][i], row[2]),
            "dn_CO2": printed_match(opt["Captured_CO2"][i], opt["Captured_CO2_std"][i], row[3]),
            "dn_N2": printed_match(opt["Captured_N2"][i], opt["Captured_N2_std"][i], row[4]),
            "T1": printed_match(Ts[0], None, row[5]), "T_end": printed_match(Ts[-1], None, row[6]),
            "P1": printed_match(Ps[0], None, row[7]), "P_end": printed_match(Ps[-1], None, row[8]),
        }
        # PC-b: recompute nominal path from raw inputs with the stored Cv
        cv_stored = arr(rp["Specific_heat_sorbent"][i])
        cv_map = {float(t): c for t, c in zip(Ts, cv_stored)}
        # The CSD material files (cell_density, cell_mass) are NOT in the public Zenodo record. The density is
        # back-solved from ONE stored number (Henry_CO2 at the first path point); every other array is then an
        # independent check (N2 Henry constants use the same density, so they test it). The saturation truncation
        # is already applied to the stored grid, so it is disabled here (sat = inf); point counts are compared.
        material = density_from_first_point(ds.kh_co2(name), Ts[0], arr(rp["Henry_CO2"][i])[0])
        t = nominal_path(Ts.copy(), Ps.copy(), 400e-6, ds.kh_co2(name), ds.kh_n2(name), material,
                         float("inf"), lambda tt: np.array([cv_map[float(x)] for x in tt]))
        s1, s2 = eb["Step_1"], eb["Step_2"]
        pcb = {"rho_kg_m3_backsolved": material["rho_kg_m3_backsolved"],
            "n_points_stored": int(Ts.size), "n_points_recomputed": int(t.ts.size),
            "Moles_CO2": rel(t.n_co2, arr(rp["Moles_CO2"][i])),
            "Moles_N2": rel(t.n_n2, arr(rp["Moles_N2"][i])),
            "q_CO2": rel(t.q_co2, arr(rp["Heat_of_adsorb_CO2"][i])),
            "q_N2": rel(t.q_n2, arr(rp["Heat_of_adsorb_N2"][i])),
            "Heat_to_adsorb_CO2": rel([t.Q_ads_co2], [s1["Heat_to_adsorb_CO2"][i]]),
            "Work_to_adsorb_N2": rel([t.W_ads_n2], [s1["Work_to_adsorb_N2"][i]]),
            "Heat_to_desorb_CO2": rel(t.Q_des_co2, arr(s2["Heat_to_desorb_CO2"][i])),
            "Heat_to_desorb_N2": rel(t.Q_des_n2, arr(s2["Heat_to_desorb_N2"][i])),
            "Work_to_desorb_CO2": rel(t.W_des_co2, arr(s2["Work_to_desorb_CO2"][i])),
            "E_to_heat_adsorbed_CO2": rel(t.E_heat_co2, arr(s2["E_to_heat_adsorbed_CO2"][i])),
            "E_to_heat_sorbent": rel(t.E_heat_sorb, arr(s2["E_to_heat_sorbent"][i])),
            "E_to_change_pressure": rel(t.E_P, arr(s2["E_to_change_pressure"][i])),
            "E1": rel([t.E1], [eb["E1"][i]]), "E2": rel([t.E2], [eb["E2"][i]]),
            "Total_E": rel([t.E], [eb["Total_E_of_cycle"][i]]),
        }
        pcb["max_rel"] = max(v for k, v in pcb.items() if not k.startswith(("n_points", "rho")))
        xi_nom = t.xi * 1e6
        # PC-d: GP re-fit
        cvj = ds.cv(name)
        gp = CvGP(cvj["Temperatures"], cvj["Cv"], cvj["CV_err"])
        dev = rel(gp(Ts), cv_stored)
        gp_dev.append(dev)
        rows.append({"row": list(row), "dataset_file": f"Optimized_Intrinsic_Cycle/OptIDC_{name}.json",
                     "solution_index": i, "match_score": best, "PC_a": cmp, "PC_b": pcb,
                     "PC_c": {"xi_nominal_umol_per_J": xi_nom,
                              "xi_posterior_mean_umol_per_J": opt["Intrinsic_capture_efficiency"][i] * 1e6,
                              "xi_nominal_from_stored_E": opt["Captured_CO2"][i] / eb["Total_E_of_cycle"][i] * 1e6,
                              "note": "Captured_CO2 is the posterior mean; the E_Balance is nominal"},
                     "PC_d_gp_max_rel_dev": dev,
                     "units_string_xi": opt["Intrinsic_capture_efficiency_units"]})
    n_a = sum(all(v["value_ok"] and v["unc_ok"] for v in r["PC_a"].values()) for r in rows)
    summary = {"rows": len(rows), "PC_a_rows_all_fields_match": n_a,
               "PC_a_field_failures": [(r["row"][0], k, v) for r in rows for k, v in r["PC_a"].items()
                                       if not (v["value_ok"] and v["unc_ok"])],
               "PC_b_max_rel_over_rows": max(r["PC_b"]["max_rel"] for r in rows),
               "PC_d_gp_max_rel_dev_over_rows": max(gp_dev)}
    out_path.write_text(json.dumps({"summary": summary, "rows": rows}, indent=1, default=float))
    print(json.dumps(summary, indent=1, default=float))
    for r in rows:
        print(r["row"][0], "xi printed", r["row"][1], "stored", round(r["PC_a"]["xi"]["stored_value"], 4),
              "+-", round(r["PC_a"]["xi"]["stored_std"], 4), "nominal", round(r["PC_c"]["xi_nominal_umol_per_J"], 4),
              "PCb", f"{r['PC_b']['max_rel']:.2e}", "npts", r["PC_b"]["n_points_stored"], r["PC_b"]["n_points_recomputed"],
              "gp", f"{r['PC_d_gp_max_rel_dev']:.2e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
