"""Auditor: I, W, Regina quad + standard matching equations, Lemma 3.1, Thurston equations (sympy resultants), SAS volume."""
import itertools, json
import regina
import sympy as sp
import mpmath as mp

PAIRS = [(0, (1, 2, 3), 0, (2, 3, 0)), (1, (0, 1, 3), 1, (1, 2, 0)),
         (0, (0, 1, 3), 1, (3, 2, 1)), (0, (0, 1, 2), 1, (3, 2, 0))]


def perm_of(f1: tuple, f2: tuple) -> tuple:
    m = dict(zip(f1, f2))
    m[[v for v in range(4) if v not in f1][0]] = [v for v in range(4) if v not in f2][0]
    return tuple(m[i] for i in range(4))


T = regina.Triangulation3()
tets = [T.newTetrahedron(), T.newTetrahedron()]
for t1, f1, t2, f2 in PAIRS:
    tets[t1].join([v for v in range(4) if v not in f1][0], tets[t2], regina.Perm4(*perm_of(f1, f2)))
out: dict = {}
# I from Regina's own skeleton (independent of my union-find): edge class of each local edge
OPP = [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]  # quad k disjoint from these
# name Regina edge classes by paper: a = A01, b = A02, c = A03
nm = {}
for lbl, (i, j) in zip('abc', [(0, 1), (0, 2), (0, 3)]):
    nm[tets[0].edge(regina.Edge3.edgeNumber[i][j]).index()] = lbl
Irows = {l: [0] * 6 for l in 'abc'}
for t in range(2):
    for k, pair in enumerate(OPP):
        for (i, j) in pair:
            e = tets[t].edge(regina.Edge3.edgeNumber[i][j]).index()
            Irows[nm[e]][3 * t + k] += 1
I = sp.Matrix([Irows[l] for l in 'abc'])
J = sp.Matrix([[0, 1, -1], [-1, 0, 1], [1, -1, 0]])
Om = sp.diag(J, J)
W = I * Om
I_paper = sp.Matrix([[1, 0, 0, 1, 0, 0], [0, 2, 0, 1, 0, 2], [1, 0, 2, 0, 2, 0]])
W_paper = sp.Matrix([[0, 1, -1, 0, 1, -1], [-2, 0, 2, 2, -1, -1], [2, -1, -1, -2, 0, 2]])
out['I'] = I.tolist()
out['I_eq_paper'] = I == I_paper
out['W_eq_paper'] = W == W_paper
out['rank_W'] = W.rank()
kerW = W.nullspace()
out['dim_kerW'] = len(kerW)
# Regina quad matching equations (Regina quad k separates 01|23 etc: check type numbering)
out['regina_quad_sep'] = [[regina.quadSeparating[0][k + 1] for k in range(3)]]
MQ = regina.makeMatchingEquations(T, regina.NS_QUAD)
RQ = sp.Matrix([[int(str(MQ.entry(r, c))) for c in range(MQ.columns())] for r in range(MQ.rows())])
out['regina_quad_matrix'] = RQ.tolist()
out['rowspace_regina_quad_eq_W'] = (RQ.rank() == W.rank() == sp.Matrix.vstack(RQ, W).rank())
# Regina standard (Haken) coordinates: 7 per tet: 4 triangles then 3 quads
MS = regina.makeMatchingEquations(T, regina.NS_STANDARD)
RS = sp.Matrix([[int(str(MS.entry(r, c))) for c in range(MS.columns())] for r in range(MS.rows())])
NS = RS.nullspace()
out['haken_rank'] = RS.rank()
out['haken_soldim'] = len(NS)
quad_idx = [4, 5, 6, 11, 12, 13]
P = sp.Matrix.hstack(*[sp.Matrix([v[i] for i in quad_idx]) for v in NS])
out['proj_dim'] = P.rank()
out['proj_eq_kerW'] = (P.rank() == len(kerW) == sp.Matrix.hstack(P, *kerW).rank())
# Lemma 3.1: 1-supports (zero columns) and 2-supports (proportional column pairs) of W
zero_cols = [k for k in range(6) if W[:, k].is_zero_matrix]
prop_pairs = [(i, j) for i, j in itertools.combinations(range(6), 2) if sp.Matrix.hstack(W[:, i], W[:, j]).rank() < 2]
out['zero_cols'] = zero_cols
out['proportional_pairs'] = prop_pairs
if prop_pairs:
    i, j = prop_pairs[0]
    out['pair_relation'] = [W[:, i].T.tolist(), W[:, j].T.tolist()]
# Thurston equations, both orientation conventions; exponents from I
z, w = sp.symbols('z w')


def shapes(s, conv: int):
    sp1, sp2 = 1 / (1 - s), (s - 1) / s
    return [s, sp1, sp2] if conv == 0 else [s, sp2, sp1]


th = {}
sing = []
for conv in (0, 1):
    zeta = shapes(z, conv) + shapes(w, conv)
    eqs = []
    for r in range(3):
        prod = sp.Integer(1)
        for q in range(6):
            prod *= zeta[q] ** I[r, q]
        eqs.append(sp.together(prod))
    th[f'conv{conv}'] = {'edge_eqs': [str(sp.factor(e)) for e in eqs]}
    for signs in itertools.product([1, -1], repeat=3):
        tag = 'c%d_%s' % (conv, ''.join('p' if s > 0 else 'm' for s in signs))
        polys = [str(sp.expand(sp.numer(e) - s * sp.denom(e))).replace('**', '^') for e, s in zip(eqs, signs)]
        sing.append('ring R_%s = 0,(t,w,z),lp;\nideal I_%s = %s, t*z*(1-z)*w*(1-w)-1;\nideal G_%s = std(I_%s);\n"%s";\nG_%s;\n'
                    % (tag, tag, ', '.join(polys), tag, tag, tag, tag))
out['thurston'] = th
with open('/tmp/luoaudit/thurston.sing', 'w') as fh:
    fh.write(''.join(sing) + 'quit;\n')
json.dump(out, open('/tmp/luoaudit/a2.json', 'w'), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
