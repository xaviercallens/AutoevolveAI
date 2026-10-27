"""Build a dac_model.Terms object directly from one stored Pareto path of an optimized-cycle JSON."""

from __future__ import annotations

import numpy as np

from dac_model import Terms
from load_data import arr


def n_paths(opt: dict) -> int:
    rp = opt.get("Refresh_Path")
    return 0 if not rp else len(rp.get("Temperatures") or [])


def terms_from_stored(opt: dict, i: int) -> Terms | None:
    rp, eb = opt["Refresh_Path"], opt["E_Balance"]
    if rp["Temperatures"][i] is None or (rp.get("Flag") and rp["Flag"][i] != "no flags"):
        return None
    s1, s2 = eb["Step_1"], eb["Step_2"]
    ts = arr(rp["Temperatures"][i])
    if ts.size < 2:
        return None
    ps = arr(rp["Pressures"][i])
    nc, nn = arr(rp["Moles_CO2"][i]), arr(rp["Moles_N2"][i])
    dc = np.concatenate([[np.nan], nc[:-1] - nc[1:]])
    dn = np.concatenate([[np.nan], nn[:-1] - nn[1:]])
    dn_c, dn_n = nc[0] - nc[-1], nn[0] - nn[-1]
    E = float(eb["Total_E_of_cycle"][i])
    return Terms(ts, ps, nc, nn, dc, dn, arr(rp["Heat_of_adsorb_CO2"][i]), arr(rp["Heat_of_adsorb_N2"][i]),
                 arr(rp["Specific_heat_sorbent"][i]), float(s1["Heat_to_adsorb_CO2"][i]),
                 float(s1["Heat_to_adsorb_N2"][i]), float(s1["Work_to_adsorb_CO2"][i]),
                 float(s1["Work_to_adsorb_N2"][i]), arr(s2["Heat_to_desorb_CO2"][i]), arr(s2["Heat_to_desorb_N2"][i]),
                 arr(s2["Work_to_desorb_CO2"][i]), arr(s2["Work_to_desorb_N2"][i]),
                 arr(s2["E_to_heat_adsorbed_CO2"][i]), arr(s2["E_to_heat_adsorbed_N2"][i]),
                 arr(s2["E_to_heat_sorbent"][i]), arr(s2["E_to_change_pressure"][i]), float(eb["E1"][i]),
                 float(eb["E2"][i]), float(eb["E3"][i]), E, dn_c, dn_n, dn_c / E, dn_c / (dn_c + dn_n))
