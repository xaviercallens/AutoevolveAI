"""Appendix B check: the 166 retained bidegree-(4,4) monomials give independent assignments in W (= ker P)."""
import itertools
from sage.all import GF, PolynomialRing, matrix
x = PolynomialRing(GF(3), "x").gen()
F = GF(9, "t", modulus=x**2 + 1); t = F.gen()
eta = [F(r % 3) + F(r // 3) * t for r in range(9)]
T = [(F(0), F(0), F(1))] + [(F(0), F(1), eta[r]) for r in range(9)] + [(F(1), eta[r], eta[s]) for r in range(9) for s in range(9)]
dot = lambda a, b: a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
edges = [(i, j) for i in range(91) for j in range(91) if dot(T[i], T[j]) == 0]
ex = [e for e in itertools.product(range(5), repeat=3) if sum(e) == 4]
mons = [(a, b) for a in ex for b in ex if not (a[0] >= 1 and b[0] >= 3) and not (a[1] >= 3 and b[1] >= 1)]
print("retained monomials", len(mons), "total", len(ex)**2)
rows = []
for a, b in mons:
    row = []
    for i, j in edges:
        p3 = [c**3 for c in T[i]]; l = T[j]
        v = F(1)
        for k in range(3): v *= p3[k]**a[k] * l[k]**b[k]
        row.append(v)
    rows.append(row)
Wm = matrix(F, rows)
print("rank of 166 assignments", Wm.rank())
# all 225 bidegree-(4,4) monomials span (should be <= dim W = 166 if the image is all of W)
allrows = []
for a in ex:
    for b in ex:
        allrows.append([F.prod([c**3 for c in T[i]][k]**a[k] * T[j][k]**b[k] for k in range(3)) for i, j in edges])
print("rank of all 225", matrix(F, allrows).rank())
import json
json.dump([[int(c.polynomial()[0]) + 3*int(c.polynomial()[1]) for c in r] for r in rows], open("/tmp/muc9audit/work/appB_rows.json", "w"))
from sage.all import vector
inc = [[] for _ in range(182)]
for q, (i, j) in enumerate(edges):
    inc[i].append(q); inc[91 + j].append(q)
bad = 0
for v in range(182):
    z = T[v] if v < 91 else T[v - 91]
    perp = [k for k in range(91) if dot(z, T[k]) == 0]
    A = matrix(F, [[T[perp[0]][k], T[perp[1]][k]] for k in range(3)])
    Mr = []
    for q in inc[v]:
        y = T[edges[q][1]] if v < 91 else T[edges[q][0]]
        lam, mu = A.solve_right(vector(F, y))
        if v >= 91: lam, mu = lam**3, mu**3
        Mr.append([lam**(4 - r) * mu**r for r in range(5)])
    M = matrix(F, Mr)
    for r in rows:
        if M.augment(matrix(F, 10, 1, [r[q] for q in inc[v]])).rank() != 5: bad += 1
print("Appendix-B assignments violating a local code:", bad)
