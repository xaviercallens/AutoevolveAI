#!/usr/bin/env python3
"""Attribute the K3-ASTRO-09 "85.1% lower Carter drift" to its cause.

compute_k3_09_carter_geodesics integrates RK4 at dt=0.005 for 300 steps (T=1.5) and "Yoshida" at dt=0.002
for 300 steps (T=0.6). This script varies one thing at a time through the generator's own function.

Controls:
  * the as-written protocol reproduces 85.1% (else we are not testing the claim);
  * dt-refinement: if the drift were a METHOD error it would vanish as dt -> 0; it converges to a nonzero
    limit, so it is a property of the equations (K is not conserved by this right-hand side);
  * drift vs total time must follow a power law (log-log slope reported).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("g13_9", HERE / "phd_k3_pipeline" / "generate_numerical_data_v13_9.py")
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def drifts(dt: float, n: int, dt_y: float, n_y: int) -> tuple[float, float]:
    r = g.compute_k3_09_carter_geodesics(dt=dt, n_steps=n, dt_y=dt_y, n_steps_y=n_y)
    return r["drift_rk4"], r["drift_yoshida"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    written = g.compute_k3_09_carter_geodesics()
    assert written["improvement_pct"] == 85.1, written["improvement_pct"]
    rk, yo = written["drift_rk4"], written["drift_yoshida"]
    print(f"control: as written reproduces {written['improvement_pct']}%  (T_rk4={written['protocol']['T_rk4']}, T_yoshida={written['protocol']['T_yoshida']:.3g})")

    arms = {
        "as_written (unequal dt, unequal T)": drifts(0.005, 300, 0.002, 300),
        "equal T=1.5, unequal dt": drifts(0.005, 300, 0.002, 750),
        "matched dt=0.005, equal T=1.5": drifts(0.005, 300, 0.005, 300),
    }
    for k, (r_, y_) in arms.items():
        print(f"  {k:<38} rk4 {r_:.6f}  yoshida {y_:.6f}  yoshida/rk4 = {y_ / r_:.4f}")

    Ts = [0.15, 0.3, 0.6, 1.5]
    by_T = [drifts(0.005, round(T / 0.005), 0.005, round(T / 0.005))[0] for T in Ts]
    slope = (math.log(by_T[-1]) - math.log(by_T[0])) / (math.log(Ts[-1]) - math.log(Ts[0]))
    print(f"  drift vs T {dict(zip(Ts, [round(x, 5) for x in by_T]))}  log-log slope {slope:.2f}")

    refine = {}
    for dtr in (0.005, 0.0025, 0.001, 0.0005):
        refine[dtr] = drifts(dtr, round(1.5 / dtr), dtr, round(1.5 / dtr))[0]
    print("  dt-refinement at T=1.5 (RK4 drift):", {k: round(v, 6) for k, v in refine.items()})
    limit = refine[0.0005]
    assert limit > 0.1, "drift vanished under refinement: it would be a method error"

    a.out.write_text(json.dumps({
        "claim": "K3-ASTRO-09: Yoshida-4 gives 85.1% lower Carter constant drift than RK4 'at matched timestep'",
        "controls": {"as_written_reproduces_85.1": True, "dt_refinement_rk4_drift_at_T_1.5": refine,
                     "drift_vs_T_log_log_slope": slope},
        "as_written": {"protocol": written["protocol"], "drift_rk4": rk, "drift_yoshida": yo, "ratio": yo / rk},
        "arms": {k: {"drift_rk4": v[0], "drift_yoshida": v[1], "ratio": v[1] / v[0]} for k, v in arms.items()},
        "drift_rk4_vs_total_time_dt_0.005": dict(zip(map(str, Ts), by_T)),
        "conclusion": "The 85.1% is the ratio of two total integration times (0.6 vs 1.5) at drift ~ T^2. At equal total time, "
                      "or at matched dt, the ratio is 1.000. The drift does not shrink under dt refinement, so it is a property "
                      "of the equations (this right-hand side does not conserve K), not of either integrator.",
        "removed": "generate_numerical_data_v13_9.py replaced the Yoshida drift with 0.45 * baseline whenever it was not smaller, "
                   "guaranteeing gate_passed; with matched dt that branch fires and reports a 55% 'improvement' from a literal.",
    }, indent=2) + "\n")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
