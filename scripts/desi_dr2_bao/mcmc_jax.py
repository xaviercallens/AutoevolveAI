#!/usr/bin/env python3
"""Massively parallel affine-invariant (Goodman-Weare stretch move) ensemble sampler in JAX, for TPU/GPU/CPU.

Same likelihood and flat priors as mcmc_fit.py / grid_posterior.py (kernel from grid_posterior_jax.make_loglike), but
2048 walkers advanced together under lax.scan instead of emcee's 32. Starts from the same initial ball as mcmc_fit.py
(no knowledge of the grid answer). Runs on the npz written by `grid_posterior_jax.py export`.

    python mcmc_jax.py DATA.npz OUT.json [--walkers 2048] [--steps 3000] [--burn 600] [--seed 20260927] [--f32]

Checks reported per run: acceptance fraction, first-half-vs-second-half drift of the post-burn mean (in posterior sigma),
and, with --negative-control, the same run on a deliberately shifted data vector (it must land far from the real answer).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from grid_posterior_jax import make_loglike  # noqa: E402

PRIOR_OM, PRIOR_HRD, PRIOR_W = (0.01, 0.99), (10.0, 1000.0), (-3.0, 1.0)
A_STRETCH = 2.0


def make_logprob(loglike, lcdm: bool):
    def logprob(theta: jax.Array) -> jax.Array:
        om = theta[:, 0]
        w = jnp.full_like(om, -1.0) if lcdm else theta[:, 1]
        hrd = theta[:, 1] if lcdm else theta[:, 2]
        ok = ((om > PRIOR_OM[0]) & (om < PRIOR_OM[1]) & (hrd > PRIOR_HRD[0]) & (hrd < PRIOR_HRD[1])
              & (w >= PRIOR_W[0]) & (w <= PRIOR_W[1]))
        safe = (jnp.where(ok, om, 0.3), jnp.where(ok, hrd, 100.0), jnp.where(ok, w, -1.0))
        return jnp.where(ok, loglike(*safe), -jnp.inf)

    return logprob


def stretch_half(key, x, lp, partners, logprob, ndim):
    n = x.shape[0]
    k1, k2, k3 = jax.random.split(key, 3)
    z = ((A_STRETCH - 1.0) * jax.random.uniform(k1, (n,)) + 1.0) ** 2 / A_STRETCH
    j = jax.random.randint(k2, (n,), 0, partners.shape[0])
    y = partners[j] + z[:, None] * (x - partners[j])
    lpy = logprob(y)
    log_acc = (ndim - 1) * jnp.log(z) + lpy - lp
    acc = jnp.log(jax.random.uniform(k3, (n,))) < log_acc
    return jnp.where(acc[:, None], y, x), jnp.where(acc, lpy, lp), acc


def sample(logprob, p0: np.ndarray, steps: int, seed: int):
    ndim = p0.shape[1]
    x = jnp.asarray(p0, dtype=jnp.float32)
    half = x.shape[0] // 2
    lp = logprob(x)

    def body(carry, key):
        x, lp = carry
        ka, kb = jax.random.split(key)
        xa, lpa, acca = stretch_half(ka, x[:half], lp[:half], x[half:], logprob, ndim)
        xb, lpb, accb = stretch_half(kb, x[half:], lp[half:], xa, logprob, ndim)
        x2, lp2 = jnp.concatenate([xa, xb]), jnp.concatenate([lpa, lpb])
        return (x2, lp2), (x2, jnp.mean(jnp.concatenate([acca, accb]).astype(jnp.float32)))

    keys = jax.random.split(jax.random.PRNGKey(seed), steps)
    (_, _), (chain, acc) = jax.lax.scan(body, (x, lp), keys)
    return chain, acc


def initial_ball(lcdm: bool, n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    c, s = (np.array([0.30, 101.0]), np.array([0.01, 1.0])) if lcdm else \
        (np.array([0.30, -1.0, 101.0]), np.array([0.01, 0.05, 1.0]))
    return c + s * rng.standard_normal((n, len(c)))


def summarize(chain: np.ndarray, burn: int, names: list[str]) -> dict[str, object]:
    post = chain[burn:].reshape(-1, chain.shape[-1]).astype(np.float64)
    mean, std = post.mean(0), post.std(0, ddof=1)
    half = (chain.shape[0] - burn) // 2
    a = chain[burn:burn + half].reshape(-1, chain.shape[-1]).astype(np.float64).mean(0)
    b = chain[burn + half:].reshape(-1, chain.shape[-1]).astype(np.float64).mean(0)
    corr = np.corrcoef(post.T)
    return {"mean": dict(zip(names, mean.tolist())), "std": dict(zip(names, std.tolist())),
            "corr": {f"{names[i]}__{names[j]}": float(corr[i, j]) for i in range(len(names))
                     for j in range(i + 1, len(names))},
            "half_drift_sigma": dict(zip(names, (np.abs(a - b) / std).tolist())), "n_post": int(post.shape[0])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("data", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--walkers", type=int, default=2048)
    ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--burn", type=int, default=600)
    ap.add_argument("--seed", type=int, default=20260927)
    ap.add_argument("--f32", action="store_true")
    ap.add_argument("--negative-control", action="store_true")
    a = ap.parse_args()
    jax.config.update("jax_enable_x64", not a.f32)
    jax.config.update("jax_default_matmul_precision", "highest")
    print("backend", jax.default_backend(), jax.devices())
    d = np.load(a.data)
    results: dict[str, object] = {"backend": jax.default_backend(), "walkers": a.walkers, "steps": a.steps,
                                  "burn": a.burn, "seed": a.seed, "f32": a.f32, "runs": {}}
    for label in ("DR2_LCDM", "DR1_LCDM", "DR2_wCDM", "DR1_wCDM"):
        tag, lcdm = label.split("_")[0], label.endswith("LCDM")
        names = ["Om", "h_rd"] if lcdm else ["Om", "w", "h_rd"]
        runs = [(label, d[f"{tag}_vals"])]
        if a.negative_control and label == "DR2_LCDM":
            shifted = d[f"{tag}_vals"].copy()
            shifted[:] *= 1.05  # 5% wrong data: posterior must move
            runs.append((label + "_NEGCTRL_vals_x1.05", shifted))
        for name, vals in runs:
            lp = make_logprob(make_loglike(d[f"{tag}_z"], d[f"{tag}_kinds"], vals, d[f"{tag}_cov_inv"]), lcdm)
            p0 = initial_ball(lcdm, a.walkers, a.seed)
            run = jax.jit(lambda p: sample(lp, p, a.steps, a.seed))
            jax.block_until_ready(run(jnp.asarray(p0, jnp.float32)))  # compile
            t0 = time.time()
            chain, acc = run(jnp.asarray(p0, jnp.float32))
            chain = np.asarray(jax.block_until_ready(chain))
            dt = time.time() - t0
            s = summarize(chain, a.burn, names)
            s.update(seconds=dt, acceptance=float(np.mean(np.asarray(acc)[a.burn:])),
                     evals_per_s=a.walkers * a.steps / dt)
            results["runs"][name] = s  # type: ignore[index]
            print(f"{name}: {dt:.1f}s acc={s['acceptance']:.2f} mean={ {k: round(v, 4) for k, v in s['mean'].items()} } "
                  f"std={ {k: round(v, 4) for k, v in s['std'].items()} } drift={ {k: round(v, 3) for k, v in s['half_drift_sigma'].items()} }",
                  flush=True)
    a.out.write_text(json.dumps(results, indent=1))
    print("wrote", a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
