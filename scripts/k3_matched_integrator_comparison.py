#!/usr/bin/env python3
"""Matched RK4 vs Yoshida-4 vs Verlet on the K3-ASTRO-01 harmonic attractor.

generate_numerical_data_v13_9.py reports "Yoshida reduces drift by 16.4% vs RK4" for this system. Its two
arms measure the drift of DIFFERENT functions: RK4 is scored on H = -exp(-|z|^2)|z|^2*I4 while integrating
dz/dt = -2i*omega*z, Yoshida on H = 0.5|p|^2 + 0.5 omega^2 |z|^2. This script puts every method on one system,
one conserved Hamiltonian, one dt, and reports force evaluations alongside.

Controls (run first, reported):
  * order: each method's observed convergence order against the exact solution (RK4 4, Yoshida 4, Verlet 2);
  * negative: the ORIGINAL mismatched protocol, re-run verbatim, must reproduce the 16.4% -- otherwise this
    script is not testing the claim it says it is.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

W1 = 1.0 / (2.0 - 2.0 ** (1.0 / 3.0))
W0 = -(2.0 ** (1.0 / 3.0)) * W1
YC = (W1 / 2, (W0 + W1) / 2, (W0 + W1) / 2, W1 / 2)
YD = (W1, W0, W1)


def force(q: float, omega: float) -> float:
    return -omega * omega * q


def verlet(q: float, p: float, h: float, omega: float) -> tuple[float, float]:
    p += 0.5 * h * force(q, omega); q += h * p; p += 0.5 * h * force(q, omega)
    return q, p


def yoshida(q: float, p: float, h: float, omega: float) -> tuple[float, float]:
    for i in range(3):
        q += YC[i] * h * p
        p += YD[i] * h * force(q, omega)
    q += YC[3] * h * p
    return q, p


def rk4(q: float, p: float, h: float, omega: float) -> tuple[float, float]:
    f = lambda qq, pp: (pp, force(qq, omega))
    k1 = f(q, p); k2 = f(q + h / 2 * k1[0], p + h / 2 * k1[1])
    k3 = f(q + h / 2 * k2[0], p + h / 2 * k2[1]); k4 = f(q + h * k3[0], p + h * k3[1])
    return q + h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]), p + h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])


METHODS = {"verlet": (verlet, 1), "yoshida4": (yoshida, 3), "rk4": (rk4, 4)}   # (step, force evals per step)


def ham(q: float, p: float, omega: float) -> float:
    return 0.5 * p * p + 0.5 * omega * omega * q * q


def run(name: str, h: float, steps: int, omega: float, q0: float = 1.0, p0: float = 0.0) -> dict[str, float]:
    step, cost = METHODS[name]
    q, p = q0, p0
    h0 = ham(q, p, omega)
    max_drift = 0.0
    for _ in range(steps):
        q, p = step(q, p, h, omega)
        max_drift = max(max_drift, abs(ham(q, p, omega) - h0) / h0)
    T = steps * h
    qe = q0 * math.cos(omega * T) + p0 / omega * math.sin(omega * T)
    pe = -q0 * omega * math.sin(omega * T) + p0 * math.cos(omega * T)
    return {"max_rel_drift": max_drift, "final_drift": abs(ham(q, p, omega) - h0) / h0,
            "final_state_error": math.hypot(q - qe, (p - pe) / omega), "force_evals": cost * steps}


def order(name: str, omega: float) -> list[float]:
    hs = [0.1, 0.05, 0.025, 0.0125]
    es = [run(name, h, round(2.0 / h), omega, 1.0, 0.3)["final_state_error"] for h in hs]
    return [math.log2(es[i] / es[i + 1]) for i in range(len(es) - 1)]


def original_mismatched_protocol() -> dict[str, float]:
    """generate_numerical_data_v13_9.py::compute_k3_01, re-run as written (two different H's)."""
    I4 = 92.0; omega = math.sqrt(I4) / (2 * math.pi); dt = 0.005; n = 2000
    z = complex(1.0, 0.5)
    H0 = -math.exp(-abs(z) ** 2) * abs(z) ** 2 * I4
    hv = [H0]
    for _ in range(n):
        f = lambda zz: -2j * omega * zz
        k1 = f(z); k2 = f(z + dt / 2 * k1); k3 = f(z + dt / 2 * k2); k4 = f(z + dt * k3)
        z = z + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        hv.append(-math.exp(-abs(z) ** 2) * abs(z) ** 2 * I4)
    drift_rk4 = max(abs(h - H0) / abs(H0) for h in hv)
    w1 = 1.0 / (2.0 - 2.0 ** (1 / 3)); w0 = 1.0 - 2.0 * w1
    c = [w1 / 2, (w1 + w0) / 2, (w1 + w0) / 2, w1 / 2]; d = [w1, w0, w1, 0.0]
    z = complex(1.0, 0.5); p = complex(0.0, omega)
    H0y = 0.5 * abs(p) ** 2 + 0.5 * omega ** 2 * abs(z) ** 2
    hy = [H0y]
    for _ in range(n):
        for i in range(4):
            p = p - c[i] * dt * omega ** 2 * z
            z = z + d[i] * dt * p
        hy.append(0.5 * abs(p) ** 2 + 0.5 * omega ** 2 * abs(z) ** 2)
    drift_y = max(abs(h - H0y) / abs(H0y) for h in hy)
    return {"rk4_drift_of_H_A": drift_rk4, "yoshida_drift_of_H_B": drift_y,
            "claimed_improvement_pct": round((drift_rk4 - drift_y) / drift_rk4 * 100, 2)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    omega = math.sqrt(92.0) / (2 * math.pi)

    orders = {m: order(m, omega) for m in METHODS}
    assert all(abs(o - 4) < 0.15 for o in orders["rk4"] + orders["yoshida4"]) and all(abs(o - 2) < 0.15 for o in orders["verlet"]), orders
    orig = original_mismatched_protocol()
    assert abs(orig["claimed_improvement_pct"] - 16.38) < 0.05, f"cannot reproduce the original 16.38%: {orig}"
    print("controls: observed orders", {m: [round(x, 2) for x in o] for m, o in orders.items()})
    print(f"          original mismatched protocol reproduces the claim: {orig['claimed_improvement_pct']}% "
          f"(RK4 drift of H_A {orig['rk4_drift_of_H_A']:.3e} vs Yoshida drift of H_B {orig['yoshida_drift_of_H_B']:.3e})")

    rows = []
    for T in (10.0, 100.0, 1000.0):
        for h in (0.05, 0.02, 0.005):
            steps = round(T / h)
            r = {m: run(m, h, steps, omega) for m in METHODS}
            rows.append({"T": T, "dt": h, "steps": steps, **{m: r[m] for m in r}})
            print(f"T={T:>6} dt={h:<6} max drift  rk4 {r['rk4']['max_rel_drift']:.2e}  yoshida4 {r['yoshida4']['max_rel_drift']:.2e}  "
                  f"verlet {r['verlet']['max_rel_drift']:.2e}   yoshida/rk4 = {r['yoshida4']['max_rel_drift'] / r['rk4']['max_rel_drift']:.2f}")

    # secular growth: does drift keep growing with time?
    h = 0.02
    growth = {m: [run(m, h, round(T / h), omega)["max_rel_drift"] for T in (10.0, 100.0, 1000.0)] for m in METHODS}
    a.out.write_text(json.dumps({
        "system": "harmonic attractor, omega = sqrt(92)/(2 pi), q0=1, p0=0, conserved H = p^2/2 + omega^2 q^2/2",
        "controls": {"observed_orders": orders, "original_protocol_reproduced": orig},
        "matched_dt_grid": rows, "drift_growth_with_time_dt_0.02": growth,
        "caveat": "Harmonic oscillator only: linear force, so Yoshida's drift is a bounded modified-Hamiltonian oscillation and RK4's is dissipative. "
                  "Says nothing about the stated K3 Hamiltonian, which is not the system integrated.",
    }, indent=2) + "\n")
    print("drift vs T at dt=0.02 (T=10,100,1000):", {m: [f"{x:.2e}" for x in v] for m, v in growth.items()})
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
