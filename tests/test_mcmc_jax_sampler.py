"""The JAX stretch-move sampler must recover a known Gaussian, and must fail against a wrong expectation."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("jax")
import jax.numpy as jnp  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "desi_dr2_bao"))
from mcmc_jax import sample, summarize  # noqa: E402

MU = np.array([1.0, -2.0])
SIG = np.array([0.5, 2.0])


def _logprob(x):
    return -0.5 * jnp.sum(((x - jnp.asarray(MU, x.dtype)) / jnp.asarray(SIG, x.dtype)) ** 2, axis=1)


def _run(seed: int = 0):
    rng = np.random.default_rng(seed)
    p0 = rng.normal(size=(512, 2)) * 3.0
    chain, acc = sample(_logprob, p0, steps=400, seed=seed)
    return np.asarray(chain), float(np.mean(np.asarray(acc)))


def test_recovers_known_gaussian() -> None:
    chain, acc = _run()
    s = summarize(chain, burn=150, names=["a", "b"])
    assert 0.2 < acc < 0.9
    assert abs(s["mean"]["a"] - MU[0]) < 0.03 * SIG[0] * 10 and abs(s["mean"]["b"] - MU[1]) < 0.06 * SIG[1] * 10
    assert abs(s["std"]["a"] / SIG[0] - 1) < 0.05 and abs(s["std"]["b"] / SIG[1] - 1) < 0.05


def test_wrong_expectation_is_detected() -> None:
    chain, _ = _run()
    s = summarize(chain, burn=150, names=["a", "b"])
    assert abs(s["std"]["a"] / (2 * SIG[0]) - 1) > 0.3  # claiming the wrong width must not pass
    assert abs(s["mean"]["a"] - (MU[0] + 3 * SIG[0])) > 5 * SIG[0] / np.sqrt(512 * 250)


def test_same_seed_is_reproducible() -> None:
    a, _ = _run(3)
    b, _ = _run(3)
    assert np.array_equal(a, b)
