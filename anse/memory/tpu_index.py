"""Exact cosine nearest-neighbour search for LTM embeddings, in JAX (TPU, GPU or CPU).

Chroma's HNSW index is approximate; at LTM scale (<= ~1e6 vectors of dim 384-1024) an exact
brute-force matmul + top-k is cheap on an accelerator and gives ground truth. `ExactIndex` keeps
a unit-normalised matrix on the device and answers batched queries. Distances are cosine
similarities (inner product of unit vectors), highest first.

Precision note (measured on TPU v5e): float32 matmuls run at reduced precision by default
(~2e-3 relative error), which can reorder near-ties; this module always uses
`jax.default_matmul_precision("highest")`.
"""

from __future__ import annotations

import numpy as np


class ExactIndex:
    def __init__(self, vectors: np.ndarray) -> None:
        import jax.numpy as jnp

        if vectors.ndim != 2 or vectors.shape[0] == 0:
            raise ValueError(f"expected a non-empty (n, d) matrix, got shape {vectors.shape}")
        v = np.asarray(vectors, dtype=np.float32)
        norms = np.linalg.norm(v, axis=1, keepdims=True)
        if np.any(norms == 0):
            raise ValueError("zero vector in index: cosine similarity is undefined")
        self.n, self.dim = v.shape
        self._mat = jnp.asarray(v / norms)

    def search(self, queries: np.ndarray, k: int, exclude: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
        """Top-k (indices, similarities) per query. `exclude[i]` removes row exclude[i] for query i
        (use it when a query is itself a stored vector)."""
        import jax
        import jax.numpy as jnp

        q = np.atleast_2d(np.asarray(queries, dtype=np.float32))
        if q.shape[1] != self.dim:
            raise ValueError(f"query dim {q.shape[1]} != index dim {self.dim}")
        qn = np.linalg.norm(q, axis=1, keepdims=True)
        if np.any(qn == 0):
            raise ValueError("zero query vector")
        if not 1 <= k <= self.n - (1 if exclude is not None else 0):
            raise ValueError(f"k={k} out of range for n={self.n}")
        with jax.default_matmul_precision("highest"):
            sims = jnp.asarray(q / qn) @ self._mat.T
            if exclude is not None:
                sims = sims.at[jnp.arange(q.shape[0]), jnp.asarray(exclude)].set(-jnp.inf)
            vals, idx = jax.lax.top_k(sims, k)
        return np.asarray(idx), np.asarray(vals)
