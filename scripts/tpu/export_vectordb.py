#!/usr/bin/env python3
"""Export a Chroma collection's real embeddings + Chroma's own top-k answers for validation on TPU.

    .venv/bin/python scripts/tpu/export_vectordb.py CHROMA_DIR COLLECTION OUT.npz [--queries 200] [--k 10]

Queries are stored vectors (seeded sample); Chroma's answer for each is its top-(k+1) ids with the
query's own id removed, so the TPU result can be scored against both brute force and Chroma/HNSW.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import chromadb
import numpy as np


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("chroma_dir", type=Path)
    p.add_argument("collection")
    p.add_argument("out", type=Path)
    p.add_argument("--queries", type=int, default=200)
    p.add_argument("--k", type=int, default=10)
    a = p.parse_args()
    col = chromadb.PersistentClient(path=str(a.chroma_dir)).get_collection(a.collection)
    n = col.count()
    rec = col.get(limit=n, include=["embeddings"])
    ids = list(rec["ids"])
    emb = np.asarray(rec["embeddings"], dtype=np.float32)
    rng = np.random.default_rng(0)
    qidx = rng.choice(len(ids), size=min(a.queries, len(ids)), replace=False)
    res = col.query(query_embeddings=emb[qidx].tolist(), n_results=a.k + 1, include=[])
    id_pos = {i: j for j, i in enumerate(ids)}
    chroma_top = np.full((len(qidx), a.k), -1, dtype=np.int64)
    for r, (qi, got) in enumerate(zip(qidx, res["ids"], strict=True)):
        row = [id_pos[g] for g in got if id_pos[g] != qi][: a.k]
        chroma_top[r, : len(row)] = row
    np.savez(a.out, emb=emb, qidx=qidx, chroma_top=chroma_top)
    print(f"{a.collection}: {emb.shape} queries={len(qidx)} k={a.k} -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
