"""B1 controls.

usage: python -I b1_controls.py OUT.json

Positive control 1 (frozen phonon): for a supercell of M x M cells with displacements u_j = eps e cos(k.R_j), the second
difference [E(eps) + E(-eps) - 2 E(0)] / eps^2 of the explicit pair-sum energy per particle (values of V only, all
periodic images) must equal (1/2) e^T D(k) e from the reciprocal-space (Poisson) D used everywhere in B1.
Positive control 2 (BZ quadrature of the Lindemann integrand): <tr D^{-1/2}> by Duffy N = 16..128 vs uniform
half-shifted grids n = 64..1024; the uniform error must decay like n^-1 (1/|k| singularity at Gamma) toward the
Duffy value.
Negative control (planted bug): dropping the Gamma-subtraction term of D (pg.C0 = 0) must break control 1.
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import b1_lib as L  # noqa: E402


def supercell_energy(a: float, x: float, y: float, M: int, disp: np.ndarray) -> float:
    A, _ = L.bases(x, y)
    ii, jj = np.meshgrid(np.arange(M), np.arange(M), indexing="ij")
    pos = ii.reshape(-1, 1) * A[0] + jj.reshape(-1, 1) * A[1] + disp
    S = M * A
    rcut = math.sqrt(L.TOL_EXP / (math.pi * a)) + 1.0
    T = L.lattice_points(S, rcut + M * (np.linalg.norm(A[0]) + np.linalg.norm(A[1])) + 1)
    T = np.vstack([T, np.zeros((1, 2))]) if not np.any(np.all(np.abs(T) < 1e-12, axis=1)) else T
    N = len(pos)
    E = 0.0
    for i in range(N):
        d = pos[i][None, None, :] - pos[None, :, :] - T[:, None, :]  # (NT, N, 2)
        r2 = (d**2).sum(-1)
        r2[np.abs(r2) < 1e-20] = np.inf  # self term
        E += float(np.exp(-math.pi * a * r2).sum())
    return 0.5 * E / N


def frozen_phonon(a: float, x: float, y: float, M: int, i: int, j: int, e: np.ndarray, bug: str = "") -> dict:
    A, Xi = L.bases(x, y)
    kap = (i / M) * Xi[0] + (j / M) * Xi[1]
    k = 2 * math.pi * kap
    ii, jj = np.meshgrid(np.arange(M), np.arange(M), indexing="ij")
    R = ii.reshape(-1, 1) * A[0] + jj.reshape(-1, 1) * A[1]
    c = np.cos(R @ k)
    eps = 1e-3
    E0 = supercell_energy(a, x, y, M, np.zeros_like(R))
    Ep = supercell_energy(a, x, y, M, eps * c[:, None] * e[None, :])
    Em = supercell_energy(a, x, y, M, -eps * c[:, None] * e[None, :])
    fd = (Ep + Em - 2 * E0) / eps**2
    pg = L.PoissonGauss(a, x, y)
    if bug == "drop_c0":
        pg.C0 = np.zeros(3)
    D = pg.D(kap.reshape(1, 2))[0]
    Dm = np.array([[D[0], D[1]], [D[1], D[2]]])
    pred = 0.5 * float(e @ Dm @ e) * 2 * float((c * c).mean())  # mean cos^2 = 1/2 for generic k
    return {"a": a, "tau": [x, y], "M": M, "ij": [i, j], "e": e.tolist(), "fd": fd, "pred": pred, "rel": abs(fd - pred) / abs(pred)}


def main() -> None:
    out = sys.argv[1]
    res: dict = {"frozen_phonon": [], "frozen_phonon_bug": [], "lindemann_quadrature": []}
    cases = [(1.0, 0.5, L.S3 / 2), (1.0, 0.3, 0.96), (0.5, 0.5, L.S3 / 2), (1.4, 0.45, 0.89)]
    for a, x, y in cases:
        for (i, j), e in (((1, 0), np.array([1.0, 0.0])), ((1, 2), np.array([0.6, 0.8])), ((2, 1), np.array([0.0, 1.0]))):
            r = frozen_phonon(a, x, y, 6, i, j, e)
            res["frozen_phonon"].append(r)
            print("FP", r, flush=True)
    r = frozen_phonon(1.0, 0.5, L.S3 / 2, 6, 1, 2, np.array([0.6, 0.8]), bug="drop_c0")
    res["frozen_phonon_bug"].append(r)
    print("FP bug", r, flush=True)
    res["frozen_phonon_max_rel"] = max(r["rel"] for r in res["frozen_phonon"])
    for a in (0.5, 1.0):
        pg = L.PoissonGauss(a, *L.RHO)
        duf = {N: L.u2_harmonic_per_lam(a, *L.RHO, N) for N in (16, 32, 64, 128)}
        uni = {}
        for n in (64, 128, 256, 512, 1024):
            idx = ((np.arange(n) + 0.5) / n + 0.5) % 1.0 - 0.5
            uu, vv = np.meshgrid(idx, idx, indexing="ij")
            D = pg.D(pg.kappa(uu.ravel(), vv.ravel()))
            uni[n] = 0.5 * float(L.tr_inv_sqrt(D).mean())
        ref = duf[128]
        errs = {n: ref - uni[n] for n in uni}
        p = [math.log(errs[n] / errs[2 * n]) / math.log(2) for n in (64, 128, 256, 512)]
        row = {"a": a, "duffy": duf, "uniform_shifted": uni, "uniform_error_vs_duffy128": errs, "observed_order": p}
        res["lindemann_quadrature"].append(row)
        print("LQ", row, flush=True)
    json.dump(res, open(out, "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
