"""Paper-stage numerical checks for the B1 paper (Tier X unless stated). Reads only data/ copies of the B1 records.

Outputs data/extra_checks.json:
  1. which a-values have the harmonic Lindemann ratio at the first-order point inside the band [0.23, 0.28] and [0.23, 0.30]
     and the exact ratio Lam_1 / Lam_L(gamma_c) = (gamma(Lam_1)/gamma_c)^2;
  2. slopes of the tie coupling along the two mirror geodesics in the disk coordinate w = (tau - rho)/(tau - conj(rho))
     (the symmetry argument of Section 3 predicts equal and opposite initial slopes in |w|);
  3. 2D Fourier transform of the soft shoulder 1/(1+(r/Rc)^6), with a Gaussian positive control against the closed form;
  4. the Rydberg-dressing parameter hbar/sqrt(m U0 Rc^2) from the Zeiher et al. numbers (inputs read from the PDF text).
Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I checks.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy import constants as const
from scipy.special import j0

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
RHO = complex(0.5, math.sqrt(3.0) / 2.0)


def band_readings(table: list[dict]) -> dict:
    rows = []
    for r in table:
        if r["hbar_star"] is None or r["Lam_1_edge"] is None:
            continue
        g1 = r["gamma_at_Lam_1_edge"]
        gs = r["gamma_at_hbar_star"]
        rows.append({
            "a": r["a"], "gamma_hbar_star": gs, "gamma_Lam1": g1,
            "in_band_023_028": 0.23 <= g1 <= 0.28, "in_band_023_030": 0.23 <= g1 <= 0.30,
            "Lam1_over_LamL": {str(gc): (g1 / gc) ** 2 for gc in (0.23, 0.25, 0.28, 0.30)},
            "hbar_star_over_LamL": {str(gc): (gs / gc) ** 2 for gc in (0.23, 0.25, 0.28, 0.30)},
        })
    return {
        "rows": rows,
        "a_inside_023_028": [x["a"] for x in rows if x["in_band_023_028"]],
        "a_inside_023_030": [x["a"] for x in rows if x["in_band_023_030"]],
        "min_gamma_Lam1": min(x["gamma_Lam1"] for x in rows),
        "min_gamma_hbar_star": min(x["gamma_hbar_star"] for x in rows),
        "a_at_min_gamma_hbar_star": min(rows, key=lambda x: x["gamma_hbar_star"])["a"],
        "sensitivity_Lam_L": {"gamma_c_x0.9": 0.9 ** 2, "gamma_c_x1.1": 1.1 ** 2, "coulomb_rs_star_x0.9": 0.9 ** -4},
    }


def disk_w(x: float, y: float) -> complex:
    tau = complex(x, y)
    return (tau - RHO) / (tau - RHO.conjugate())


def slope_fit(path: list[dict], wmax: float) -> dict:
    pts = [(abs(disk_w(p["x"], p["y"])), p["ratio"]) for p in path if p["stable_screen"] and p["ratio"] is not None]
    pts = [(w, t) for w, t in pts if 0.003 <= w <= wmax]
    w = np.array([p[0] for p in pts])
    t = np.array([p[1] for p in pts])
    c2 = np.polyfit(w, t, 2)
    return {"n": len(pts), "w_range": [float(w.min()), float(w.max())], "intercept": float(c2[2]), "slope": float(c2[1]), "quad": float(c2[0])}


def ray_slopes() -> dict:
    out = {}
    for name in ("1", "0.5", "0.7", "0.8", "1.2"):
        f = DATA / f"scan_a{name}.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text())
        up = slope_fit(d["paths"]["line_up"], 0.035)
        arc = slope_fit(d["paths"]["arc_to_i"], 0.035)
        out[name] = {"line_up": up, "arc_to_i": arc, "slope_ratio_up_over_arc": up["slope"] / arc["slope"]}
    return out


def hankel(kk: np.ndarray, f, rmax: float, n: int) -> np.ndarray:
    """u~(k) = 2 pi int_0^rmax r J0(kr) f(r) dr by composite Gauss-Legendre on n panels."""
    xg, wg = np.polynomial.legendre.leggauss(8)
    edges = np.linspace(0.0, rmax, n + 1)
    r = np.concatenate([0.5 * (b - a) * xg + 0.5 * (b + a) for a, b in zip(edges[:-1], edges[1:])])
    w = np.concatenate([0.5 * (b - a) * wg for a, b in zip(edges[:-1], edges[1:])])
    return np.array([2 * math.pi * float(np.sum(w * r * j0(k * r) * f(r))) for k in kk])


def shoulder_ft() -> dict:
    kk = np.linspace(0.0, 8.0, 801)
    shoulder = lambda r: 1.0 / (1.0 + r ** 6)
    u1 = hankel(kk, shoulder, 400.0, 8000)
    u2 = hankel(kk, shoulder, 600.0, 16000)
    imin = int(np.argmin(u1))
    gauss = hankel(kk, lambda r: np.exp(-r * r), 12.0, 400)
    gauss_exact = math.pi * np.exp(-kk ** 2 / 4.0)
    return {
        "shoulder_min_value": float(u1[imin]), "shoulder_min_k": float(kk[imin]), "shoulder_value_at_k0": float(u1[0]),
        "shoulder_k0_exact": 2 * math.pi * math.pi / (6 * math.sin(math.pi / 3)),
        "shoulder_two_cutoffs_max_abs_diff": float(np.max(np.abs(u1 - u2))),
        "fraction_of_k_grid_negative": float(np.mean(u1 < 0)),
        "first_zero_crossing_k": float(kk[int(np.where(u1 < 0)[0][0])]),
        "gaussian_positive_control_max_abs_error": float(np.max(np.abs(gauss - gauss_exact))),
        "gaussian_min_value": float(gauss.min()),
        "note": "units Rc = 1 (shoulder) and e^{-r^2} (Gaussian); k in units of 1/Rc",
    }


def rydberg() -> dict:
    hbar, u = const.hbar, const.atomic_mass
    m = 86.909180527 * u  # Rb-87 atomic mass (AME), assumed species; see Section 8
    a_lat = 532e-9
    rc = 2.02 * a_lat
    u0 = 2 * math.pi * hbar * 1.8e3
    e_rc = hbar ** 2 / (m * rc ** 2)
    return {
        "Rc_m": rc, "E_Rc_over_h_Hz": e_rc / const.h, "U0_over_E_Rc": u0 / e_rc,
        "hbar_over_sqrt_m_U0_Rc2": 1.0 / math.sqrt(u0 / e_rc),
        "assumptions": "Rb-87 mass; U0/2pi = 1.8 kHz, Rc/a_lat = 2.02 and a_lat = 532 nm as printed in Zeiher et al. (arXiv:1602.06313v3)",
    }


def main() -> int:
    table = json.loads((DATA / "result_numbers.json").read_text())["hbar_star_table"]
    out = {"bands": band_readings(table), "ray_slopes": ray_slopes(), "shoulder_ft": shoulder_ft(), "rydberg": rydberg()}
    (DATA / "extra_checks.json").write_text(json.dumps(out, indent=1))
    b = out["bands"]
    print("inside 0.23-0.28:", b["a_inside_023_028"], "inside 0.23-0.30:", b["a_inside_023_030"])
    print("min gamma(Lam1)", b["min_gamma_Lam1"], "min gamma(hbar*)", b["min_gamma_hbar_star"], "at a", b["a_at_min_gamma_hbar_star"])
    for k, v in out["ray_slopes"].items():
        print("a", k, "slope up", v["line_up"]["slope"], "arc", v["arc_to_i"]["slope"], "ratio", v["slope_ratio_up_over_arc"])
    print(json.dumps(out["shoulder_ft"], indent=1))
    print(json.dumps(out["rydberg"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
