"""Tier X: does the transcribed NS reactivity fit (P1..P7 + resonant term) match the Maxwellian integral of the
transcribed NS S-factor (C0..B)? Two independent coefficient sets that would have to be mis-transcribed compatibly.
Writes ../logs/ns_consistency.json.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from scipy import integrate

HERE = Path(__file__).resolve().parent
F = json.loads((HERE.parent / "data" / "fits.json").read_text())
S = {k: float(v) for k, v in F["nevins_swain_pB11_S_factor_lowE"].items() if k not in ("source", "units", "boundaries_keV")}
R = F["nevins_swain_pB11_reactivity_highT"]


def s_factor(E: float) -> float:
    if E <= 400:
        return S["C0"] + S["C1"] * E + S["C2"] * E * E + S["AL"] / ((E - S["EL"]) ** 2 + S["delEL"] ** 2)
    if E < 642:
        x = (E - 400) / 100
        return S["D0"] + S["D1"] * x + S["D2"] * x * x + S["D5"] * x ** 5
    return S["B"] + sum(S[f"A{k}"] / ((E - S[f"E{k}"]) ** 2 + S[f"delE{k}"] ** 2) for k in range(4))


def sv_integral(T: float) -> float:
    EG = 22589.0
    g = lambda E: 1000 * s_factor(E) * math.exp(-math.sqrt(EG / E) - E / T)  # noqa: E731
    val = integrate.quad(g, 1e-3, 3500, points=[148, 400, 581.3, 642, 1083, 2405, 3344], limit=1000, epsrel=1e-10)[0]
    return math.sqrt(8 / math.pi) * 299792458.0 / math.sqrt(float(R["Mrc2_keV"])) * T ** -1.5 * val * 1e-28


def sv_fit(T: float) -> float:
    P = [0.0] + [float(R[f"P{i}"]) for i in range(1, 8)]
    th = T / (1 - T * (P[2] + T * (P[4] + T * P[6])) / (1 + T * (P[3] + T * (P[5] + T * P[7]))))
    xi = (22589.0 / (4 * th)) ** (1 / 3)
    nr = P[1] * th * math.sqrt(xi / (float(R["Mrc2_keV"]) * T ** 3)) * math.exp(-3 * xi)
    return nr + 5.41e-21 * T ** -1.5 * math.exp(-148 / T)


def main() -> None:
    out = {}
    for T in (50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 400.0, 500.0):
        a, b = sv_fit(T), sv_integral(T)
        out[str(T)] = {"fit": a, "integral_of_S_0_3500keV": b, "fit_over_integral": a / b}
    (HERE.parent / "logs" / "ns_consistency.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
