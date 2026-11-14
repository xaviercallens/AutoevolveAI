#!/usr/bin/env python3
"""Convert aud_search completion lines ("v a,b,c ...") into Levi-graph graph6 (points 0..v-1, blocks v..2v-1).
Writes one file per v: OUTDIR/v<v>.g6 . Checks each completion is a linear 3-regular configuration."""
from __future__ import annotations

import sys
from collections import defaultdict

import networkx as nx


def main() -> None:
    src, outdir = sys.argv[1], sys.argv[2]
    outs: dict[int, list[str]] = defaultdict(list)
    with open(src) as fh:
        for line in fh:
            t = line.split()
            v = int(t[0])
            blocks = [tuple(int(x) for x in s.split(",")) for s in t[1:]]
            assert len(blocks) == v, "block count != point count"
            deg = [0] * v
            pairs = set()
            for b in blocks:
                for x in b:
                    deg[x] += 1
                for i in range(3):
                    for j in range(i + 1, 3):
                        pr = (min(b[i], b[j]), max(b[i], b[j]))
                        assert pr not in pairs, "non-linear completion"
                        pairs.add(pr)
            assert all(d == 3 for d in deg), "not 3-regular"
            g = nx.Graph()
            g.add_nodes_from(range(2 * v))
            for k, b in enumerate(blocks):
                for x in b:
                    g.add_edge(x, v + k)
            assert nx.is_connected(g)
            outs[v].append(nx.to_graph6_bytes(g, header=False).decode().strip())
    for v, lst in outs.items():
        with open(f"{outdir}/v{v}.g6", "w") as fh:
            fh.write("\n".join(lst) + "\n")
        print(v, len(lst))


if __name__ == "__main__":
    main()
