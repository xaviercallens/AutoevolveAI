"""FLUX rule, own implementation: extreme rays of the flux cone and copositivity of R^T H R."""
import sys
from itertools import combinations
sys.path.insert(0, "/tmp/bistabaudit/code")
import sympy as sp
from net import catalogue, C, label

ids = catalogue()
FLUX = "N0350 N0354 N0355 N0361 N0369 N0391 N0600 N0610 N0638 N0646 N0648 N0649 N0661 N0673".split()


def analyse(es):
    m = len(es)
    w = sp.symbols(f"w0:{m + 2}")
    av, bv, v = w[0], w[1], w[2:]
    S = sp.Matrix([[C[j][s] - C[i][s] for (i, j) in es] for s in range(2)])
    A = sp.Matrix([[C[i][s] for (i, j) in es] for s in range(2)])
    U = sp.Matrix([av, bv]) + S * sp.Matrix(v)
    M = S * sp.diag(*v) * A.T - sp.diag(U[0], U[1])
    D = sp.expand(M.det())
    H = sp.Matrix(m + 2, m + 2, lambda i, j: sp.Rational(1, 1) * (sp.diff(D, w[i], w[j]) / (1 if i != j else 1)) / 2)
    assert sp.expand((sp.Matrix(w).T * H * sp.Matrix(w))[0] - D) == 0
    # inequalities: w_i >= 0, U_X >= 0, U_Y >= 0, as rows of a matrix G w >= 0
    rows = [[1 if k == i else 0 for k in range(m + 2)] for i in range(m + 2)]
    rows += [[sp.Poly(U[s], *w).coeff_monomial(w[k]) for k in range(m + 2)] for s in range(2)]
    Gm = sp.Matrix(rows)
    rays = set()
    for act in combinations(range(len(rows)), m + 1):
        ns = Gm[list(act), :].nullspace()
        if len(ns) != 1:
            continue
        r = ns[0]
        r = r * sp.ilcm(*[sp.Rational(c).q for c in r])
        for sgn in (1, -1):
            rr = sgn * r
            if all(c >= 0 for c in Gm * rr):
                g = sp.igcd(*[int(c) for c in rr])
                rays.add(tuple(int(c) // g for c in rr))
    R = sp.Matrix([list(r) for r in sorted(rays)]).T
    Gram = R.T * H * R
    n = Gram.shape[0]
    keep = [i for i in range(n) if any(Gram[i, j] < 0 for j in range(n))]
    red = Gram[keep, keep] if keep else sp.zeros(0, 0)
    psd = True
    if keep:
        psd = all(ev >= 0 for ev in [sp.Matrix(red[:k, :k]).det() for k in range(1, len(keep) + 1)]) and \
            all(red.eigenvals(multiple=True)[i] >= 0 for i in range(len(keep)))
    return len(rays), keep, red, psd


if __name__ == "__main__":
    ok = 0
    for n in FLUX:
        nr, keep, red, psd = analyse(ids[n])
        status = "nonneg" if not keep else ("PSD-reduced" if psd else "FAIL")
        ok += status != "FAIL"
        print(n, label(ids[n]), "rays", nr, status, "" if not keep else red.tolist())
    print("FLUX certified (det M >= 0 on cone):", ok, "/14")
