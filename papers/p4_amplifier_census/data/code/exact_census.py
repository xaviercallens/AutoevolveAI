"""Exact-rational N_eff for every graph in a graph6 file (independent of the enclosure code).
Usage: exact_census.py <graph6 file> <N> <out.json> [<enclosure json to cross-check>]
Classifies each graph as N_eff > N, = N, < N with Python Fractions (Allen eqs. 5, 6, 9 directly, not the edge identity)."""

from __future__ import annotations

import json
import sys
import time
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dbcore as d  # noqa: E402


def main() -> None:
    path, n, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    enc = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else None
    gt: list[str] = []
    eq: list[dict[str, object]] = []
    lt = 0
    best: tuple[Fraction, str] | None = None
    t0 = time.time()
    count = 0
    with open(path) as fh:
        for line in fh:
            s = line.strip()
            if not s:
                continue
            g = d.parse_graph6(s)
            ne = d.neff_exact(g)[0]
            count += 1
            if best is None or ne > best[0]:
                best = (ne, s)
            if ne > n:
                gt.append(s)
            elif ne == n:
                degs = sorted(len(a) for a in g)
                eq.append({"graph6": s, "regular": degs[0] == degs[-1]})
            else:
                lt += 1
            if count % 20000 == 0:
                print(f"{time.time() - t0:.0f}s {count}", flush=True)
    assert best is not None
    summary: dict[str, object] = {"file": path, "N": n, "graphs": count, "N_eff_gt_N": gt, "N_eff_eq_N": eq, "N_eff_lt_N": lt,
                                  "max_N_eff": str(best[0]), "max_N_eff_float": float(best[0]), "argmax_graph6": best[1],
                                  "max_ratio": float(best[0] / n), "seconds": time.time() - t0}
    if enc is not None:
        cand = {c["graph6"] for c in enc["candidates"]}
        eq_set = {e["graph6"] for e in eq}
        summary["crosscheck_enclosure"] = {
            "graphs_match": enc["graphs"] == count,
            "every_exact_ge_N_is_enclosure_candidate": (set(gt) | eq_set) <= cand,
            "enclosure_excluded_plus_candidates": enc["excluded_certified"] + len(cand),
        }
    json.dump(summary, open(out, "w"), indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("N_eff_eq_N",)}, indent=1)[:3000])


if __name__ == "__main__":
    main()
