"""Five figures for the five re-exported theorems of `formal_cert/Programmes/Famille/Acronymes.lean`.

Every plotted quantity is computed here from its defining formula; nothing is hand-entered.
Each figure comes with numeric self-checks (positive and negative controls). A failing check
raises AssertionError and no figure is written for it.

  ALIX    Gaussian lattice energy (theta sums) over the shape fundamental domain; minimum at e^{i pi/3}.
  KAL     P^n(i, N) for neutral Wright-Fisher (exact matrix powers) -> i/N; Moran (1 - r^-i)/(1 - r^-N).
  ILENE   Exact birth-death fixation probabilities on an isothermal graph vs a star.
  ALEXIS  Rytova-Keldysh potential as a positive mixture of Gaussians; signs of (-1)^n g^(n).
  AURELIA Mean fitness under haploid selection (simplex) and the Hardy-Weinberg diploid case.

Usage:
  .venv/bin/python -I papers/textbook_formalisation_2026/code/easter_egg_images.py [--only NAME ...]
Outputs: papers/textbook_formalisation_2026/figures/egg_{NAME}.{pdf,png} and
         results/textbook_formalisation_2026/easter_eggs_selfcheck.json
"""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Callable, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, LogNorm, Normalize  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Polygon  # noqa: E402
from scipy import integrate, optimize, special  # noqa: E402
from scipy.spatial import Voronoi  # noqa: E402

HERE = Path(__file__).resolve().parent
FIGDIR = HERE.parent / "figures"
REPO = HERE.parents[2]
CHECK_JSON = REPO / "results" / "textbook_formalisation_2026" / "easter_eggs_selfcheck.json"

# ---------------------------------------------------------------- style
INK = "#1f2430"
INK2 = "#5b6170"
MUTED = "#9aa0ab"
GRID = "#e4e2dc"
PAPER = "#fbfaf7"
# Okabe-Ito categorical order (colour-blind safe), fixed order.
OI = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9"]
# One sequential hue (deep blue), light -> dark.
SEQ = LinearSegmentedColormap.from_list(
    "egg_seq", ["#f6f3ea", "#cfe0ea", "#8fb9d3", "#4a8bb8", "#1d5e95", "#0b3560"])
# Second sequential hue (amber), used where two magnitudes must not be confused.
SEQ2 = LinearSegmentedColormap.from_list(
    "egg_seq2", ["#fbf4e4", "#f6dca6", "#eab65e", "#d08a1e", "#9a5b07"])


def set_style() -> None:
    plt.rcParams.update({
        "font.family": "STIXGeneral",
        "mathtext.fontset": "stix",
        "font.size": 9.5,
        "axes.titlesize": 10.5,
        "axes.labelsize": 9.5,
        "axes.edgecolor": INK2,
        "axes.labelcolor": INK,
        "axes.linewidth": 0.6,
        "axes.facecolor": PAPER,
        "figure.facecolor": PAPER,
        "savefig.facecolor": PAPER,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "xtick.major.width": 0.5,
        "ytick.major.width": 0.5,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "text.color": INK,
        "legend.frameon": False,
        "legend.fontsize": 8.5,
        "pdf.fonttype": 42,
    })


def tidy(ax: plt.Axes, grid: bool = True) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    if grid:
        ax.grid(True, color=GRID, lw=0.5, zorder=0)
        ax.set_axisbelow(True)


def bare(ax: plt.Axes) -> None:
    ax.set_axis_off()
    ax.set_aspect("equal")


def panel_tag(ax: plt.Axes, tag: str, x: float = -0.10) -> None:
    ax.text(x, 1.02, tag, transform=ax.transAxes, fontsize=10.5, fontweight="bold",
            color=INK, ha="right", va="bottom")


def footer(fig: plt.Figure, text: str) -> None:
    fig.text(0.01, -0.035, text, fontsize=7.5, color=INK2, ha="left", va="top")


def monogram(fig: plt.Figure, word: str) -> None:
    spaced = " ".join(word)
    fig.text(0.992, -0.03, spaced, ha="right", va="top", fontsize=7.5, color=MUTED,
             fontstyle="italic",
             bbox=dict(boxstyle="round,pad=0.35,rounding_size=0.6", fc="none", ec=MUTED, lw=0.5))


def save(fig: plt.Figure, name: str) -> list[str]:
    FIGDIR.mkdir(parents=True, exist_ok=True)
    out = []
    for ext, kw in (("pdf", {"metadata": {"CreationDate": None, "Creator": "easter_egg_images.py"}}),
                    ("png", {"dpi": 300})):
        p = FIGDIR / f"egg_{name}.{ext}"
        fig.savefig(p, bbox_inches="tight", pad_inches=0.06, **kw)
        out.append(str(p.relative_to(REPO)))
    plt.close(fig)
    return out


# ================================================================ ALIX
def lattice_energy(x: np.ndarray, y: np.ndarray, alpha: float, M: int = 18) -> np.ndarray:
    """E(tau) = sum_{(m,n) != 0} exp(-pi alpha |m + n tau|^2 / Im tau): Gaussian energy per point of the
    covolume-1 lattice of shape tau = x + i y (density 1)."""
    m = np.arange(-M, M + 1)
    mm, nn = np.meshgrid(m, m, indexing="ij")
    keep = (mm != 0) | (nn != 0)
    mm = mm[keep].astype(float)
    nn = nn[keep].astype(float)
    xs = np.asarray(x, float)[..., None]
    ys = np.asarray(y, float)[..., None]
    q = ((mm + nn * xs) ** 2 + (nn * ys) ** 2) / ys
    return np.exp(-np.pi * alpha * q).sum(axis=-1)


def reduce_modular(x: float, y: float) -> tuple[float, float]:
    """Map tau to the standard fundamental domain |Re| <= 1/2, |tau| >= 1, then fold Re >= 0."""
    t = complex(x, y)
    for _ in range(200):
        t = complex(t.real - round(t.real), t.imag)
        if abs(t) < 1 - 1e-15:
            t = -1 / t
        else:
            break
    return abs(t.real), t.imag


def lattice_points(x: float, y: float, R: float) -> np.ndarray:
    b1 = np.array([1.0, 0.0]) / math.sqrt(y)
    b2 = np.array([x, y]) / math.sqrt(y)
    K = int(R * 2 / min(np.linalg.norm(b1), y / math.sqrt(y))) + 3
    pts = [m * b1 + n * b2 for m in range(-K, K + 1) for n in range(-K, K + 1)]
    P = np.array(pts)
    return P[np.linalg.norm(P, axis=1) <= R]


def fig_alix(checks: dict) -> list[str]:
    alpha = 0.4
    rho = (0.5, math.sqrt(3) / 2)
    sq = (0.0, 1.0)
    E_tri = float(lattice_energy(np.array(rho[0]), np.array(rho[1]), alpha))
    E_sq = float(lattice_energy(np.array(sq[0]), np.array(sq[1]), alpha))
    # independent check of E_tri from explicit points (direct sum over a disc)
    P = lattice_points(*rho, R=14.0)
    r2 = (P ** 2).sum(1)
    E_tri_direct = float(np.exp(-np.pi * alpha * r2[r2 > 1e-12]).sum())
    assert abs(E_tri - E_tri_direct) < 1e-12, (E_tri, E_tri_direct)

    # landscape over the fundamental domain
    gx = np.linspace(-0.5, 0.5, 321)
    gy = np.linspace(0.84, 1.75, 321)
    X, Y = np.meshgrid(gx, gy)
    E = lattice_energy(X, Y, alpha)
    inside = X ** 2 + Y ** 2 >= 1.0 - 1e-12
    Ein = np.where(inside, E, np.nan)
    i_min = np.nanargmin(Ein)
    xmin, ymin = X.flat[i_min], Y.flat[i_min]
    step = max(gx[1] - gx[0], gy[1] - gy[0])
    assert min(math.hypot(xmin - rho[0], ymin - rho[1]),
               math.hypot(xmin + rho[0], ymin - rho[1])) < 1.5 * step
    assert np.nanmin(Ein) >= E_tri - 1e-12
    # continuous minimisation from several starts, reduced to the fundamental domain
    found = []
    for s in [(0.05, 1.6), (0.3, 1.2), (-0.2, 1.05), (0.45, 1.5), (0.0, 1.0)]:
        res = optimize.minimize(lambda v: float(lattice_energy(np.array(v[0]), np.array(abs(v[1]) + 1e-9),
                                                               alpha)),
                                np.array(s), method="Nelder-Mead",
                                options={"xatol": 1e-11, "fatol": 1e-15, "maxiter": 4000})
        fx, fy = reduce_modular(res.x[0], abs(res.x[1]))
        found.append((fx, fy))
        assert math.hypot(fx - rho[0], fy - rho[1]) < 1e-5, (s, fx, fy)
    # every density: E_sq / E_tri > 1 for a range of alpha (density rho <-> alpha / rho)
    alphas = np.geomspace(0.15, 6.0, 60)
    ratio = np.array([float(lattice_energy(np.array(0.0), np.array(1.0), a, M=30)) /
                      float(lattice_energy(np.array(rho[0]), np.array(rho[1]), a, M=30)) for a in alphas])
    assert np.all(ratio > 1.0)
    # negative control: the square lattice is not a minimiser (positive gap)
    assert E_sq - E_tri > 1e-3
    checks["ALIX"] = {
        "alpha": alpha, "E_triangular": E_tri, "E_triangular_direct_sum": E_tri_direct,
        "E_square": E_sq, "grid_argmin": [float(xmin), float(ymin)], "grid_step": float(step),
        "nelder_mead_minima_reduced": found, "ratio_sq_over_tri_min_over_alpha": float(ratio.min()),
        "alpha_range": [float(alphas[0]), float(alphas[-1])],
    }

    # ---------- figure
    fig = plt.figure(figsize=(11.2, 3.45))
    gs = fig.add_gridspec(1, 5, width_ratios=[1, 1, 0.045, 0.32, 1.32], wspace=0.08)
    axT, axS, axL = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[0, 4])
    axC = fig.add_subplot(gs[0, 2])
    axC.set_box_aspect(18)
    norm = LogNorm(vmin=1e-4, vmax=1.0)
    R = 3.6
    for ax, shape, title, Eval in ((axT, rho, "triangulaire", E_tri), (axS, sq, "carré", E_sq)):
        pts = lattice_points(*shape, R=R + 3.0)
        vor = Voronoi(pts)
        for k, p in enumerate(pts):
            if np.linalg.norm(p) > R:
                continue
            reg = vor.regions[vor.point_region[k]]
            if -1 in reg or len(reg) == 0:
                continue
            poly = vor.vertices[reg]
            d2 = float((p ** 2).sum())
            if d2 < 1e-12:
                ax.add_patch(Polygon(poly, closed=True, fc="#ffffff", ec=INK, lw=0.9, zorder=3))
                ax.plot(*p, "o", ms=4.2, color=OI[3], zorder=4)
                continue
            c = SEQ(norm(math.exp(-math.pi * alpha * d2)))
            ax.add_patch(Polygon(poly, closed=True, fc=c, ec=PAPER, lw=1.1, zorder=2))
            ax.plot(*p, "o", ms=1.6, color=INK, alpha=0.55, zorder=3)
        circ = plt.Circle((0, 0), R, fill=False, ec=MUTED, lw=0.4, ls=(0, (2, 3)))
        ax.add_patch(circ)
        ax.set_xlim(-R - 0.4, R + 0.4)
        ax.set_ylim(-R - 0.4, R + 0.4)
        bare(ax)
        ax.set_title(f"réseau {title}, densité 1", color=INK, pad=4)
        ax.text(0, -R - 0.75, rf"$E_\alpha = {Eval:.5f}$", ha="center", va="top", fontsize=10, color=INK)
    panel_tag(axT, "a", x=0.02)
    panel_tag(axS, "b", x=0.02)
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=SEQ), cax=axC)
    cb.outline.set_linewidth(0.4)
    cb.set_label(r"contribution $e^{-\pi\alpha|p|^2}$ au site central", fontsize=8.5)
    cb.ax.tick_params(labelsize=7.5)

    # landscape
    gap = np.where(inside, E - E_tri, np.nan)
    lvl = np.geomspace(1e-4, np.nanmax(gap), 40)
    cs = axL.contourf(X, Y, np.clip(gap, 1e-4, None), levels=lvl, cmap=SEQ2.reversed(), norm=LogNorm())
    axL.contour(X, Y, np.clip(gap, 1e-4, None), levels=lvl[::4], colors=[PAPER], linewidths=0.35)
    th = np.linspace(math.pi / 3, 2 * math.pi / 3, 200)
    axL.plot(np.cos(th), np.sin(th), color=INK2, lw=0.7)
    axL.plot([-0.5, -0.5], [rho[1], gy[-1]], color=INK2, lw=0.7)
    axL.plot([0.5, 0.5], [rho[1], gy[-1]], color=INK2, lw=0.7)
    axL.fill_between(np.linspace(-0.5, 0.5, 200), 0.8, np.sqrt(1 - np.linspace(-0.5, 0.5, 200) ** 2),
                     color=PAPER, zorder=2)
    for sx in (-1, 1):
        axL.plot(sx * rho[0], rho[1], marker="*", ms=13, color=OI[3], mec=PAPER, mew=0.8, zorder=5)
    axL.plot(*sq, marker="s", ms=6, color=OI[0], mec=PAPER, mew=0.8, zorder=5)
    axL.annotate(r"$\tau=e^{i\pi/3}$" + "\nminimum", xy=rho, xytext=(0.19, 0.93), fontsize=9, color=INK,
                 arrowprops=dict(arrowstyle="-", color=INK2, lw=0.5), zorder=6)
    axL.annotate(r"$\tau=i$ (carré)", xy=sq, xytext=(-0.43, 1.06), fontsize=9, color=INK,
                 arrowprops=dict(arrowstyle="-", color=INK2, lw=0.5), zorder=6)
    axL.set_xlim(-0.56, 0.56)
    axL.set_ylim(0.84, 1.75)
    axL.set_aspect("equal")
    tidy(axL, grid=False)
    axL.set_xlabel(r"$\mathrm{Re}\,\tau$")
    axL.set_ylabel(r"$\mathrm{Im}\,\tau$")
    axL.set_title(r"$E_\alpha(\tau)-E_\alpha(e^{i\pi/3})$ sur le domaine fondamental", pad=4)
    panel_tag(axL, "c")
    cbl = fig.colorbar(cs, ax=axL, fraction=0.045, pad=0.02, ticks=[1e-4, 1e-3, 1e-2, 1e-1, 1])
    cbl.outline.set_linewidth(0.4)
    cbl.ax.tick_params(labelsize=7.5)
    # inset: every density
    ins = axL.inset_axes([0.50, 0.56, 0.44, 0.36])
    ins.loglog(alphas, ratio - 1, color=OI[0], lw=1.4)
    ins.set_xticks([0.2, 0.5, 1, 2, 5])
    ins.set_xticklabels(["0.2", "0.5", "1", "2", "5"])
    ins.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ins.axvline(alpha, color=OI[3], lw=0.6, ls=(0, (2, 2)))
    ins.set_facecolor("#ffffffdd")
    ins.tick_params(labelsize=6.5, length=1.8)
    for s in ins.spines.values():
        s.set_linewidth(0.4)
        s.set_color(MUTED)
    ins.set_xlabel(r"$\alpha$ (échelle $\leftrightarrow$ densité)", fontsize=6.8, labelpad=1)
    ins.set_title(r"$E_{\mathrm{carré}}/E_{\mathrm{tri}}-1>0$", fontsize=7.5, pad=2)
    footer(fig, rf"noyau gaussien $h(r^2)=e^{{-\pi\alpha r^2}}$, $\alpha={alpha}$ ; "
             r"sommes thêta $\Sigma_{(m,n)\neq 0}\, e^{-\pi\alpha|m+n\tau|^2/\mathrm{Im}\,\tau}$")
    monogram(fig, "ALIX")
    return save(fig, "ALIX")


# ================================================================ KAL
def wright_fisher(N: int) -> np.ndarray:
    i = np.arange(N + 1)[:, None] / N
    j = np.arange(N + 1)[None, :]
    return special.comb(N, j) * i ** j * (1 - i) ** (N - j)


def moran(N: int, r: float) -> np.ndarray:
    P = np.zeros((N + 1, N + 1))
    P[0, 0] = P[N, N] = 1.0
    for i in range(1, N):
        F = r * i + (N - i)
        up = r * i / F * (N - i) / N
        dn = (N - i) / F * i / N
        P[i, i + 1], P[i, i - 1], P[i, i] = up, dn, 1 - up - dn
    return P


def moran_fix(i: int, N: int, r: float) -> float:
    return (1 - r ** (-i)) / (1 - r ** (-N))


def fig_kal(checks: dict) -> list[str]:
    N = 24
    P = wright_fisher(N)
    assert np.allclose(P.sum(1), 1, atol=1e-13)
    h = np.arange(N + 1) / N
    assert np.max(np.abs(P @ h - h)) < 1e-13  # harmonic
    # exact harmonicity in rationals (small N)
    Nq = 8
    for i in range(Nq + 1):
        s = sum(Fraction(math.comb(Nq, j)) * Fraction(i, Nq) ** j * (1 - Fraction(i, Nq)) ** (Nq - j) * Fraction(j, Nq)
                for j in range(Nq + 1))
        assert s == Fraction(i, Nq)
    nmax = 160
    H = np.zeros((N + 1, nmax + 1))
    Pn = np.eye(N + 1)
    for n in range(nmax + 1):
        H[:, n] = Pn[:, N]
        Pn = Pn @ P
    Pbig = np.linalg.matrix_power(P, 4096)
    err_wf = float(np.max(np.abs(Pbig[:, N] - h)))
    err_wf0 = float(np.max(np.abs(Pbig[:, 0] - (1 - h))))
    assert err_wf < 1e-10 and err_wf0 < 1e-10

    r = 1.25
    M = moran(N, r)
    hm = np.array([moran_fix(i, N, r) for i in range(N + 1)])
    assert np.max(np.abs(M @ hm - hm)) < 1e-14
    # exact rationals: harmonicity of (1 - r^-i)/(1 - r^-N), r = 5/4
    rq = Fraction(5, 4)
    hq = [(1 - rq ** (-i)) / (1 - rq ** (-N)) for i in range(N + 1)]
    for i in range(1, N):
        F = rq * i + (N - i)
        up = rq * i / F * Fraction(N - i, N)
        dn = Fraction(N - i) / F * Fraction(i, N)
        assert up * hq[i + 1] + dn * hq[i - 1] + (1 - up - dn) * hq[i] == hq[i]
    ns = np.unique(np.geomspace(1, 3.0e4, 500).astype(int))
    track = [1, 2, 4, 8, 16]
    curves = {i: [] for i in track}
    v = np.eye(N + 1)
    Mn = np.eye(N + 1)
    last = 0
    for n in ns:
        Mn = Mn @ np.linalg.matrix_power(M, int(n - last))
        last = n
        for i in track:
            curves[i].append(Mn[i, N])
    Mbig = np.linalg.matrix_power(M, 2 ** 22)
    err_m = float(np.max(np.abs(Mbig[:, N] - hm)))
    assert err_m < 1e-10
    # negative control: the neutral value i/N is not the Moran limit
    neg = float(np.max(np.abs(Mbig[:, N] - h)))
    assert neg > 0.05
    checks["KAL"] = {
        "WF_N": N, "WF_max_abs_err_P4096_iN_vs_i_over_N": err_wf, "WF_max_abs_err_P4096_i0_vs_1_minus_i_over_N": err_wf0,
        "WF_exact_rational_harmonic_N8": True,
        "Moran_N": N, "Moran_r": r, "Moran_max_abs_err_P^(2^22)_vs_formula": err_m,
        "Moran_exact_rational_harmonic_r5/4": True,
        "negative_control_neutral_vs_Moran_max_gap": neg,
    }
    del v

    fig = plt.figure(figsize=(11.2, 4.1))
    gs = fig.add_gridspec(1, 4, width_ratios=[1.25, 0.06, 0.16, 1.25], wspace=0.08)
    ax = fig.add_subplot(gs[0, 0])
    axs = fig.add_subplot(gs[0, 1], sharey=ax)
    ax2 = fig.add_subplot(gs[0, 3])
    im = ax.pcolormesh(np.arange(nmax + 2) - 0.5, np.arange(N + 2) - 0.5, H, cmap=SEQ, vmin=0, vmax=1,
                       shading="flat", edgecolors="face", linewidth=0.05)
    cl = ax.contour(np.arange(nmax + 1), np.arange(N + 1), H, levels=[0.1, 0.3, 0.5, 0.7, 0.9],
                    colors=[PAPER], linewidths=0.5)
    ax.clabel(cl, fmt="%.1f", fontsize=6.5, colors=PAPER)
    ax.set_xlabel(r"génération $n$")
    ax.set_ylabel(r"état initial $i$ (copies de l'allèle)")
    ax.set_title(r"Wright–Fisher neutre, $N=24$ : $P^n(i,N)$", pad=4)
    for s in ax.spines.values():
        s.set_linewidth(0.4)
    panel_tag(ax, "a")
    axs.pcolormesh(np.array([0.0, 1.0]), np.arange(N + 2) - 0.5, h[:, None], cmap=SEQ, vmin=0, vmax=1,
                   shading="flat", edgecolors="face", linewidth=0.05)
    axs.set_xlim(0, 1)
    axs.set_xticks([0.5])
    axs.set_xticklabels([r"$i/N$"], fontsize=9)
    axs.tick_params(axis="y", left=False, labelleft=False)
    for s in axs.spines.values():
        s.set_linewidth(0.4)
    axs.set_title(r"$n\to\infty$", fontsize=9, pad=4)
    for i, c in zip(track, OI):
        ax2.semilogx(ns, curves[i], color=c, lw=1.6, solid_capstyle="round")
        ax2.axhline(hm[i], color=c, lw=0.7, ls=(0, (3, 3)))
        ax2.text(ns[-1] * 1.35, hm[i], rf"$i={i}$ : $\frac{{1-r^{{-{i}}}}}{{1-r^{{-N}}}}={hm[i]:.4f}$",
                 color=INK, fontsize=8, va="center")
    ax2.set_xlim(1, ns[-1])
    ax2.set_ylim(-0.02, 1.0)
    ax2.set_xlabel(r"pas $n$ (échelle log)")
    ax2.set_ylabel(r"$P^n(i,N)$")
    ax2.set_title(rf"Moran avec sélection, $N={N}$, $r={r}$", pad=4)
    tidy(ax2)
    panel_tag(ax2, "b")
    footer(fig, r"puissances exactes de la matrice de transition (Chapman–Kolmogorov) ; "
             r"$h$ harmonique, $h(0)=0$, $h(N)=1$ $\Rightarrow$ $P^n(i,N)\to h(i)$")
    monogram(fig, "KAL")
    del im
    return save(fig, "KAL")


# ================================================================ ILENE
def bd_matrix(W: Sequence[Sequence[float | Fraction]], r: float | Fraction,
              one: float | Fraction) -> tuple[list[dict[int, object]], int]:
    """Birth-death configuration kernel with mu = 1 (bdK in BirthDeath.lean). States are bitmasks."""
    n = len(W)
    rows: list[dict[int, object]] = []
    for S in range(1 << n):
        fit = [r if (S >> i) & 1 else one for i in range(n)]
        F = sum(fit)
        row: dict[int, object] = {}
        for i in range(n):
            for j in range(n):
                if W[i][j] == 0:
                    continue
                c = fit[i] / F * W[i][j]
                T = S | (1 << j) if (S >> i) & 1 else S & ~(1 << j)
                row[T] = row.get(T, 0 * one) + c
        rows.append(row)
    return rows, n


def solve_fraction(A: list[list[Fraction]], b: list[Fraction]) -> list[Fraction]:
    n = len(b)
    A = [row[:] + [b[k]] for k, row in enumerate(A)]
    for c in range(n):
        p = next(k for k in range(c, n) if A[k][c] != 0)
        A[c], A[p] = A[p], A[c]
        piv = A[c][c]
        A[c] = [v / piv for v in A[c]]
        for k in range(n):
            if k != c and A[k][c] != 0:
                f = A[k][c]
                A[k] = [a - f * bb for a, bb in zip(A[k], A[c])]
    return [A[k][n] for k in range(n)]


def fixation_exact(W: list[list[Fraction]], r: Fraction) -> list[Fraction]:
    rows, n = bd_matrix(W, r, Fraction(1))
    full = (1 << n) - 1
    idx = {S: k for k, S in enumerate(range(1, full))}
    A = [[Fraction(0)] * len(idx) for _ in idx]
    b = [Fraction(0)] * len(idx)
    for S, k in idx.items():
        A[k][k] += 1
        for T, p in rows[S].items():
            if T == full:
                b[k] += p
            elif T != 0:
                A[k][idx[T]] -= p
    x = solve_fraction(A, b)
    return [x[idx[1 << v]] for v in range(n)]


def fixation_float(W: np.ndarray, r: float) -> tuple[np.ndarray, np.ndarray]:
    """Single-mutant fixation per node, by linear solve and by the limit of the matrix power."""
    rows, n = bd_matrix(W.tolist(), r, 1.0)
    full = (1 << n) - 1
    P = np.zeros((full + 1, full + 1))
    for S, row in enumerate(rows):
        for T, p in row.items():
            P[S, T] += p
    assert np.allclose(P.sum(1), 1, atol=1e-13)
    inner = list(range(1, full))
    A = np.eye(len(inner)) - P[np.ix_(inner, inner)]
    x = np.linalg.solve(A, P[inner, full])
    solve = np.array([x[(1 << v) - 1] for v in range(n)])
    Q = P.copy()
    for _ in range(60):
        Q2 = Q @ Q
        if np.max(np.abs(Q2 - Q)) < 1e-15:
            Q = Q2
            break
        Q = Q2
    power = np.array([Q[1 << v, full] for v in range(n)])
    return solve, power


def draw_graph(ax: plt.Axes, pos: np.ndarray, W: np.ndarray, vals: np.ndarray, norm: Normalize,
               labels: list[str], node_size: float, directed: bool, lw_scale: float,
               label_out: float = 0.0) -> None:
    n = len(pos)
    for i in range(n):
        for j in range(n):
            if i == j or W[i, j] <= 0:
                continue
            if directed:
                a = FancyArrowPatch(pos[i], pos[j], connectionstyle="arc3,rad=0.16", arrowstyle="-|>",
                                    mutation_scale=4 + 5 * W[i, j], lw=0.4 + lw_scale * W[i, j],
                                    color=INK2, alpha=0.30 + 0.5 * W[i, j], shrinkA=node_size * 0.55,
                                    shrinkB=node_size * 0.62, zorder=1)
            else:
                a = FancyArrowPatch(pos[i], pos[j], arrowstyle="-", lw=0.4 + lw_scale * W[i, j],
                                    color=INK2, alpha=0.55, shrinkA=0, shrinkB=0, zorder=1)
            ax.add_patch(a)
    ax.scatter(pos[:, 0], pos[:, 1], s=node_size ** 2, c=SEQ(norm(vals)), edgecolors=INK, linewidths=0.6,
               zorder=3)
    for k, (p, lab) in enumerate(zip(pos, labels)):
        if label_out:
            d = p / (np.linalg.norm(p) + 1e-12)
            q = p + label_out * d if np.linalg.norm(p) > 1e-9 else p + np.array([0, -label_out])
            ax.text(*q, lab, ha="center", va="center", fontsize=8.5, color=INK, zorder=4)
        else:
            col = PAPER if norm(vals[k]) > 0.55 else INK
            ax.text(*p, lab, ha="center", va="center", fontsize=7.5, color=col, zorder=4)
    bare(ax)


def frac_tex(q: Fraction) -> str:
    return rf"$\frac{{{q.numerator}}}{{{q.denominator}}}$"


def fig_ilene(checks: dict) -> list[str]:
    n = 8
    r = 2.0
    moran_val = (1 - 1 / r) / (1 - r ** (-n))
    # doubly stochastic W: convex combination of three derangements (Birkhoff), rational weights
    rng = np.random.default_rng(20261026)
    perms = [np.roll(np.arange(n), -1), np.roll(np.arange(n), -3)]
    while True:
        p = rng.permutation(n)
        if np.all(p != np.arange(n)):
            break
    perms.append(p)
    cw = [Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)]
    Wq = [[Fraction(0)] * n for _ in range(n)]
    for c, pm in zip(cw, perms):
        for i in range(n):
            Wq[i][int(pm[i])] += c
    for i in range(n):
        assert sum(Wq[i]) == 1 and sum(Wq[k][i] for k in range(n)) == 1
    W = np.array([[float(v) for v in row] for row in Wq])
    iso_solve, iso_power = fixation_float(W, r)
    err_iso = float(np.max(np.abs(iso_solve - moran_val)))
    err_iso_pow = float(np.max(np.abs(iso_power - moran_val)))
    assert err_iso < 1e-12 and err_iso_pow < 1e-12, (err_iso, err_iso_pow)
    # star with 7 leaves (node 0 = centre): row-stochastic, not doubly stochastic
    Ws = np.zeros((n, n))
    Ws[0, 1:] = 1 / (n - 1)
    Ws[1:, 0] = 1.0
    star_solve, star_power = fixation_float(Ws, r)
    assert np.max(np.abs(star_solve - star_power)) < 1e-12
    assert np.max(np.abs(star_solve - moran_val)) > 0.05  # negative control
    # exact n = 3
    third = Fraction(1, 3)
    half = Fraction(1, 2)
    cyc3 = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
    cyc3q = [[Fraction(v) for v in row] for row in cyc3]
    st3 = [[Fraction(0), half, half], [Fraction(1), Fraction(0), Fraction(0)], [Fraction(1), Fraction(0), Fraction(0)]]
    rq = Fraction(2)
    moran3 = (1 - 1 / rq) / (1 - rq ** -3)
    cyc_ex = fixation_exact(cyc3q, rq)
    st_ex = fixation_exact(st3, rq)
    assert moran3 == Fraction(4, 7)
    assert all(v == Fraction(4, 7) for v in cyc_ex)
    assert st_ex[0] == Fraction(5, 12) and st_ex[1] == Fraction(2, 3) and st_ex[2] == Fraction(2, 3)
    assert sum(st_ex) * third == Fraction(7, 12)
    checks["ILENE"] = {
        "n": n, "r": r, "moran": moran_val, "isothermal_W_perms": [pm.tolist() for pm in perms],
        "isothermal_W_weights": [str(c) for c in cw],
        "isothermal_fixation_per_node_solve": iso_solve.tolist(),
        "isothermal_max_abs_err_vs_moran_solve": err_iso, "isothermal_max_abs_err_vs_moran_matrix_power": err_iso_pow,
        "star8_fixation_centre_then_leaves": star_solve.tolist(),
        "exact_n3_cycle": [str(v) for v in cyc_ex], "exact_n3_star_centre_leaf_leaf": [str(v) for v in st_ex],
        "exact_n3_star_uniform_average": str(sum(st_ex) * third), "exact_n3_moran": str(moran3),
    }

    allv = np.concatenate([iso_solve, star_solve, [float(v) for v in st_ex], [4 / 7]])
    norm = Normalize(vmin=0.0, vmax=1.0)
    fig = plt.figure(figsize=(11.2, 4.6))
    gs = fig.add_gridspec(2, 5, width_ratios=[1.15, 1.15, 0.62, 0.16, 0.05], height_ratios=[1, 1],
                          wspace=0.1, hspace=0.25)
    axI = fig.add_subplot(gs[:, 0])
    axS = fig.add_subplot(gs[:, 1])
    axc3 = fig.add_subplot(gs[0, 2])
    axs3 = fig.add_subplot(gs[1, 2])
    axC = fig.add_subplot(gs[:, 4])
    ang = np.pi / 2 - 2 * np.pi * np.arange(n) / n
    pos = np.c_[np.cos(ang), np.sin(ang)]
    draw_graph(axI, pos, W, iso_solve, norm, [f"{v:.3f}" for v in iso_solve], 25, True, 1.6)
    axI.set_xlim(-1.3, 1.3)
    axI.set_ylim(-1.3, 1.3)
    axI.set_title("graphe isotherme pondéré ($W$ bistochastique)", pad=4)
    panel_tag(axI, "a", x=0.02)
    angS = np.pi / 2 - 2 * np.pi * np.arange(n - 1) / (n - 1)
    posS = np.vstack([[0, 0], np.c_[np.cos(angS), np.sin(angS)]])
    draw_graph(axS, posS, Ws, star_solve, norm, [f"{v:.3f}" for v in star_solve], 25, False, 0.6)
    axS.set_xlim(-1.3, 1.3)
    axS.set_ylim(-1.3, 1.3)
    axS.set_title("étoile (non isotherme)", pad=4)
    panel_tag(axS, "b", x=0.02)
    for ax in (axI, axS):
        ax.text(0, -1.42, rf"valeur de Moran $\frac{{1-r^{{-1}}}}{{1-r^{{-{n}}}}}={moran_val:.5f}$, $r={r:g}$",
                ha="center", va="top", fontsize=8.5, color=INK2)
    tri = np.c_[np.cos(np.pi / 2 - 2 * np.pi * np.arange(3) / 3), np.sin(np.pi / 2 - 2 * np.pi * np.arange(3) / 3)]
    draw_graph(axc3, tri, np.array(cyc3, float), np.array([float(v) for v in cyc_ex]), norm,
               [frac_tex(v) for v in cyc_ex], 13, True, 1.2, label_out=0.55)
    axc3.set_xlim(-1.6, 1.6)
    axc3.set_ylim(-1.15, 1.95)
    axc3.set_title(r"cycle $n=3$ (exact)", fontsize=9, pad=2)
    panel_tag(axc3, "c")
    st_pos = np.array([[0, 0.25], [-1.0, -0.55], [1.0, -0.55]])
    draw_graph(axs3, st_pos, np.array([[float(v) for v in row] for row in st3]),
               np.array([float(v) for v in st_ex]), norm, [frac_tex(v) for v in st_ex], 13, False, 0.6,
               label_out=0.0)
    for p, v in zip(st_pos, st_ex):
        axs3.text(p[0], p[1] + 0.42, frac_tex(v), ha="center", va="bottom", fontsize=9.5, color=INK)
    for t in list(axs3.texts)[:3]:
        t.set_visible(False)
    axs3.set_xlim(-1.6, 1.6)
    axs3.set_ylim(-1.15, 1.25)
    axs3.set_title(r"étoile $n=3$ (exact)", fontsize=9, pad=2)
    axs3.text(0, -1.05, "Moran " + frac_tex(moran3) + " ; moyenne " + frac_tex(sum(st_ex) * third),
              ha="center", va="top", fontsize=8.5, color=INK2)
    axc3.text(0, -1.05, "Moran " + frac_tex(moran3) + " partout", ha="center", va="top", fontsize=8.5,
              color=INK2)
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=SEQ), cax=axC)
    cb.outline.set_linewidth(0.4)
    cb.ax.tick_params(labelsize=7.5)
    cb.ax.axhline(moran_val, color=OI[3], lw=1.2)
    cb.ax.axhline(float(moran3), color=OI[1], lw=1.2, ls=(0, (2, 1)))
    cb.ax.text(-0.3, moran_val, rf"Moran $n={n}$", transform=cb.ax.get_yaxis_transform(), ha="right",
               va="top", fontsize=7, color=INK2)
    cb.ax.text(-0.3, float(moran3), r"Moran $n=3$", transform=cb.ax.get_yaxis_transform(), ha="right",
               va="bottom", fontsize=7, color=INK2)
    cb.set_label("probabilité de fixation d'un mutant unique", fontsize=8.5)
    del allv
    footer(fig, "naissance–mort, sélection uniforme ; probabilités exactes (système linéaire sur les "
             r"$2^n$ configurations, contrôlé par $\lim_t P^t$)")
    monogram(fig, "ILENE")
    return save(fig, "ILENE")


# ================================================================ ALEXIS
R0 = 1.0


def kel_weight(a: float | np.ndarray) -> np.ndarray:
    return special.erfcx(np.sqrt(a) / R0) / R0


def kel_struve(r: float | np.ndarray) -> np.ndarray:
    x = np.asarray(r, float) / R0
    return np.pi / (2 * R0) * (special.struve(0, x) - special.y0(x))


def kel_moment(t: float, n: int, lo: float = -np.inf, hi: float = np.inf) -> float:
    """(-1)^n g^(n)(t) restricted to a in (e^lo, e^hi): int (4a)^{-n} w(a)/(2a) e^{-t/(4a)} da, a = e^s."""
    f: Callable[[float], float] = lambda s: (float(kel_weight(math.exp(s))) / 2 *
                                             math.exp(-t / (4 * math.exp(s)) - n * math.log(4 * math.exp(s))))
    a = max(lo, -40.0)
    b = min(hi, 60.0)
    val, _ = integrate.quad(f, a, b, limit=400, epsabs=0, epsrel=1e-12)
    return val


def fig_alexis(checks: dict) -> list[str]:
    rr = np.array([0.1, 0.5, 1.0, 2.0, 5.0])
    mix = np.array([kel_moment(float(r) ** 2, 0) for r in rr])
    st = kel_struve(rr)
    rel0 = float(np.max(np.abs(mix / st - 1)))
    assert rel0 < 1e-8, rel0
    # derivative: d/dt V(sqrt t) = -int (4a)^-1 ...  vs centred difference of the Struve form
    rel1 = []
    for t in (0.25, 1.0, 4.0):
        hstep = 1e-4 * t
        fd = (kel_struve(math.sqrt(t + hstep)) - kel_struve(math.sqrt(t - hstep))) / (2 * hstep)
        rel1.append(abs(-kel_moment(t, 1) / fd - 1))
    assert max(rel1) < 1e-6, rel1
    # negative control: wrong normalisation pi/r0 differs from the mixture
    neg = float(np.min(np.abs(mix / (2 * st) - 1)))
    assert neg > 0.4
    ts = np.geomspace(0.02, 30, 90)
    orders = list(range(7))
    D = np.array([[kel_moment(float(t), k) for t in ts] for k in orders])
    assert np.all(D > 0)
    # second derivative sign by finite differences of the Struve form (independent of the mixture)
    g = lambda t: float(kel_struve(math.sqrt(t)))
    for t in (0.3, 2.0):
        hs = 1e-3 * t
        d2 = (g(t + hs) - 2 * g(t) + g(t - hs)) / hs ** 2
        assert d2 > 0 and abs(d2 / kel_moment(t, 2) - 1) < 1e-3
    # Gaussian components on log-bins in a; exact bin integrals sum to V
    edges = np.concatenate([[-np.inf], np.linspace(math.log(0.02), math.log(30.0), 11), [np.inf]])
    rgrid = np.linspace(0.04, 4.0, 160)
    comps = np.array([[kel_moment(float(r) ** 2, 0, edges[k], edges[k + 1]) for r in rgrid]
                      for k in range(len(edges) - 1)])
    Vg = kel_struve(rgrid)
    rel_sum = float(np.max(np.abs(comps.sum(0) / Vg - 1)))
    assert rel_sum < 1e-8, rel_sum
    checks["ALEXIS"] = {
        "r0": R0, "mixture_vs_struve_max_rel_err_at_r": rr.tolist(), "rel_err_n0": rel0,
        "rel_err_n1_vs_finite_difference": max(rel1), "negative_control_pi_over_r0_min_rel_gap": neg,
        "all_(-1)^n_g^(n)_positive_n0..6_on_90_t": True, "bins_sum_vs_struve_max_rel_err": rel_sum,
    }

    fig = plt.figure(figsize=(11.2, 4.1))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.35, 0.85, 1.15], wspace=0.32)
    ax = fig.add_subplot(gs[0, 0])
    axw = fig.add_subplot(gs[0, 1])
    axd = fig.add_subplot(gs[0, 2])
    nb = comps.shape[0]
    cols = [SEQ(0.18 + 0.8 * k / (nb - 1)) for k in range(nb)]
    ax.stackplot(rgrid, comps, colors=cols, edgecolor=PAPER, linewidth=0.5)
    ax.plot(rgrid, Vg, color=INK, lw=1.0)
    rdots = np.linspace(0.15, 4.0, 14)
    ax.plot(rdots, kel_struve(rdots), "o", ms=4, mfc=PAPER, mec=OI[3], mew=1.0, zorder=5)
    ax.annotate(r"$\frac{\pi}{2r_0}\left[\mathbf{H}_0-Y_0\right](r/r_0)$", xy=(rdots[2], kel_struve(rdots[2])),
                xytext=(1.05, 2.35), fontsize=10, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.5))
    ax.text(2.25, 1.0, "somme de gaussiennes\n" + r"$\frac{w(a)}{2a}\,e^{-r^2/4a}$, $a$ par tranches",
            fontsize=8.5, color=INK2, ha="left")
    ax.set_xlim(0, 4.0)
    ax.set_ylim(0, 3.6)
    ax.set_xlabel(r"$r/r_0$")
    ax.set_ylabel(r"$V(r)\cdot r_0$")
    ax.set_title(r"potentiel de Keldysh = mélange positif de gaussiennes", pad=4)
    tidy(ax)
    panel_tag(ax, "a")
    aa = np.geomspace(1e-3, 1e3, 400)
    axw.semilogx(aa, kel_weight(aa), color=INK, lw=1.3)
    for k in range(nb):
        lo = max(math.exp(edges[k]), 1e-3)
        hi = min(math.exp(edges[k + 1]), 1e3)
        m = (aa >= lo) & (aa <= hi)
        axw.fill_between(aa[m], 0, kel_weight(aa[m]), color=cols[k], lw=0)
    axw.set_ylim(0, 1.05)
    axw.set_xlim(1e-3, 1e3)
    axw.set_xlabel(r"$a$ (échelle log)")
    axw.set_title(r"poids $w(a)=\frac{1}{r_0}e^{a/r_0^2}\mathrm{erfc}\,\frac{\sqrt{a}}{r_0}>0$", pad=4)
    tidy(axw)
    panel_tag(axw, "b")
    ends = np.log10(D[:, -1])
    lab_y = ends.copy()
    for k in range(len(orders) - 2, -1, -1):  # push labels apart (>= 0.55 decade), from the bottom up
        lab_y[k] = max(lab_y[k], lab_y[k + 1] + 0.55)
    for k in orders:
        c = SEQ2(0.25 + 0.75 * k / orders[-1])
        axd.loglog(ts, D[k], color=c, lw=1.4)
        axd.text(ts[-1] * 1.25, 10 ** lab_y[k], rf"$n={k}$", fontsize=7.5, color=INK, va="center")
    axd.set_xlim(ts[0], ts[-1] * 3.4)
    axd.set_xlabel(r"$t=r^2$")
    axd.set_title(r"$(-1)^n g^{(n)}(t)>0$, $g(t)=V(\sqrt{t})$", pad=4)
    tidy(axd)
    panel_tag(axd, "c")
    # sign of g^(n) itself, read off the computed values: sgn g^(n) = (-1)^n sgn D_n
    sg = [((-1) ** k) * int(np.sign(D[k].min())) for k in orders]
    sgn = r"\ ".join([r"+" if s > 0 else r"-" for s in sg])
    axd.text(0.97, 0.96, r"signe de $g^{(n)}$, $n=0,\dots,6$ :" + "\n" + rf"${sgn}$", transform=axd.transAxes,
             fontsize=8.5, color=INK2, ha="right", va="top")
    footer(fig, r"$r_0=1$ ; intégrales de Laplace évaluées par quadrature (tol. rel. $10^{-12}$), "
             r"comparées à la forme de Struve")
    monogram(fig, "ALEXIS")
    return save(fig, "ALEXIS")


# ================================================================ AURELIA
def haploid_step(x: np.ndarray, w: np.ndarray) -> np.ndarray:
    return x * w / float(x @ w)


def diploid_step(p: float, w11: float, w12: float, w22: float) -> float:
    q = 1 - p
    wb = p * p * w11 + 2 * p * q * w12 + q * q * w22
    return p * (p * w11 + q * w12) / wb


def diploid_wbar(p: np.ndarray | float, w11: float, w12: float, w22: float) -> np.ndarray:
    q = 1 - np.asarray(p)
    return np.asarray(p) ** 2 * w11 + 2 * np.asarray(p) * q * w12 + q ** 2 * w22


def bary(x: np.ndarray) -> np.ndarray:
    V = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, math.sqrt(3) / 2]])
    return x @ V


def fig_aurelia(checks: dict) -> list[str]:
    # exact Price/Fisher identity on random rational data
    rng = np.random.default_rng(7)
    worst = Fraction(1)
    for _ in range(400):
        k = int(rng.integers(2, 7))
        nq = [Fraction(int(v)) for v in rng.integers(0, 20, k)]
        wq = [Fraction(int(a), int(b)) for a, b in zip(rng.integers(1, 40, k), rng.integers(1, 9, k))]
        N = sum(nq)
        if N == 0:
            continue
        wb = sum(a * b for a, b in zip(nq, wq)) / N
        n2 = [a * b for a, b in zip(nq, wq)]
        wb2 = sum(a * b for a, b in zip(n2, wq)) / sum(n2)
        var = sum(a * (b - wb) ** 2 for a, b in zip(nq, wq)) / N
        assert wb2 - wb == var / wb
        assert wb <= wb2
        worst = min(worst, wb2 - wb)
    w = np.array([1.0, 1.45, 1.9])
    starts = [np.array(s) for s in ([0.90, 0.08, 0.02], [0.70, 0.02, 0.28], [0.45, 0.53, 0.02],
                                    [0.15, 0.83, 0.02], [0.96, 0.02, 0.02], [0.30, 0.30, 0.40])]
    trajs = []
    for s in starts:
        x = s / s.sum()
        tr = [x]
        for _ in range(40):
            x = haploid_step(x, w)
            tr.append(x)
        T = np.array(tr)
        wb = T @ w
        assert np.all(np.diff(wb) >= -1e-15)
        trajs.append(T)
    w11, w12, w22 = 0.78, 1.0, 0.62
    pstar = (w12 - w22) / (2 * w12 - w11 - w22)
    dtraj = []
    for p0 in (0.03, 0.985):
        p = p0
        tr = [p]
        for _ in range(60):
            p = diploid_step(p, w11, w12, w22)
            tr.append(p)
        T = np.array(tr)
        assert np.all(np.diff(diploid_wbar(T, w11, w12, w22)) >= -1e-15)
        dtraj.append(T)
    assert abs(dtraj[0][-1] - pstar) < 1e-3 and abs(dtraj[1][-1] - pstar) < 1e-3
    # negative control: with a transmission bias (mutation best -> worst, rate 0.4) wbar can decrease
    x = np.array([0.01, 0.01, 0.98])
    xs = x * w / (x @ w)
    xs = xs + 0.4 * xs[2] * np.array([1.0, 0, -1.0])
    neg_drop = float(x @ w - xs @ w)
    assert neg_drop > 0.1
    checks["AURELIA"] = {
        "exact_price_identity_random_rational_cases": 400, "min_increment_wbar'-wbar": str(worst),
        "haploid_w": w.tolist(), "haploid_trajectories_nondecreasing": True,
        "diploid_w11_w12_w22": [w11, w12, w22], "diploid_pstar": pstar,
        "diploid_final_p": [float(t[-1]) for t in dtraj],
        "negative_control_mutation_bias_wbar_drop": neg_drop,
    }

    fig = plt.figure(figsize=(11.2, 4.3))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.1, 1.0], wspace=0.36)
    ax = fig.add_subplot(gs[0, 0])
    axd = fig.add_subplot(gs[0, 1])
    axt = fig.add_subplot(gs[0, 2])
    c_hap, c_d1, c_d2 = OI[0], OI[2], OI[4]
    # simplex background
    m = 120
    P, C = [], []
    for i in range(m + 1):
        for j in range(m + 1 - i):
            xb = np.array([i, j, m - i - j]) / m
            P.append(bary(xb))
            C.append(xb @ w)
    P = np.array(P)
    C = np.array(C)
    tc = ax.tripcolor(P[:, 0], P[:, 1], C, cmap=SEQ2, shading="gouraud", vmin=w.min(), vmax=w.max())
    ax.tricontour(P[:, 0], P[:, 1], C, levels=np.linspace(1.1, 1.8, 8), colors=[PAPER], linewidths=0.5)
    tri = bary(np.eye(3))
    ax.add_patch(Polygon(tri, closed=True, fill=False, ec=INK2, lw=0.7))
    for T in trajs:
        B = bary(T)
        ax.plot(B[:, 0], B[:, 1], color=INK, lw=0.7, alpha=0.8)
        ax.plot(B[:, 0], B[:, 1], "o", ms=2.6, mfc=c_hap, mec=PAPER, mew=0.35)
        ax.plot(*B[0], "o", ms=4.4, mfc=PAPER, mec=c_hap, mew=1.0)
    off = [(-0.02, -0.04), (1.02, -0.04), (0.5, math.sqrt(3) / 2 + 0.04)]
    for k in range(3):
        ax.text(*off[k], rf"$w_{k + 1}={w[k]:g}$", ha="center", va="top" if k < 2 else "bottom",
                fontsize=9, color=INK)
    ax.set_xlim(-0.08, 1.08)
    ax.set_ylim(-0.12, 1.0)
    bare(ax)
    ax.set_title(r"haploïde, 3 types : $x_i'=x_i w_i/\bar w$", pad=6)
    panel_tag(ax, "a")
    cax = ax.inset_axes([0.86, 0.50, 0.035, 0.42])
    cb = fig.colorbar(tc, cax=cax)
    cb.outline.set_linewidth(0.4)
    cb.ax.tick_params(labelsize=7)
    cb.ax.set_title(r"$\bar w$", fontsize=9, pad=3)
    pp = np.linspace(0, 1, 400)
    axd.plot(pp, diploid_wbar(pp, w11, w12, w22), color=INK, lw=1.3)
    axd.fill_between(pp, 0.55, diploid_wbar(pp, w11, w12, w22), color=SEQ2(0.18), lw=0)
    for T, c in zip(dtraj, (c_d1, c_d2)):
        wv = diploid_wbar(T, w11, w12, w22)
        axd.plot(T, wv, "o", ms=3.8, mfc=c, mec=PAPER, mew=0.4, zorder=4)
        axd.plot(T[0], wv[0], "o", ms=5, mfc=PAPER, mec=c, mew=1.1, zorder=5)
    axd.axvline(pstar, color=OI[3], lw=0.7, ls=(0, (3, 3)))
    axd.text(pstar - 0.02, 0.575,rf"$p^*=\frac{{w_{{12}}-w_{{22}}}}{{2w_{{12}}-w_{{11}}-w_{{22}}}}={pstar:.4f}$",
             color=INK, fontsize=8.5, ha="right")
    axd.text(0.03, 0.965, rf"$w_{{11}}={w11}$, $w_{{12}}={w12:g}$, $w_{{22}}={w22}$" + "\n"
             + r"$\bar w=p^2w_{11}+2pq\,w_{12}+q^2w_{22}$", fontsize=8.5, color=INK2, va="top")
    axd.set_xlim(0, 1)
    axd.set_ylim(0.55, 1.0)
    axd.set_xlabel(r"fréquence allélique $p$")
    axd.set_ylabel(r"$\bar w(p)$")
    axd.set_title("diploïde, Hardy–Weinberg (surdominance)", pad=6)
    tidy(axd)
    panel_tag(axd, "b")
    for T in trajs:
        axt.plot(np.arange(len(T)), T @ w, color=c_hap, lw=1.1, alpha=0.85)
    for T, c in zip(dtraj, (c_d1, c_d2)):
        axt.plot(np.arange(len(T)), diploid_wbar(T, w11, w12, w22), color=c, lw=1.3, ls=(0, (4, 2)))
    axt.text(42, 1.86, "haploïde (a)", color=INK, fontsize=8.5, ha="right", va="top")
    axt.text(60, 0.90, "diploïde (b)", color=INK, fontsize=8.5, ha="right", va="bottom")
    axt.set_xlim(0, 60)
    axt.set_xlabel("génération")
    axt.set_ylabel(r"$\bar w$")
    axt.set_title(r"$\bar w$ au fil des générations", pad=6)
    axt.text(58, 1.30, r"haploïde : $\bar w'-\bar w=\frac{\mathrm{Var}(w)}{\bar w}\geq 0$", fontsize=9,
             color=INK, ha="right", va="center")
    tidy(axt)
    panel_tag(axt, "c")
    footer(fig, "itérations exactes des récurrences de sélection ; identité de Price vérifiée en rationnels "
           "sur 400 cas aléatoires")
    monogram(fig, "AURELIA")
    return save(fig, "AURELIA")


# ================================================================ main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=None)
    args = ap.parse_args()
    set_style()
    makers: dict[str, Callable[[dict], list[str]]] = {
        "ALIX": fig_alix, "KAL": fig_kal, "ILENE": fig_ilene, "ALEXIS": fig_alexis, "AURELIA": fig_aurelia}
    checks: dict = {}
    if CHECK_JSON.exists():
        checks = json.loads(CHECK_JSON.read_text())
    outputs = {}
    for name, fn in makers.items():
        if args.only and name not in args.only:
            continue
        outputs[name] = fn(checks)
        print(name, "self-checks passed ->", ", ".join(outputs[name]))
    CHECK_JSON.parent.mkdir(parents=True, exist_ok=True)
    CHECK_JSON.write_text(json.dumps(checks, indent=1, default=str))
    print("self-check record:", CHECK_JSON.relative_to(REPO))


if __name__ == "__main__":
    main()
