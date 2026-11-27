"""Auditor DFN mesh refinement (x_n=40) for the max-over-x crossing, and positive-surface at 3C failure."""
import json
import warnings

import numpy as np
import pybamm

CMAX = 33133.0


def params(C, x0, posx=0.99):
    p = pybamm.ParameterValues("Chen2020")
    p["Initial concentration in negative electrode [mol.m-3]"] = x0 * CMAX
    p["Initial concentration in positive electrode [mol.m-3]"] = posx * 63104.0
    p["Current function [A]"] = -C * 5.0
    p["Upper voltage cut-off [V]"] = 50.0
    p["Lower voltage cut-off [V]"] = -50.0
    return p


def cross(t, c, level):
    if not (c >= level).any():
        return None
    i = int(np.argmax(c >= level))
    return float(t[i - 1] + (level - c[i - 1]) * (t[i] - t[i - 1]) / (c[i] - c[i - 1]))


res = []
for C, x0, xn, tmax in [(1, 0.25, 40, 2000.0), (3, 0.25, 20, 900.0), (3, 0.25, 40, 900.0)]:
    sim = pybamm.Simulation(pybamm.lithium_ion.DFN(), parameter_values=params(C, x0),
                            solver=pybamm.IDAKLUSolver(on_failure="ignore"),
                            var_pts={"x_n": xn, "x_s": 20, "x_p": 20, "r_n": 20, "r_p": 20})
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sol = sim.solve(np.arange(0, tmax, 0.5))
    t = sol["Time [s]"].entries
    cs = sol["Negative particle surface concentration [mol.m-3]"].entries
    cp = sol["Positive particle surface concentration [mol.m-3]"].entries
    ce = sol["Electrolyte concentration [mol.m-3]"].entries
    xall = sol["x [m]"].entries[:, 0]
    # time when electrolyte min first < 1 mol/m3, and when local cs first >= 0.9999 cmax
    t_ce1 = cross(t, -ce.min(axis=0), -1.0)
    rec = dict(C=C, x0=x0, x_n=xn, t_end=float(t[-1]), t_max_cross_09014=cross(t, cs.max(axis=0), 29866.0),
               t_avg_cross_09014=cross(t, cs.mean(axis=0), 29866.0), t_ce_below_1=t_ce1,
               t_cs_local_09999=cross(t, cs.max(axis=0), 0.9999 * CMAX),
               cp_min_sto_end=float(cp[:, -1].min() / 63104.0), ce_min_end=float(ce[:, -1].min()),
               ce_min_x_um_end=float(xall[np.argmin(ce[:, -1])] * 1e6))
    res.append(rec)
    print(rec, flush=True)
json.dump(res, open("/tmp/e2audit/pb_audit2.json", "w"), indent=1)
