"""N3: can a 2D-style glued trial potential reproduce the bcc Green function exactly?

In the 2D proof the square term (1/2) int |grad(h - H)|^2 vanishes at the triangular lattice because, in each
Voronoi sector, h_tri is a function of (r, t) only (cos(6m phi) = T_{6m}(d/t)). This script measures, for the
bcc Green function h (-Delta h = 4 pi (delta - 1), unit density), rigorous LOWER bounds on the 3D square term
(1/8 pi) int |grad(h - H)|^2 (per particle, same units as the jellium energy) for three trial classes:

  radial : H = H(r) in each cell                      -> slack >= (1/8pi) int_C |grad_tan h|^2
  axial  : H = H(r, angle to the face normal) per face pyramid (the literal 3D transcription of the 2D
           sector ansatz H = B(r) + sum (r/t)^k D(t))  -> slack >= (1/8pi) int_C (e_psi . grad h)^2
  hier   : H built from piece-intrinsic data of in-face sectors (no neighbour-edge data); on the regular
           hexagonal faces the six in-face sectors are congruent, so H is invariant under the 60-degree
           rotation R about the face normal  -> slack >= (1/8pi) int_{hex pyramids} |grad(h - (h + h o R)/2)|^2

Each lower bound is the squared Dirichlet distance from h to a closed subspace containing the trial class
(orthogonal projection / isometric group average), so it is a valid lower bound for every member of the class.

Comparison scale: fcc - bcc = 8.97e-5 per particle (n1_energies.json).

Controls:
  positive: Wigner-Seitz radial field 1/r + (2pi/3) r^2 gives zero for all three bounds;
            finite-difference Laplacian of the Ewald h equals 4 pi off the sites;
            symmetry: hex-face trace has no cos(psi), cos(2 psi) content; square-face trace none below cos(4 psi).
  2D reference: the same radial bound for h_tri (manuscript series) vs the 2D square-triangular gap, and the
            2D axial analogue is identically zero (cos(k phi) is even in each sector).
Tier X: quasi-Monte Carlo quadrature in floating point.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Callable

import numpy as np
from scipy.stats import qmc

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ewald3d as ew  # noqa: E402

OUT = Path(__file__).resolve().parent / "n3_green_obstruction.json"


def rot_about(axis: np.ndarray, ang: float) -> np.ndarray:
    a = axis / np.linalg.norm(axis)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * K @ K


def bcc_geometry() -> tuple[float, np.ndarray, np.ndarray]:
    a = 2.0 ** (1.0 / 3.0)  # conventional cube edge at unit density
    hexn = np.array([[sx, sy, sz] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)], dtype=float) * a / 2
    sqn = np.vstack([np.eye(3) * a, -np.eye(3) * a])
    return a, hexn, sqn


def sample_cell(n_pow: int, seed: int) -> tuple[np.ndarray, np.ndarray, float]:
    a, hexn, sqn = bcc_geometry()
    Q = np.vstack([hexn, sqn])
    sob = qmc.Sobol(d=3, scramble=True, seed=seed)
    U = (sob.random_base2(n_pow) - 0.5) * a  # cube [-a/2, a/2]^3, volume a^3 = 2
    s = (U @ Q.T) / (0.5 * np.einsum("ij,ij->i", Q, Q))[None, :]
    face = np.argmax(s, axis=1)
    inside = s[np.arange(U.shape[0]), face] <= 1.0
    w = a**3 / U.shape[0]
    return U[inside], face[inside], w


def bounds_for_gradient(gradf: Callable[[np.ndarray], np.ndarray], P: np.ndarray, face: np.ndarray, w: float, hex_rot_pairs: bool) -> dict[str, float]:
    a, hexn, sqn = bcc_geometry()
    Q = np.vstack([hexn, sqn])
    G = gradf(P)
    r = np.linalg.norm(P, axis=1)
    rhat = P / r[:, None]
    gt = G - (np.einsum("ij,ij->i", G, rhat))[:, None] * rhat
    rad = np.einsum("ij,ij->i", gt, gt)
    axis = Q[face] / np.linalg.norm(Q[face], axis=1)[:, None]
    epsi = np.cross(axis, P)
    nrm = np.linalg.norm(epsi, axis=1)
    ok = nrm > 1e-12
    epsi[ok] /= nrm[ok, None]
    ax = np.einsum("ij,ij->i", epsi, G) ** 2
    ax[~ok] = 0.0
    c = 1.0 / (8.0 * math.pi)
    out = {
        "radial_lb": c * w * float(rad.sum()),
        "axial_lb": c * w * float(ax.sum()),
        "radial_lb_mc_se": c * w * float(rad.std()) * math.sqrt(rad.size),
        "axial_lb_mc_se": c * w * float(ax.std()) * math.sqrt(ax.size),
    }
    if hex_rot_pairs:
        hier = np.zeros(P.shape[0])
        for j in range(8):
            m = face == j
            if not np.any(m):
                continue
            R = rot_about(Q[j], math.pi / 3)
            Pr = P[m] @ R.T
            Gr = gradf(Pr) @ R  # R^T grad h(R x), row-vector form
            dlt = 0.5 * (G[m] - Gr)
            hier[m] = np.einsum("ij,ij->i", dlt, dlt)
        out["hier_lb"] = c * w * float(hier.sum())
        out["hier_lb_mc_se"] = c * w * float(hier.std()) * math.sqrt(hier.size)
        # The axial class (H depends on r and the polar angle about the face normal) is D6-invariant on each
        # hex pyramid, hence contained in the hier class there: the D6 bound also bounds the axial slack.
        # Squared Dirichlet distances add over disjoint pyramids, so a valid combined axial lower bound is
        #   max(D6 bound, azimuthal bound) on hex pyramids + azimuthal bound on square pyramids.
        hexm = face < 8
        ax_hex = c * w * float(ax[hexm].sum())
        ax_sq = c * w * float(ax[~hexm].sum())
        out["axial_lb_hex_share"] = ax_hex
        out["axial_lb_square_share"] = ax_sq
        out["axial_lb_combined"] = max(out["hier_lb"], ax_hex) + ax_sq
    return out


def face_traces(pot: ew.Potential) -> dict[str, object]:
    a, hexn, sqn = bcc_geometry()
    res: dict[str, object] = {}
    psi = np.linspace(0, 2 * math.pi, 720, endpoint=False)
    for label, q, frac in (("hex", hexn[7], (0.3, 0.6, 0.9)), ("square", sqn[0], (0.3, 0.6, 0.9))):
        n = q / np.linalg.norm(q)
        d = np.linalg.norm(q) / 2
        u = np.cross(n, [0.0, 0.0, 1.0]) if abs(n[2]) < 0.9 else np.cross(n, [1.0, 0.0, 0.0])
        u /= np.linalg.norm(u)
        v = np.cross(n, u)
        inr = (a * math.sqrt(2) / 4) * math.sqrt(3) / 2 if label == "hex" else a * math.sqrt(2) / 8  # edge a*sqrt2/4
        rows = []
        for fr in frac:
            rho = fr * inr
            P = d * n + rho * (np.cos(psi)[:, None] * u + np.sin(psi)[:, None] * v)
            hv = pot.value(P)
            coef = {f"cos{k}": float(2 * np.mean(hv * np.cos(k * psi))) for k in range(1, 9)}
            coef.update({f"sin{k}": float(2 * np.mean(hv * np.sin(k * psi))) for k in range(1, 9)})
            amp = {k: math.hypot(coef[f"cos{k}"], coef[f"sin{k}"]) for k in range(1, 9)}
            rows.append(
                {
                    "rho_over_inradius": fr,
                    "t": math.hypot(d, rho),
                    "trace_max_minus_min": float(hv.max() - hv.min()),
                    "fourier_amplitudes": amp,
                }
            )
        res[label] = {"d": d, "inradius": inr, "circles": rows}
    return res


def laplacian_check(pot: ew.Potential) -> float:
    x0 = np.array([[0.21, -0.13, 0.17]])
    h = 1e-3
    lap = -6 * pot.value(x0)
    for k in range(3):
        e = np.zeros(3)
        e[k] = h
        lap = lap + pot.value(x0 + e) + pot.value(x0 - e)
    return float(lap[0] / h**2)


def cubic_coefficient(pot: ew.Potential) -> dict[str, float]:
    """Fit h - 1/r - (2pi/3) r^2 = C + c4 r^4 K4 + c6 r^6 K6 on small spheres (degree-4 cubic harmonic)."""
    rng = np.random.default_rng(0)
    rows, rhs = [], []
    for r in (0.08, 0.12, 0.16, 0.2):
        Wd = rng.standard_normal((400, 3))
        Wd /= np.linalg.norm(Wd, axis=1)[:, None]
        P = r * Wd
        x, y, z = Wd.T
        K4 = x**4 + y**4 + z**4 - 0.6
        K6 = x**6 + y**6 + z**6 + 30 * (x * y * z) ** 2 * 0 - (3.0 / 7.0)  # not orthogonal; fitted jointly
        rows.append(np.column_stack([np.ones_like(x), r**4 * K4, r**6 * K6, r**6 * (x * y * z) ** 2]))
        rhs.append(pot.value(P) - 1 / r - (2 * math.pi / 3) * r**2)
    A = np.vstack(rows)
    b = np.concatenate(rhs)
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    resid = float(np.max(np.abs(A @ sol - b)))
    return {"C_regular": float(sol[0]), "c4": float(sol[1]), "fit_max_residual": resid}


def two_d_reference(n_pts: int = 400000) -> dict[str, float]:
    """2D: radial-only slack of h_tri on its hexagon vs the 2D square-triangular gap (manuscript units)."""
    a = math.sqrt(2 / math.sqrt(3))
    w1 = a * 1.0
    w2 = a * complex(0.5, math.sqrt(3) / 2)
    pts = np.array([m * w1 + n * w2 for m in range(-60, 61) for n in range(-60, 61) if (m, n) != (0, 0)])
    cm = {}
    for mm in range(1, 30):
        k = 6 * mm
        cm[mm] = float(np.real(np.sum(pts ** (-k))) / k)
    p = a / 2
    R0 = 2 * p / math.sqrt(3)
    rng = np.random.default_rng(3)
    Z = (rng.random(n_pts) - 0.5) * 2 * R0 + 1j * (rng.random(n_pts) - 0.5) * 2 * R0
    # inside hexagon: |Re(z e^{-i k pi/3})| <= p for k=0,1,2 (normal along real axis)
    ins = np.ones(n_pts, bool)
    for kk in range(3):
        ins &= np.abs(np.real(Z * np.exp(-1j * kk * math.pi / 3))) <= p
    Z = Z[ins]
    area_box = (2 * R0) ** 2
    w = area_box / n_pts
    r = np.abs(Z)
    ph = np.angle(Z)
    tang = np.zeros(Z.size)
    for mm, c in cm.items():
        k = 6 * mm
        tang += -c * k * r ** (k - 1) * np.sin(k * ph)
    slack_rad = 0.5 * w * float(np.sum(tang**2))
    return {
        "c1": cm[1],
        "hexagon_area_mc": float(w * Z.size),
        "radial_lb_2d": slack_rad,
        "gap_square_minus_tri_2d": -4.1171606 + 4.1504128077,
        "ratio_radial_lb_over_gap_2d": slack_rad / (-4.1171606 + 4.1504128077),
        "axial_lb_2d": 0.0,
        "axial_note": "identically zero: in each sector h_tri = gamma(r) + sum c_m r^{6m} T_{6m}(d/t) (manuscript Sec. 4.2)",
    }


def main() -> None:
    res: dict[str, object] = {}
    st = ew.bcc()
    pot = ew.Potential(st, alpha=2.4)
    res["laplacian_fd_off_site"] = {"value": laplacian_check(pot), "expected": 4 * math.pi}
    print("lap", res["laplacian_fd_off_site"], flush=True)
    # finite-difference gradient check
    x0 = np.array([[0.11, 0.23, -0.07]])
    g = pot.gradient(x0)[0]
    fd = [(pot.value(x0 + 1e-5 * e) - pot.value(x0 - 1e-5 * e))[0] / 2e-5 for e in np.eye(3)]
    res["gradient_fd_max_abs_dev"] = float(np.max(np.abs(g - np.array(fd))))
    res["cubic_fit"] = cubic_coefficient(pot)
    print("cubic", res["cubic_fit"], flush=True)
    res["face_traces"] = face_traces(pot)
    print("traces done", flush=True)

    def ws_grad(P: np.ndarray) -> np.ndarray:
        r = np.linalg.norm(P, axis=1)[:, None]
        return -P / r**3 + (4 * math.pi / 3) * P

    reps = []
    for seed in (11, 12):
        P, face, w = sample_cell(19, seed)
        b = bounds_for_gradient(pot.gradient, P, face, w, True)
        b["seed"] = seed
        b["n_points_in_cell"] = int(P.shape[0])
        b["cell_volume_mc"] = w * P.shape[0]
        reps.append(b)
        print("bounds", b, flush=True)
        if seed == 11:
            res["positive_control_ws_radial_field"] = bounds_for_gradient(ws_grad, P, face, w, True)
            print("ws", res["positive_control_ws_radial_field"], flush=True)
    res["bcc_bounds_replicates"] = reps
    gap = 8.969424e-05
    res["gap_fcc_minus_bcc"] = gap
    for key in ("radial_lb", "axial_lb", "hier_lb", "axial_lb_hex_share", "axial_lb_square_share", "axial_lb_combined"):
        m = float(np.mean([r[key] for r in reps]))
        res[f"{key}_mean"] = m
        res[f"{key}_over_gap"] = m / gap
    res["two_d_reference"] = two_d_reference()
    print("2d", res["two_d_reference"], flush=True)
    OUT.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
