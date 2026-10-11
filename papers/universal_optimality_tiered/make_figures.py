"""Figures for the tiered universal-optimality paper, generated from result files only.

Inputs: rusty-SUNDIALS crates/qf-yukawa-crystal/results/{figures_data/*.csv,snapshots.jsonl,main_kappa*.jsonl,
jellium/controls.jsonl}. Output: figures/*.pdf and *.png. Coordination uses the same rule as the Rust code:
neighbours within 1.35 d0, d0 = median nearest-neighbour distance.
Run: <venv>/bin/python -I make_figures.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from scipy.spatial import Voronoi, cKDTree  # noqa: E402

HERE = Path(__file__).resolve().parent
FIG = HERE / "figures"
RES = Path("/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-yukawa/crates/qf-yukawa-crystal/results")
SNAP = RES / "figures_data"
A = math.sqrt(2.0 / math.sqrt(3.0))
LX, LY = 16 * A, 9 * math.sqrt(3) * A
INK, PAPER = "#0b1020", "#f7f5ef"
PSI = LinearSegmentedColormap.from_list("psi", ["#20113a", "#5b2a86", "#c0398b", "#f28f3b", "#f9e79f"])
COORD = {5: "#2f6db3", 6: "#d9d4c7", 7: "#c8423b"}


def load(name: str) -> np.ndarray:
    return np.loadtxt(SNAP / f"{name}.csv", delimiter=",")


def jl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def periodic_neighbours(x: np.ndarray, box: tuple[float, float] | None):
    """Neighbour lists (1.35 d0 rule) and local psi6, with minimum image when box is given."""
    n = len(x)
    if box is not None:
        tree = cKDTree(np.mod(x, box), boxsize=box)
        pts = np.mod(x, box)
    else:
        tree = cKDTree(x)
        pts = x
    d, _ = tree.query(pts, k=2)
    d0 = np.median(d[:, 1])
    pairs = tree.query_ball_point(pts, 1.35 * d0)
    coord = np.zeros(n, dtype=int)
    psi = np.zeros(n)
    for i, nb in enumerate(pairs):
        nb = [j for j in nb if j != i]
        coord[i] = len(nb)
        if nb:
            dv = pts[nb] - pts[i]
            if box is not None:
                dv -= np.asarray(box) * np.round(dv / np.asarray(box))
            psi[i] = abs(np.exp(6j * np.arctan2(dv[:, 1], dv[:, 0])).mean())
    return coord, psi, d0


def voronoi_cells(x: np.ndarray, box: tuple[float, float] | None, clip_r: float | None = None):
    """Voronoi polygons of the points; periodic via a 3x3 tiling when box is given."""
    if box is not None:
        lx, ly = box
        base = np.mod(x, box)
        tiles = np.vstack([base + [i * lx, j * ly] for i in (-1, 0, 1) for j in (-1, 0, 1)])
        vor = Voronoi(tiles)
        idx = range(4 * len(x), 5 * len(x))  # the (0, 0) tile
        offset = 4 * len(x)
    else:
        far = 4 * (np.abs(x).max() + 1)
        ring = np.array([[far * math.cos(t), far * math.sin(t)] for t in np.linspace(0, 2 * math.pi, 24, endpoint=False)])
        vor = Voronoi(np.vstack([x, ring]))
        idx = range(len(x))
        offset = 0
    polys = []
    for i in idx:
        reg = vor.regions[vor.point_region[i]]
        if -1 in reg or not reg:
            polys.append(None)
            continue
        poly = vor.vertices[reg]
        if clip_r is not None and np.max(np.hypot(poly[:, 0], poly[:, 1])) > clip_r:
            polys.append(None)
            continue
        polys.append(poly)
    return polys, offset


def draw_psi(ax, x, box, title=None, clip_r=None):
    coord, psi, _ = periodic_neighbours(x, box)
    if box is not None:
        # Draw the cells of all nine periodic copies so cells crossing the box edge are complete (no cropped gaps);
        # each copy carries the order parameter of its base particle, and the axes clip to the box.
        lx, ly = box
        base = np.mod(x, box)
        tiles = np.vstack([base + [i * lx, j * ly] for i in (-1, 0, 1) for j in (-1, 0, 1)])
        vor = Voronoi(tiles)
        polys, vals = [], []
        for t in range(len(tiles)):
            reg = vor.regions[vor.point_region[t]]
            if reg and -1 not in reg:
                poly = vor.vertices[reg]
                if poly[:, 0].max() > -1 and poly[:, 0].min() < lx + 1 and poly[:, 1].max() > -1 and poly[:, 1].min() < ly + 1:
                    polys.append(poly)
                    vals.append(psi[t % len(x)])
        pc = PolyCollection(polys, array=np.asarray(vals), cmap=PSI, edgecolors=INK, linewidths=0.35)
    else:
        polys, _ = voronoi_cells(x, box, clip_r)
        keep = [i for i, p in enumerate(polys) if p is not None]
        pc = PolyCollection([polys[i] for i in keep], array=psi[keep], cmap=PSI, edgecolors=INK, linewidths=0.35)
    pc.set_clim(0, 1)
    ax.add_collection(pc)
    defect = coord != 6
    pts = np.mod(x, box) if box is not None else x
    ax.scatter(pts[defect, 0], pts[defect, 1], s=7, c=[COORD.get(c, "#ffffff") for c in coord[defect]], zorder=3,
               edgecolors="white", linewidths=0.3)
    if box is not None:
        ax.set_xlim(0, box[0])
        ax.set_ylim(0, box[1])
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, color=PAPER, fontsize=9, pad=4)
    return pc, int(defect.sum())


def cover() -> None:
    """Cover: OC20-derived disorder -> T=0 quench (defects) -> anneal + CVODE quench (perfect triangular lattice)."""
    snaps = {r["name"]: r["e_per_particle"] for r in jl(SNAP / "snapshots.jsonl")}
    e_tri = jl(RES / "references.jsonl")[1]["e_tri_sum"]
    fig = plt.figure(figsize=(12, 4.7), facecolor=INK)
    names = [("yuk_oc20_00_initial", "OC20-derived initial condition"), ("yuk_oc20_00_quench", "CVODE quench at T = 0"),
             ("yuk_oc20_17_anneal_quench", "anneal + CVODE quench")]
    pc = None
    for k, (nm, ttl) in enumerate(names):
        ax = fig.add_axes([0.01 + k * 0.325, 0.09, 0.31, 0.72], facecolor=INK)
        x = load(nm)
        pc, nd = draw_psi(ax, x, (LX, LY))
        gap = (snaps[nm] - e_tri) / e_tri
        ax.set_title(f"{ttl}\n$(e-e_{{\\rm tri}})/e_{{\\rm tri}}$ = {gap:.1e},  {nd} defects", color=PAPER, fontsize=9.5, pad=5)
    cax = fig.add_axes([0.33, 0.045, 0.34, 0.025])
    cb = fig.colorbar(pc, cax=cax, orientation="horizontal")
    cb.set_label(r"local bond order $|\psi_6|$  (dots mark non-6-fold sites: 5 blue, 7 red, other white)", color=PAPER, fontsize=8.5)
    cb.ax.tick_params(colors=PAPER, labelsize=7)
    fig.text(0.5, 0.965, "288 particles, 2D Yukawa interaction ($\\kappa=2$), density 1, periodic box", color=PAPER,
             ha="center", fontsize=10.5)
    save(fig, "cover")


def gaps() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
    for ax, kv in zip(axes, (2, 1)):
        rows = jl(RES / f"main_kappa{kv}.jsonl")
        series = {}
        for r in rows:
            for st in ("quench", "anneal_quench"):
                s = r.get(st)
                if s and "rel_gap" in s:
                    series.setdefault((r["family"], st), []).append(max(s["rel_gap"], 1e-16))
        colors = {"hf_oc20": "#c0398b", "uniform": "#2f6db3", "ctl_neg_incommensurate_box": "#7a7a7a"}
        labels = {"hf_oc20": "OC20-derived", "uniform": "uniform", "ctl_neg_incommensurate_box": "incomm. box (ctl)"}
        y = 0
        for (fam, st), v in sorted(series.items()):
            v = np.sort(v)
            ax.scatter(v, np.full(len(v), y) + np.linspace(-0.25, 0.25, len(v)), s=12, color=colors[fam],
                       marker="o" if st == "anneal_quench" else "^", alpha=0.85,
                       label=f"{labels[fam]}, {'anneal+quench' if st == 'anneal_quench' else 'T=0 quench'}")
            y += 1
        ax.set_xscale("log")
        ax.axvline(1e-8, color="#444", lw=0.8, ls=":")
        ax.text(1.3e-8, -0.9, "perfect-lattice threshold", fontsize=7, color="#444")
        ax.set_ylim(-1.2, y)
        ax.set_xlabel(r"$(e-e_{\rm tri})/e_{\rm tri}$ (values $\leq 10^{-16}$ shown at $10^{-16}$)")
        ax.set_title(f"$\\kappa={kv}$: no run below the triangular lattice (P1)", fontsize=10)
        ax.set_yticks([])
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, fontsize=7.5, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.12))
    fig.tight_layout()
    save(fig, "gaps", dark=False)


def disks() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.6), facecolor=INK)
    for ax, (nm, ttl) in zip(axes, [("disk_00_open_bowl", "open disk: harmonic bowl"), ("disk_00_closed_wall", "closed disk: soft wall")]):
        ax.set_facecolor(INK)
        x = load(nm)
        x = x - x.mean(axis=0)
        r = np.hypot(x[:, 0], x[:, 1]).max()
        coord, psi, d0 = periodic_neighbours(x, None)
        polys, _ = voronoi_cells(x, None, clip_r=r + 0.6 * d0)
        keep = [i for i, p in enumerate(polys) if p is not None]
        cols = [COORD.get(coord[i], "#f2c14e" if coord[i] < 5 else "#7b1e1e") for i in keep]
        ax.add_collection(PolyCollection([polys[i] for i in keep], facecolors=cols, edgecolors=INK, linewidths=0.4))
        ax.set_xlim(-r - 1, r + 1)
        ax.set_ylim(-r - 1, r + 1)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"{ttl}\n{(coord != 6).sum()} of {len(x)} sites not 6-fold", color=PAPER, fontsize=9.5)
    fig.text(0.5, 0.02, "Voronoi cells by coordination: 4 or fewer gold, 5 blue, 6 sand, 7 red, 8 or more dark red (N = 300, Yukawa $\\kappa=2$, annealed + CVODE quench)",
             color=PAPER, ha="center", fontsize=8.5)
    save(fig, "disks")


def vacancy() -> None:
    """Illustration of the non-uniqueness theorem: A and A minus the origin have the same energy for every admissible g."""
    b = math.sqrt(3) / 2
    pts = np.array([[(j + k / 2) / math.sqrt(b), k * b / math.sqrt(b)] for j in range(-6, 7) for k in range(-6, 7)])
    pts = pts[np.hypot(pts[:, 0], pts[:, 1]) < 5.2]
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 4.2), facecolor="white")
    for ax, vac in zip(axes, (False, True)):
        p = pts[np.hypot(pts[:, 0], pts[:, 1]) > 1e-9] if vac else pts
        for q in p:
            ax.add_patch(plt.Circle(q, 0.36, color="#20113a" if np.hypot(*q) > 1.2 else "#c0398b", zorder=2))
        if vac:
            ax.add_patch(plt.Circle((0, 0), 0.36, fill=False, ls="--", lw=1.2, color="#c0398b", zorder=3))
            u = np.array([1 / math.sqrt(b), 0.0])
            for q, lab, dy in ((u, r"$p(1,0)$", 0.75), (2 * u, r"$p(2,0)$", -0.95)):
                ax.add_patch(plt.Circle(q, 0.5, fill=False, lw=1.8, color="#f28f3b", zorder=4))
                ax.text(q[0], q[1] + dy, lab, ha="center", fontsize=8, color="#b35c00", zorder=5,
                        bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))
            ax.text(0, -6.3, "an isometry $f$ is affine, so\n$f(2a-b)=2\\,p(1,0)-p(2,0)=p(0,0)=0\\notin A\\setminus\\{0\\}$",
                    ha="center", fontsize=8, color="#5b2a86")
        ax.set_xlim(-5.4, 5.4)
        ax.set_ylim(-6.8, 5.4)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(r"$A$: triangular lattice" if not vac else r"$A\setminus\{0\}$: one vacancy", fontsize=11)
    fig.text(0.5, 0.03, r"Same lower energy for every admissible $g$ (Lean: vacancy_energy); not an isometric image of $A$"
             r" (vacancy_not_isometric_image)", ha="center", fontsize=8.5)
    save(fig, "vacancy", dark=False)


def lattices() -> None:
    refs = {r["kappa"]: r for r in jl(RES / "references.jsonl")}
    jel = {r["label"]: r for r in jl(RES / "jellium/controls.jsonl")}
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4), gridspec_kw={"width_ratios": [1, 1, 1.25]})
    for ax, kv in zip(axes[:2], (2, 1)):
        r = refs[kv]
        vals = [r["e_tri_sum"], r["e_square_sum"]]
        ax.scatter([0, 1], vals, color=["#c0398b", "#2f6db3"], s=160, zorder=2)
        for xx, v in zip((0, 1), vals):
            ax.text(xx + 0.12, v, f"{v:.6f}", fontsize=7.5, va="center")
        ax.set_xticks([0, 1], ["triangular", "square"])
        ax.set_xlim(-0.4, 1.6)
        pad = 0.25 * (vals[1] - vals[0])
        ax.set_ylim(vals[0] - pad, vals[1] + pad)
        ax.set_title(f"Yukawa $\\kappa={kv}$: $e_{{\\rm sq}}-e_{{\\rm tri}}$ = {r['square_minus_tri']:.2e}", fontsize=9.5)
        ax.set_ylabel("energy per particle (axis not from 0)")
    ax = axes[2]
    tri = jel["ctl_pos_perfect"]["quench"]["e"]
    sq = jel["ctl_neg_square_saddle"]["e_square_box"]
    lit_t = jel["ctl_pos_perfect"]["e_ref_literature"]
    lit_s = jel["ctl_neg_square_saddle"]["e_square_literature"]
    ax.scatter([0, 1], [tri, sq], color=["#c0398b", "#2f6db3"], s=160, zorder=2, label="this code (Ewald)")
    ax.scatter([0, 1], [lit_t, lit_s], color="black", marker="_", s=900, zorder=3, label="Alves et al. (2021), = Bonsall-Maradudin")
    for xx, v, lv in ((0, tri, lit_t), (1, sq, lit_s)):
        ax.text(xx + 0.12, v, f"{v:.9f}\n(rel. diff {abs(v - lv) / abs(lv):.1e})", fontsize=7, va="center")
    ax.set_xticks([0, 1], ["triangular", "square"])
    ax.set_xlim(-0.4, 1.8)
    ax.set_ylim(min(tri, sq) - 0.004, max(tri, sq) + 0.004)
    ax.set_ylabel("energy per particle")
    ax.set_title(f"2D Wigner jellium ($1/r$): square is a saddle\n({jel['ctl_neg_square_saddle']['hess_negative']} unstable modes)",
                 fontsize=9.5)
    ax.legend(fontsize=7, frameon=False, loc="lower right")
    fig.tight_layout()
    save(fig, "lattices", dark=False)


def save(fig, name: str, dark: bool = True) -> None:
    FIG.mkdir(exist_ok=True)
    kw = {"facecolor": fig.get_facecolor()} if dark else {}
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", **kw)
    fig.savefig(FIG / f"{name}.png", dpi=180, bbox_inches="tight", **kw)
    plt.close(fig)
    print("wrote", FIG / f"{name}.pdf")


if __name__ == "__main__":
    vacancy()
    lattices()
    gaps()
    if (SNAP / "snapshots.jsonl").exists():
        cover()
        disks()
    else:
        print("snapshots not ready: cover and disk figures skipped")
