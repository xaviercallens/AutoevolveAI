"""Figure c04: why the October 11 cut-off was an erratum, recomputed.

For the planar Yukawa potential V(r) = exp(-kappa r)/r at kappa = 1, density one, this script recomputes the energy
per particle (1/2) sum V(|v|) of the triangular lattice with the exact potential, with a plain cut at r_c and with the
shifted-force cut at r_c, and plots the error of each cut against r_c next to the square-minus-triangular gap.
Checks: the sweep rows ("kind": "sweep") of papers/ar_yukawa_crystal/data/exact_refs.jsonl and the exact values of
papers/ar_yukawa_crystal/data/mpmath_control.json.
Run: .venv/bin/python -I papers/discovery_journal_2026/code/fig04.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "papers" / "discovery_journal_2026" / "figures"
OKABE = {"orange": "#E69F00", "bleu_ciel": "#56B4E9", "vert": "#009E73", "jaune": "#F0E442",
         "bleu": "#0072B2", "vermillon": "#D55E00", "pourpre": "#CC79A7", "noir": "#000000"}
IVOIRE = "#FFFFF0"
A_TRI = np.sqrt(2.0 / np.sqrt(3.0))
KAPPA = 1.0


def style() -> None:
    plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9,
                         "mathtext.fontset": "dejavuserif",
                         "axes.facecolor": IVOIRE, "figure.facecolor": IVOIRE, "savefig.facecolor": IVOIRE,
                         "axes.edgecolor": "#555555", "axes.linewidth": 0.6, "axes.grid": True,
                         "grid.color": "#dddddd", "grid.linewidth": 0.5, "axes.spines.top": False,
                         "axes.spines.right": False})


def virgule(x: float, _pos: int) -> str:
    return f"{x:g}".replace(".", ",")


def dists(kind: str, rmax: float) -> np.ndarray:
    m = int(rmax / 0.8) + 2
    i, j = np.meshgrid(np.arange(-m, m + 1), np.arange(-m, m + 1), indexing="ij")
    if kind == "tri":
        x, y = A_TRI * (i + 0.5 * j), A_TRI * (np.sqrt(3.0) / 2.0) * j
    else:
        x, y = i.astype(float), j.astype(float)
    r = np.hypot(x, y).ravel()
    return np.sort(r[(r > 0) & (r < rmax)])


def e_exact(kind: str) -> float:
    r = dists(kind, 50.0)
    return float(0.5 * np.sum(np.exp(-KAPPA * r) / r))


def e_plain(kind: str, rc: float) -> float:
    r = dists(kind, rc)
    return float(0.5 * np.sum(np.exp(-KAPPA * r) / r))


def e_sf(kind: str, rc: float) -> float:
    r = dists(kind, rc)
    vc = np.exp(-KAPPA * rc) / rc
    dvc = -np.exp(-KAPPA * rc) * (KAPPA * rc + 1.0) / rc ** 2
    return float(0.5 * np.sum(np.exp(-KAPPA * r) / r - vc - (r - rc) * dvc))


def main() -> None:
    style()
    tri, sq = e_exact("tri"), e_exact("sq")
    mpc = {(r["kappa"], r["lattice"]): float(r["mp_direct"])
           for r in json.loads((ROOT / "papers/ar_yukawa_crystal/data/mpmath_control.json").read_text())["rows"]}
    print(f"check exact tri {tri:.13f} vs mpmath {mpc[(1, 'tri')]:.13f}; square {sq:.13f} vs {mpc[(1, 'square')]:.13f}")
    assert abs(tri - mpc[(1, "tri")]) < 1e-12 and abs(sq - mpc[(1, "square")]) < 1e-12
    gap = sq - tri
    print(f"gap square - triangular (exact) = {gap:.6e} (record 9.534156e-3)")
    rows = [json.loads(line) for line in (ROOT / "papers/ar_yukawa_crystal/data/exact_refs.jsonl").read_text().splitlines()
            if line.strip()]
    for row in rows:
        if row.get("kind") == "sweep" and row["kappa"] == 1:
            rc = float(row["rc"])
            sf_err, pl_err = e_sf("tri", rc) - tri, e_plain("tri", rc) - tri
            print(f"check rc={rc:g}: sf err {sf_err:.3e} (record {row['tri']['sf_err']:.3e}), "
                  f"plain err {pl_err:.3e} (record {row['tri']['plain_err']:.3e})")
            assert abs(sf_err - row["tri"]["sf_err"]) <= 0.002 * abs(row["tri"]["sf_err"]) + 5e-14
            assert abs(pl_err - row["tri"]["plain_err"]) <= 0.002 * abs(row["tri"]["plain_err"]) + 5e-14
    sf8 = e_sf("tri", 8.0)
    print(f"shifted force at r_c=8: {sf8:.10f}; exact - sf = {tri - sf8:.6e} (record 1.771212e-2); "
          f"ratio to gap = {(tri - sf8) / gap:.2f}")

    rcs = np.arange(6.0, 20.5, 0.5)
    err_sf = np.array([abs(e_sf("tri", rc) - tri) for rc in rcs])
    err_pl = np.array([abs(e_plain("tri", rc) - tri) for rc in rcs])

    fig, ax = plt.subplots(figsize=(6.3, 2.7))
    ax.xaxis.set_major_formatter(FuncFormatter(virgule))
    ax.semilogy(rcs, err_sf, color=OKABE["vermillon"], lw=1.6, label="erreur de la coupure « à force décalée »")
    ax.semilogy(rcs, err_pl, color=OKABE["bleu"], lw=1.6, label="erreur d'une coupure simple")
    ax.axhline(gap, color=OKABE["noir"], lw=0.9, ls="--", label="écart à mesurer : carré moins triangle")
    ax.axvline(8.0, color="#888888", lw=0.8, ls=":")
    ax.plot([8.0], [tri - sf8], "o", ms=6, color=OKABE["orange"], mec=IVOIRE, mew=1.2)
    ax.annotate(r"$r_c=8$ : 0,0177", (8.0, tri - sf8), xytext=(8, 6), textcoords="offset points", fontsize=8)
    ax.set_xlabel("rayon de coupure $r_c$ (densité 1)")
    ax.set_ylabel("erreur sur l'énergie par particule")
    ax.set_xlim(6, 20)
    ax.legend(fontsize=7.5, loc="lower left", frameon=False)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"c04_coupure.{ext}", dpi=300)
    print("wrote", OUT / "c04_coupure.pdf", "and .png")


if __name__ == "__main__":
    main()
