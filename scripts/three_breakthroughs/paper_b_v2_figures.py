"""Figures for Paper B, edition 2. Every plotted number is read from paper_b_v2_results.json or
recomputed from the model functions of paper_b_v2_experiment.py (Fig. 2 density, Fig. 5 symbols).

Run: .venv/bin/python scripts/three_breakthroughs/paper_b_v2_figures.py [results.json]
Writes vector PDFs into papers/three_breakthroughs/paper_b/. 3D axes use matplotlib's built-in
mplot3d projection (projection="3d").
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import scipy.fft as sfft  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper_b_v2_experiment as X  # noqa: E402

PAPER_DIR = X.ROOT / "papers" / "three_breakthroughs" / "paper_b"
# validated categorical slots (dataviz palette check: CVD and normal-vision separation PASS)
COL = {"ns": "#5b5b5b", "piecewise": "#2a78d6", "smooth": "#eb6834"}
LS = {"ns": ":", "piecewise": "-", "smooth": "--"}
LABEL = {"ns": "Navier–Stokes ($m\\equiv1$)", "piecewise": "piecewise scale-dual", "smooth": "smooth (ML-$\\alpha$)"}

plt.rcParams.update({"font.size": 10, "axes.labelsize": 10, "axes.titlesize": 10.5, "legend.fontsize": 8.5,
                     "xtick.labelsize": 9, "ytick.labelsize": 9, "pdf.fonttype": 42, "font.family": "DejaVu Sans",
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e3e3e3",
                     "grid.linewidth": 0.6})


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def runs_where(res: dict[str, Any], **kw: Any) -> list[dict[str, Any]]:
    return [r for r in res["runs"] if all(r.get(k) == v for k, v in kw.items())]


def fig1_trajectories_3d(res: dict[str, Any], out: Path) -> None:
    fig = plt.figure(figsize=(7.2, 5.6))
    ax = fig.add_subplot(111, projection="3d")
    zmax = 0.0
    for kind in X.KINDS:
        for nu, lw, alpha_line in (("0", 2.0, 1.0), ("1/100", 1.4, 0.75)):
            sel = runs_where(res, group="ensemble", kind=kind, alpha_exact="1/25", nu_exact=nu, seed=0)
            if not sel:
                continue
            r = sel[0]
            x = np.array(r["E_over_E0"])
            y = np.array(r["Q_over_Q0"])
            z = np.array(r["alpha_Omega_eff_over_Q0"])
            zmax = max(zmax, float(z.max()))
            lab = f"{LABEL[kind]}, $\\nu$={'0' if nu == '0' else '1/100'}"
            ax.plot(x, y, z, color=COL[kind], ls=LS[kind] if nu == "0" else "-.", lw=lw, alpha=alpha_line, label=lab)
            ax.scatter([x[-1]], [y[-1]], [z[-1]], color=COL[kind], s=14, depthshade=False)
    allx = [v for r in runs_where(res, group="ensemble", alpha_exact="1/25", seed=0) for v in r["E_over_E0"]]
    ally = [v for r in runs_where(res, group="ensemble", alpha_exact="1/25", seed=0) for v in r["Q_over_Q0"]]
    x0, x1 = 0.0, max(allx) * 1.05
    y0, y1 = min(ally) * 0.95, 1.05
    zt = max(zmax, y1) * 1.05
    # ceiling surface alpha*Omega_eff/Q0 = Q/Q0 (Lean: omega_eff_le_Q_div_alpha); model curves lie below it
    xx, yy = np.meshgrid(np.linspace(x0, x1, 2), np.linspace(y0, y1, 2))
    ax.plot_surface(xx, yy, yy, color="#2a78d6", alpha=0.10, linewidth=0, shade=False)
    # plane Q/Q0 = 1
    xq, zq = np.meshgrid(np.linspace(x0, x1, 2), np.linspace(0, zt, 2))
    ax.plot_surface(xq, np.ones_like(xq), zq, color="#999999", alpha=0.07, linewidth=0, shade=False)
    ax.set_xlabel("$E(t)/E_0$  (dimensionless)", labelpad=6)
    ax.set_ylabel("$Q(t)/Q_0$  (dimensionless)", labelpad=6)
    ax.set_zlabel("$\\alpha'\\,\\Omega_{\\rm eff}(t)/Q_0$  (dimensionless)", labelpad=6)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_zlim(0, zt)
    ax.view_init(elev=22, azim=-58)
    ax.set_title("Inviscid model curves stay on $Q/Q_0=1$ while $E$ grows;\n"
                 "blue plane: ceiling $\\alpha'\\Omega_{\\rm eff}=Q$ (Lean); $N=32^3$, $\\alpha'=1/25$, seed 0", pad=2)
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.93), frameon=False, ncol=1)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


# A genuinely three-dimensional solenoidal triad (k_z != 0), integer amplitudes u_k = k x a + i k x b.
FIG2_TRIAD_3D: dict[X.Vec, tuple[X.GInt, X.GInt, X.GInt]] = {
    (1, 1, 0): X.solenoidal_amplitude((1, 1, 0), (1, 0, 0), (0, 0, 1)),
    (0, 1, 1): X.solenoidal_amplitude((0, 1, 1), (1, 0, 0), (0, 1, 0)),
    (-1, -2, -1): X.solenoidal_amplitude((-1, -2, -1), (1, 0, 0), (0, 1, 1)),
}


def production_density(kind: str, n: int = 48) -> tuple[np.ndarray, float]:
    g = X.Galerkin(n, 0.25, kind, 0.0)
    uh = X.field_from_modes(g, FIG2_TRIAD_3D)
    adv = g.advection(uh)
    u = sfft.irfftn(uh, s=g.shape, axes=(1, 2, 3))
    a = sfft.irfftn(adv, s=g.shape, axes=(1, 2, 3))
    dens = -np.sum(u * a, axis=0)  # -u.[(u.grad)(Mu)], volume mean = dE/dt
    return dens, float(dens.mean())


def fig2_density_3d(res: dict[str, Any], out: Path) -> None:
    n = 48
    dens = {k: production_density(k, n) for k in ("piecewise", "ns")}
    thr = np.quantile(np.abs(dens["piecewise"][0]), 0.93)
    x = np.arange(n) * 2 * np.pi / n
    gx, gy, gz = np.meshgrid(x, x, x, indexing="ij")
    fig = plt.figure(figsize=(7.4, 3.9))
    from fractions import Fraction

    ex = {k: X.exact_rates(FIG2_TRIAD_3D, X.exact_weight(k, Fraction(1, 4))) for k in ("piecewise", "ns")}
    exact = {k: str(v["dE_dt"]) for k, v in ex.items()}
    side = {"field": {str(k): v for k, v in FIG2_TRIAD_3D.items()}, "alpha": "1/4",
            "exact": {k: {q: str(v[q]) for q in ("E0", "Q0", "dE_dt", "dQ_dt")} for k, v in ex.items()},
            "float_volume_mean_N48": {k: dens[k][1] for k in dens}, "voxel_threshold": float(thr)}
    (out.parent / "paper_b_v2_fig2_values.json").write_text(json.dumps(side, indent=1))
    for i, kind in enumerate(("piecewise", "ns")):
        d, mean = dens[kind]
        ax = fig.add_subplot(1, 2, i + 1, projection="3d")
        for sign, col, lab in ((1, "#eb6834", "creates $E$"), (-1, "#2a78d6", "destroys $E$")):
            mask = sign * d > thr
            ax.scatter(gx[mask], gy[mask], gz[mask], s=1.2, c=col, alpha=0.35, linewidths=0, label=lab, depthshade=False)
        ax.set_xlim(0, 2 * np.pi)
        ax.set_ylim(0, 2 * np.pi)
        ax.set_zlim(0, 2 * np.pi)
        ticks = [0, np.pi, 2 * np.pi]
        for setter in (ax.set_xticks, ax.set_yticks, ax.set_zticks):
            setter(ticks)
        for setter in (ax.set_xticklabels, ax.set_yticklabels, ax.set_zticklabels):
            setter(["0", "$\\pi$", "$2\\pi$"])
        ax.set_xlabel("$x$")
        ax.set_ylabel("$y$")
        ax.set_zlabel("$z$")
        name = "piecewise scale-dual, $\\alpha'=1/4$" if kind == "piecewise" else "Navier–Stokes control"
        ax.set_title(f"{name}\nvolume mean $dE/dt$ = {mean:+.4f} (exact {exact[kind]})", fontsize=9.5, pad=0)
        ax.view_init(elev=24, azim=-60)
        if i == 0:
            ax.legend(loc="upper left", markerscale=6, frameon=False, fontsize=8)
    fig.suptitle("Local $L^2$ production $-u\\cdot[(u\\cdot\\nabla)(Mu)]$ of one 3D triad field ($48^3$ grid)\n"
                 f"voxels with $|\\cdot|>{thr:.1f}$, same threshold in both panels", fontsize=9.5)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(out)
    plt.close(fig)


def fig3_time_series_threshold(res: dict[str, Any], out: Path) -> None:
    fig, axs = plt.subplots(1, 3, figsize=(10.2, 3.3))
    for ax, nu, title in ((axs[0], "0", "(a) inviscid"), (axs[1], "1/100", "(b) $\\nu=1/100$")):
        for kind in X.KINDS:
            sel = runs_where(res, group="ensemble", kind=kind, alpha_exact="1/25", nu_exact=nu)
            if not sel:
                continue
            t = np.array(sel[0]["t"])
            for qty, ls_, tag in (("E_over_E0", LS[kind], "E"), ("Q_over_Q0", (0, (1, 1.5)), "Q")):
                arr = np.array([r[qty] for r in sel])
                mu, sd = arr.mean(0), arr.std(0, ddof=1) if len(sel) > 1 else np.zeros(arr.shape[1])
                if kind == "ns" and tag == "Q":
                    continue  # Q = E for Navier-Stokes
                ax.plot(t, mu, color=COL[kind], ls=ls_ if tag == "E" else ":", lw=1.8 if tag == "E" else 1.2,
                        label=f"{tag}/{tag}$_0$, {LABEL[kind]}")
                ax.fill_between(t, mu - sd, mu + sd, color=COL[kind], alpha=0.15, linewidth=0)
        ax.axhline(1.0, color="#222222", lw=0.7)
        ax.ticklabel_format(axis="y", useOffset=False)
        ax.set_xlabel("time $t$ (box units, $E_0=1/2$)")
        ax.set_ylabel("ratio to initial value")
        ax.set_title(f"{title}, $\\alpha'=1/25$, {len(sel)} seeds (mean $\\pm$ s.d.)", fontsize=9.5)
    axs[0].legend(frameon=False, fontsize=7.2, loc="upper left")
    # (c) exact growth threshold lambda*(nu) = 2 nu Omega / R for the alpha'=1/25 triad
    a2 = res["exact"]["A2_triad_alpha_1_25"]
    slope = a2["lambda_star_over_nu"]["float"]
    nus = np.linspace(0, 0.02, 200)
    ax = axs[2]
    ax.plot(nus, slope * nus, color=COL["piecewise"], lw=2)
    ax.fill_between(nus, slope * nus, slope * 0.02 * 1.1, color=COL["piecewise"], alpha=0.12, linewidth=0)
    lam = a2["lambda_star_growth_threshold"]
    ax.plot([0.01], [lam["float"]], "o", color="#222222", ms=6)
    ax.annotate(f"paper's $\\nu=1/100$:\n$\\lambda^*={lam['exact']}$", (0.01, lam["float"]), xytext=(0.0122, lam["float"] * 0.62),
                arrowprops={"arrowstyle": "-", "color": "#555555", "lw": 0.7}, fontsize=8.5)
    ax.text(0.002, slope * 0.0165, "$dE/dt>0$\n(exact)", fontsize=8.5, color="#1c5cab")
    ax.text(0.0145, slope * 0.0025, "$dE/dt<0$", fontsize=8.5, color="#444444")
    ax.set_xlim(0, 0.02)
    ax.set_ylim(0, slope * 0.02 * 1.1)
    ax.set_xlabel("viscosity $\\nu$ (box units)")
    ax.set_ylabel("amplitude $\\lambda$ of the triad")
    ax.set_title(f"(c) growth threshold $\\lambda^*=2\\nu\\Omega/R={a2['lambda_star_over_nu']['exact']}\\,\\nu$")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def fig4_amplitude(res: dict[str, Any], out: Path) -> None:
    fig, ax = plt.subplots(figsize=(5.6, 3.9))
    e0s = [X.E_TARGET] + list(X.AMP_E0)
    for j, kind in enumerate(X.KINDS):
        mus, sds, xs = [], [], []
        for e0 in e0s:
            sel = (runs_where(res, group="ensemble", kind=kind, alpha_exact="1/25", nu_exact="1/100") if e0 == X.E_TARGET
                   else runs_where(res, group="amplitude_scan", kind=kind, e0=e0))
            vals = np.array([r["maxE_over_E0"] for r in sel])
            if vals.size == 0:
                continue
            xs.append(e0 * (1 + 0.06 * (j - 1)))
            mus.append(vals.mean())
            sds.append(vals.std(ddof=1) if vals.size > 1 else 0.0)
            ax.scatter(np.full(vals.size, e0 * (1 + 0.06 * (j - 1))), vals, s=9, color=COL[kind], alpha=0.45, linewidths=0)
        ax.errorbar(xs, mus, yerr=sds, color=COL[kind], ls=LS[kind], marker="o", ms=5, lw=1.5, capsize=3,
                    label=f"{LABEL[kind]}, $N=32^3$")
        conv = [r for r in res["runs"] if r["group"] == "conv_N64" and r["kind"] == kind]
        if conv:
            ax.scatter([r["e0"] * (1 + 0.06 * (j - 1)) for r in conv], [r["maxE_over_E0"] for r in conv], marker="s",
                       s=30, facecolors="none", edgecolors=COL[kind], linewidths=1.2,
                       label=f"{LABEL[kind]}, $N=64^3$ (seeds 0–2)")
    ax.axhline(1.0, color="#222222", lw=0.7)
    ax.set_xscale("log")
    ax.set_xticks(e0s)
    ax.set_xticklabels([f"{e:g}" for e in e0s])
    ax.set_xlabel("initial energy $E_0$ (box units)")
    ax.set_ylabel("$\\max_{t\\leq 3} E(t)/E_0$")
    ax.set_title("Edition-1 bound $E(t)\\leq E_0$ tested at $\\alpha'=1/25$, $\\nu=1/100$")
    ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def fig5_symbols(out: Path) -> None:
    a = 1 / 25
    k = np.linspace(0.05, 20, 800)
    y = a * k ** 2
    mp = np.minimum(1, 1 / y)
    ms = 1 / (1 + y)
    fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.2))
    ax = axs[0]
    ax.plot(k, mp, color=COL["piecewise"], lw=2, label="$m_{\\rm pw}=\\min(1,1/(\\alpha'|k|^2))$")
    ax.plot(k, ms, color=COL["smooth"], lw=2, ls="--", label="$m_{\\rm ML}=1/(1+\\alpha'|k|^2)$")
    ax.plot(k, 2 * ms, color=COL["smooth"], lw=1, ls=":", label="$2\\,m_{\\rm ML}$ (Lean upper bound)")
    ax.axvline(1 / np.sqrt(a), color="#888888", lw=0.7)
    ax.text(1 / np.sqrt(a) + 0.3, 1.6, "$k_*=1/\\sqrt{\\alpha'}=5$", fontsize=8.5)
    ax.set_xlabel("wavenumber $|k|$ (box units)")
    ax.set_ylabel("advected-field weight $m$")
    ax.set_title("(a) symbols, $\\alpha'=1/25$")
    ax.legend(frameon=False, fontsize=8)
    ax = axs[1]
    ax.plot(k, k * mp, color=COL["piecewise"], lw=2, label="$k_{\\rm eff}=|k|\\,m_{\\rm pw}$")
    ax.plot(k, k * ms, color=COL["smooth"], lw=2, ls="--", label="$k_{\\rm smooth}=|k|\\,m_{\\rm ML}$")
    ax.plot(k, k, color=COL["ns"], lw=1, ls=":", label="$|k|$ (Navier–Stokes)")
    ax.set_ylim(0, 8)
    ax.set_xlabel("wavenumber $|k|$ (box units)")
    ax.set_ylabel("effective wavenumber")
    ax.set_title("(b) $k_{\\rm eff}\\leq 1/\\sqrt{\\alpha'}$, $k_{\\rm smooth}\\leq 1/(2\\sqrt{\\alpha'})$")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else X.OUT
    res = load(path)
    outs = {
        "fig1_v2_invariant_trajectories_3d.pdf": lambda p: fig1_trajectories_3d(res, p),
        "fig2_v2_energy_production_density_3d.pdf": lambda p: fig2_density_3d(res, p),
        "fig3_v2_energy_vs_Q_and_threshold.pdf": lambda p: fig3_time_series_threshold(res, p),
        "fig4_v2_amplitude_scan.pdf": lambda p: fig4_amplitude(res, p),
        "fig5_v2_symbols.pdf": fig5_symbols,
    }
    outdir = Path(sys.argv[2]) if len(sys.argv) > 2 else PAPER_DIR
    for name, fn in outs.items():
        fn(outdir / name)
        print("wrote", outdir / name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
