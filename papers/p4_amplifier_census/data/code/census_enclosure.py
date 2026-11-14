"""Certified census of N_eff over connected graphs (C1). Usage: census_enclosure.py <graph6 file> <N> <shard> <nshards> <out.json>

Method (rigorous; floating point is used only to *propose* tau, never to decide):
  Scaled integer system for i<j (Allen eq. 5 times 2 k_i k_j):
     2 k_i k_j tau_ij - k_j sum_{k~i, k!=j} tau_jk - k_i sum_{k~j, k!=i} tau_ik = 2 k_i k_j.
  1. float64 LAPACK solve gives tau~;  2. round to t = rint(tau~ 2^30) (int64), x^ = t / 2^30;
  3. exact int64 residual res = 2^30 rhs - A_s t; unscaled residual |r|_inf <= E / 2^31 =: eps, E = max|res|
     (since every scaling factor 2 k_i k_j >= 2);
  4. A = I - M, M >= 0 substochastic with A^{-1} = sum M^n >= 0 and A^{-1} 1 = tau, so
     |tau - x^| <= eps tau_max and tau_max <= X / (2^30 (1 - eps)), X = max t;
  5. N_eff = 1 + (1/m) sum_{ij in E} tau_ij (identity pi_i p_ij = 1/2m), so
     |N_eff - N^_eff| <= eps tau_max. The graph is EXCLUDED (N_eff < N certified) iff, in exact integers,
     (m 2^30 + S)(2^31 - E) + m E X < N m 2^30 (2^31 - E),  S = sum_{E} t.
  Everything not excluded is a candidate and is solved exactly with Fractions by finish_candidates.py.
"""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import heapq  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from itertools import combinations  # noqa: E402

import numpy as np  # noqa: E402

SCALE_BITS = 30
BATCH = 8000
NEAREST: list[tuple[float, str, float]] = []  # non-regular graphs with the smallest certified gap N - N_eff


def decode_batch(lines: list[bytes], n: int) -> np.ndarray:
    nb = n * (n - 1) // 2
    nchar = (nb + 5) // 6
    arr = np.frombuffer(b"".join(x[1:1 + nchar] for x in lines), dtype=np.uint8).reshape(len(lines), nchar).astype(np.int64) - 63
    bits = ((arr[:, :, None] >> np.arange(5, -1, -1)[None, None, :]) & 1).reshape(len(lines), nchar * 6)[:, :nb]
    adj = np.zeros((len(lines), n, n), dtype=np.int64)
    idx = 0
    for j in range(1, n):
        for i in range(j):
            adj[:, i, j] = bits[:, idx]
            adj[:, j, i] = bits[:, idx]
            idx += 1
    return adj


def build_tables(n: int) -> tuple[list[tuple[int, int]], np.ndarray, np.ndarray]:
    pairs = list(combinations(range(n), 2))
    index = {p: t for t, p in enumerate(pairs)}
    npairs = len(pairs)
    qj = np.full((npairs, n), npairs, dtype=np.int64)  # column of tau_{j k}; dummy npairs if k == j
    qi = np.full((npairs, n), npairs, dtype=np.int64)  # column of tau_{i k}; dummy if k == i
    for t, (i, j) in enumerate(pairs):
        for k in range(n):
            if k != j:
                qj[t, k] = index[(min(j, k), max(j, k))]
            if k != i:
                qi[t, k] = index[(min(i, k), max(i, k))]
    return pairs, qj, qi


def process(adj: np.ndarray, n: int, pairs: list[tuple[int, int]], qj: np.ndarray, qi: np.ndarray) -> dict[str, np.ndarray]:
    b = adj.shape[0]
    npairs = len(pairs)
    deg = adj.sum(axis=2)
    pi = np.array([p[0] for p in pairs])
    pj = np.array([p[1] for p in pairs])
    ki = deg[:, pi]
    kj = deg[:, pj]
    a = np.zeros((b, npairs, npairs + 1), dtype=np.int64)
    rows = np.arange(npairs)
    a[:, rows, rows] = 2 * ki * kj
    for k in range(n):
        a_ik = adj[:, pi, k]  # (b, npairs)
        a_jk = adj[:, pj, k]
        a[:, rows, qj[:, k]] -= kj * a_ik
        a[:, rows, qi[:, k]] -= ki * a_jk
    a = a[:, :, :npairs]
    rhs = 2 * ki * kj
    x = np.linalg.solve(a.astype(np.float64), rhs.astype(np.float64)[:, :, None])[:, :, 0]
    # Added in the audit revision, after the census run (see REVISION.md): precondition of the int64 residual (audit item 11).
    assert np.isfinite(x).all() and np.abs(x).max() * float(1 << SCALE_BITS) < float(1 << 50), "non-finite or huge proposal: int64 residual unsafe"
    t = np.rint(x * float(1 << SCALE_BITS)).astype(np.int64)
    assert np.abs(t).max() < (1 << 50)
    res = (rhs << SCALE_BITS) - np.einsum("bpq,bq->bp", a, t)
    e_int = np.abs(res).max(axis=1)
    x_int = t.max(axis=1)
    edge_mask = adj[:, pi, pj]  # pair (i,j) is an edge
    s_int = (t * edge_mask).sum(axis=1)
    m = edge_mask.sum(axis=1)
    regular = (deg.min(axis=1) == deg.max(axis=1))
    return {"E": e_int, "X": x_int, "S": s_int, "m": m, "regular": regular, "t": t}


def main() -> None:
    path, n, shard, nshards, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    pairs, qj, qi = build_tables(n)
    two30 = 1 << SCALE_BITS
    two31 = 1 << (SCALE_BITS + 1)
    total = excluded = 0
    candidates: list[dict[str, object]] = []
    top: list[tuple[float, str]] = []
    worst_margin_excluded = None
    max_eps = 0.0
    hist = np.zeros(200, dtype=np.int64)  # N_eff/N in [0.5, 1.0+) bins of 0.0025
    t0 = time.time()
    with open(path, "rb") as fh:
        buf: list[bytes] = []
        lineno = 0
        for line in fh:
            if lineno % nshards == shard:
                buf.append(line)
            lineno += 1
            if len(buf) == BATCH:
                total, excluded, worst_margin_excluded, max_eps = flush(buf, n, pairs, qj, qi, two30, two31, total, excluded,
                                                                     candidates, top, hist, worst_margin_excluded, max_eps)
                buf = []
                if total % (BATCH * 25) == 0:
                    print(f"{time.time() - t0:.0f}s processed {total} excluded {excluded} cand {len(candidates)}", flush=True)
        if buf:
            total, excluded, worst_margin_excluded, max_eps = flush(buf, n, pairs, qj, qi, two30, two31, total, excluded,
                                                                 candidates, top, hist, worst_margin_excluded, max_eps)
    summary = {"file": path, "N": n, "shard": shard, "nshards": nshards, "graphs": total, "excluded_certified": excluded,
               "candidates": candidates, "top_by_float_neff": sorted(top, reverse=True),
               "min_certified_gap_among_excluded": worst_margin_excluded, "max_eps": max_eps,
               "nonregular_nearest_to_N": sorted(({"gap_upper": -a, "graph6": b, "neff_float": c} for a, b, c in NEAREST),
                                                 key=lambda x: x["gap_upper"]),
               "hist_neff_over_N_bins_0.5_step_0.0025": hist.tolist(), "seconds": time.time() - t0}
    with open(out, "w") as fo:
        json.dump(summary, fo, indent=1)
    print("done", total, excluded, len(candidates), f"{time.time() - t0:.0f}s", flush=True)


def flush(buf: list[bytes], n: int, pairs: list[tuple[int, int]], qj: np.ndarray, qi: np.ndarray, two30: int, two31: int,
          total: int, excluded: int, candidates: list[dict[str, object]], top: list[tuple[float, str]], hist: np.ndarray,
          worst: float | None, max_eps: float) -> tuple[int, int, float | None, float]:
    adj = decode_batch(buf, n)
    r = process(adj, n, pairs, qj, qi)
    for g in range(len(buf)):
        e = int(r["E"][g])
        x = int(r["X"][g])
        s = int(r["S"][g])
        m = int(r["m"][g])
        neff_hat = 1 + s / (m * two30)
        ratio = neff_hat / n
        bi = int((ratio - 0.5) / 0.0025)
        hist[min(max(bi, 0), 199)] += 1
        g6 = buf[g].strip().decode()
        if len(top) < 25:
            heapq.heappush(top, (ratio, g6))
        elif ratio > top[0][0]:
            heapq.heapreplace(top, (ratio, g6))
        max_eps = max(max_eps, e / two31)
        ok = e < two31 and (m * two30 + s) * (two31 - e) + m * e * x < n * m * two30 * (two31 - e)
        if ok and not bool(r["regular"][g]):
            excluded += 1
            gap = n - neff_hat - (e / two31) * x / (two30 * (1 - e / two31))
            worst = gap if worst is None else min(worst, gap)
            if len(NEAREST) < 10:
                heapq.heappush(NEAREST, (-gap, g6, neff_hat))
            elif -gap > NEAREST[0][0]:
                heapq.heapreplace(NEAREST, (-gap, g6, neff_hat))
        else:
            candidates.append({"graph6": g6, "regular": bool(r["regular"][g]), "neff_float": neff_hat, "E": e})
    return total + len(buf), excluded, worst, max_eps


if __name__ == "__main__":
    main()
