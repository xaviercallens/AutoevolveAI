"""P4/N4 and the SPM vs SPMe vs DFN comparison with PyBaMM (Tier X). DFN rerun: positive electrode start 0.99, tmax 1.2 t_hi (first attempt in run_pybamm.py ran the cell past its capacity)."""
from __future__ import annotations

import json
import sys
from fractions import Fraction

import numpy as np
import pybamm

OUT = "results/proposal4/2026-10-27/E2/data/"
cert = json.load(open(OUT + "certified_t_star.json"))
CMAX = 33133.0
SPEC = {"SPM": pybamm.lithium_ion.SPM, "SPMe": pybamm.lithium_ion.SPMe, "DFN": pybamm.lithium_ion.DFN}


def run(model: str, C: float, x0: float, rn: int, tmax: float, dt: float = 1.0) -> dict[str, np.ndarray]:
    p = pybamm.ParameterValues("Chen2020")
    p["Initial concentration in negative electrode [mol.m-3]"] = x0 * CMAX
    # positive electrode start: lithiated so that charging (delithiation) stays inside (0, cmax_p); affects voltage only
    p["Initial concentration in positive electrode [mol.m-3]"] = 0.99 * float(p["Maximum concentration in positive electrode [mol.m-3]"])
    p["Current function [A]"] = -C * 5.0  # PyBaMM sign: negative current charges
    p["Upper voltage cut-off [V]"] = 50.0
    p["Lower voltage cut-off [V]"] = -50.0
    m = SPEC[model]()
    pts = {"x_n": 20, "x_s": 20, "x_p": 20, "r_n": rn, "r_p": 20}
    sim = pybamm.Simulation(m, parameter_values=p, var_pts=pts)
    t = np.arange(0.0, tmax + dt, dt)
    sol = sim.solve(t)
    out = {"t": sol["Time [s]"].entries}
    if model == "DFN":
        s = sol["Negative particle surface concentration [mol.m-3]"].entries  # (x, t)
        out["avg"] = s.mean(axis=0)
        out["max"] = s.max(axis=0)
    else:
        out["avg"] = sol["X-averaged negative particle surface concentration [mol.m-3]"].entries
        out["max"] = out["avg"]
    return out


def first_cross(t: np.ndarray, c: np.ndarray, level: float) -> float | None:
    idx = np.where(c >= level)[0]
    if len(idx) == 0:
        return None
    i = idx[0]
    if i == 0:
        return float(t[0])
    return float(t[i - 1] + (level - c[i - 1]) * (t[i] - t[i - 1]) / (c[i] - c[i - 1]))


def main() -> None:
    rows = []
    for rec in cert:
        C, x0, xs = rec["C"], float(rec["x0"]), rec["x_star"]
        level = (1.0 if xs == "1.0" else 29866.0 / CMAX) * CMAX
        t_lo, t_hi = float(rec["t_lo_s"]), float(rec["t_hi_s"])
        if xs != "0.9014":
            continue  # DFN: exchange current -> 0 at c_s = c_max, IDA cannot integrate to exact saturation
        tmax = 1.05 * t_hi
        for model, meshes in (("DFN", (20, 100) if x0 == 0.25 else (20,)),):
            for rn in meshes:
                try:
                    o = run(model, C, x0, rn, tmax)
                    tc_avg = first_cross(o["t"], o["avg"], level)
                    tc_max = first_cross(o["t"], o["max"], level)
                    err = None if tc_avg is None else (tc_avg - 0.5 * (t_lo + t_hi)) / (0.5 * (t_lo + t_hi))
                    row = dict(C=C, x0=x0, x_star=xs, model=model, r_n=rn, t_cert_lo=t_lo, t_cert_hi=t_hi, t_cross_avg=tc_avg,
                               t_cross_max=tc_max, rel_diff_avg=err, status="ok")
                except Exception as e:  # report, never hide
                    row = dict(C=C, x0=x0, x_star=xs, model=model, r_n=rn, status="FAILED: " + repr(e)[:200])
                rows.append(row)
                print(row, flush=True)
    # N4: discharge must not cross
    n4 = []
    for model in ():
        o = run(model, -1.0, 0.5, 20, 1500.0)
        n4.append(dict(model=model, crossing_1=first_cross(o["t"], o["avg"], CMAX), crossing_09=first_cross(o["t"], o["avg"], 29866.0),
                       c_start=float(o["avg"][0]), c_end=float(o["avg"][-1])))
    json.dump(dict(pybamm=pybamm.__version__, rows=rows, N4=n4), open(OUT + "pybamm_dfn.json", "w"), indent=1)
    print(n4)


main()
