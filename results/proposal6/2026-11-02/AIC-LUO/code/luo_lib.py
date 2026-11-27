"""Own exact code for gluing-based checks of 3-manifold triangulations.
Spec: gl[(t,f)] = (t2, p) where f = face index (opposite vertex f) of tet t and p is a tuple,
p[i] = image in t2 of vertex i of t (a permutation of 0..3 with p[f] = the opposite vertex of the glued face)."""
from __future__ import annotations
import itertools
from fractions import Fraction
from typing import Dict, List, Tuple

Perm = Tuple[int, int, int, int]
Spec = Dict[Tuple[int, int], Tuple[int, Perm]]

def perm_from_faces(src: Tuple[int, int, int], dst: Tuple[int, int, int]) -> Perm:
    p = [-1] * 4
    for a, b in zip(src, dst):
        p[a] = b
    r_src = ({0, 1, 2, 3} - set(src)).pop()
    r_dst = ({0, 1, 2, 3} - set(dst)).pop()
    p[r_src] = r_dst
    return tuple(p)  # type: ignore

def inv(p: Perm) -> Perm:
    q = [0] * 4
    for i, x in enumerate(p):
        q[x] = i
    return tuple(q)  # type: ignore

def sign(p: Perm) -> int:
    s = 1
    for i in range(4):
        for j in range(i + 1, 4):
            if p[i] > p[j]:
                s = -s
    return s

def spec_from_pairings(pairings: List[Tuple[int, Tuple[int, int, int], int, Tuple[int, int, int]]]) -> Spec:
    gl: Spec = {}
    for t, fs, t2, fd in pairings:
        p = perm_from_faces(fs, fd)
        f = ({0, 1, 2, 3} - set(fs)).pop()
        f2 = ({0, 1, 2, 3} - set(fd)).pop()
        assert (t, f) not in gl and (t2, f2) not in gl, "face used twice"
        gl[(t, f)] = (t2, p)
        gl[(t2, f2)] = (t, inv(p))
    return gl

def ntets(gl: Spec) -> int:
    return 1 + max(t for t, _ in gl)

def check_closed(gl: Spec) -> None:
    n = ntets(gl)
    for t in range(n):
        for f in range(4):
            assert (t, f) in gl, f"free face {(t,f)}"
            t2, p = gl[(t, f)]
            t3, q = gl[(t2, p[f])]
            assert t3 == t and q == inv(p) and p[f] in range(4)

def orientable_consistent(gl: Spec) -> bool:
    """every gluing orientation reversing on the ordered vertices (sign -1), valid for a fixed global orientation by vertex order."""
    return all(sign(p) == -1 for (_, _), (_, p) in gl.items())

class UF:
    def __init__(self) -> None:
        self.par: Dict = {}
        self.par_sign: Dict = {}
    def find(self, x):
        self.par.setdefault(x, x); self.par_sign.setdefault(x, 1)
        if self.par[x] == x:
            return x, 1
        r, s = self.find(self.par[x])
        self.par[x] = r
        self.par_sign[x] *= s
        return r, self.par_sign[x]
    def union(self, x, y, s):  # x ~ s*y
        rx, sx = self.find(x); ry, sy = self.find(y)
        if rx == ry:
            return (sx * sy * s) == 1  # consistent?
        self.par[rx] = ry
        self.par_sign[rx] = sx * s * sy  # rx = sx*x... keep simple: sign relating
        return True

def vertex_classes(gl: Spec) -> Dict[Tuple[int, int], int]:
    uf = UF()
    n = ntets(gl)
    for t in range(n):
        for v in range(4):
            uf.find((t, v))
    for (t, f), (t2, p) in gl.items():
        for v in range(4):
            if v != f:
                uf.union((t, v), (t2, p[v]), 1)
    reps: Dict = {}
    out = {}
    for t in range(n):
        for v in range(4):
            r, _ = uf.find((t, v))
            out[(t, v)] = reps.setdefault(r, len(reps))
    return out

def edge_classes(gl: Spec):
    """Return (cls, sgn, degrees, reversed_flag): cls[(t,i,j)] for i<j local edge -> class id; sgn = +1 if the class orientation
    agrees with i->j. reversed_flag True if some edge is identified with itself with reversed orientation."""
    n = ntets(gl)
    # directed edge nodes (t,i,j) i != j ; reverse edge identified with sign -1
    par: Dict = {}
    def find(x):
        par.setdefault(x, (x, 1))
        r, s = par[x]
        if r == x:
            return x, 1
        r2, s2 = find(r)
        par[x] = (r2, s * s2)
        return r2, s * s2
    bad = [False]
    def union(x, y, s):
        rx, sx = find(x); ry, sy = find(y)
        if rx == ry:
            if sx * sy != s:
                bad[0] = True
            return
        par[rx] = (ry, sx * s * sy)
    for t in range(n):
        for i in range(4):
            for j in range(i + 1, 4):
                union((t, i, j), (t, j, i), -1)
    for (t, f), (t2, p) in gl.items():
        vs = [v for v in range(4) if v != f]
        for i in vs:
            for j in vs:
                if i < j:
                    union((t, i, j), (t2, p[i], p[j]), 1)
    ids: Dict = {}
    cls = {}; sgn = {}
    for t in range(n):
        for i in range(4):
            for j in range(i + 1, 4):
                r, s = find((t, i, j))
                cid = ids.setdefault(r, len(ids))
                cls[(t, i, j)] = cid; sgn[(t, i, j)] = s
    deg = [0] * len(ids)
    for c in cls.values():
        deg[c] += 1
    return cls, sgn, deg, bad[0]

def link_euler(gl: Spec) -> Tuple[int, int, int, int]:
    """vertex link complex: triangles (t,v); edges (t,face,v) v in face; vertices (t,v,w) directed edge (corner at v along edge vw).
    Returns (V,E,F,chi) summed over all vertex links; also connectedness separately via vertex_classes."""
    n = ntets(gl)
    par: Dict = {}
    def find(x):
        par.setdefault(x, x)
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            par[ra] = rb
    # link vertices: (t,v,w), v!=w : the point of edge vw near v.
    for (t, f), (t2, p) in gl.items():
        for v in range(4):
            for w in range(4):
                if v != w and v != f and w != f:
                    union((t, v, w), (t2, p[v], p[w]))
    V = len({find((t, v, w)) for t in range(n) for v in range(4) for w in range(4) if v != w})
    # link edges: (t, f, v) with v != f: edge of link triangle at v, in face f. glued with (t2,p[f],p[v])
    par2: Dict = {}
    def find2(x):
        par2.setdefault(x, x)
        while par2[x] != x:
            par2[x] = par2[par2[x]]; x = par2[x]
        return x
    for (t, f), (t2, p) in gl.items():
        for v in range(4):
            if v != f:
                a, b = find2((t, f, v)), find2((t2, p[f], p[v]))
                if a != b:
                    par2[a] = b
    E = len({find2((t, f, v)) for t in range(n) for f in range(4) for v in range(4) if v != f})
    F = 4 * n
    return V, E, F, V - E + F

def local_edge_disjoint(q: int) -> List[Tuple[int, int]]:
    """quad type q = 0,1,2 for partitions 01|23, 02|13, 03|12; the quad is disjoint from (does not meet) the two edges of the pair."""
    pairs = [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]
    return list(pairs[q])

def I_matrix(gl: Spec):
    """I[e][t*3+q] = number of the two local edges disjoint from q (in tet t) in class e."""
    cls, sgn, deg, bad = edge_classes(gl)
    n = ntets(gl); ne = len(deg)
    I = [[0] * (3 * n) for _ in range(ne)]
    for t in range(n):
        for q in range(3):
            for (i, j) in local_edge_disjoint(q):
                I[cls[(t, i, j)]][3 * t + q] += 1
    return I

# ---- Haken matching equations (7 coords per tet: t0..t3, q0..q2)
def quad_for_arc(face_opp: int, corner: int) -> int:
    """quad type meeting face (opp face_opp) in the arc cutting off `corner`: separates {corner,face_opp} from the other two."""
    others = tuple(sorted(set(range(4)) - {corner, face_opp}))
    a = tuple(sorted((corner, face_opp)))
    pairs = {(0, 1): 0, (2, 3): 0, (0, 2): 1, (1, 3): 1, (0, 3): 2, (1, 2): 2}
    assert pairs[a] == pairs[others]
    return pairs[a]

def haken_matching(gl: Spec):
    n = ntets(gl)
    rows = []
    seen = set()
    for (t, f), (t2, p) in sorted(gl.items()):
        if (t2, p[f]) in seen:
            continue
        seen.add((t, f))
        for i in range(4):
            if i == f:
                continue
            row = [0] * (7 * n)
            row[7 * t + i] += 1
            row[7 * t + 4 + quad_for_arc(f, i)] += 1
            j = p[i]; f2 = p[f]
            row[7 * t2 + j] -= 1
            row[7 * t2 + 4 + quad_for_arc(f2, j)] -= 1
            rows.append(row)
    return rows

def quad_cols(n: int) -> List[int]:
    return [7 * t + 4 + q for t in range(n) for q in range(3)]
