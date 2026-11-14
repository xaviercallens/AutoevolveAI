#!/usr/bin/env python3
"""Colour-preserving automorphism count and self-duality test of the v=19 configuration."""
from __future__ import annotations

import sys

import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher


def main() -> None:
    line = open(sys.argv[1]).read().split()[0]
    g = nx.from_graph6_bytes(line.encode())
    n = g.number_of_nodes(); v = n // 2
    col = {x: (0 if x < v else 1) for x in g}
    nx.set_node_attributes(g, col, "c")
    same = lambda a, b: a["c"] == b["c"]
    aut = sum(1 for _ in GraphMatcher(g, g, node_match=same).isomorphisms_iter())
    dual = nx.relabel_nodes(g, {x: (x + v) % n for x in g})
    nx.set_node_attributes(dual, {x: (0 if x < v else 1) for x in dual}, "c")
    selfdual = GraphMatcher(g, dual, node_match=same).is_isomorphic()
    total = sum(1 for _ in GraphMatcher(g, g).isomorphisms_iter())
    print(f"colour-preserving aut={aut} all aut={total} self-dual={selfdual}")


if __name__ == "__main__":
    main()
