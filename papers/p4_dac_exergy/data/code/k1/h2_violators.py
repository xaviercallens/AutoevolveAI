"""Diagnose the H2 violators found by h2_all.py (B_rev per mol CO2 below W_min): list them with path end-points,
purity, heat-of-adsorption range along the path, sign of the step-2 heat, and loading vs CO2 saturation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exergy import build_ledger, exergy_cost, w_min_per_mol  # noqa: E402
from load_data import Dataset  # noqa: E402
from stored import n_paths, terms_from_stored  # noqa: E402


def main() -> int:
    ds = Dataset(Path(sys.argv[1]))
    h2 = json.loads(Path(sys.argv[2]).read_text())
    outp = Path(sys.argv[3])
    rows = []
    for m in h2["per_material"]:
        name = m["name"]
        opt = ds.optimized(name)
        for i in range(n_paths(opt)):
            t = terms_from_stored(opt, i)
            if t is None or not np.isfinite(t.xi) or t.dn_co2 <= 0:
                continue
            L = build_ledger(t)
            for T0 in (273.15, 298.15, 313.15):
                brev = exergy_cost(L, T0, 1.0) / t.dn_co2
                wl = w_min_per_mol(T0, 400e-6, t.purity, min(L.Pend, L.P1) / 101325.0)
                wp = w_min_per_mol(T0, 400e-6, t.purity, 1.0)
                if brev < wp:
                    rows.append({"name": name, "i": i, "T0": T0, "T1": float(t.ts[0]), "Tend": float(t.ts[-1]),
                                 "Pend": float(t.ps[-1]), "purity": float(t.purity), "dn_CO2": float(t.dn_co2),
                                 "B_rev_kJ_per_mol": brev / 1e3, "W_min_P0_kJ": wp / 1e3, "W_min_lowP_kJ": wl / 1e3,
                                 "violates_lowP": bool(brev < wl), "q_CO2_kJ_min_max": [float(np.nanmin(t.q_co2)) / 1e3,
                                                                                       float(np.nanmax(t.q_co2)) / 1e3],
                                 "xi_fv": float(t.xi * 1e6)})
    outp.write_text(json.dumps(rows, indent=1))
    names = sorted({r["name"] for r in rows})
    print(len(rows), "violating (path, T0) pairs vs W_min(P0);", len(names), "materials")
    for r in rows:
        if r["T0"] == 298.15:
            print(r["name"], r["i"], "T1", round(r["T1"], 1), "Tend", round(r["Tend"], 1), "Pend", round(r["Pend"]),
                  "y", round(r["purity"], 4), "Brev", round(r["B_rev_kJ_per_mol"], 2), "Wmin P0/lowP",
                  round(r["W_min_P0_kJ"], 2), round(r["W_min_lowP_kJ"], 2), "lowP-viol", r["violates_lowP"], "q",
                  [round(x, 1) for x in r["q_CO2_kJ_min_max"]], "xi_fv", round(r["xi_fv"], 3))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
