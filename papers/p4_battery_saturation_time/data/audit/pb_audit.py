"""Auditor PyBaMM checks: SPM crossing vs auditor enclosure; DFN location of max, electrolyte, failure diagnosis."""
import json
import sys
import warnings

import numpy as np
import pybamm

CMAX = 33133.0
mine = {(c["C"], c["x0"], c["xs"]): float(c["my_t"][0].strip("[]").split(",")[0]) for c in
        json.load(open("/tmp/e2audit/my_cert.json"))["cases"]}


def params(C, x0, posx=0.99):
    p = pybamm.ParameterValues("Chen2020")
    p["Initial concentration in negative electrode [mol.m-3]"] = x0 * CMAX
    p["Initial concentration in positive electrode [mol.m-3]"] = posx * 63104.0
    p["Current function [A]"] = -C * 5.0
    p["Upper voltage cut-off [V]"] = 50.0
    p["Lower voltage cut-off [V]"] = -50.0
    return p


def cross(t, c, level):
    i = int(np.argmax(c >= level))
    if not (c >= level).any():
        return None
    return float(t[i - 1] + (level - c[i - 1]) * (t[i] - t[i - 1]) / (c[i] - c[i - 1]))


out = {"spm": [], "dfn": []}
# SPM with an independent mesh choice (r_n=200) and a different time grid (dt=0.25 s)
for (C, x0, xs) in [(1, "0.05", "1.0"), (4, "0.50", "0.9014"), (2, "0.25", "1.0"), (3, "0.05", "0.9014")]:
    lvl = CMAX if xs == "1.0" else 29866.0
    tc = mine[(C, x0, xs)]
    sim = pybamm.Simulation(pybamm.lithium_ion.SPM(), parameter_values=params(C, float(x0)),
                            var_pts={"x_n": 10, "x_s": 10, "x_p": 10, "r_n": 200, "r_p": 20})
    sol = sim.solve(np.arange(0, 1.1 * tc, 0.25))
    s = sol["X-averaged negative particle surface concentration [mol.m-3]"].entries
    t = sol["Time [s]"].entries
    tx = cross(t, s, lvl)
    out["spm"].append(dict(C=C, x0=x0, xs=xs, t_cert=tc, t_pybamm=tx, rel=(tx - tc) / tc))
    print("SPM", out["spm"][-1], flush=True)

# DFN: where is the max, what does electrolyte do, why does it fail at 3C
for C, x0, posx, tmax in [(1, 0.25, 0.99, 2800.0), (1, 0.25, 0.60, 2800.0), (3, 0.25, 0.99, 900.0), (4, 0.05, 0.99, 900.0)]:
    solver = pybamm.IDAKLUSolver(on_failure="ignore")
    sim = pybamm.Simulation(pybamm.lithium_ion.DFN(), parameter_values=params(C, x0, posx), solver=solver,
                            var_pts={"x_n": 20, "x_s": 20, "x_p": 20, "r_n": 20, "r_p": 20})
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sol = sim.solve(np.arange(0, tmax, 1.0))
    t = sol["Time [s]"].entries
    cs = sol["Negative particle surface concentration [mol.m-3]"].entries
    xn = sol["x_n [m]"].entries[:, 0]
    ce = sol["Electrolyte concentration [mol.m-3]"].entries
    xall = sol["x [m]"].entries[:, 0]
    iv = sol["Negative electrode interfacial current density [A.m-2]"].entries
    k = -1
    rec = dict(C=C, x0=x0, posx=posx, t_end=float(t[-1]), t_req=tmax, n_t=len(t),
               argmax_x_end_um=float(xn[np.argmax(cs[:, k])] * 1e6), Ln_um=85.2,
               cs_max_sto_end=float(cs[:, k].max() / CMAX), cs_min_sto_end=float(cs[:, k].min() / CMAX),
               cs_avg_sto_end=float(cs[:, k].mean() / CMAX),
               ce_min_end=float(ce[:, k].min()), ce_min_at_x_um=float(xall[np.argmin(ce[:, k])] * 1e6),
               j_ratio_sep_over_cc_end=float(iv[-1, k] / iv[0, k]),
               j_ratio_sep_over_cc_t10=float(iv[-1, min(10, len(t) - 1)] / iv[0, min(10, len(t) - 1)]),
               t_max_cross_09014=cross(t, cs.max(axis=0), 29866.0),
               t_avg_cross_09014=cross(t, cs.mean(axis=0), 29866.0),
               t_max_cross_0999=cross(t, cs.max(axis=0), 0.999 * CMAX),
               voltage_end=float(sol["Voltage [V]"].entries[-1]))
    out["dfn"].append(rec)
    print("DFN", rec, flush=True)
json.dump(out, open("/tmp/e2audit/pb_audit.json", "w"), indent=1)
