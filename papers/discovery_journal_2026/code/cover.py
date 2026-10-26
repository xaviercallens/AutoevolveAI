"""Cover of « Le journal des découvertes »: Voronoi cells of the triangular lattice of density 1.

Each cell is coloured by the weight exp(-pi * alpha * |p - c|^2) of its site p in the Gaussian energy of the
central site c (the kernel of the textbook's ALIX figure, here with a small alpha so that the colour spreads).
The geometry is computed, not drawn by hand: scipy's Voronoi diagram of the lattice points.

Self-checks (the script stops if one fails):
  positive control: every interior Voronoi cell of the triangular lattice is a hexagon of area 1 (density 1);
  negative control: on a randomly perturbed copy of the lattice, the cell areas are NOT all equal to 1,
                    so the area test can fail.
Usage: python -I code/cover.py   (run from papers/discovery_journal_2026)
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Polygon
from scipy.spatial import Voronoi

IVORY = "#FAF6EC"
OKABE = {
    "orange": "#E69F00",
    "sky": "#56B4E9",
    "green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
}
PAPER_W_CM, PAPER_H_CM = 19.5, 26.0


def triangular_lattice(n: int) -> np.ndarray:
    """Points of the triangular lattice of covolume 1, indices -n..n in both basis directions."""
    a = math.sqrt(2.0 / math.sqrt(3.0))  # spacing giving one point per unit area
    b1 = np.array([a, 0.0])
    b2 = np.array([a / 2.0, a * math.sqrt(3.0) / 2.0])
    ij = np.array([(i, j) for i in range(-n, n + 1) for j in range(-n, n + 1)], dtype=float)
    return ij[:, :1] * b1 + ij[:, 1:] * b2


def polygon_area(vertices: np.ndarray) -> float:
    """Shoelace area of a polygon given in cyclic order."""
    x, y = vertices[:, 0], vertices[:, 1]
    return 0.5 * abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def interior_cells(points: np.ndarray, radius: float) -> list[tuple[int, np.ndarray]]:
    """Bounded Voronoi cells of the sites within `radius` of the origin, vertices in angular order."""
    vor = Voronoi(points)
    cells: list[tuple[int, np.ndarray]] = []
    for k, p in enumerate(points):
        if np.hypot(*p) > radius:
            continue
        region = vor.regions[vor.point_region[k]]
        if not region or -1 in region:
            continue
        verts = vor.vertices[region]
        ang = np.arctan2(verts[:, 1] - p[1], verts[:, 0] - p[0])
        cells.append((k, verts[np.argsort(ang)]))
    return cells


def self_check(points: np.ndarray) -> dict[str, float | int | bool]:
    """Positive and negative controls on the cell geometry."""
    cells = interior_cells(points, 8.0)
    areas = np.array([polygon_area(v) for _, v in cells])
    sides = {len(v) for _, v in cells}
    positive_ok = bool(np.allclose(areas, 1.0, atol=1e-9) and sides == {6})
    rng = np.random.default_rng(20261026)
    perturbed = points + rng.normal(scale=0.08, size=points.shape)
    p_areas = np.array([polygon_area(v) for _, v in interior_cells(perturbed, 8.0)])
    negative_detected = bool(np.max(np.abs(p_areas - 1.0)) > 1e-3)
    if not positive_ok:
        raise SystemExit(f"positive control failed: areas {areas.min()}..{areas.max()}, sides {sides}")
    if not negative_detected:
        raise SystemExit("negative control failed: perturbed cells all have area 1")
    return {
        "n_cells_checked": int(len(areas)),
        "max_abs_area_error": float(np.max(np.abs(areas - 1.0))),
        "sides": sorted(sides)[0],
        "positive_control_ok": positive_ok,
        "perturbed_max_area_deviation": float(np.max(np.abs(p_areas - 1.0))),
        "negative_control_detected": negative_detected,
    }


def draw_cover(points: np.ndarray, out_stem: Path, alpha: float) -> None:
    """Full-page cover: the coloured cells fill the lower part, the top stays ivory for the title."""
    w_in, h_in = PAPER_W_CM / 2.54, PAPER_H_CM / 2.54
    fig = plt.figure(figsize=(w_in, h_in), facecolor=IVORY)
    ax = fig.add_axes((0.0, 0.0, 1.0, 1.0))
    ax.set_facecolor(IVORY)
    half_w = 11.0  # lattice units shown across half the page width
    half_h = half_w * h_in / w_in
    centre = np.array([0.0, -0.5 * half_h])  # the central site sits in the lower half
    shift = points[np.argmin(np.hypot(*(points - centre).T))]
    pts = points - shift + centre
    cmap = LinearSegmentedColormap.from_list(
        "okabe_cover",
        [IVORY, OKABE["sky"], OKABE["blue"], OKABE["green"], OKABE["orange"], OKABE["vermillion"]],
    )
    cells = interior_cells(pts, 1.6 * half_h)
    for k, verts in cells:
        r2 = float(np.sum((pts[k] - centre) ** 2))
        weight = math.exp(-math.pi * alpha * r2)
        # cells above the band fade out so the title area stays calm
        fade = 1.0 / (1.0 + math.exp((pts[k][1] - 0.12 * half_h) / 1.6))
        face = cmap(weight**0.55)
        edge = IVORY if weight > 0.06 else "#DDD3BC"
        ax.add_patch(
            Polygon(verts, closed=True, facecolor=face, edgecolor=edge, linewidth=0.9, alpha=0.06 + 0.94 * fade)
        )
        dot = 0.055 + 0.05 * weight
        ax.add_patch(plt.Circle(tuple(pts[k]), dot, color="#2B2A26", alpha=0.08 + 0.77 * fade, lw=0))
    ax.add_patch(plt.Circle(tuple(centre), 0.16, color=IVORY, lw=0, zorder=5))
    ax.add_patch(plt.Circle(tuple(centre), 0.11, color="#2B2A26", lw=0, zorder=6))
    ax.set_xlim(-half_w, half_w)
    ax.set_ylim(-half_h, half_h)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(out_stem.with_suffix(".pdf"), facecolor=IVORY)
    fig.savefig(out_stem.with_suffix(".png"), dpi=300, facecolor=IVORY)
    plt.close(fig)


def main() -> None:
    here = Path(__file__).resolve().parent.parent
    points = triangular_lattice(34)
    checks = self_check(points)
    alpha = 0.009
    draw_cover(points, here / "figures" / "cover", alpha)
    record = {"alpha": alpha, "kernel": "exp(-pi*alpha*r^2)", "density": 1, **checks}
    (here / "figures" / "cover_selfcheck.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
