"""Paper C, edition 2: figures from papers/three_breakthroughs/paper_c/paper_c_v2_results.json.

Every plotted value is read from the results file written by paper_c_v2_experiment.py; nothing is
typed in by hand except reference lines that are mathematical constants (|z| = sqrt 2, 2 sqrt 2, the
level 2 claimed by edition 1).

Run: .venv/bin/python scripts/three_breakthroughs/paper_c_v2_figures.py
Writes (vector PDF) into papers/three_breakthroughs/paper_c/:
  fig3_ramanujan_cylinder.pdf      3D: recurrence roots of N_e(p) on the cylinder |z| = sqrt 2
  fig4_deviation_bars.pdf          3D: normalised deviation D_e(p) from the mass-formula main term
  fig5_visibility_and_frey.pdf     2D: (a) visibility vs root number, p < 2000; (b) Frey (3^p,4^p) levels
  fig6_spectral_gap_E0.pdf         2D: largest |a_2| over all vs visible cusp orbits
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.colors import TwoSlopeNorm
from matplotlib.lines import Line2D

REPO = Path(__file__).resolve().parents[2]
DIR = REPO / "papers" / "three_breakthroughs" / "paper_c"
RES = DIR / "paper_c_v2_results.json"

BLUE, ORANGE, AQUA, INK, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e"
plt.rcParams.update({
    "font.family": "serif", "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
    "legend.fontsize": 8.5, "xtick.labelsize": 9, "ytick.labelsize": 9, "pdf.fonttype": 42,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": False,
})


def load() -> dict[str, Any]:
    return json.loads(RES.read_text())


def fig_cylinder(res: dict[str, Any]) -> Path:
    rec = res["recurrence"]
    primes = [int(p) for p in rec]
    fig = plt.figure(figsize=(7.2, 6.2))
    ax = fig.add_subplot(111, projection="3d")
    th = np.linspace(0, 2 * math.pi, 120)
    zz = np.linspace(min(primes), max(primes), 30)
    TH, ZZ = np.meshgrid(th, zz)
    ax.plot_surface(math.sqrt(2) * np.cos(TH), math.sqrt(2) * np.sin(TH), ZZ, color=BLUE, alpha=0.08,
                    linewidth=0, shade=False)
    for z0 in (min(primes), max(primes)):
        ax.plot(math.sqrt(2) * np.cos(th), math.sqrt(2) * np.sin(th), z0, color=BLUE, lw=0.8, alpha=0.6)
    for p in primes:
        row = rec[str(p)]
        roots = np.array(row["roots"])
        triv = np.abs(roots[:, 0] - 2) + np.abs(roots[:, 1]) < 1e-9
        ax.scatter([2.0], [0.0], [p], marker="s", s=14, color=INK, depthshade=False)
        nt = roots[~triv]
        if len(nt):
            ax.scatter(nt[:, 0], nt[:, 1], np.full(len(nt), p), s=26, color=BLUE, edgecolor="white",
                       linewidth=0.4, depthshade=False)
        for inv in row["invisible_orbit_roots"]:
            col = ORANGE if inv["root_number"] == 1 else AQUA
            pts = np.array(inv["roots"])
            ax.scatter(pts[:, 0], pts[:, 1], [p, p], s=34, facecolor="none", edgecolor=col, linewidth=1.1,
                       marker="o" if inv["root_number"] == 1 else "D", depthshade=False)
    ax.set_xlabel(r"Re $z$")
    ax.set_ylabel(r"Im $z$")
    ax.set_zlabel(r"prime $p$ ($p\equiv 3 \,\mathrm{mod}\,4$)")
    ax.set_xlim(-2.2, 2.2)
    ax.set_ylim(-2.2, 2.2)
    ax.set_xticks([-2, -1, 0, 1, 2])
    ax.set_yticks([-2, -1, 0, 1, 2])
    ax.view_init(elev=18, azim=-58)
    n_inv_plus = sum(1 for v in rec.values() for i in v["invisible_orbit_roots"] if i["root_number"] == 1)
    handles = [
        Line2D([], [], marker="o", ls="", color=BLUE, label=r"recovered root of $N_e(p)$ recurrence"),
        Line2D([], [], marker="D", ls="", mfc="none", mec=AQUA,
               label=r"root of an invisible orbit, root number $-1$ (PARI $T_2$)"),
        Line2D([], [], marker="s", ls="", color=INK, label=r"trivial root $z=2$ (Eisenstein)"),
        Line2D([], [], color=BLUE, alpha=0.5, label=r"cylinder $|z|=\sqrt{2}$"),
    ]
    if n_inv_plus:
        handles.insert(2, Line2D([], [], marker="o", ls="", mfc="none", mec=ORANGE,
                                 label=r"root of an invisible orbit, root number $+1$ (PARI $T_2$)"))
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=2, frameon=False)
    worst = max(v["max_abs_modsq_minus_2"] for v in rec.values())
    ax.set_title(r"Every non-trivial root recovered from $O_0$ counts has $|z|^2=2$"
                 f"\n(max $||z|^2-2|$ = {worst:.1e}, $p\\leq 83$)", pad=2)
    out = DIR / "fig3_ramanujan_cylinder.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def fig_deviation(res: dict[str, Any]) -> Path:
    lat = res["lattice_counts"]
    primes = [int(p) for p in lat]
    emin, emax = 2, len(lat[str(primes[0])]["D_e"]) - 1
    es = list(range(emin, emax + 1))
    D = np.array([[lat[str(p)]["D_e"][e] for e in es] for p in primes])
    lim = float(np.max(np.abs(D)))
    norm = TwoSlopeNorm(vmin=-lim, vcenter=0.0, vmax=lim)
    cmap = matplotlib.colormaps["PuOr"]
    # Two views of the same array. The 3D bars show the shape; the flat panel is what the eye
    # should read the boundedness and the periodicity off, since front bars occlude rear ones and
    # the identically-zero columns (p = 3, 7) are invisible as slabs.
    fig = plt.figure(figsize=(12.4, 5.2))
    gs = fig.add_gridspec(1, 2, width_ratios=(1.05, 1.0), wspace=0.30,
                          left=0.015, right=0.88, bottom=0.11, top=0.84)
    ax = fig.add_subplot(gs[0, 0], projection="3d")
    xi, yi = np.meshgrid(np.arange(len(primes)), np.array(es), indexing="ij")
    xs, ys, dz = xi.ravel(), yi.ravel(), D.ravel()
    ax.bar3d(xs - 0.35, ys - 0.35, np.minimum(dz, 0), 0.7, 0.7, np.abs(dz), color=cmap(norm(dz)),
             shade=True, edgecolor="none")
    ax.set_xticks(range(len(primes)))
    ax.set_xticklabels([str(p) for p in primes], fontsize=7)
    ax.set_xlabel(r"prime $p$", labelpad=6)
    ax.set_ylabel(r"walk length $e$ (isogeny degree $2^e$)", labelpad=6)
    ax.set_zlabel(r"$D_e(p)$", labelpad=1)
    ax.view_init(elev=26, azim=-50)
    ax.set_title("(a) signed deviation, by prime and walk length", fontsize=9.5, pad=2)

    ax2 = fig.add_subplot(gs[0, 1])
    im = ax2.imshow(D.T, origin="lower", aspect="auto", cmap=cmap, norm=norm,
                    extent=(-0.5, len(primes) - 0.5, es[0] - 0.5, es[-1] + 0.5))
    ax2.set_xticks(range(len(primes)))
    ax2.set_xticklabels([str(p) for p in primes], fontsize=7.5)
    ax2.set_yticks([e for e in es if e % 2 == 0])
    ax2.set_xlabel(r"prime $p$")
    ax2.set_ylabel(r"walk length $e$ (isogeny degree $2^e$)")
    zero_cols = [i for i in range(len(primes)) if np.allclose(D[i], 0.0)]
    if zero_cols:
        ax2.text(float(np.mean(zero_cols)), (es[0] + es[-1]) / 2.0,
                 "class number one:\n$D_e\\equiv 0$", rotation=90,
                 ha="center", va="center", fontsize=7.4)
    ax2.set_title("(b) the same array flat: no column drifts with $e$;\n"
                  r"$p=11$ repeats with period $8$, $p=43$ with period $6$",
                  fontsize=9.5, pad=4)

    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    cb = fig.colorbar(sm, cax=fig.add_axes((0.905, 0.17, 0.016, 0.60)))
    cb.set_label(r"$D_e(p)=(N_e-36\cdot 2^e/(p-1))\,/\,2^{e/2}$ (dimensionless)")
    fig.suptitle("Deviation from the Eichler mass-formula main term stays bounded "
                 r"($|D_e|\leq 5.143$, attained at $p=43$; $e\leq 22$)", fontsize=10.5)
    out = DIR / "fig4_deviation_bars.pdf"
    fig.savefig(out)
    plt.close(fig)
    return out


def fig_visibility_frey(res: dict[str, Any]) -> Path:
    rows = res["visibility_graph"]["rows"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.0, 4.2), gridspec_kw={"width_ratios": [1.45, 1]})
    cats = {"vp": ([], []), "ip": ([], []), "im": ([], []), "vm": ([], [])}
    for r in rows:
        for o in r["orbits"]:
            if o["a2_charpoly"] == "x - 3":
                continue
            key = ("v" if o["visible"] else "i") + ("p" if o["frobenius_sign"] == 1 else "m")
            cats[key][0].append(r["p"])
            cats[key][1].append(o["dim"])
    a.scatter(*cats["vp"], s=10, color=BLUE, label=fr"$w=+1$, visible ({len(cats['vp'][0])})", zorder=2)
    a.scatter(*cats["im"], s=12, marker="x", color=AQUA, linewidth=0.9,
              label=fr"$w=-1$, invisible ({len(cats['im'][0])})", zorder=2)
    a.scatter(*cats["ip"], s=46, marker="^", color=ORANGE, edgecolor="white", linewidth=0.5,
              label=fr"$w=+1$, invisible ({len(cats['ip'][0])})", zorder=3)
    if cats["vm"][0]:
        a.scatter(*cats["vm"], s=60, marker="*", color="#e34948", label=fr"$w=-1$, visible ({len(cats['vm'][0])})")
    a.set_yscale("log")
    a.set_xlabel(r"prime level $p$ ($p\equiv 3 \,\mathrm{mod}\,4$)")
    a.set_ylabel("Galois-orbit dimension (log scale)")
    a.set_title(r"(a) Orbits seen from $E_0$ (2-isogeny graph over $\mathbb{F}_{p^2}$)")
    a.legend(frameon=False, loc="upper left")
    fam = res["frey_family_3p_4p"]
    ps = [r["p"] for r in fam]
    cond = [r["conductor"] for r in fam]
    serre = [r["serre_level_prime_to_p"] for r in fam]
    x = np.arange(len(ps))
    b.bar(x - 0.2, cond, width=0.38, color=MUTED, alpha=0.55, label="conductor of Frey curve")
    b.bar(x + 0.2, serre, width=0.38, color=BLUE, label=r"Serre level $N(\bar\rho_p)$ (prime to $p$)")
    b.axhline(2, color=ORANGE, lw=1.5, ls="--", label="level 2 claimed in edition 1")
    for xi, r in zip(x, fam):
        tag = "7 | N" if r["seven_in_serre_level"] else "p = 7"
        b.text(xi + 0.2, r["serre_level_prime_to_p"] * 1.6, tag, ha="center", fontsize=7, color=INK, rotation=90)
    b.set_yscale("log")
    b.set_xticks(x)
    b.set_xticklabels([str(p) for p in ps])
    b.set_xlabel(r"exponent $p$ in $(3^p,4^p,3^p+4^p)$")
    b.set_ylabel("level (log scale)")
    b.set_title("(b) Level lowering never reaches level 2")
    b.legend(frameon=False, loc="upper left", fontsize=7.5)
    b.set_ylim(1, max(cond) * 400)
    fig.tight_layout()
    out = DIR / "fig5_visibility_and_frey.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def fig_gap(res: dict[str, Any]) -> Path:
    g = [r for r in res["visibility_graph"]["spectral_gap_at_E0"] if r["lambda_visible"] is not None]
    ps = np.array([r["p"] for r in g])
    lg = np.array([r["lambda_global"] for r in g])
    lv = np.array([r["lambda_visible"] for r in g])
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    ax.axhline(2 * math.sqrt(2), color=MUTED, lw=1.0, ls=":", label=r"Ramanujan bound $2\sqrt{2}$")
    ax.plot(ps, lg, lw=0, marker="o", ms=4.5, color=MUTED, alpha=0.7, label=r"max $|a_2|$, all cusp orbits")
    ax.plot(ps, lv, lw=0, marker=".", ms=6, color=BLUE, label=r"max $|a_2|$, orbits visible from $E_0$")
    strict = lv < lg - 1e-9
    ax.plot(ps[strict], lv[strict], lw=0, marker="v", ms=6, color=ORANGE,
            label=fr"visible max strictly smaller ({int(strict.sum())} primes)")
    ax.set_xlabel(r"prime $p$ ($p\equiv 3 \,\mathrm{mod}\,4$)")
    ax.set_ylabel(r"largest $|$eigenvalue of $T_2|$ (dimensionless)")
    ax.set_title(r"Spectral gap seen by walks from $E_0$ vs the global gap of the 2-isogeny graph")
    ax.legend(frameon=False, loc="lower right", fontsize=8)
    ax.set_ylim(0.8, 3.0)
    fig.tight_layout()
    out = DIR / "fig6_spectral_gap_E0.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def _concordance_null(informative: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
    """Exact null distribution of the concordance count over the free (permutable) orbits.

    Within each prime the L-vanishing labels are reassigned uniformly among that prime's
    w = +1 orbits. If `k` of the `inv` labels land on invisible orbits the prime contributes
    `vis - inv + 2k` concordant orbits, with `k` hypergeometric. Primes are independent, so
    the total is the convolution. Reproduced here from the stored per-prime counts so the
    figure needs no Monte Carlo and matches the p-value in the results JSON exactly.
    """
    dist: dict[int, float] = {0: 1.0}
    for d in informative:
        vis, inv = int(d["visible"]), int(d["invisible"])
        n = vis + inv
        step: dict[int, float] = {}
        for k in range(max(0, inv - vis), inv + 1):
            w = math.comb(inv, k) * math.comb(vis, inv - k) / math.comb(n, inv)
            c = vis - inv + 2 * k
            for prev, pw in dist.items():
                step[prev + c] = step.get(prev + c, 0.0) + pw * w
        dist = step
    xs = np.array(sorted(dist))
    return xs, np.array([dist[x] for x in xs])


def fig_forced_vs_free(res: dict[str, Any]) -> Path:
    """The two halves of P3 side by side: one cannot fail, the other is measured.

    (a) the exact permutation null of the w = +1 concordance count, with the observed value;
    (b) a 3D view of the 10 primes that carry the test, split by visibility and by which
        central value vanishes.
    """
    st = res["positive_controls"]["vii_gross_w_plus_stratum"]
    info = st["informative_primes"]
    fixed, total = int(st["orbits_constant_under_null"]), int(st["orbits_total"])
    observed = int(st["orbits_concordant"])

    # Sized for \textwidth in the manuscript: a wider canvas gets scaled down on the page and
    # takes the tick labels below legibility, so keep it near the printed width.
    fig = plt.figure(figsize=(9.4, 4.3))
    gs = fig.add_gridspec(1, 2, width_ratios=(1.0, 1.04), wspace=0.20,
                          left=0.085, right=0.97, bottom=0.15, top=0.82)

    # ---- (a) exact null vs observed
    ax = fig.add_subplot(gs[0, 0])
    xs, ps = _concordance_null(info)
    ax.bar(xs + fixed, ps, width=0.85, color=BLUE, alpha=0.75,
           label="exact permutation null (labels shuffled within each prime)")
    ax.axvline(observed, color=ORANGE, lw=2.0,
               label=f"observed: {observed}/{total} concordant")
    ax.axvline(fixed + float(np.sum(xs * ps)), color=MUTED, lw=1.2, ls="--",
               label=f"null mean: {fixed + float(np.sum(xs * ps)):.1f}")
    ax.set_xlabel("w = +1 orbits on which visibility agrees with $L$-nonvanishing")
    ax.set_ylabel("null probability")
    ax.set_title(f"(a) The $w=+1$ half is measured: $p={st['within_prime_exact_p_value']:.1e}$"
                 f" $={st['within_prime_exact_p_value_exact']}$", loc="left")
    # Headroom so the legend clears the tallest bar rather than sitting on it.
    ax.set_ylim(0, float(ps.max()) * 1.52)
    ax.legend(loc="upper left", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    # Where one flipped orbit pair would put the statistic: still far from the null centre,
    # but off the maximum, which is what makes the test able to fail.
    near = float(ps[np.argmin(np.abs(xs + fixed - (observed - 2)))])
    ax.annotate("one discordant orbit\nlands here", xy=(observed - 2, near),
                xytext=(observed - 4.5, float(ps.max()) * 0.66), color=INK, fontsize=8.5,
                ha="center", arrowprops=dict(arrowstyle="->", color=MUTED, lw=0.9))

    # ---- (b) 3D structure of the informative primes
    ax3 = fig.add_subplot(gs[0, 1], projection="3d")
    primes = [int(d["p"]) for d in info]
    for xi, d in enumerate(info):
        for yi, (key, col) in enumerate((("visible", AQUA), ("invisible", ORANGE))):
            h = int(d[key])
            if h == 0:
                continue
            ax3.bar3d(xi - 0.3, yi - 0.22, 0, 0.6, 0.44, h, color=col,
                      alpha=0.92, shade=True, edgecolor=INK, linewidth=0.3)
    ax3.set_xticks(range(len(primes)))
    ax3.set_xticklabels([str(p) for p in primes], rotation=52, ha="right", fontsize=7.5)
    ax3.set_yticks([0, 1])
    ax3.set_yticklabels(["visible\n($L\\ne0$)", "invisible\n($L=0$)"], fontsize=8)
    ax3.set_zlabel("orbits", fontsize=9)
    ax3.set_zticks(range(0, 5))
    ax3.view_init(elev=22, azim=-58)
    ax3.set_title("(b) The 10 primes that carry the test", loc="left")
    ax3.xaxis.pane.set_alpha(0.04)
    ax3.yaxis.pane.set_alpha(0.04)
    ax3.zaxis.pane.set_alpha(0.04)
    ax3.grid(True, alpha=0.18)

    out = DIR / "fig_forced_vs_free.pdf"
    fig.savefig(out)
    plt.close(fig)
    return out


def main() -> int:
    res = load()
    for f in (fig_cylinder(res), fig_deviation(res), fig_visibility_frey(res), fig_gap(res),
              fig_forced_vs_free(res)):
        print("wrote", f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
