"""Independent exact tools for two-species mass-action networks (own code)."""
from __future__ import annotations
from fractions import Fraction as Fr
from itertools import combinations
import sympy as sp

CX = [(1, 0), (0, 1), (2, 0), (1, 1), (0, 2)]
NAMES = ["X", "Y", "2X", "X+Y", "2Y"]
EDGES = [(i, j) for i in range(5) for j in range(5) if i != j]  # lexicographic, 20
SW = {0: 1, 1: 0, 2: 4, 3: 3, 4: 2}  # species exchange on complexes
x, y, rho = sp.symbols("x y rho", positive=True)
a, b = sp.symbols("a b", positive=True)


def swap_set(es):
    return tuple(sorted(EDGES.index((SW[EDGES[e][0]], SW[EDGES[e][1]])) for e in es))


def enumerate_all():
    labelled = [tuple(c) for m in range(4) for c in combinations(range(20), m)]
    seen, reps = set(), []
    for s in labelled:
        if s in seen:
            continue
        t = swap_set(s)
        seen.add(s)
        seen.add(t)
        reps.append(s)
    return labelled, reps


def parse_edge(txt):
    p = txt.replace(" ", "").split("->")
    return EDGES.index((NAMES.index(p[0]), NAMES.index(p[1])))


def fields(es, ks, a_=a, b_=b, rho_=rho):
    f = a_ - rho_ * x
    g = b_ - y
    for e, k in zip(es, ks):
        s, t = EDGES[e]
        m = x ** CX[s][0] * y ** CX[s][1]
        f += k * (CX[t][0] - CX[s][0]) * m
        g += k * (CX[t][1] - CX[s][1]) * m
    return sp.expand(f), sp.expand(g)
