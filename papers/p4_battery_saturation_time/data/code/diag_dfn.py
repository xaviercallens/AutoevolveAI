"""Diagnose why DFN IDA fails in run_pybamm.py (setup variants)."""
import numpy as np
import pybamm

CMAX = 33133.0


def attempt(label: str, x0: float, posx: float | None, tmax: float, C: float = 1.0) -> None:
    p = pybamm.ParameterValues("Chen2020")
    p["Initial concentration in negative electrode [mol.m-3]"] = x0 * CMAX
    if posx is not None:
        p["Initial concentration in positive electrode [mol.m-3]"] = posx * float(
            p["Maximum concentration in positive electrode [mol.m-3]"])
    p["Current function [A]"] = -C * 5.0
    p["Upper voltage cut-off [V]"] = 50.0
    p["Lower voltage cut-off [V]"] = -50.0
    sim = pybamm.Simulation(pybamm.lithium_ion.DFN(), parameter_values=p,
                            var_pts={"x_n": 20, "x_s": 20, "x_p": 20, "r_n": 20, "r_p": 20})
    try:
        sol = sim.solve(np.arange(0.0, tmax + 1, 1.0))
        v = sol["Voltage [V]"].entries
        print(label, "OK", float(v[0]), float(v[-1]), flush=True)
    except Exception as e:
        print(label, "FAILED", repr(e)[:160], flush=True)


for label, x0, posx, tmax in [
    ("default-pos x0=.25 t=500", 0.25, None, 500.0),
    ("pos.95 x0=.25 t=500", 0.25, 0.95, 500.0),
    ("pos.95 x0=.25 t=60", 0.25, 0.95, 60.0),
    ("pos.60 x0=.25 t=500", 0.25, 0.60, 500.0),
    ("pos.60 x0=.25 t=1500", 0.25, 0.60, 1500.0),
    ("pos.60 x0=.05 t=1500", 0.05, 0.60, 1500.0),
]:
    attempt(label, x0, posx, tmax)
