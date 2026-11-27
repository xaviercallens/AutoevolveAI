"""Ewald sums and Voronoi geometry for 3D jellium (one-component plasma) feasibility numerics.

Normalization (used everywhere in B3):
  unit charges, uniform neutralizing background of density N/V,
  energy per particle e = (1/N) * [ (1/2) sum'_{i,j,n} 1/|x_i - x_j + n| - background terms ],
  equivalently e = (1/N) lim [ (1/8 pi) int_{T minus balls} |grad h|^2 - N/(2 eta) ],
  with -Delta h = 4 pi (sum delta_{x_i} - N/V), h of mean zero.
At density one (V = N) the bcc value should be -0.895929255682 / r_s with r_s = (3/(4 pi))^(1/3).

Tier X (floating point, not interval arithmetic).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")

import itertools
import math
from dataclasses import dataclass

import numpy as np
from scipy.special import erfc
from scipy.spatial import ConvexHull, Voronoi

R_S_UNIT_DENSITY: float = (3.0 / (4.0 * math.pi)) ** (1.0 / 3.0)


@dataclass
class Structure:
    """Periodic point set: lattice rows A (3x3), fractional basis F (N x 3)."""

    name: str
    A: np.ndarray
    F: np.ndarray

    @property
    def volume(self) -> float:
        return float(abs(np.linalg.det(self.A)))

    @property
    def n(self) -> int:
        return int(self.F.shape[0])

    def cart(self) -> np.ndarray:
        return self.F @ self.A

    def scaled_to_unit_density(self) -> "Structure":
        s = (self.n / self.volume) ** (1.0 / 3.0)
        return Structure(self.name, self.A * s, self.F.copy())


def _images(A: np.ndarray, rcut: float) -> np.ndarray:
    """Lattice vectors n = m @ A with |n| <= rcut + diameter margin."""
    inv = np.linalg.inv(A)
    # bound on integer range from the dual row norms
    m_max = [int(math.ceil(rcut * np.linalg.norm(inv[:, i]))) + 1 for i in range(3)]
    rng = [np.arange(-m, m + 1) for m in m_max]
    M = np.array(list(itertools.product(*rng)), dtype=float)
    return M @ A


def _kvectors(A: np.ndarray, kcut: float) -> np.ndarray:
    B = 2.0 * math.pi * np.linalg.inv(A).T
    Kv = _images(B, kcut)
    k2 = np.einsum("ij,ij->i", Kv, Kv)
    return Kv[(k2 > 1e-12) & (k2 <= kcut * kcut)]


def ewald_energy_per_particle(
    st: Structure, alpha: float | None = None, tol: float = 1e-15, background: bool = True
) -> float:
    """Ewald energy per particle of the OCP. background=False is a negative control
    (it drops the -pi N^2/(2 V alpha^2) neutralization term, making the result alpha-dependent)."""
    A = st.A
    V = st.volume
    N = st.n
    X = st.cart()
    if alpha is None:
        alpha = 2.6 * (N / V) ** (1.0 / 3.0) / max(1.0, N ** (1.0 / 3.0) / 2.0)
    s = math.sqrt(-math.log(tol))
    rcut = s / alpha
    kcut = 2.0 * alpha * s
    # real space
    diam = float(np.max(np.linalg.norm(X - X.mean(0), axis=1))) * 2.0
    L = _images(A, rcut + diam)
    e_real = 0.0
    for i in range(N):
        d = X[i] - X  # (N,3)
        R = d[:, None, :] + L[None, :, :]
        r = np.linalg.norm(R, axis=2)
        mask = (r > 1e-12) & (r <= rcut)
        e_real += 0.5 * float(np.sum(erfc(alpha * r[mask]) / r[mask]))
    # reciprocal space
    Kv = _kvectors(A, kcut)
    k2 = np.einsum("ij,ij->i", Kv, Kv)
    phase = X @ Kv.T  # (N,K)
    S2 = np.sum(np.cos(phase), axis=0) ** 2 + np.sum(np.sin(phase), axis=0) ** 2
    e_rec = (2.0 * math.pi / V) * float(np.sum(np.exp(-k2 / (4 * alpha * alpha)) / k2 * S2))
    e_self = -alpha * N / math.sqrt(math.pi)
    e_bg = -math.pi * N * N / (2.0 * V * alpha * alpha) if background else 0.0
    return (e_real + e_rec + e_self + e_bg) / N


class Potential:
    """Mean-zero periodic potential h, -Delta h = 4 pi (sum_i delta_{x_i} - N/V), and its gradient."""

    def __init__(self, st: Structure, alpha: float = 2.4, tol: float = 1e-14) -> None:
        self.st = st
        self.alpha = alpha
        s = math.sqrt(-math.log(tol))
        self.rcut = s / alpha
        self.kcut = 2.0 * alpha * s
        X = st.cart()
        diam = float(np.max(np.linalg.norm(X - X.mean(0), axis=1))) * 2.0
        L = _images(st.A, self.rcut + diam + 2.0)
        self.src = (X[:, None, :] + L[None, :, :]).reshape(-1, 3)
        self.K = _kvectors(st.A, self.kcut)
        k2 = np.einsum("ij,ij->i", self.K, self.K)
        V = st.volume
        self.kw = (4.0 * math.pi / V) * np.exp(-k2 / (4 * alpha * alpha)) / k2
        # structure factor phases of the sources
        ph = X @ self.K.T
        self.Sc = np.sum(np.cos(ph), axis=0)
        self.Ss = np.sum(np.sin(ph), axis=0)
        self.const = -math.pi * st.n / (alpha * alpha * V)

    def _real(self, P: np.ndarray, grad: bool) -> tuple[np.ndarray, np.ndarray | None]:
        a = self.alpha
        out = np.zeros(P.shape[0])
        g = np.zeros_like(P) if grad else None
        chunk = max(1, 200000 // max(1, self.src.shape[0]))
        for s0 in range(0, P.shape[0], chunk):
            Q = P[s0 : s0 + chunk]
            D = Q[:, None, :] - self.src[None, :, :]
            r = np.linalg.norm(D, axis=2)
            m = r <= self.rcut
            rr = np.where(m, r, 1.0)
            val = np.where(m, erfc(a * rr) / rr, 0.0)
            out[s0 : s0 + chunk] = val.sum(1)
            if grad:
                dv = np.where(
                    m, -erfc(a * rr) / rr**2 - (2 * a / math.sqrt(math.pi)) * np.exp(-(a * rr) ** 2) / rr, 0.0
                )
                g[s0 : s0 + chunk] = np.einsum("qs,qsi->qi", dv / rr, D)
        return out, g

    def _rec(self, P: np.ndarray, grad: bool) -> tuple[np.ndarray, np.ndarray | None]:
        out = np.zeros(P.shape[0])
        g = np.zeros_like(P) if grad else None
        chunk = 4000
        for s0 in range(0, P.shape[0], chunk):
            Q = P[s0 : s0 + chunk]
            ph = Q @ self.K.T
            c, s = np.cos(ph), np.sin(ph)
            # sum_i cos(k.(x - x_i)) = cos(kx) Sc + sin(kx) Ss
            val = c * self.Sc + s * self.Ss
            out[s0 : s0 + chunk] = val @ self.kw
            if grad:
                dval = -s * self.Sc + c * self.Ss
                g[s0 : s0 + chunk] = (dval * self.kw) @ self.K
        return out, g

    def value(self, P: np.ndarray) -> np.ndarray:
        r, _ = self._real(P, False)
        k, _ = self._rec(P, False)
        return r + k + self.const

    def gradient(self, P: np.ndarray) -> np.ndarray:
        _, gr = self._real(P, True)
        _, gk = self._rec(P, True)
        return gr + gk


# ---------------------------------------------------------------- structures


def sc() -> Structure:
    return Structure("sc", np.eye(3), np.zeros((1, 3))).scaled_to_unit_density()


def bcc() -> Structure:
    A = 0.5 * np.array([[-1.0, 1, 1], [1, -1, 1], [1, 1, -1]])
    return Structure("bcc", A, np.zeros((1, 3))).scaled_to_unit_density()


def fcc() -> Structure:
    A = 0.5 * np.array([[0.0, 1, 1], [1, 0, 1], [1, 1, 0]])
    return Structure("fcc", A, np.zeros((1, 3))).scaled_to_unit_density()


def hcp(c_over_a: float = math.sqrt(8.0 / 3.0)) -> Structure:
    A = np.array([[1.0, 0, 0], [-0.5, math.sqrt(3) / 2, 0], [0, 0, c_over_a]])
    F = np.array([[1 / 3, 2 / 3, 0.25], [2 / 3, 1 / 3, 0.75]])
    return Structure("hcp", A, F).scaled_to_unit_density()


def a15() -> Structure:
    """A15 (Cr3Si / beta-W) sites: the Weaire-Phelan foam is its Voronoi tessellation."""
    F = [[0, 0, 0], [0.5, 0.5, 0.5]]
    F += [[0.25, 0.5, 0], [0.75, 0.5, 0], [0, 0.25, 0.5], [0, 0.75, 0.5], [0.5, 0, 0.25], [0.5, 0, 0.75]]
    return Structure("A15", np.eye(3), np.array(F, dtype=float)).scaled_to_unit_density()


def c15() -> Structure:
    """C15 Laves (MgCu2), 24 sites per cubic cell, origin choice 2 style coordinates."""
    fcc_t = np.array([[0, 0, 0], [0, 0.5, 0.5], [0.5, 0, 0.5], [0.5, 0.5, 0]])
    mg = np.array([[0, 0, 0], [0.25, 0.25, 0.25]])
    cu = np.array([[5 / 8, 5 / 8, 5 / 8], [5 / 8, 7 / 8, 7 / 8], [7 / 8, 5 / 8, 7 / 8], [7 / 8, 7 / 8, 5 / 8]])
    pts = [(t + b) % 1.0 for t in fcc_t for b in np.vstack([mg, cu])]
    return Structure("C15", np.eye(3), np.array(pts)).scaled_to_unit_density()


def supercell(st: Structure, reps: tuple[int, int, int]) -> Structure:
    F = []
    for i, j, k in itertools.product(range(reps[0]), range(reps[1]), range(reps[2])):
        F.append((st.F + np.array([i, j, k])) / np.array(reps, dtype=float))
    A = st.A * np.array(reps, dtype=float)[:, None]
    return Structure(f"{st.name}x{reps[0]}{reps[1]}{reps[2]}", A, np.vstack(F))


def perturbed(st: Structure, amp: float, seed: int) -> Structure:
    """Gaussian displacement with rms per coordinate = amp (Cartesian, unit density units)."""
    rng = np.random.default_rng(seed)
    X = st.cart() + amp * rng.standard_normal((st.n, 3))
    F = X @ np.linalg.inv(st.A)
    return Structure(f"{st.name}+pert{amp}", st.A.copy(), F % 1.0)


def poisson(n: int, seed: int) -> Structure:
    rng = np.random.default_rng(seed)
    L = n ** (1.0 / 3.0)
    return Structure(f"poisson{n}", np.eye(3) * L, rng.random((n, 3)))


# ---------------------------------------------------------------- Voronoi


@dataclass
class Cell:
    site: np.ndarray
    faces: list[np.ndarray]  # ordered polygon vertices (cartesian)
    neighbors: list[np.ndarray]  # neighbor site positions, one per face


def voronoi_cells(st: Structure, area_tol: float = 1e-9, vtx_tol: float = 1e-7) -> list[Cell]:
    X = st.cart()
    shifts = np.array(list(itertools.product((-1, 0, 1), repeat=3)), dtype=float) @ st.A
    P = (X[None, :, :] + shifts[:, None, :]).reshape(-1, 3)
    central0 = 13 * st.n  # shift (0,0,0) is index 13 in product order
    vor = Voronoi(P, qhull_options="Qbb Qc Qz")
    cells: list[Cell] = []
    face_lists: dict[int, list[tuple[np.ndarray, np.ndarray]]] = {i: [] for i in range(st.n)}
    for (a, b), rv in zip(vor.ridge_points, vor.ridge_vertices):
        for me, other in ((a, b), (b, a)):
            if central0 <= me < central0 + st.n:
                if -1 in rv:
                    raise RuntimeError("unbounded ridge for a central site; replica too small")
                V = vor.vertices[rv]
                face_lists[me - central0].append((V, P[other]))
    for i in range(st.n):
        site = X[i]
        faces, nbrs = [], []
        for V, q in face_lists[i]:
            # order polygon around its centroid in the bisector plane
            nrm = (q - site) / np.linalg.norm(q - site)
            c = V.mean(0)
            u = V[0] - c
            if np.linalg.norm(u) < 1e-14:
                continue
            u = u - nrm * (u @ nrm)
            u /= np.linalg.norm(u)
            w = np.cross(nrm, u)
            ang = np.arctan2((V - c) @ w, (V - c) @ u)
            V = V[np.argsort(ang)]
            # merge near-duplicate consecutive vertices (degenerate Voronoi vertices)
            keep = [V[0]]
            for v in V[1:]:
                if np.linalg.norm(v - keep[-1]) > vtx_tol:
                    keep.append(v)
            if len(keep) > 1 and np.linalg.norm(keep[0] - keep[-1]) <= vtx_tol:
                keep.pop()
            V = np.array(keep)
            if V.shape[0] < 3:
                continue
            area = polygon_area(V, nrm)
            if area < area_tol:
                continue
            faces.append(V)
            nbrs.append(q)
        cells.append(Cell(site, faces, nbrs))
    return cells


def polygon_area(V: np.ndarray, nrm: np.ndarray) -> float:
    s = np.zeros(3)
    for k in range(V.shape[0]):
        s += np.cross(V[k], V[(k + 1) % V.shape[0]])
    return 0.5 * abs(float(s @ nrm))


def cell_stats(cell: Cell) -> dict[str, float]:
    """Face count f, sum_F (6 - n_F), volume, second moment about the site, centroid offset."""
    f = len(cell.faces)
    nsum = sum(F.shape[0] for F in cell.faces)
    vol = 0.0
    m2 = 0.0
    first = np.zeros(3)
    o = cell.site
    for F in cell.faces:
        c = F.mean(0)
        for k in range(F.shape[0]):
            v1, v2, v3 = F[k] - o, F[(k + 1) % F.shape[0]] - o, c - o
            tv = abs(float(np.dot(v1, np.cross(v2, v3)))) / 6.0
            vs = [np.zeros(3), v1, v2, v3]
            ssum = sum(v @ v for v in vs) + float(np.sum(vs, axis=0) @ np.sum(vs, axis=0))
            m2 += tv / 20.0 * ssum
            vol += tv
            first += tv * (v1 + v2 + v3) / 4.0
    return {
        "faces": f,
        "euler_weight": 6 * f - nsum,
        "volume": vol,
        "second_moment_site": m2,
        "centroid_offset": float(np.linalg.norm(first / vol)),
    }
