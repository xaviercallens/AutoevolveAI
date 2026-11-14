"""Positive and negative controls for the AIC-LUO recheck."""
import cmath, itertools, json, math, os, sys
import sympy as sp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luo_lib import *
from m12_structure import PAIRINGS, analyze, dual_words, gap_run
from m34_equations import analyse, solve_thurston, thurston
import regina

out = {}


def spec_from_regina(tri):
    gl = {}
    for t in range(tri.size()):
        tet = tri.tetrahedron(t)
        for f in range(4):
            adj = tet.adjacentTetrahedron(f)
            if adj is None:
                raise RuntimeError("boundary face")
            g = tet.adjacentGluing(f)
            gl[(t, f)] = (adj.index(), tuple(g[i] for i in range(4)))
    return gl


# ---- P-a: figure eight knot complement (ideal triangulation, 2 tets)
fig = regina.Example3.figureEight()
fig.orient()
gl8 = spec_from_regina(fig)
pa = {"signs_all_odd": orientable_consistent(gl8), "n_edge_classes": None}
cls, sgn, deg, bad = edge_classes(gl8)
pa["edge_degrees"] = deg
I8 = I_matrix(gl8)
pa["I"] = I8
for conv in ("paper", "mirror"):
    ok, gb = solve_thurston(I8, 2, conv)
    zs, eqs = thurston(sp.Matrix(I8).tolist(), 2, conv)
    # test z=w=exp(+-i pi/3) numerically
    vals = {}
    for sgn_ in (1, -1):
        z = cmath.exp(sgn_ * 1j * math.pi / 3)
        res = [complex(e.subs({zs[0]: z, zs[1]: z}).evalf()) for e in eqs]
        vals[f"z=w=exp({sgn_}i*pi/3)"] = [abs(r - 1) < 1e-12 for r in res]
    pa[conv] = {"groebner_solvable": ok, "edge_eqs_hold_at": vals}
# SnapPy shapes against my equations
import snappy
M = snappy.Manifold("4_1")
shapes = [complex(s) for s in M.tetrahedra_shapes("rect")]
pa["snappy_shapes"] = [str(s) for s in shapes]
try:
    best = None
    for conv in ("paper", "mirror"):
        zs, eqs = thurston(sp.Matrix(I8).tolist(), 2, conv)
        r = max(abs(complex(e.subs({zs[0]: shapes[0], zs[1]: shapes[1]}).evalf()) - 1) for e in eqs)
        pa[f"snappy_shapes_residual_{conv}"] = r
except Exception as ex:
    pa["snappy_error"] = repr(ex)
out["P_a_figure_eight"] = pa

# ---- P-b: lens spaces and sphere from Regina through my pi1 code
pb = {}
for name, tri in (("lens(3,1)", regina.Example3.lens(3, 1)), ("lens(5,2)", regina.Example3.lens(5, 2)), ("lens(7,2)", regina.Example3.lens(7, 2)), ("lens(2,1)=RP3", regina.Example3.lens(2, 1)), ("S3_lens(1,0)", regina.Example3.lens(1, 0)) ):
    try:
        gl = spec_from_regina(tri)
        res, cls, sgn = analyze(gl)
        pb[name] = {"size": tri.size(), "vertex_classes": res["n_vertex_classes"], "link_chi": res["link_V_E_F_chi"][3],
                    "gap_edge_presentation": res["gap_edge_presentation"][:3], "regina_homology": str(tri.homology())}
    except Exception as ex:
        pb[name] = {"error": repr(ex)}
out["P_b_known_manifolds"] = pb

# ---- P-c: my Haken-quad projection vs Regina quad coordinates on the paper triangulation
tri = regina.Triangulation3()
tets = [tri.newTetrahedron(), tri.newTetrahedron()]
for (t, fs, t2, fd) in PAIRINGS:
    p = perm_from_faces(fs, fd)
    f = ({0, 1, 2, 3} - set(fs)).pop()
    tets[t].join(f, tets[t2], regina.Perm4(*p))
gl = spec_from_pairings(PAIRINGS)
res, I, W = analyse(gl, "paper")
pc = {"my_projection_dim": res["projection_dim"], "my_haken_solution_dim": res["haken_solution_dim"]}
try:
    mat = regina.makeMatchingEquations(tri, regina.NS_QUAD) if hasattr(regina, "makeMatchingEquations") else None
    if mat is not None:
        m = sp.Matrix([[int(mat.entry(i, j).longValue()) if hasattr(mat.entry(i, j), "longValue") else int(mat.entry(i, j)) for j in range(mat.columns())] for i in range(mat.rows())])
        pc["regina_quad_matching_rank"] = m.rank(); pc["regina_quad_columns"] = mat.columns()
        pc["regina_quad_kernel_dim"] = mat.columns() - m.rank()
        pc["regina_kernel_dim_equals_my_kerW_dim"] = (mat.columns() - m.rank()) == res["kernel_dim_W"]
except Exception as ex:
    pc["regina_quad_error"] = repr(ex)
out["P_c_regina_quad"] = pc

# ---- N-a: perturb one face pairing (every alternative vertex-image of the target face for each of the 4 pairings)
na = []
base_sig = None
for idx in range(len(PAIRINGS)):
    t, fs, t2, fd = PAIRINGS[idx]
    for perm in itertools.permutations(fd):
        if perm == fd:
            continue
        pairs = list(PAIRINGS)
        pairs[idx] = (t, fs, t2, perm)
        try:
            g = spec_from_pairings(pairs)
            check_closed(g)
            r, c, s = analyze(g)
            I2 = sp.Matrix(I_matrix(g))
            rw, I_, W_ = analyse(g, "x")
            na.append({"pairing_index": idx, "new_target": list(perm), "all_odd": r["orientation_reversing_all_gluings"],
                       "vertex_classes": r["n_vertex_classes"], "degrees": r["edge_degrees"], "link_chi": r["link_V_E_F_chi"][3],
                       "pi1": r["gap_edge_presentation"][:2] if r["n_vertex_classes"] == 1 else "n/a(multi-vertex: edge presentation invalid)",
                       "same_claim_profile": (r["edge_degrees"] == [2, 5, 5] and r["n_vertex_classes"] == 1 and r["gap_edge_presentation"][0] == "ORDER 3" and I_ == sp.Matrix([[1,0,0,1,0,0],[0,2,0,1,0,2],[1,0,2,0,2,0]])),
                       "kernel_W_dim": rw["kernel_dim_W"], "smallsupport": list(rw["small_support_kerW"].keys())})
        except Exception as ex:
            na.append({"pairing_index": idx, "new_target": list(perm), "error": repr(ex)[:80]})
out["N_a_perturbed_pairings"] = na
out["N_a_summary"] = {"n_perturbations": len(na), "n_with_identical_claim_profile": sum(1 for x in na if x.get("same_claim_profile")),
                      "n_that_failed_or_changed": sum(1 for x in na if not x.get("same_claim_profile"))}

# ---- N-b: perturb one entry of I and rerun the Thurston solver and kernel check
nb = []
I0 = [[1, 0, 0, 1, 0, 0], [0, 2, 0, 1, 0, 2], [1, 0, 2, 0, 2, 0]]
for r_ in range(3):
    for c_ in range(6):
        I1 = [row[:] for row in I0]
        I1[r_][c_] += 1
        solv, _ = solve_thurston(I1, 2, "paper")
        Ws = sp.Matrix(I1) * sp.diag(*([sp.Matrix([[0, 1, -1], [-1, 0, 1], [1, -1, 0]])] * 2))
        nb.append({"entry": [r_, c_], "thurston_solvable": solv, "rank_W": Ws.rank()})
out["N_b_perturbed_I"] = nb
out["N_b_summary"] = {"n_perturbations": len(nb), "n_solvable_after_perturbation": sum(1 for x in nb if x["thurston_solvable"])}
print(json.dumps(out, indent=1, default=str))
