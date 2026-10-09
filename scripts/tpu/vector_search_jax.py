#!/usr/bin/env python3
"""Run on a host with jax (TPU or CPU): exact search over exported Chroma embeddings.

    python vector_search_jax.py EXPORT.npz [--k 10]

Positive control: ExactIndex top-k == numpy float64 brute force (ties aside).
Negative control: a deliberately wrong query set (shuffled queries) must NOT match.
Reports Chroma/HNSW recall against that exact ground truth, and a timing on the real matrix.
Needs anse/memory/tpu_index.py next to this script (the runner uploads both).
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "anse" / "memory"))  # repo checkout
from tpu_index import ExactIndex  # noqa: E402


def recall(found: np.ndarray, truth: np.ndarray) -> float:
    return float(np.mean([len(set(f.tolist()) & set(t.tolist())) / len(t) for f, t in zip(found, truth, strict=True)]))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("export", type=Path)
    p.add_argument("--k", type=int, default=10)
    a = p.parse_args()
    import jax

    d = np.load(a.export)
    emb, qidx, chroma_top = d["emb"], d["qidx"], d["chroma_top"]
    k = chroma_top.shape[1]
    print("backend", jax.default_backend(), "matrix", emb.shape, "queries", len(qidx))
    idx = ExactIndex(emb)
    got, sims = idx.search(emb[qidx], k, exclude=qidx)

    e64 = emb.astype(np.float64)
    e64 /= np.linalg.norm(e64, axis=1, keepdims=True)
    s64 = e64[qidx] @ e64.T
    s64[np.arange(len(qidx)), qidx] = -np.inf
    truth = np.argsort(-s64, axis=1)[:, :k]
    r_exact = recall(got, truth)
    # near-ties may legitimately swap members at the k-th boundary; compare the similarity values too
    sim_err = float(np.max(np.abs(sims - np.take_along_axis(s64, got, axis=1))))
    shuffled = np.roll(qidx, 1)
    wrong, _ = idx.search(emb[shuffled], k, exclude=shuffled)
    r_neg = recall(wrong, truth)
    ok = r_exact >= 0.99 and sim_err < 1e-5 and r_neg < 0.5
    print(f"positive: recall@{k} vs float64 brute force = {r_exact:.4f}, max |sim err| = {sim_err:.2e}")
    print(f"negative: recall@{k} of mismatched queries = {r_neg:.4f} (must be < 0.5)")
    print("controls", "PASS" if ok else "FAIL")
    if not ok:
        return 1
    print(f"Chroma/HNSW recall@{k} vs exact ground truth = {recall(chroma_top, truth):.4f}")
    qv = emb[qidx]
    idx.search(qv, k)  # compile
    t = time.time()
    for _ in range(20):
        idx.search(qv, k)
    dt = (time.time() - t) / 20
    print(f"exact search: {len(qidx)} queries x {emb.shape[0]} vectors in {dt * 1e3:.2f} ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
