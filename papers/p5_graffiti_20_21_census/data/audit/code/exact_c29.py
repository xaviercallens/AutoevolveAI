"""Exact Graffiti-29 check for given graph6 strings: distance-matrix inertia via integer charpoly
(sympy, Descartes; D symmetric => real-rooted) and Randic index enclosed with mpmath 60 digits;
R compared to the integer n_neg(D). Also prints adjacency inertia."""
import sys
import sympy as sp
import mpmath as mp

mp.mp.dps = 60
x = sp.symbols('x')


def g6(s: str) -> list[list[int]]:
    n = ord(s[0]) - 63
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


def dist(A: list[list[int]]) -> list[list[int]]:
    n = len(A)
    D = [[0] * n for _ in range(n)]
    for s in range(n):
        seen = {s: 0}; fr = [s]
        while fr:
            nf = []
            for u in fr:
                for v in range(n):
                    if A[u][v] and v not in seen:
                        seen[v] = seen[u] + 1; nf.append(v)
            fr = nf
        for v in range(n):
            D[s][v] = seen[v]
    return D


def inertia(M: list[list[int]]) -> tuple[int, int, int]:
    cf = sp.Poly(sp.Matrix(M).charpoly(x).as_expr(), x).all_coeffs()
    def ch(c: list[int]) -> int:
        c = [v for v in c if v != 0]
        return sum(1 for a, b in zip(c, c[1:]) if (a > 0) != (b > 0))
    N = len(cf) - 1
    p = ch(cf); q = ch([c * (-1) ** (N - k) for k, c in enumerate(cf)])
    return p, q, N - p - q


if __name__ == '__main__':
  for s in [l.strip() for l in open(sys.argv[1]) if l.strip()]:
        A = g6(s); n = len(A)
        deg = [sum(r) for r in A]
        R = mp.fsum(1 / mp.sqrt(deg[u] * deg[v]) for u in range(n) for v in range(u + 1, n) if A[u][v])
        dp, dn, d0 = inertia(dist(A))
        ap, an, a0 = inertia(A)
        print(s, 'n', n, 'regular', len(set(deg)) == 1, 'R', mp.nstr(R, 25), 'D inertia(+,-,0)', (dp, dn, d0),
              'fires(R>dneg)', R > dn, 'A inertia', (ap, an, a0))
