"""
anse.jepa.latent_geometry — Universal-Optimality Latent Geometry, Order & Lattice Quantisation.

Integrates the measurement core and Horizon-0 feedback from OptimalEnergyAI
(v0.2.0 / v0.3.0, `docs/results/h0.md`, `docs/results/next_actions.md`, `src/oai_ml/core/`):

1. Explicit Conventions in Types (`Convention.ORDERED_PAIRS` vs `Convention.HALF`) and
   `Potential` (Gaussian g_alpha(r^2) = exp(-pi * alpha * r^2), Yukawa, Riesz).
2. Density-1 Rescaling (`voronoi_density`, `radial_interior_mask`, `rescale_to_density`)
   and Reference Lattice Energies (`e_tri`, `e_sq`, `cloud_energy`, `jellium_gamma`).
3. Hexatic Order `psi6` and the `Crystallized` Predicate (H0 Finding 2 & Issue #2):
   - Poisson clouds have *local* <|psi6|> ~= 0.78-0.79 because low-coordination sites
     yield |psi6| near 1. Order MUST be gated through `is_crystallized(tau=0.9, delta=0.1)`
     requiring BOTH interior <|psi6|> >= tau AND `defect_fraction` (coordination != 6) <= delta.
   - Supports both `'1.35d0'` metric cutoff and `'voronoi'` (Delaunay topological) neighbor
     rules (Issue #2), plus window-corrected `structure_factor` at S(k -> 0).
   - Ships with automatic positive (`A2` patch) and negative (Poisson disk) controls.
4. Conway-Sloane Lattice Quantisers (`nearest`, `nsm_mc`, `index_entropy`, `is_lattice_member`):
   - Exact nearest-point decoders for Z^n, D_n, E_8, and A_2 with deterministic tie rules.
   - Explicit `is_lattice_member` verification and two-sided oracle cross-check (H0 Finding 1
     & Issue #16).
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Literal

import numpy as np
from scipy.spatial import ConvexHull, Delaunay, Voronoi, cKDTree

from anse.harness import two_sided_oracle_check

B = math.sqrt(3.0) / 2.0  # Lean `OAI.AtomicTriangular.b`
TRI_SCALE = 1.0 / math.sqrt(B)  # b^{-1/2}, covolume-1 triangular lattice scale
SQ3 = math.sqrt(3.0)

COVOLUME: dict[str, float] = {"Z": 1.0, "A2": 1.0, "D": 2.0, "E8": 1.0}


class Convention(Enum):
    """Pair-summation convention (Lean Def 1.3 vs Chapter 3 ½ convention)."""

    ORDERED_PAIRS = "lean_def_1_3"
    HALF = "ch3_lab_half"

    @property
    def factor(self) -> float:
        return 1.0 if self is Convention.ORDERED_PAIRS else 0.5


@dataclass(frozen=True)
class Potential:
    """Radial pair interaction law v(r)."""

    kind: Literal["gaussian", "yukawa", "riesz"]
    alpha: float | None = None
    kappa: float | None = None
    s: float | None = None
    rc: float | None = None
    shift: Literal["none", "force"] = "none"

    def __post_init__(self) -> None:
        need = {"gaussian": "alpha", "yukawa": "kappa", "riesz": "s"}[self.kind]
        if getattr(self, need) is None:
            raise ValueError(f"{self.kind} potential requires {need}")
        if self.shift == "force" and self.rc is None:
            raise ValueError("shifted-force potential requires rc")

    def _v(self, r: np.ndarray | float) -> np.ndarray:
        r_arr = np.asarray(r, dtype=float)
        if self.kind == "gaussian":
            assert self.alpha is not None
            return np.exp(-math.pi * self.alpha * r_arr * r_arr)
        if self.kind == "yukawa":
            assert self.kappa is not None
            return np.exp(-self.kappa * r_arr) / r_arr
        assert self.s is not None
        return r_arr ** (-self.s)

    def _dv(self, r: np.ndarray | float) -> np.ndarray:
        r_arr = np.asarray(r, dtype=float)
        if self.kind == "gaussian":
            assert self.alpha is not None
            return -2.0 * math.pi * self.alpha * r_arr * np.exp(-math.pi * self.alpha * r_arr * r_arr)
        if self.kind == "yukawa":
            assert self.kappa is not None
            return -np.exp(-self.kappa * r_arr) * (self.kappa * r_arr + 1.0) / (r_arr * r_arr)
        assert self.s is not None
        return -self.s * r_arr ** (-self.s - 1.0)

    def __call__(self, r: np.ndarray) -> np.ndarray:
        r_arr = np.asarray(r, dtype=float)
        v = self._v(r_arr)
        if self.rc is None:
            return v
        if self.shift == "force":
            rc_val = float(self.rc)
            v = v - self._v(rc_val) - (r_arr - rc_val) * self._dv(rc_val)
        return np.where(r_arr < self.rc, v, 0.0)

    def support(self, tol: float = 1e-18) -> float:
        if self.rc is not None:
            return float(self.rc)
        if self.kind == "gaussian":
            assert self.alpha is not None
            return math.sqrt(-math.log(tol) / (math.pi * self.alpha))
        raise ValueError(f"{self.kind} without rc has no finite support; pass rc")

    def label(self) -> str:
        p = {"gaussian": f"alpha={self.alpha}", "yukawa": f"kappa={self.kappa}", "riesz": f"s={self.s}"}[self.kind]
        cut = "" if self.rc is None else f",rc={self.rc},{self.shift}"
        return f"{self.kind}({p}{cut})"


def gaussian(alpha: float, rc: float | None = None) -> Potential:
    return Potential("gaussian", alpha=alpha, rc=rc)


def yukawa(kappa: float, rc: float | None = None, shift: Literal["none", "force"] = "none") -> Potential:
    return Potential("yukawa", kappa=kappa, rc=rc, shift=shift)


def jellium_gamma(n_points: int, lam: float, alpha: float) -> float:
    """Dimensionless Jellium-JEPA droplet control parameter Gamma = N * sqrt(lambda / (pi * alpha)).

    Crystallizes for Gamma <= ~1, amorphous around Gamma ~= 7, shell collapse for Gamma >= 70.
    """
    if n_points <= 0 or lam < 0.0 or alpha <= 0.0:
        raise ValueError("n_points > 0, lam >= 0, alpha > 0 required")
    return float(n_points) * math.sqrt(lam / (math.pi * alpha))


@dataclass(frozen=True)
class EnergyReport:
    value: float
    potential: str
    rho: float
    convention: str
    n_interior: int
    rcut: float
    e_tri: float
    gap: float
    rel_gap: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OrderReport:
    n: int
    n_interior: int
    d0: float
    psi6_local_mean: float | None
    psi6_global: float
    defect_fraction: float | None
    crystallized: bool
    tau: float
    delta: float
    neighbour_rule: str
    g_r: dict[str, list[float]]
    s_k: dict[str, list[float]]
    controls: dict[str, Any]

    @property
    def controls_ok(self) -> bool:
        return all(bool(c.get("ok")) for c in self.controls.values())

    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "controls_ok": self.controls_ok}


# ---------------------------------------------------------------------------
# Lattices and Null Point Clouds
# ---------------------------------------------------------------------------


def triangular_point(j: np.ndarray | Sequence[float] | float, k: np.ndarray | Sequence[float] | float) -> np.ndarray:
    """Lean `triangularPoint (j, k) = b^{-1/2} (j + k/2, k b)`; ||p||^2 = (2/sqrt(3))(j^2 + j*k + k^2)."""
    j_arr, k_arr = np.asarray(j, dtype=float), np.asarray(k, dtype=float)
    return TRI_SCALE * np.stack([j_arr + 0.5 * k_arr, k_arr * B], axis=-1)


def square_point(j: np.ndarray | Sequence[float] | float, k: np.ndarray | Sequence[float] | float) -> np.ndarray:
    return np.stack([np.asarray(j, dtype=float), np.asarray(k, dtype=float)], axis=-1)


def _index_box(r: float) -> tuple[np.ndarray, np.ndarray]:
    m = math.ceil(2.0 * r)
    j, k = np.meshgrid(np.arange(-m, m + 1), np.arange(-m, m + 1), indexing="ij")
    return j.ravel(), k.ravel()


def hex_codebook(r: float) -> tuple[np.ndarray, np.ndarray]:
    j, k = _index_box(r)
    p = triangular_point(j, k)
    keep = np.linalg.norm(p, axis=1) <= r + 1e-12
    return p[keep], np.stack([j[keep], k[keep]], axis=1)


def square_codebook(r: float) -> tuple[np.ndarray, np.ndarray]:
    j, k = _index_box(r)
    p = square_point(j, k)
    keep = np.linalg.norm(p, axis=1) <= r + 1e-12
    return p[keep], np.stack([j[keep], k[keep]], axis=1)


def planar_patch(kind: Literal["A2", "Z2"], n: int, rho: float = 1.0) -> np.ndarray:
    """Radial patch of n points of A2 or Z2 rescaled to density rho, centred at the origin."""
    r = math.sqrt(n / math.pi) * 1.02 + 1.0
    pts = hex_codebook(r)[0] if kind == "A2" else square_codebook(r)[0]
    pts = pts[np.argsort(np.linalg.norm(pts, axis=1), kind="stable")[:n]]
    return pts / math.sqrt(rho)


def poisson_disk(n: int, rho: float, rng: np.random.Generator) -> np.ndarray:
    """Uniform Poisson point cloud of n points in a disk of area n / rho."""
    radius = math.sqrt(n / (math.pi * rho))
    u = rng.uniform(0.0, 1.0, size=n)
    theta = rng.uniform(0.0, 2.0 * math.pi, size=n)
    r = radius * np.sqrt(u)
    return np.stack([r * np.cos(theta), r * np.sin(theta)], axis=1)


def lattice_points(kind: str, n: int, radius: float) -> np.ndarray:
    """All points of `kind` in {Z, D, E8, A2} in dimension n with norm <= radius."""
    if kind == "A2":
        return hex_codebook(radius)[0]
    m = int(math.floor(radius))
    grid = np.array(list(itertools.product(range(-m, m + 1), repeat=n)), dtype=float)
    pts = [grid]
    if kind == "E8":
        h = math.floor(radius - 0.5) if radius >= 0.5 else -1
        half = np.arange(-h - 0.5, h + 1.0, 1.0)
        pts.append(np.array(list(itertools.product(half, repeat=n)), dtype=float))
    x = np.concatenate(pts)
    if kind in ("D", "E8"):
        x = x[np.isclose(np.mod(x.sum(axis=1), 2.0), 0.0)]
    return x[np.einsum("ij,ij->i", x, x) <= radius * radius + 1e-9]


# ---------------------------------------------------------------------------
# Density Normalisation and Pair Energies
# ---------------------------------------------------------------------------


def interior_mask(x: np.ndarray, margin: float) -> np.ndarray:
    x_arr = np.asarray(x, dtype=float)
    lo, hi = x_arr.min(axis=0) + margin, x_arr.max(axis=0) - margin
    return np.all((x_arr >= lo) & (x_arr <= hi), axis=1)


def radial_interior_mask(x: np.ndarray, margin: float) -> np.ndarray:
    x_arr = np.asarray(x, dtype=float)
    r = np.linalg.norm(x_arr - x_arr.mean(axis=0), axis=1)
    return r <= r.max() - margin


def voronoi_density(x: np.ndarray, mask: np.ndarray) -> float:
    """Density = 1 / mean Voronoi cell area of the masked points (exact on a lattice)."""
    x_arr = np.asarray(x, dtype=float)
    vor = Voronoi(x_arr)
    areas = []
    for i in np.flatnonzero(mask):
        reg = vor.regions[vor.point_region[i]]
        if reg and -1 not in reg:
            areas.append(ConvexHull(vor.vertices[reg]).volume)
    if not areas:
        raise ValueError("voronoi_density mask selected 0 closed Voronoi cells")
    return 1.0 / float(np.mean(areas))


def rescale_to_density(
    x: np.ndarray,
    rho: float = 1.0,
    margin: float = 3.0,
    window: Literal["disk", "box"] = "disk",
) -> tuple[np.ndarray, float, np.ndarray]:
    """Rescale point cloud so interior points (>= margin from edge in density-1 units) have density `rho`."""
    x_arr = np.asarray(x, dtype=float)
    c = x_arr.mean(axis=0)
    if window == "box":
        span = x_arr.max(axis=0) - x_arr.min(axis=0)
        central = np.all(np.abs(x_arr - c) <= span / 4.0, axis=1)
        rho_hat = voronoi_density(x_arr, central)
        for _ in range(2):
            x1 = (x_arr - c) * math.sqrt(rho_hat)
            mask = interior_mask(x1, margin)
            rho_hat *= voronoi_density(x1, mask)
        x1 = (x_arr - c) * math.sqrt(rho_hat)
        return x1 / math.sqrt(rho), float(rho_hat), interior_mask(x1, margin)

    r = np.linalg.norm(x_arr - c, axis=1)
    rho_hat = voronoi_density(x_arr, r <= 0.5 * r.max())
    for _ in range(2):
        x1 = (x_arr - c) * math.sqrt(rho_hat)
        mask = radial_interior_mask(x1, margin)
        rho_hat *= voronoi_density(x1, mask)
    x1 = (x_arr - c) * math.sqrt(rho_hat)
    return x1 / math.sqrt(rho), float(rho_hat), radial_interior_mask(x1, margin)


def lattice_energy(
    kind: Literal["A2", "Z2"],
    pot: Potential,
    rho: float = 1.0,
    conv: Convention = Convention.ORDERED_PAIRS,
) -> float:
    rmax = pot.support()
    m = int(math.ceil(2.0 * rmax * math.sqrt(rho))) + 2
    j, k = np.meshgrid(np.arange(-m, m + 1), np.arange(-m, m + 1), indexing="ij")
    j, k = j.ravel(), k.ravel()
    nz = ~((j == 0) & (k == 0))
    p = (triangular_point if kind == "A2" else square_point)(j[nz], k[nz])
    r = np.linalg.norm(p, axis=1) / math.sqrt(rho)
    v = pot(r[r < rmax + 1e-12])
    return conv.factor * float(np.sort(v).sum())


def e_tri(pot: Potential, rho: float = 1.0, conv: Convention = Convention.ORDERED_PAIRS) -> float:
    return lattice_energy("A2", pot, rho, conv)


def e_sq(pot: Potential, rho: float = 1.0, conv: Convention = Convention.ORDERED_PAIRS) -> float:
    return lattice_energy("Z2", pot, rho, conv)


def per_point_energy(x: np.ndarray, pot: Potential, mask: np.ndarray, rcut: float | None = None) -> np.ndarray:
    x_arr = np.asarray(x, dtype=float)
    rcut_val = pot.support() if rcut is None else rcut
    idx = np.flatnonzero(mask)
    nbs = cKDTree(x_arr).query_ball_point(x_arr[idx], rcut_val)
    counts = np.fromiter((len(n) for n in nbs), dtype=np.int64, count=len(idx))
    i = np.repeat(np.arange(len(idx)), counts)
    j = np.fromiter((v for n in nbs for v in n), dtype=np.int64, count=int(counts.sum()))
    keep = idx[i] != j
    d = np.linalg.norm(x_arr[idx[i[keep]]] - x_arr[j[keep]], axis=1)
    out = np.zeros(len(idx))
    np.add.at(out, i[keep], pot(d))
    return out


def cloud_energy(
    x: np.ndarray,
    pot: Potential,
    mask: np.ndarray,
    rho: float = 1.0,
    conv: Convention = Convention.ORDERED_PAIRS,
    rcut: float | None = None,
) -> EnergyReport:
    rcut_val = pot.support() if rcut is None else rcut
    e = per_point_energy(x, pot, mask, rcut_val)
    value = conv.factor * float(e.mean()) if len(e) else float("nan")
    ref = e_tri(pot, rho, conv)
    return EnergyReport(
        value=value,
        potential=pot.label(),
        rho=rho,
        convention=conv.value,
        n_interior=int(len(e)),
        rcut=float(rcut_val),
        e_tri=ref,
        gap=value - ref,
        rel_gap=(value - ref) / abs(ref),
    )


# ---------------------------------------------------------------------------
# Hexatic Bond-Orientational Order & Crystallized Predicate (H0 Finding 2 & Issue #2)
# ---------------------------------------------------------------------------


def _voronoi_neighbours(x: np.ndarray) -> list[list[int]]:
    """Topological Delaunay/Voronoi neighbors (OptimalEnergyAI Issue #2)."""
    tri = Delaunay(x)
    indptr, indices = tri.vertex_neighbor_vertices
    return [indices[indptr[i] : indptr[i + 1]].tolist() for i in range(len(x))]


def psi6_metrics(
    x: np.ndarray,
    mask: np.ndarray,
    neighbour_rule: Literal["1.35d0", "voronoi"] = "1.35d0",
) -> dict[str, Any]:
    """Compute interior <|psi6|>, global |psi6|, and defect fraction (coordination != 6)."""
    x_arr = np.asarray(x, dtype=float)
    mask_arr = np.asarray(mask, dtype=bool)
    tree = cKDTree(x_arr)
    d, _ = tree.query(x_arr, k=2)
    d0 = float(np.median(d[:, 1]))

    if neighbour_rule == "1.35d0":
        nbs = tree.query_ball_point(x_arr, 1.35 * d0)
    elif neighbour_rule == "voronoi":
        nbs = _voronoi_neighbours(x_arr)
    else:
        raise ValueError(f"Unknown neighbour_rule: {neighbour_rule!r}")

    coord: list[int] = []
    psi_loc: list[float] = []
    re, im = 0.0, 0.0
    for i in np.flatnonzero(mask_arr):
        nb = [j for j in nbs[i] if j != i]
        coord.append(len(nb))
        if nb:
            dv = x_arr[nb] - x_arr[i]
            z = np.exp(6j * np.arctan2(dv[:, 1], dv[:, 0])).mean()
            psi_loc.append(float(abs(z)))
            re += float(z.real)
            im += float(z.imag)
    n = max(len(coord), 1)
    coord_arr = np.asarray(coord)
    return {
        "counted": int(len(coord)),
        "defect_fraction": float((coord_arr != 6).mean()) if len(coord_arr) else None,
        "psi6_local_mean": float(np.mean(psi_loc)) if psi_loc else None,
        "psi6_global": float(math.hypot(re / n, im / n)),
        "d0": d0,
    }


def is_crystallized(m: dict[str, Any], tau: float = 0.9, delta: float = 0.1) -> bool:
    """Lean `Crystallized tau delta`: interior <|psi6|> >= tau AND defect_fraction <= delta.

    Crucial (OptimalEnergyAI H0 Finding 2): Poisson point clouds have local <|psi6|> ~= 0.78-0.79,
    so local <|psi6|> alone never separates order from disorder; defect_fraction <= delta does.
    """
    if m.get("psi6_local_mean") is None or m.get("defect_fraction") is None:
        return False
    return bool(m["psi6_local_mean"] >= tau and m["defect_fraction"] <= delta)


def radial_distribution(
    x: np.ndarray,
    mask: np.ndarray,
    rho: float = 1.0,
    rmax: float = 5.0,
    nbins: int = 100,
) -> dict[str, list[float]]:
    x_arr = np.asarray(x, dtype=float)
    idx = np.flatnonzero(mask)
    nbs = cKDTree(x_arr).query_ball_point(x_arr[idx], rmax)
    d = np.concatenate(
        [np.linalg.norm(x_arr[[j for j in nb if j != i]] - x_arr[i], axis=1) for i, nb in zip(idx, nbs)]
        or [np.zeros(0)]
    )
    edges = np.linspace(0.0, rmax, nbins + 1)
    h, _ = np.histogram(d, bins=edges)
    r = 0.5 * (edges[1:] + edges[:-1])
    shell = math.pi * (edges[1:] ** 2 - edges[:-1] ** 2)
    g = h / (max(len(idx), 1) * rho * shell)
    return {"r": r.tolist(), "g": g.tolist()}


def structure_factor(
    x: np.ndarray,
    mask: np.ndarray,
    kmax: float = 12.0,
    nk: int = 60,
    ndir: int = 48,
    window_correction: bool = True,
) -> dict[str, list[float]]:
    """Radially averaged S(k) with optional Hann-tapered window correction for S(k -> 0) (Issue #2)."""
    p = np.asarray(x, dtype=float)[np.asarray(mask, dtype=bool)]
    if len(p) == 0:
        return {"k": [], "S": []}
    p_centered = p - p.mean(axis=0)
    k = np.linspace(kmax / nk, kmax, nk)
    th = np.linspace(0.0, math.pi, ndir, endpoint=False)
    dirs = np.stack([np.cos(th), np.sin(th)], axis=1)

    if window_correction:
        rmax = float(np.linalg.norm(p_centered, axis=1).max()) or 1.0
        r_norm = np.linalg.norm(p_centered, axis=1) / rmax
        w = 0.5 * (1.0 + np.cos(math.pi * np.clip(r_norm, 0.0, 1.0)))
        w_zero_mean = w - w.mean()
        norm_w = float((w * w).sum()) or 1.0
    else:
        w_zero_mean = np.ones(len(p_centered))
        norm_w = float(len(p_centered))

    s = np.empty(nk)
    for a, kk in enumerate(k):
        ph = p_centered @ (kk * dirs).T
        if window_correction:
            amp = (w_zero_mean[:, None] * np.exp(-1j * ph)).sum(axis=0)
        else:
            amp = np.exp(-1j * ph).sum(axis=0)
        s[a] = float(np.mean(np.abs(amp) ** 2) / norm_w)
    return {"k": k.tolist(), "S": s.tolist()}


def _order_control(
    x: np.ndarray,
    margin: float,
    tau: float,
    delta: float,
    expect: bool,
    neighbour_rule: Literal["1.35d0", "voronoi"] = "1.35d0",
) -> dict[str, Any]:
    m = psi6_metrics(x, radial_interior_mask(x, margin), neighbour_rule=neighbour_rule)
    c = is_crystallized(m, tau, delta)
    return {
        "psi6_local_mean": m["psi6_local_mean"],
        "psi6_global": m["psi6_global"],
        "defect_fraction": m["defect_fraction"],
        "n_interior": m["counted"],
        "crystallized": c,
        "expected": expect,
        "ok": c == expect,
    }


def order_report(
    x: np.ndarray,
    mask: np.ndarray,
    tau: float = 0.9,
    delta: float = 0.1,
    seed: int = 0,
    neighbour_rule: Literal["1.35d0", "voronoi"] = "1.35d0",
    with_spectra: bool = True,
    control_margin: float = 2.0,
) -> OrderReport:
    """Order report of a density-1 point set on its interior `mask`, with built-in A2 and Poisson controls."""
    x_arr = np.asarray(x, dtype=float)
    m = psi6_metrics(x_arr, mask, neighbour_rule=neighbour_rule)
    n = len(x_arr)
    rng = np.random.default_rng(seed)
    controls = {
        "positive_A_patch": _order_control(
            planar_patch("A2", n), control_margin, tau, delta, True, neighbour_rule=neighbour_rule
        ),
        "negative_poisson": _order_control(
            poisson_disk(n, 1.0, rng), control_margin, tau, delta, False, neighbour_rule=neighbour_rule
        ),
    }
    return OrderReport(
        n=n,
        n_interior=m["counted"],
        d0=m["d0"],
        psi6_local_mean=m["psi6_local_mean"],
        psi6_global=m["psi6_global"],
        defect_fraction=m["defect_fraction"],
        crystallized=is_crystallized(m, tau, delta),
        tau=tau,
        delta=delta,
        neighbour_rule=neighbour_rule,
        g_r=radial_distribution(x_arr, mask) if with_spectra else {},
        s_k=structure_factor(x_arr, mask) if with_spectra else {},
        controls=controls,
    )


# ---------------------------------------------------------------------------
# Conway-Sloane Lattice Decoders, Membership & Two-Sided Oracle Check
# ---------------------------------------------------------------------------


def nearest_zn(x: np.ndarray) -> np.ndarray:
    return np.rint(x)


def nearest_dn(x: np.ndarray) -> np.ndarray:
    x_arr = np.asarray(x, dtype=float)
    f = np.rint(x_arr)
    odd = np.mod(f.sum(axis=-1), 2.0) != 0
    if not odd.any():
        return f
    d = x_arr - f
    i = np.argmax(np.abs(d), axis=-1)
    rows = np.arange(len(x_arr))
    step = np.where(d[rows, i] >= 0.0, 1.0, -1.0)
    g = f.copy()
    g[rows, i] += step
    return np.where(odd[:, None], g, f)


def _closer(a: np.ndarray, b: np.ndarray, x: np.ndarray) -> np.ndarray:
    da = np.einsum("ij,ij->i", x - a, x - a)
    db = np.einsum("ij,ij->i", x - b, x - b)
    return np.where((db < da)[:, None], b, a)


def nearest_e8(x: np.ndarray) -> np.ndarray:
    x_arr = np.asarray(x, dtype=float)
    return _closer(nearest_dn(x_arr), nearest_dn(x_arr - 0.5) + 0.5, x_arr)


def nearest_a2(x: np.ndarray) -> np.ndarray:
    x_arr = np.asarray(x, dtype=float)
    y = x_arr / TRI_SCALE
    c0 = np.stack([np.rint(y[:, 0]), np.rint(y[:, 1] / SQ3) * SQ3], axis=1)
    c1 = np.stack([np.rint(y[:, 0] - 0.5) + 0.5, (np.rint(y[:, 1] / SQ3 - 0.5) + 0.5) * SQ3], axis=1)
    return _closer(c0, c1, y) * TRI_SCALE


def a2_index(c: np.ndarray) -> np.ndarray:
    y = c / TRI_SCALE
    k = np.rint(2.0 * y[:, 1] / SQ3)
    j = np.rint(y[:, 0] - 0.5 * k)
    return np.stack([j, k], axis=1).astype(np.int64)


DECODERS = {"Z": nearest_zn, "D": nearest_dn, "E8": nearest_e8, "A2": nearest_a2}


def dim_ok(kind: str, n: int) -> bool:
    return {"Z": n >= 1, "D": n >= 2, "E8": n == 8, "A2": n == 2}[kind]


def nearest(kind: str, y: np.ndarray, scale: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """Quantise rows of `y` to the scaled lattice `scale * L`, returning `(codeword, integer_index)`."""
    y_arr = np.atleast_2d(np.asarray(y, dtype=float))
    if not dim_ok(kind, y_arr.shape[1]):
        raise ValueError(f"{kind} does not exist in dimension {y_arr.shape[1]}")
    c = DECODERS[kind](y_arr / scale)
    if kind == "A2":
        idx = a2_index(c)
    elif kind == "E8":
        idx = np.rint(2.0 * c).astype(np.int64)
    else:
        idx = c.astype(np.int64)
    return scale * c, idx


def is_lattice_member(kind: str, pts: np.ndarray, scale: float = 1.0, tol: float = 1e-9) -> np.ndarray:
    """Verify row-wise membership in the scaled lattice `scale * L` (OptimalEnergyAI Issue #16)."""
    c = np.atleast_2d(np.asarray(pts, dtype=float)) / scale
    if not dim_ok(kind, c.shape[1]):
        return np.zeros(len(c), dtype=bool)
    if kind == "Z":
        return np.all(np.abs(c - np.rint(c)) <= tol, axis=1)
    if kind == "D":
        is_int = np.all(np.abs(c - np.rint(c)) <= tol, axis=1)
        even_sum = np.abs(np.mod(np.rint(c).sum(axis=1), 2.0)) <= tol
        return is_int & even_sum
    if kind == "E8":
        in_d8 = is_lattice_member("D", c, scale=1.0, tol=tol)
        in_coset = is_lattice_member("D", c - 0.5, scale=1.0, tol=tol)
        return in_d8 | in_coset
    if kind == "A2":
        idx = a2_index(c)
        reconstructed = triangular_point(idx[:, 0], idx[:, 1])
        return np.linalg.norm(c - reconstructed, axis=1) <= tol
    raise ValueError(f"Unknown lattice kind: {kind!r}")


def nsm_reference(kind: str, n: int) -> float:
    """Classical Conway-Sloane normalised second moments G(L)."""
    if kind == "Z":
        return 1.0 / 12.0
    if kind == "A2":
        return 5.0 / (36.0 * SQ3)
    if kind == "D" and n == 4:
        return 0.0766032
    if kind == "E8":
        return 929.0 / 12960.0
    raise KeyError((kind, n))


def nsm_mc(
    kind: str,
    n: int,
    samples: int,
    rng: np.random.Generator,
    chunk: int = 1 << 17,
) -> tuple[float, float]:
    """Monte Carlo normalised second moment G = E||x - Q(x)||^2 / (n * V^{2/n})."""
    tot, tot2, done = 0.0, 0.0, 0
    while done < samples:
        m = min(chunk, samples - done)
        if kind == "A2":
            u = rng.uniform(size=(m, 2))
            x = u[:, :1] * np.array([TRI_SCALE, 0.0]) + u[:, 1:] * np.array([0.5 * TRI_SCALE, SQ3 / 2.0 * TRI_SCALE])
        else:
            x = rng.uniform(0.0, 2.0, size=(m, n))
        c, _ = nearest(kind, x)
        e = np.einsum("ij,ij->i", x - c, x - c)
        tot += float(e.sum())
        tot2 += float((e * e).sum())
        done += m
    mean = tot / samples
    se = math.sqrt(max(tot2 / samples - mean * mean, 0.0) / samples)
    norm = n * (COVOLUME[kind] ** (2.0 / n))
    return mean / norm, se / norm


def brute_force_nearest(points: np.ndarray, x: np.ndarray, chunk: int = 4096) -> np.ndarray:
    """Exhaustive nearest point of `points` for each row of x (returns minimal squared distance)."""
    p2 = np.einsum("ij,ij->i", points, points)
    out = np.empty(len(x))
    for s in range(0, len(x), chunk):
        xs = x[s : s + chunk]
        d = p2[None, :] - 2.0 * (xs @ points.T)
        out[s : s + chunk] = d.min(axis=1) + np.einsum("ij,ij->i", xs, xs)
    return out


def verify_lattice_decoder(
    kind: str,
    n: int,
    radius: float,
    queries: int,
    rng: np.random.Generator,
    decode_fn: Any = None,
) -> dict[str, Any]:
    """Verify a lattice decoder against brute-force search using the two-sided distance + membership check."""
    pts = lattice_points(kind, n, radius)
    v = rng.normal(size=(queries, n))
    v /= np.linalg.norm(v, axis=1, keepdims=True)
    q = v * (rng.uniform(size=(queries, 1)) ** (1.0 / n))
    cand = decode_fn(q) if decode_fn is not None else nearest(kind, q)[0]
    oracle_d = brute_force_nearest(pts, q)
    return two_sided_oracle_check(
        candidate_points=cand,
        query_points=q,
        oracle_sq_dists=oracle_d,
        is_valid_member_fn=lambda c: is_lattice_member(kind, c),
    )


def index_entropy(idx: np.ndarray) -> float:
    """Plug-in Shannon entropy (bits per vector) of codeword indices."""
    _, counts = np.unique(idx, axis=0, return_counts=True)
    p = counts / counts.sum()
    return float(-(p * np.log2(p)).sum())
