"""Figures for Paper A edition 2. Every plotted value is read from paper_a_v2_results.json
(written by paper_a_v2_experiment.py) or recomputed from the model potential; nothing is drawn
from a formula standing in for data.

Run: .venv/bin/python scripts/three_breakthroughs/paper_a_v2_figures.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # 3D axes come from projection="3d" (mpl_toolkits.mplot3d, bundled)
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import Normalize  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DIR = REPO / "papers" / "three_breakthroughs" / "paper_a"
RES = DIR / "paper_a_v2_results.json"

# validated categorical order (dataviz reference palette, light mode); reference solver in ink
COL = {"rk4": "#2a78d6", "rrk": "#eb6834", "euler": "#1baf7a", "midpoint": "#eda100", "dop853": "#0b0b0b"}
LS = {"rk4": "-", "rrk": "--", "euler": "-.", "midpoint": ":", "dop853": "-"}
MK = {"rk4": "o", "rrk": "s", "euler": "^", "midpoint": "D", "dop853": "x"}
LABEL = {"rk4": "RK4", "rrk": "RRK (relaxed on $H$)", "euler": "forward Euler", "midpoint": "explicit midpoint RK2",
         "dop853": "DOP853 reference"}
H_STAR = 29 / 40

plt.rcParams.update({"font.size": 9, "axes.titlesize": 9.5, "axes.labelsize": 9, "legend.fontsize": 7.5,
                     "xtick.labelsize": 8, "ytick.labelsize": 8, "pdf.fonttype": 42, "font.family": "DejaVu Sans",
                     "axes.spines.top": False, "axes.spines.right": False})


def potential(r: np.ndarray, z: np.ndarray) -> np.ndarray:
    return 0.5 * (1.0 + 0.6 * r * r + 0.8 * z * z + 0.8 * r * r * z)


def fig_well_3d(d: dict[str, Any]) -> Path:
    tr = d["figure_trajectory"]
    fig = plt.figure(figsize=(7.2, 3.5))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    r = np.linspace(-2.2, 2.2, 161)
    z = np.linspace(-1.6, 1.2, 141)
    rg, zg = np.meshgrid(r, z)
    vg = potential(rg, zg)
    floor, top = 0.0, 1.2
    vm = np.where((vg >= floor) & (vg <= top), vg, np.nan)
    ax.plot_surface(rg, zg, vm, cmap="cividis", norm=Normalize(0.45, top), rstride=3, cstride=3, linewidth=0,
                    antialiased=True, alpha=0.9)
    # floor projection: the V = H* level set (the line z = -3/4 and the inner basin boundary) and the orbit
    ax.contour(rg, zg, vg, levels=[H_STAR], colors="k", linewidths=0.9, offset=floor, zdir="z")
    dop = tr["dop853"]
    ax.plot(dop["r"], dop["z"], np.full(len(dop["r"]), floor), color="#52514e", lw=0.3, alpha=0.8)
    s = np.sqrt(1.5)
    ax.scatter([s, -s], [-0.75, -0.75], [H_STAR, H_STAR], color="#e34948", s=30, depthshade=False, zorder=10)
    ax.scatter([s, -s], [-0.75, -0.75], [floor, floor], color="#e34948", s=12, depthshade=False)
    ax.set_xlabel("$r$ (model units)")
    ax.set_ylabel("$z$ (model units)")
    ax.set_zlabel(r"$V=\mu B(r,z)$ (energy units)")
    ax.set_zlim(floor, top)
    ax.view_init(elev=30, azim=-60)
    ax.set_title("(a) potential $V$; red: saddles at $V=H^*=29/40$;\n"
                 "floor: level set $V=H^*$ (black), DOP853 orbit (grey)", pad=0)

    ax2 = fig.add_subplot(1, 2, 2, projection="3d")
    # The window is set by the three conservative integrators, not by Euler: with Euler's +0.03
    # excursion included the RK4 sinking that this panel exists to show is a sub-pixel smear.
    # Euler is clipped and labelled as leaving the window instead.
    span = [np.array(tr[m]["H"]) - H_STAR for m in ("dop853", "rk4", "rrk")]
    lo = min(s.min() for s in span)
    hi = max(s.max() for s in span)
    pad = max(0.12 * (hi - lo), 1e-4)
    lo, hi = lo - pad, hi + pad
    for m in ("dop853", "rk4", "rrk", "euler"):
        t = tr[m]
        dh = np.array(t["H"]) - H_STAR
        keep = dh <= hi
        if not np.all(keep):
            cut = int(np.argmax(~keep))
            keep = np.arange(dh.size) < cut + 1
            dh = np.clip(dh, lo, hi)
        ax2.plot(np.array(t["r"])[keep], np.array(t["z"])[keep], dh[keep], color=COL[m], ls=LS[m],
                 lw=0.6 if m != "euler" else 1.2, label=LABEL[m] + (" (leaves window)" if m == "euler" else ""))
    # H^* itself (the plane H_n - H^* = 0) now lies above the window; say so rather than draw a
    # clipped sliver of it.
    ax2.set_zlim(lo, hi)
    ax2.set_xlabel("$r$")
    ax2.set_ylabel("$z$")
    ax2.set_zlabel("$H_n - H^*$")
    ax2.view_init(elev=18, azim=-62)
    ax2.set_title(f"(b) same orbit, $H_0-H^*={tr['H0'] - H_STAR:.2e}$, $\\Delta t={tr['dt']}$;\n"
                  "RK4 sinks; escape energy $H^*$ is above the window", pad=0)
    # A legend inside the 3D box collides with either the title or the r-axis ticks; put it under
    # the panel instead.
    ax2.legend(loc="upper center", frameon=False, fontsize=6.4, ncol=2, borderaxespad=0.0,
               bbox_to_anchor=(0.5, -0.02), columnspacing=1.0, handlelength=1.8)
    fig.tight_layout()
    out = DIR / "fig_a1_well_trajectories_3d.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def fig_energy_sign(d: dict[str, Any]) -> Path:
    runs = d["runs"]
    dts = d["model"]["dts"]
    h0 = {b: np.array(d["initial_H0"][b]) - H_STAR for b in ("below", "above")}
    edges_b = np.linspace(-0.03, -0.001, 5)
    edges_a = np.linspace(0.001, 0.02, 3)
    cells = [("below", edges_b[i], edges_b[i + 1]) for i in range(4)] + [("above", edges_a[i], edges_a[i + 1])
                                                                          for i in range(2)]
    med = np.full((len(cells), len(dts)), np.nan)
    p1 = np.full_like(med, np.nan)
    p99 = np.full_like(med, np.nan)
    for j, dt in enumerate(dts):
        for i, (b, lo, hi) in enumerate(cells):
            run = next(x for x in runs if x["band"] == b and x["method"] == "rk4" and x["dt"] == dt)
            f = np.array([np.nan if v is None else v for v in run["per_orbit"]["final_dH"]], dtype=float)
            esc = np.array(run["per_orbit"]["escaped"])
            sel = (h0[b] >= lo) & (h0[b] < hi) & ~esc
            if np.any(sel):
                med[i, j], p1[i, j], p99[i, j] = np.nanpercentile(f[sel], [50, 1, 99])
    n_orb = d["model"]["n_orbits"]
    ref_frac = d["dop853_reference"]["above"]["frac_escaped"]
    fig = plt.figure(figsize=(7.2, 5.8))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1])
    ax = fig.add_subplot(gs[0, :])
    bx = fig.add_subplot(gs[1, 0])
    cx = fig.add_subplot(gs[1, 1])
    mag = np.log10(np.abs(med))
    im = ax.imshow(mag, cmap="cividis", aspect="auto", origin="lower")
    for i in range(len(cells)):
        for j in range(len(dts)):
            tag = "1st-99th pct < 0" if p99[i, j] < 0 else ("all > 0" if p1[i, j] > 0 else "mixed sign")
            ax.text(j, i, f"median {med[i, j]:+.1e}\n{tag}", ha="center", va="center", fontsize=6.5,
                    color="w" if mag[i, j] < np.nanmean(mag) else "k")
    ax.set_xticks(range(len(dts)), [str(x) for x in dts])
    ax.set_yticks(range(len(cells)), [f"[{lo:+.4f}, {hi:+.4f})" for _, lo, hi in cells])
    ax.set_xlabel(r"step size $\Delta t$ (model time units)")
    ax.set_ylabel(r"$H_0 - H^*$ bin (energy units)")
    ax.axhline(3.5, color="w", lw=2.0)
    cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.09)
    cb.set_label(r"$\log_{10}|\mathrm{median}(H_N - H_0)|$")
    ax.set_title("(a) RK4 final energy error $H_N-H_0$ of non-escaped orbits (rows above the white line: $H_0>H^*$)")
    for m in ("rk4", "rrk", "midpoint", "euler"):
        below = [next(x for x in runs if x["band"] == "below" and x["method"] == m and x["dt"] == dt)["escaped"]
                 / n_orb for dt in dts]
        above = [next(x for x in runs if x["band"] == "above" and x["method"] == m and x["dt"] == dt)["escape_frac"]
                 for dt in dts]
        bx.plot(dts, below, color=COL[m], ls=LS[m], marker=MK[m], ms=4.5, lw=1.6, label=LABEL[m])
        cx.plot(dts, above, color=COL[m], ls=LS[m], marker=MK[m], ms=4.5, lw=1.6, label=LABEL[m])
    cx.axhline(ref_frac, color=COL["dop853"], lw=1.0, ls=(0, (4, 2)), label=f"DOP853 reference ({ref_frac:.3f})")
    for axx, title in ((bx, "(b) spurious escape, $H_0<H^*$ (all escapes are spurious)"),
                       (cx, "(c) escape fraction, $H_0>H^*$, vs DOP853")):
        axx.set_xscale("log")
        axx.set_xticks(dts, [str(x) for x in dts])
        axx.minorticks_off()
        axx.set_ylim(-0.03, 1.05)
        axx.set_xlabel(r"step size $\Delta t$")
        axx.set_ylabel(f"fraction of {n_orb} orbits")
        axx.set_title(title, fontsize=8.5)
    bx.legend(frameon=False, fontsize=7, loc="center right")
    cx.legend(frameon=False, fontsize=7, loc="lower left")
    fig.tight_layout()
    out = DIR / "fig_a2_energy_sign_escape.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def fig_linear_control(d: dict[str, Any]) -> Path:
    pc = d["positive_control_linear_well"]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    cmap = plt.get_cmap("viridis")
    for k, row in enumerate(pc["per_dt"]):
        c = cmap(k / (len(pc["per_dt"]) - 1) * 0.9)
        ax.plot(row["curve_n"], 1 - np.array(row["curve_closed_form"]), color=c, lw=1.4, label=f"$\\Delta t={row['dt']}$")
        ax.plot(row["curve_n"], 1 - np.array(row["curve_measured"]), color=c, lw=0, marker="o", ms=2.5)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("steps $N$")
    ax.set_ylabel(r"energy lost, $1 - E_N/E_0$")
    ax.set_title(r"(a) RK4, linear well: markers measured," "\n" r"lines $\sum_i E_i\rho_4(y_i)^N$ (Lean closed form)")
    ax.legend(frameon=False, fontsize=6.5, loc="upper left")
    row = next(r for r in pc["per_dt"] if r["dt"] == 0.2)
    bx.plot(row["euler_n"], np.array(row["euler_closed_form"]) - 1, color=COL["euler"], lw=1.4,
            label=r"Euler, $(1+y^2)^N$")
    bx.plot(row["euler_n"], np.array(row["euler_measured"]) - 1, color=COL["euler"], lw=0, marker=MK["euler"], ms=4)
    bx.plot(row["euler_n"], np.array(row["midpoint_closed_form"]) - 1, color=COL["midpoint"], ls=":", lw=1.6,
            label=r"midpoint, $(1+y^4/4)^N$")
    bx.plot(row["euler_n"], np.array(row["midpoint_measured"]) - 1, color=COL["midpoint"], lw=0, marker=MK["midpoint"],
            ms=4)
    bx.set_xscale("log")
    bx.set_yscale("log")
    bx.set_xlabel("steps $N$")
    bx.set_ylabel(r"energy gained, $E_N/E_0 - 1$")
    bx.set_title(r"(b) negative controls at $\Delta t = 0.2$: heating" "\n(markers measured, lines closed form)")
    bx.legend(frameon=False, fontsize=6.5)
    fig.tight_layout()
    out = DIR / "fig_a3_linear_well_controls.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def fig_poincare_3d(d: dict[str, Any]) -> Path:
    pc = d["figure_poincare"]
    zlo = min(min(pc[m]["H"]) for m in ("rk4", "rrk")) - H_STAR - 0.002
    zhi = max(max(pc[m]["H"]) for m in ("rk4", "rrk")) - H_STAR + 0.001
    fig = plt.figure(figsize=(7.2, 3.4))
    for k, m in enumerate(("rk4", "rrk")):
        ax = fig.add_subplot(1, 2, k + 1, projection="3d")
        s = pc[m]
        h = np.array(s["H"]) - H_STAR
        ax.scatter(s["r"], s["p_r"], h, c=h, cmap="cividis", vmin=zlo, vmax=zhi, s=1.2, depthshade=False)
        ax.set_xlabel("$r$")
        ax.set_ylabel("$p_r$")
        ax.set_zlabel("$H - H^*$")
        ax.set_zlim(zlo, zhi)
        ax.view_init(elev=14, azim=-55)
        ax.set_title(f"({'ab'[k]}) {LABEL[m]}: section $z=0$, $v>0$,\n{pc['orbits']} orbits, "
                     f"$\\Delta t={pc['dt']}$, $T={pc['horizon']:.0f}$", pad=0)
    fig.tight_layout()
    out = DIR / "fig_a4_poincare_energy_shells_3d.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def main() -> int:
    d = json.loads(RES.read_text())
    for f in (fig_well_3d(d), fig_energy_sign(d), fig_linear_control(d), fig_poincare_3d(d)):
        print("wrote", f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
