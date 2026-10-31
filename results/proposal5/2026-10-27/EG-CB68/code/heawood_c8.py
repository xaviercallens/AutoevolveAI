#!/usr/bin/env python3
"""heawood_c8.py -- negative control N2 (independent of cb_search): the Fano plane's Levi graph is the Heawood
graph, which has an 8-cycle, so the incremental C8 test must reject the last block of the Fano plane.
Uses networkx only (no code shared with cb_search.c / cb_check.py).
usage: heawood_c8.py OUTJSON
"""
from __future__ import annotations

import json
import sys

import networkx as nx


def levi(blocks: list[tuple[int, int, int]]) -> nx.Graph:
    g = nx.Graph()
    for k, b in enumerate(blocks):
        for x in b:
            g.add_edge(("p", x), ("b", k))
    return g


def has_simple_path_len(g: nx.Graph, s: object, t: object, length: int) -> bool:
    return any(len(path) == length + 1 for path in nx.all_simple_paths(g, s, t, cutoff=length))


def count_cycles(g: nx.Graph, length: int) -> int:
    """Number of simple cycles of the given length (each counted once)."""
    order = {v: i for i, v in enumerate(sorted(g.nodes, key=repr))}
    total = 0

    def dfs(s: object, v: object, depth: int, seen: set) -> None:
        nonlocal total
        for w in g.neighbors(v):
            if w == s and depth == length:
                total += 1
            elif w not in seen and order[w] > order[s] and depth < length:
                seen.add(w)
                dfs(s, w, depth + 1, seen)
                seen.remove(w)

    for s in g.nodes:
        dfs(s, s, 1, {s})
    return total // 2


def main() -> int:
    fano = [tuple(sorted(((i) % 7, (i + 1) % 7, (i + 3) % 7))) for i in range(7)]
    g = levi(fano)
    res: dict[str, object] = {"fano_blocks": fano}
    res["isomorphic_to_networkx_heawood"] = nx.is_isomorphic(g, nx.heawood_graph())
    cyc = {}
    for L in (4, 6, 8, 10, 12, 14):
        cyc[str(L)] = count_cycles(g, L)
    res["simple_cycle_counts_by_length"] = cyc
    res["girth"] = min(int(L) for L, c in cyc.items() if c > 0)
    # incremental test on the last block
    last = fano[-1]
    h = levi(fano[:-1])
    pairs = [(last[i], last[j]) for i in range(3) for j in range(i + 1, 3)]
    res["c8_test_rejects_last_block"] = any(has_simple_path_len(h, ("p", a), ("p", b), 6) for a, b in pairs)
    res["pass"] = bool(res["isomorphic_to_networkx_heawood"] and res["girth"] == 6 and cyc["8"] > 0
                       and res["c8_test_rejects_last_block"])
    with open(sys.argv[1], "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
