"""Analysis pipeline for laboratory tests of planar universal optimality (protocols L1-L4 of the paper).

Input: tracked 2D particle positions (one frame per CSV, columns x,y, any length unit), e.g. exported from
trackpy. The script rescales to density 1 using the measured interior density, then computes the same observables
as the simulation code (rusty-SUNDIALS qf-yukawa-crystal):
  coordination by neighbours within 1.35 d0 (d0 = median nearest-neighbour distance), defect fraction, local and
  global |psi6|; and the interaction energy per interior particle for a chosen law, compared with the triangular
  lattice value at the same density (the theorem's prediction is e_measured >= e_tri, up to the thermal excess).

Laws: dipolar (r^-3, superparamagnetic colloids; Riesz s = 3), yukawa:<kappa> (exp(-kappa r)/r, dusty plasma or
charged colloids). The open field of view has no periodic images, so energies are per-particle sums over neighbours
within r_cut, for particles at least r_cut from the field-of-view edge; the triangular reference is computed the same
way on a synthetic lattice of the same density.

Usage:
  python lab_analysis.py frame.csv --law dipolar [--rcut 8]
  python lab_analysis.py --selftest
"""
from __future__ import annotations

import argparse
import json
import math
import sys

import numpy as np
from scipy.spatial import cKDTree


def pair_law(law: str):
    if law == "dipolar":
        return lambda r: r ** -3.0
    if law.startswith("yukawa:"):
        k = float(law.split(":")[1])
        return lambda r: np.exp(-k * r) / r
    raise ValueError(f"unknown law {law}")


def interior_mask(x: np.ndarray, margin: float) -> np.ndarray:
    lo, hi = x.min(axis=0) + margin, x.max(axis=0) - margin
    return np.all((x >= lo) & (x <= hi), axis=1)


def voronoi_density(x: np.ndarray, mask: np.ndarray) -> float:
    """Density = 1 / mean Voronoi cell area of the masked particles (exact for a lattice; a bounding-box estimate is
    biased by the edge half-cell, which the self-test caught)."""
    from scipy.spatial import ConvexHull, Voronoi

    vor = Voronoi(x)
    areas = []
    for i in np.flatnonzero(mask):
        reg = vor.regions[vor.point_region[i]]
        if reg and -1 not in reg:
            areas.append(ConvexHull(vor.vertices[reg]).volume)
    return 1.0 / float(np.mean(areas))


def to_density_one(x: np.ndarray, rcut: float) -> tuple[np.ndarray, float, np.ndarray]:
    """Rescale so that the density of the ENERGY-MASK particles (those at least rcut from the field-of-view edge,
    in density-1 units) is 1. Two passes: a central-region estimate fixes the units, then the density is
    re-estimated on the energy mask itself, so density and energy refer to the same particles."""
    c = x.mean(axis=0)
    span = x.max(axis=0) - x.min(axis=0)
    central = np.all(np.abs(x - c) <= span / 4, axis=1)
    rho = voronoi_density(x, central)
    for _ in range(2):
        x1 = (x - c) * math.sqrt(rho)
        mask = interior_mask(x1, rcut)
        rho = rho * voronoi_density(x1, mask)  # density of the masked particles, in input units
    x1 = (x - c) * math.sqrt(rho)
    return x1, rho, interior_mask(x1, rcut)


def tail(law: str, rcut: float) -> float:
    """Uniform-density tail of the per-particle energy beyond rcut at density 1: (1/2) int_rcut^inf 2 pi r v(r) dr."""
    if law == "dipolar":
        return math.pi / rcut
    k = float(law.split(":")[1])
    return math.pi * math.exp(-k * rcut) / k


def order(x: np.ndarray, mask: np.ndarray) -> dict:
    tree = cKDTree(x)
    d, _ = tree.query(x, k=2)
    d0 = float(np.median(d[:, 1]))
    nbs = tree.query_ball_point(x, 1.35 * d0)
    coord, psi_loc, re, im = [], [], 0.0, 0.0
    for i in np.flatnonzero(mask):
        nb = [j for j in nbs[i] if j != i]
        coord.append(len(nb))
        if nb:
            dv = x[nb] - x[i]
            z = np.exp(6j * np.arctan2(dv[:, 1], dv[:, 0])).mean()
            psi_loc.append(abs(z))
            re, im = re + z.real, im + z.imag
    n = max(len(coord), 1)
    coord = np.asarray(coord)
    return {"counted": int(len(coord)), "defect_fraction": float((coord != 6).mean()) if len(coord) else None,
            "psi6_local_mean": float(np.mean(psi_loc)) if psi_loc else None,
            "psi6_global": float(math.hypot(re / n, im / n)), "d0": d0}


def energy_per_particle(x: np.ndarray, mask: np.ndarray, law: str, rcut: float) -> float:
    v = pair_law(law)
    tree = cKDTree(x)
    tot, cnt = 0.0, 0
    for i in np.flatnonzero(mask):
        nb = [j for j in tree.query_ball_point(x[i], rcut) if j != i]
        r = np.linalg.norm(x[nb] - x[i], axis=1)
        tot += 0.5 * float(v(r).sum())
        cnt += 1
    return tot / max(cnt, 1)


def triangular_patch(n: int) -> np.ndarray:
    a = math.sqrt(2 / math.sqrt(3))
    pts = [((j + (k % 2) / 2) * a, k * a * math.sqrt(3) / 2) for j in range(n) for k in range(n)]
    return np.asarray(pts)


def square_patch(n: int) -> np.ndarray:
    return np.asarray([(j, k) for j in range(n) for k in range(n)], dtype=float)


def analyse(x: np.ndarray, law: str, rcut: float) -> dict:
    """`law` is 'dipolar' or 'yukawa:<kappa>' with kappa in the INPUT length units; it is converted to density-1
    units internally (kappa_1 = kappa_input / sqrt(rho)). Energies are truncated at rcut (density-1 units) with a
    uniform tail correction; measured and reference are truncated identically. The truncated potential is not exactly
    completely monotone, so the comparison is between equally truncated energies (see the paper's kill criteria)."""
    x1, rho, mask = to_density_one(x, rcut)
    law1 = law
    if law.startswith("yukawa:"):
        law1 = f"yukawa:{float(law.split(':')[1]) / math.sqrt(rho)}"
    ref = triangular_patch(int(2 * math.sqrt(len(x1))) + 2 * int(rcut) + 6)
    ref = ref - ref.mean(axis=0)
    e_tri = energy_per_particle(ref, interior_mask(ref, rcut), law1, rcut)
    e = energy_per_particle(x1, mask, law1, rcut)
    tc = tail(law1, rcut)
    out = {"n": int(len(x)), "measured_density_input_units": rho, "law": law, "law_density1": law1, "rcut": rcut,
           **order(x1, mask), "e_per_particle_truncated": e, "e_tri_truncated": e_tri, "tail_correction": tc,
           "e_per_particle": e + tc, "e_tri_same_density": e_tri + tc, "rel_gap": (e - e_tri) / abs(e_tri + tc),
           "prediction_e_ge_e_tri": bool(e >= e_tri * (1 - 1e-9))}
    return out


def selftest() -> int:
    rng = np.random.default_rng(0)
    ok = True
    tri = triangular_patch(40)
    r_tri = analyse(tri * 3.7, "dipolar", 6.0)  # arbitrary unit: rescaling must not matter
    ok &= r_tri["defect_fraction"] == 0.0 and abs(r_tri["rel_gap"]) < 1e-6
    noisy = triangular_patch(40) + 0.08 * rng.normal(size=(1600, 2))
    r_noisy = analyse(noisy, "dipolar", 6.0)
    ok &= r_noisy["rel_gap"] > 0 and r_noisy["psi6_local_mean"] > 0.8  # thermal noise raises e above e_tri
    sq = square_patch(40)
    r_sq = analyse(sq, "dipolar", 6.0)
    ok &= r_sq["defect_fraction"] == 1.0 and r_sq["rel_gap"] > 0  # negative control: square is detected and costs more
    # Yukawa kappa supplied in input units: a lattice scaled by 3.7 with kappa_input = 2/3.7 must give kappa_1 = 2.
    r_yuk = analyse(tri * 3.7, f"yukawa:{2 / 3.7}", 6.0)
    ok &= abs(float(r_yuk["law_density1"].split(":")[1]) - 2.0) < 1e-9 and abs(r_yuk["rel_gap"]) < 1e-6
    print(json.dumps({"triangular": r_tri, "noisy_triangular": r_noisy, "square": r_sq, "yukawa_units": r_yuk}, indent=1))
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("frame", nargs="?")
    ap.add_argument("--law", default="dipolar")
    ap.add_argument("--rcut", type=float, default=8.0)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    x = np.loadtxt(a.frame, delimiter=",")
    print(json.dumps(analyse(x, a.law, a.rcut), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
