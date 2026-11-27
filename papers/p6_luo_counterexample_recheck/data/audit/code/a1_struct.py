"""Auditor's own rebuild of Guo's triangulation: union-find, chain complex SNF, pi1 via sympy, Regina cross-check."""
import itertools, json
import regina
from sympy import Matrix, ZZ
from sympy.matrices.normalforms import smith_normal_form
from sympy.combinatorics.free_groups import free_group
from sympy.combinatorics.fp_groups import FpGroup

# pairings: (T1, ordered face verts) -> (T2, ordered face verts), from paper eq (1)
PAIRS = [(0, (1, 2, 3), 0, (2, 3, 0)), (1, (0, 1, 3), 1, (1, 2, 0)),
         (0, (0, 1, 3), 1, (3, 2, 1)), (0, (0, 1, 2), 1, (3, 2, 0))]


def perm_of(f1: tuple, f2: tuple) -> tuple:
    m = dict(zip(f1, f2))
    a = [v for v in range(4) if v not in f1][0]
    b = [v for v in range(4) if v not in f2][0]
    m[a] = b
    return tuple(m[i] for i in range(4))


def parity(p: tuple) -> int:
    return sum(1 for i in range(len(p)) for j in range(i + 1, len(p)) if p[i] > p[j]) % 2


out: dict = {}
perms = [perm_of(f1, f2) for _, f1, _, f2 in PAIRS]
out['perms'] = [''.join(map(str, p)) for p in perms]
out['parities'] = [parity(p) for p in perms]
faces = [(t, [v for v in range(4) if v not in f][0]) for t, f, _, _ in PAIRS] + \
        [(t, [v for v in range(4) if v not in f][0]) for _, _, t, f in PAIRS]
out['faces_each_once'] = sorted(faces) == sorted((t, v) for t in range(2) for v in range(4))

par: dict = {}


def find(x):
    s = 1
    while par[x][0] != x:
        y, sg = par[x]
        s *= sg
        x = y
    return x, s


for t in range(2):
    for i, j in itertools.combinations(range(4), 2):
        par[(t, i, j)] = ((t, i, j), 1)


def edge_key(t: int, i: int, j: int):
    return ((t, i, j), 1) if i < j else ((t, j, i), -1)


selfrev = False
for (t1, f1, t2, f2), p in zip(PAIRS, perms):
    for i, j in itertools.combinations(f1, 2):
        a, sa = edge_key(t1, i, j)
        b, sb = edge_key(t2, p[i], p[j])
        ra, s1 = find(a)
        rb, s2 = find(b)
        rel = sa * sb * s1 * s2
        if ra == rb:
            if rel != 1:
                selfrev = True
        else:
            par[ra] = (rb, rel)
classes: dict = {}
for k in par:
    r, _ = find(k)
    classes.setdefault(r, []).append(k)
cl = sorted(classes.values(), key=len)
out['edge_degrees'] = [len(c) for c in cl]
out['edge_self_reversed'] = selfrev
names = {}
for nm, (i, j) in zip('abc', [(0, 1), (0, 2), (0, 3)]):
    names[find((0, i, j))[0]] = nm
table = {}
for t in range(2):
    table['AB'[t]] = {f'{i}{j}': names[find((t, i, j))[0]] for i, j in itertools.combinations(range(4), 2)}
out['edge_table'] = table
keys = ['01', '02', '03', '12', '13', '23']
paper = {'A': dict(zip(keys, 'abccbc')), 'B': dict(zip(keys, 'bcbbca'))}
out['edge_table_matches_paper'] = table == paper
vp = {(t, v): (t, v) for t in range(2) for v in range(4)}


def vf(x):
    while vp[x] != x:
        x = vp[x]
    return x


for (t1, f1, t2, f2), p in zip(PAIRS, perms):
    for v in f1:
        ra, rb = vf((t1, v)), vf((t2, p[v]))
        if ra != rb:
            vp[ra] = rb
out['n_vertex_classes'] = len({vf(k) for k in vp})
out['link_VEF'] = (2 * len(cl), 3 * 4, 8)
out['link_chi'] = 2 * len(cl) - 12 + 8
out['chi_M'] = out['n_vertex_classes'] - len(cl) + 4 - 2
gens = 'abc'
REF = {find((0, 0, j))[0]: find((0, 0, j))[1] for j in (1, 2, 3)}


def edge_vec(t: int, i: int, j: int) -> list:
    a, sa = edge_key(t, i, j)
    r, s = find(a)
    v = [0, 0, 0]
    v[gens.index(names[r])] = sa * s * REF[r]
    return v


d2 = []
words = []
for t1, f1, _, _ in PAIRS:
    i, j, k = sorted(f1)
    e1, e2, e3 = edge_vec(t1, i, j), edge_vec(t1, j, k), edge_vec(t1, i, k)
    d2.append([e1[n] + e2[n] - e3[n] for n in range(3)])
    words.append([(t1, i, j, 1), (t1, j, k, 1), (t1, i, k, -1)])
D2 = Matrix(d2).T


def face_sign_and_index(t: int, m: int):
    for idx, (t1, f1, t2, f2) in enumerate(PAIRS):
        p = perm_of(f1, f2)
        o1 = [v for v in range(4) if v not in f1][0]
        o2 = [v for v in range(4) if v not in f2][0]
        if (t, m) == (t1, o1):
            return idx, 1
        if (t, m) == (t2, o2):
            src = sorted(f1)
            img = [p[v] for v in src]
            tgt = sorted(f2)
            perm = tuple(tgt.index(v) for v in img)
            return idx, (-1 if parity(perm) else 1)
    raise RuntimeError('face not found')


d3 = [[0] * 4 for _ in range(2)]
for t in range(2):
    for m in range(4):
        idx, sg = face_sign_and_index(t, m)
        d3[t][idx] += (-1) ** m * sg
D3 = Matrix(d3).T
out['D2'] = D2.tolist()
out['D3'] = D3.tolist()
out['d2d3_zero'] = (D2 * D3).is_zero_matrix
out['SNF_d2'] = str(smith_normal_form(D2, domain=ZZ))
out['SNF_d3'] = str(smith_normal_form(D3, domain=ZZ))
out['rank_d2'] = D2.rank()
out['rank_d3'] = D3.rank()
F, a, b, c = free_group('a b c')
g = {'a': a, 'b': b, 'c': c}
rels = []
for wd in words:
    w = F.identity
    for (t, i, j, s) in wd:
        a_, sa = edge_key(t, i, j)
        r, s0 = find(a_)
        w = w * g[names[r]] ** (s * sa * s0 * REF[r])
    rels.append(w)
out['pi1_relators'] = [str(r) for r in rels]
G = FpGroup(F, rels)
out['pi1_order_sympy'] = int(G.order())
C = G.coset_enumeration([a])
C.compress()
out['index_of_<a>'] = len(C.table)
T = regina.Triangulation3()
A = T.newTetrahedron()
B = T.newTetrahedron()
tets = [A, B]
for (t1, f1, t2, f2), p in zip(PAIRS, perms):
    o1 = [v for v in range(4) if v not in f1][0]
    tets[t1].join(o1, tets[t2], regina.Perm4(*p))
L31 = regina.Example3.lens(3, 1)
out['regina'] = dict(valid=T.isValid(), closed=T.isClosed(), orientable=T.isOrientable(),
                     nverts=T.countVertices(), degrees=sorted(e.degree() for e in T.edges()),
                     isosig=T.isoSig(), H1=str(T.homology()), pi1=str(T.group()),
                     iso_lens31=bool(T.isIsomorphicTo(L31)), lens31_sig=L31.isoSig(),
                     lens31_nverts=L31.countVertices())
try:
    out['regina']['census'] = [h.name() for h in regina.Census.lookup(T.isoSig())]
except Exception as ex:
    out['regina']['census'] = 'err ' + str(ex)
json.dump(out, open('/tmp/luoaudit/a1.json', 'w'), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
