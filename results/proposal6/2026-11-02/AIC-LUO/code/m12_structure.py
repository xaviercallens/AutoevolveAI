"""M1/M2: build the paper's triangulation, validity, edge classes, pi1 (own derivation + GAP), cross-check with Regina."""
import json, subprocess, sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luo_lib import *

PAIRINGS = [(0, (1, 2, 3), 0, (2, 3, 0)), (1, (0, 1, 3), 1, (1, 2, 0)),
            (0, (0, 1, 3), 1, (3, 2, 1)), (0, (0, 1, 2), 1, (3, 2, 0))]
PAPER_EDGE_TABLE = {0: {(0,1):'a',(0,2):'b',(0,3):'c',(1,2):'c',(1,3):'b',(2,3):'c'},
                    1: {(0,1):'b',(0,2):'c',(0,3):'b',(1,2):'b',(1,3):'c',(2,3):'a'}}


def pi1_edge_presentation(gl, cls, sgn):
    """one-vertex presentation: generators = edge classes (class orientation); one relation per glued face pair:
    e(ij) e(jk) e(ik)^-1 for face vertices i<j<k of the first side."""
    rels = []
    seen = set()
    for (t, f), (t2, p) in sorted(gl.items()):
        if (t2, p[f]) in seen:
            continue
        seen.add((t, f))
        i, j, k = [v for v in range(4) if v != f]

        def e(a, b, t=t):
            lo, hi = min(a, b), max(a, b)
            s = sgn[(t, lo, hi)] * (1 if a < b else -1)
            return (cls[(t, lo, hi)], s)
        w = [e(i, j), e(j, k), (e(i, k)[0], -e(i, k)[1])]
        rels.append(w)
    return rels


def gap_run(ngen, rels, extra_trivial_gens):
    lines = [f"F:=FreeGroup({ngen});;", "gens:=GeneratorsOfGroup(F);;"]
    rl = []
    for r in rels:
        rl.append("*".join(f"gens[{g+1}]^({s})" for g, s in r))
    for g in extra_trivial_gens:
        rl.append(f"gens[{g+1}]")
    lines.append("rels:=[" + ",".join(rl) + "];;")
    lines.append("G:=F/rels;;")
    lines.append('Print("ORDER ",Size(G),"\\n");')
    lines.append('Print("ABINV ",AbelianInvariants(G),"\\n");')
    lines.append('Print("STRUCT ",StructureDescription(G),"\\n");')
    for g in range(ngen):
        lines.append(f'Print("GEN{g} trivial: ",IsOne(GeneratorsOfGroup(G)[{g+1}]),"\\n");')
    lines.append("QUIT;")
    with tempfile.NamedTemporaryFile("w", suffix=".g", delete=False) as fh:
        fh.write("\n".join(lines))
    return subprocess.run(["gap", "-q", fh.name], capture_output=True, text=True, timeout=300).stdout.strip().splitlines()


def analyze(gl):
    res = {}
    check_closed(gl)
    res["orientation_reversing_all_gluings"] = orientable_consistent(gl)
    vc = vertex_classes(gl)
    res["n_vertex_classes"] = len(set(vc.values()))
    V, E, F, chi = link_euler(gl)
    res["link_V_E_F_chi"] = [V, E, F, chi]
    cls, sgn, deg, bad = edge_classes(gl)
    n = ntets(gl)
    res["edge_classes"] = len(deg)
    res["edge_degrees"] = deg
    res["edge_reversed_self_identification"] = bad
    res["euler_char_manifold"] = res["n_vertex_classes"] - len(deg) + 2 * n - n
    rels = pi1_edge_presentation(gl, cls, sgn)
    res["pi1_relators"] = rels
    res["gap_edge_presentation"] = gap_run(len(deg), rels, [])
    return res, cls, sgn


def dual_words(gl, cls):
    pairs = {}
    nxt = 0
    for key in sorted(gl):
        t2, p = gl[key]
        other = (t2, p[key[1]])
        if other in pairs:
            pairs[key] = (pairs[other][0], -1)
        else:
            pairs[key] = (nxt, 1)
            nxt += 1
    ncls = len(set(cls.values()))
    words = []
    for c in range(ncls):
        (t, i, j) = next(k for k, v in cls.items() if v == c)
        others = [v for v in range(4) if v not in (i, j)]
        state = (t, i, j, others[0], others[1])
        start = state
        w = []
        for _ in range(100):
            t, u, v, w1, w2 = state
            t2, p = gl[(t, w2)]
            w.append(pairs[(t, w2)])
            state = (t2, p[u], p[v], p[w2], p[w1])
            if state == start:
                break
        else:
            raise RuntimeError("no closure")
        words.append(w)
    return pairs, nxt, words


if __name__ == "__main__":
    gl = spec_from_pairings(PAIRINGS)
    res, cls, sgn = analyze(gl)
    name = {cls[(0, 0, 1)]: 'a', cls[(0, 0, 2)]: 'b', cls[(0, 0, 3)]: 'c'}
    mine = {t: {(i, j): name[cls[(t, i, j)]] for i in range(4) for j in range(i + 1, 4)} for t in range(2)}
    res["edge_table_matches_paper"] = (mine == PAPER_EDGE_TABLE)
    res["my_edge_table"] = {str(t): {f"{i}{j}": v for (i, j), v in d.items()} for t, d in mine.items()}
    res["perms"] = {f"{t}:{f}": ["".join(map(str, p)), t2] for (t, f), (t2, p) in gl.items()}
    pairs, ngen, words = dual_words(gl, cls)
    res["dual_complex_words"] = words
    tree_gen = pairs[(0, 2)][0]
    res["dual_tree_generator"] = tree_gen
    res["gap_dual_presentation"] = gap_run(ngen, words, [tree_gen])
    import regina
    tri = regina.Triangulation3()
    tets = [tri.newTetrahedron(), tri.newTetrahedron()]
    for (t, fs, t2, fd) in PAIRINGS:
        p = perm_from_faces(fs, fd)
        f = ({0, 1, 2, 3} - set(fs)).pop()
        tets[t].join(f, tets[t2], regina.Perm4(*p))
    g = tri.group()
    g.intelligentSimplify()
    lens = regina.Example3.lens(3, 1)
    res["regina"] = {"valid": tri.isValid(), "closed": tri.isClosed(), "orientable": tri.isOrientable(),
                     "vertices": tri.countVertices(), "edges": tri.countEdges(), "isoSig": tri.isoSig(),
                     "homology": str(tri.homology()), "pi1_simplified": g.detail(),
                     "edge_degrees": [e.degree() for e in tri.edges()],
                     "isomorphic_to_Regina_Example3_lens(3,1)": tri.isIsomorphicTo(lens) is not None,
                     "Regina_lens(3,1)_isoSig": lens.isoSig(), "Regina_lens(3,1)_size": lens.size()}
    print(json.dumps(res, indent=1, default=str))
