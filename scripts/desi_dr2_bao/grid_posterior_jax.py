#!/usr/bin/env python3
"""JAX/TPU port of the grid_posterior.py likelihood kernel (dr2_model.predict_gl + chi2_vals).

Two stages, so the TPU host needs only jax + numpy (no repo data, scipy or astropy):
  export  (local, repo venv):  python scripts/desi_dr2_bao/grid_posterior_jax.py export OUT.npz
          writes z, kinds, vals, cov_inv per dataset plus a numpy reference loglike on random points.
  run     (any host with jax): python grid_posterior_jax.py run IN.npz [f32]   (default float64)
          positive control: JAX loglike == numpy reference; negative control: shifted params differ;
          then evaluates the full DR2 LCDM / wCDM grids and prints moments and wall time.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

C_KM_S = 299792.458
GL_ORDER = 96
KIND_CODE = {"DM_over_rs": 0, "DH_over_rs": 1, "DV_over_rs": 2}
CHUNK = 16384


def export(out: Path) -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import dr2_model as m

    rng = np.random.default_rng(0)
    arrs: dict[str, np.ndarray] = {}
    for name, ds in (("DR1", m.load_dr1()), ("DR2", m.load_dr2())):
        arrs[f"{name}_z"] = ds.z
        arrs[f"{name}_kinds"] = np.array([KIND_CODE[k] for k in ds.kinds])
        arrs[f"{name}_vals"] = ds.vals
        arrs[f"{name}_cov_inv"] = ds.cov_inv
        n = 2000
        om = rng.uniform(0.2, 0.5, n)
        hrd = rng.uniform(80.0, 120.0, n)
        w = rng.uniform(-1.5, -0.5, n)
        arrs[f"{name}_ref_params"] = np.stack([om, hrd, w], axis=1)
        arrs[f"{name}_ref_loglike"] = -0.5 * m.chi2_vals(ds, np.atleast_2d(m.predict_gl(ds, om, hrd, w, 0.0)))
    for tag, ds, model, n in (("DR2_LCDM", m.load_dr2(), "lcdm", 601), ("DR1_LCDM", m.load_dr1(), "lcdm", 601),
                              ("DR2_wCDM", m.load_dr2(), "wcdm", 141), ("DR1_wCDM", m.load_dr1(), "wcdm", 141)):
        bf = m.fit_chi2_min(ds, model, orad=0.0)
        x = np.array(bf["x"])
        fsig = np.sqrt(np.diag(m.fisher_cov(ds, model, x, orad=0.0)))
        names = ["Om", "h_rd"] if model == "lcdm" else ["Om", "w", "h_rd"]
        for k, name in enumerate(names):
            lo, hi = x[k] - 10.0 * fsig[k], x[k] + 10.0 * fsig[k]
            if name == "Om":
                lo, hi = max(lo, m.PRIOR_OM[0] + 1e-9), min(hi, m.PRIOR_OM[1] - 1e-9)
            elif name == "w":
                lo, hi = max(lo, m.PRIOR_W[0]), min(hi, m.PRIOR_W[1])
            arrs[f"{tag}_axis_{name}"] = np.linspace(lo, hi, n)
    np.savez(out, **arrs)
    print("wrote", out, {k: v.shape for k, v in arrs.items()})


def make_loglike(z: np.ndarray, kinds: np.ndarray, vals: np.ndarray, cov_inv: np.ndarray):
    import jax
    import jax.numpy as jnp

    gx, gw = np.polynomial.legendre.leggauss(GL_ORDER)
    zj, vj, cj = jnp.asarray(z), jnp.asarray(vals), jnp.asarray(cov_inv)
    zp = 0.5 * zj[:, None] * (jnp.asarray(gx)[None, :] + 1.0)
    gwj = jnp.asarray(gw)
    kj = jnp.asarray(kinds)

    @jax.jit
    def loglike(om: jax.Array, hrd: jax.Array, w: jax.Array) -> jax.Array:
        def e_of(zz: jax.Array, o: jax.Array, ww: jax.Array) -> jax.Array:
            zp1 = 1.0 + zz
            return jnp.sqrt(o * zp1**3 + (1.0 - o) * zp1 ** (3.0 * (1.0 + ww)))

        inv_e = 1.0 / e_of(zp[None], om[:, None, None], w[:, None, None])
        integral = 0.5 * zj[None, :] * jnp.einsum("mng,g->mn", inv_e, gwj)
        dm = (C_KM_S / 100.0) * integral / hrd[:, None]
        dh = C_KM_S / (100.0 * e_of(zj[None, :], om[:, None], w[:, None])) / hrd[:, None]
        dv = jnp.cbrt(zj[None, :] * dm**2 * dh)
        pred = jnp.where(kj == 0, dm, jnp.where(kj == 1, dh, dv))
        r = vj - pred
        return -0.5 * jnp.einsum("mi,ij,mj->m", r, cj, r)

    return loglike


def eval_points(fn, om: np.ndarray, hrd: np.ndarray, w: np.ndarray) -> np.ndarray:
    import jax.numpy as jnp

    out = np.empty(om.shape[0])
    for s in range(0, om.shape[0], CHUNK):
        e = slice(s, s + CHUNK)
        out[e] = np.asarray(fn(jnp.asarray(om[e]), jnp.asarray(hrd[e]), jnp.asarray(w[e])))
    return out


def moments(axes: list[np.ndarray], logp: np.ndarray, names: list[str]) -> dict[str, object]:
    p = np.exp(logp - logp.max())
    p /= p.sum()
    mesh = np.meshgrid(*axes, indexing="ij")
    mean = [float(np.sum(p * g)) for g in mesh]
    cov = np.array([[float(np.sum(p * (mesh[i] - mean[i]) * (mesh[j] - mean[j]))) for j in range(len(axes))]
                    for i in range(len(axes))])
    std = np.sqrt(np.diag(cov))
    corr = {f"{names[i]}__{names[j]}": float(cov[i, j] / (std[i] * std[j]))
            for i in range(len(names)) for j in range(i + 1, len(names))}
    return {"mean": dict(zip(names, mean)), "std": dict(zip(names, [float(v) for v in std])), "corr": corr}


def run(npz: Path, f32: bool = False) -> int:
    import jax

    jax.config.update("jax_enable_x64", not f32)
    jax.config.update("jax_default_matmul_precision", "highest")
    print("backend:", jax.default_backend(), jax.devices())
    d = np.load(npz)
    ok = True
    for name in ("DR1", "DR2"):
        fn = make_loglike(d[f"{name}_z"], d[f"{name}_kinds"], d[f"{name}_vals"], d[f"{name}_cov_inv"])
        p, ref = d[f"{name}_ref_params"], d[f"{name}_ref_loglike"]
        got = eval_points(fn, p[:, 0], p[:, 1], p[:, 2])
        err = float(np.max(np.abs(got - ref) / (1.0 + np.abs(ref))))
        neg = eval_points(fn, p[:, 0] + 0.05, p[:, 1], p[:, 2])
        neg_gap = float(np.max(np.abs(neg - ref) / (1.0 + np.abs(ref))))
        passed = err < (1e-3 if f32 else 1e-8) and neg_gap > 1e-3
        ok &= passed
        print(f"{name} positive control max rel err={err:.3e} | negative control gap={neg_gap:.3e} | "
              f"{'PASS' if passed else 'FAIL'}")
    if not ok:
        print("controls failed; not reporting grid numbers")
        return 1

    results: dict[str, object] = {}
    for label in ("DR2_LCDM", "DR1_LCDM", "DR2_wCDM", "DR1_wCDM"):
        ds_tag = label.split("_")[0]
        fn = make_loglike(d[f"{ds_tag}_z"], d[f"{ds_tag}_kinds"], d[f"{ds_tag}_vals"], d[f"{ds_tag}_cov_inv"])
        lcdm = label.endswith("LCDM")
        names = ["Om", "h_rd"] if lcdm else ["Om", "w", "h_rd"]
        axes = [d[f"{label}_axis_{nm}"] for nm in names]
        mesh = [g.ravel() for g in np.meshgrid(*axes, indexing="ij")]
        if lcdm:
            om, hrd, w = mesh[0], mesh[1], np.full(mesh[0].shape, -1.0)
        else:
            om, w, hrd = mesh
        eval_points(fn, om[:CHUNK], hrd[:CHUNK], w[:CHUNK])  # compile
        t0 = time.time()
        logp = eval_points(fn, om, hrd, w).reshape([a.size for a in axes])
        dt = time.time() - t0
        res = moments(axes, logp, names)
        res["grid_chi2_min"] = float(-2 * logp.max())
        res["seconds"], res["points"] = dt, int(om.size)
        results[label] = res
        print(f"{label}: {om.size} pts in {dt:.2f}s mean={res['mean']} std={res['std']}", flush=True)
    Path("grid_summary_jax_f32.json" if f32 else "grid_summary_jax.json").write_text(json.dumps(results, indent=1))
    print("wrote summary json")
    return 0


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4) or sys.argv[1] not in ("export", "run"):
        raise SystemExit(__doc__)
    path = Path(sys.argv[2])
    if sys.argv[1] == "export":
        export(path)
        raise SystemExit(0)
    raise SystemExit(run(path, f32=len(sys.argv) == 4 and sys.argv[3] == "f32"))
