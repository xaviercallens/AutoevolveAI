"""Auditor's own network model (independent of producer code)."""
from itertools import combinations
import sympy as sp

C = [(1, 0), (0, 1), (2, 0), (1, 1), (0, 2)]
NAMES = ["X", "Y", "2X", "X+Y", "2Y"]
EDGES = [(i, j) for i in range(5) for j in range(5) if i != j]
SWAP = {0: 1, 1: 0, 2: 4, 3: 3, 4: 2}
x, y, a, b, rho = sp.symbols("x y a b rho", positive=True)
K = sp.symbols("k1 k2 k3", positive=True)


def swap(es: tuple) -> tuple:
    return tuple(sorted((SWAP[i], SWAP[j]) for i, j in es))


def enumerate_catalogue() -> tuple:
    labelled = []
    for m in range(4):
        labelled += list(combinations(EDGES, m))
    reps, seen, fixed, sizes = [], set(), 0, {}
    for es in labelled:
        if swap(es) == es:
            fixed += 1
        if es in seen:
            continue
        seen.add(es)
        seen.add(swap(es))
        reps.append(es)
        sizes[len(es)] = sizes.get(len(es), 0) + 1
    return labelled, reps, fixed, sizes


def catalogue() -> dict:
    return {"N%04d" % i: e for i, e in enumerate(enumerate_catalogue()[1])}


def label(es: tuple) -> str:
    return ", ".join(f"{NAMES[i]}->{NAMES[j]}" for i, j in es)


def field(es: tuple, model: str = "F", ks=None, params=None):
    ks = ks if ks is not None else K
    H = [sp.Integer(0), sp.Integer(0)]
    for (i, j), k in zip(es, ks):
        al, be = C[i], C[j]
        mon = x**al[0] * y**al[1]
        H[0] += k * (be[0] - al[0]) * mon
        H[1] += k * (be[1] - al[1]) * mon
    r = rho if model == "F" else 1
    return sp.expand(a - r * x + H[0]), sp.expand(b - y + H[1])
