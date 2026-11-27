"""Exact verdict for flagged graphs. usage: exact_check.py <n> <flagged files...>
For each distinct graph6: charpoly over Z (sympy). Adjacency is symmetric so the charpoly is real-rooted:
Descartes' rule is exact: #positive roots = sign changes of p(x), #negative = sign changes of p(-x).
S+ is enclosed by rigorous rational root isolation (sympy Poly.intervals, width <= 1e-30).
Verdict for conjecture k in {20,21}: count <= S+ is HOLDS if lo >= count, VIOLATED if hi < count, else TIE_OR_UNDECIDED
(complete graph K_n is the hand-proved tie S+ = n-1 = n_neg)."""
import sys, json
import sympy as sp
from fractions import Fraction

x = sp.symbols('x')

def g6(s, n):
    nb = n * (n - 1) // 2
    bits = []
    for ch in s[1:]:
        v = ord(ch) - 63
        bits += [(v >> k) & 1 for k in range(5, -1, -1)]
    A = [[0] * n for _ in range(n)]
    t = 0
    for j in range(1, n):
        for i in range(j):
            A[i][j] = A[j][i] = bits[t]; t += 1
    return A

def changes(coeffs):
    c = [v for v in coeffs if v != 0]
    return sum(1 for a, b in zip(c, c[1:]) if (a > 0) != (b > 0))

def check(s, n):
    A = g6(s, n)
    p = sp.Poly(sp.Matrix(A).charpoly(x).as_expr(), x)
    cf = p.all_coeffs()
    npos = changes(cf)
    nneg = changes([c * (-1) ** (len(cf) - 1 - k) for k, c in enumerate(cf)])
    # S+ enclosure
    sq = sp.Poly(p.as_expr(), x)
    lo = hi = Fraction(0)
    for (a, b), m in sq.intervals(eps=sp.Rational(1, 10 ** 30)):
        if a >= 0 or b > 0 and a >= 0:
            pass
        if b > 0 and a >= 0:
            lo += m * Fraction(int(a.p), int(a.q)); hi += m * Fraction(int(b.p), int(b.q))
        elif a < 0 < b:
            # interval straddles 0: root is 0 (charpoly root at 0 exactly -> isolate returns (0,0)); treat as 0
            hi += m * Fraction(int(b.p), int(b.q))
    out = {'g6': s, 'n_pos': npos, 'n_neg': nneg, 'splus_lo': float(lo), 'splus_hi': float(hi)}
    for k, c in (('20', npos), ('21', nneg)):
        out['c' + k] = 'HOLDS' if lo >= c else ('VIOLATED' if hi < c else 'TIE_OR_UNDECIDED')
    out['complete'] = all(A[i][j] == 1 for i in range(n) for j in range(n) if i != j)
    return out

if __name__ == '__main__':
    n = int(sys.argv[1]); seen = {}
    for f in sys.argv[2:]:
        for l in open(f):
            if l.strip():
                seen[l.split()[1]] = 1
    for s in seen:
        print(json.dumps(check(s, n)))
