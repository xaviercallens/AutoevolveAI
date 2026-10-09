"""Tests for anse.memory.tpu_index.ExactIndex (runs on whatever JAX backend is present)."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("jax")
from hypothesis import given, settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

from anse.memory.tpu_index import ExactIndex  # noqa: E402


def _brute(mat: np.ndarray, q: np.ndarray, k: int) -> np.ndarray:
    m = mat.astype(np.float64)
    m /= np.linalg.norm(m, axis=1, keepdims=True)
    qq = q.astype(np.float64)
    qq /= np.linalg.norm(qq, axis=1, keepdims=True)
    return np.argsort(-(qq @ m.T), axis=1)[:, :k]


def test_matches_float64_brute_force() -> None:
    rng = np.random.default_rng(1)
    mat, q = rng.normal(size=(300, 32)), rng.normal(size=(20, 32))
    got, sims = ExactIndex(mat).search(q, 5)
    assert np.array_equal(got, _brute(mat, q, 5))
    assert np.all(np.diff(sims, axis=1) <= 1e-7)


def test_exclude_removes_self_match() -> None:
    rng = np.random.default_rng(2)
    mat = rng.normal(size=(50, 16))
    idx = ExactIndex(mat)
    plain, _ = idx.search(mat[:5], 3)
    excl, _ = idx.search(mat[:5], 3, exclude=np.arange(5))
    assert np.array_equal(plain[:, 0], np.arange(5))
    assert not np.any(excl == np.arange(5)[:, None])


def test_wrong_neighbour_expectation_is_detected() -> None:
    rng = np.random.default_rng(3)
    mat = rng.normal(size=(100, 16))
    got, _ = ExactIndex(mat).search(mat[:10], 1, exclude=np.arange(10))
    assert not np.array_equal(got[:, 0], np.arange(10))


@pytest.mark.parametrize(("vectors", "msg"), [(np.zeros((0, 4)), "non-empty"), (np.zeros((3, 4)), "zero vector")])
def test_bad_index_input_rejected(vectors: np.ndarray, msg: str) -> None:
    with pytest.raises(ValueError, match=msg):
        ExactIndex(vectors)


def test_bad_queries_rejected() -> None:
    idx = ExactIndex(np.eye(4))
    with pytest.raises(ValueError, match="dim"):
        idx.search(np.ones((1, 3)), 1)
    with pytest.raises(ValueError, match="out of range"):
        idx.search(np.ones((1, 4)), 5)
    with pytest.raises(ValueError, match="zero query"):
        idx.search(np.zeros((1, 4)), 1)


@settings(max_examples=25, deadline=None)
@given(st.integers(min_value=2, max_value=40), st.integers(min_value=2, max_value=12), st.integers(0, 10_000))
def test_every_stored_vector_is_its_own_nearest_neighbour(n: int, d: int, seed: int) -> None:
    mat = np.random.default_rng(seed).normal(size=(n, d))
    got, _ = ExactIndex(mat).search(mat, 1)
    assert np.array_equal(got[:, 0], np.arange(n))
