"""M3/M4: Haken matching, Q-matching matrix, <=2-support kernel vectors, Thurston edge equations (exact)."""
import itertools, json, os, sys
import sympy as sp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luo_lib import *
from m12_structure import PAIRINGS


def omega(n):
    J = sp.Matrix([[0, 1, -1], [-1, 0, 1], [1, -1, 0]])  # w(q,q')=1 if q->q' (x1->x2->x3->x1), paper's convention
    return sp.diag(*([J] * n))


def small_support_vectors(basis_cols, ncoord, maxsupp=2):
    """basis_cols: sympy Matrix whose columns span the space S (in R^ncoord). Return for every support T with |T|<=maxsupp
    the dimension of {v in S : supp(v) subset T} and a basis."""
    out = {}
    for k in range(1, maxsupp + 1):
        for T in itertools.combinations(range(ncoord), k):
            rest = [i for i in range(ncoord) if i not in T]
            if basis_cols.shape[1] == 0:
                continue
            M = basis_cols.extract(rest, list(range(basis_cols.shape[1]))) if rest else sp.zeros(0, basis_cols.shape[1])
            ns = M.nullspace() if rest else [sp.eye(basis_cols.shape[1])[:, i] for i in range(basis_cols.shape[1])]
            vecs = [(basis_cols * v) for v in ns]
            vecs = [v for v in vecs if any(x != 0 for x in v)]
            if vecs:
                out[T] = [list(v) for v in vecs]
    return out


def analyse(gl, label, keep_vectors=True):
    n = ntets(gl)
    res = {"label": label}
    I = sp.Matrix(I_matrix(gl))
    res["I"] = I.tolist()
    W = I * omega(n)
    res["W"] = W.tolist()
    res["rank_W"] = W.rank()
    ker = W.nullspace()
    kerM = sp.Matrix.hstack(*ker) if ker else sp.zeros(3 * n, 0)
    res["kernel_dim_W"] = len(ker)
    # Haken
    H = sp.Matrix(haken_matching(gl))
    ns = H.nullspace()
    res["haken_vars"] = 7 * n; res["haken_rank"] = H.rank(); res["haken_solution_dim"] = len(ns)
    qc = quad_cols(n)
    proj = sp.Matrix.hstack(*ns).extract(qc, list(range(len(ns)))) if ns else sp.zeros(3 * n, 0)
    # column space basis of projection
    projbasis = sp.Matrix.hstack(*proj.columnspace()) if proj.shape[1] else sp.zeros(3 * n, 0)
    res["projection_dim"] = projbasis.shape[1]
    # is the projection space equal to ker(W)?
    res["projection_subset_kerW"] = bool((W * projbasis).is_zero_matrix) if projbasis.shape[1] else True
    res["projection_equals_kerW"] = (projbasis.shape[1] == len(ker)) and res["projection_subset_kerW"]
    sv_proj = small_support_vectors(projbasis, 3 * n)
    sv_ker = small_support_vectors(kerM, 3 * n)
    names = [f"{'xy'[t]}{q+1}" for t in range(n) for q in range(3)] if n == 2 else [f"t{t}q{q+1}" for t in range(n) for q in range(3)]
    fmt = lambda d: {",".join(names[i] for i in T): v for T, v in d.items()}
    res["small_support_projection"] = fmt(sv_proj)
    res["small_support_kerW"] = fmt(sv_ker)
    res["supports_agree"] = set(sv_proj) == set(sv_ker)
    return res, I, W


def thurston(I, n, convention):
    """edge equations product zeta(q)^I = 1. convention 'paper': (s, 1/(1-s), (s-1)/s); 'mirror': (s, (s-1)/s, 1/(1-s))."""
    zs = sp.symbols("z0:%d" % n)
    zeta = []
    for z in zs:
        if convention == "paper":
            zeta += [z, 1 / (1 - z), (z - 1) / z]
        else:
            zeta += [z, (z - 1) / z, 1 / (1 - z)]
    eqs = []
    for row in I:
        prod = sp.Integer(1)
        for e, q in zip(row, zeta):
            prod *= q ** e
        eqs.append(sp.together(prod))
    return zs, eqs


def solve_thurston(I, n, convention, signs=None):
    """Groebner basis over QQ of numerators(edge product - s_e) plus nondegeneracy t*prod(z(1-z))-1. Returns (solvable, gb, remarks)."""
    zs, eqs = thurston(I, n, convention)
    t = sp.Symbol("t")
    polys = []
    for k, e in enumerate(eqs):
        s = 1 if signs is None else signs[k]
        num, den = sp.fraction(sp.together(e - s))
        polys.append(sp.expand(num))
    nd = sp.Integer(1)
    for z in zs:
        nd *= z * (1 - z)
    polys.append(sp.expand(t * nd - 1))
    gb = sp.groebner(polys, *zs, t, order="lex", domain=sp.QQ)
    solvable = not (len(gb.exprs) == 1 and gb.exprs[0] == 1)
    return solvable, [str(g) for g in gb.exprs]


if __name__ == "__main__":
    gl = spec_from_pairings(PAIRINGS)
    out = {}
    res, I, W = analyse(gl, "paper_T")
    paperW = sp.Matrix([[0, 1, -1, 0, 1, -1], [-2, 0, 2, 2, -1, -1], [2, -1, -1, -2, 0, 2]])
    paperI = sp.Matrix([[1, 0, 0, 1, 0, 0], [0, 2, 0, 1, 0, 2], [1, 0, 2, 0, 2, 0]])
    # my edge class numbering is by first appearance sorted by (t,i,j): a<->0,b<->1,c<->2 matches paper (A01=a, A02=b, A03=c)
    res["I_equals_paper_I"] = (I == paperI)
    res["W_equals_paper_W"] = (W == paperW)
    res["W_minus_paper_W"] = (W - paperW).tolist()
    out["structure_matching"] = res
    th = {}
    for conv in ("paper", "mirror"):
        solvable, gb = solve_thurston(I.tolist(), 2, conv)
        th[conv] = {"strict_all_products_1_solvable": solvable, "groebner": gb}
        # generalized: every sign pattern in {1,-1}^3
        gen = {}
        for sg in itertools.product([1, -1], repeat=3):
            s_ok, g2 = solve_thurston(I.tolist(), 2, conv, list(sg))
            gen[str(sg)] = s_ok
        th[conv]["generalized_sign_patterns_solvable"] = gen
        # check z=w=-1
        zs, eqs = thurston(I.tolist(), 2, conv)
        th[conv]["edge_products_at_z=w=-1"] = [str(sp.simplify(e.subs({zs[0]: -1, zs[1]: -1}))) for e in eqs]
    out["thurston"] = th
    # the paper's own printed system
    z, w = sp.symbols("z w")
    e1 = z * w
    e2 = (1 / (1 - z)) ** 2 * w * ((w - 1) / w) ** 2
    e3 = z * ((z - 1) / z) ** 2 * (1 / (1 - w)) ** 2
    out["paper_printed_system_after_w=1/z"] = [str(sp.simplify(e.subs(w, 1 / z))) for e in (e2, e3)]
    out["paper_system_equals_mine_paper_convention"] = None
    zs, eqs = thurston(I.tolist(), 2, "paper")
    mine = [sp.simplify(e.subs({zs[0]: z, zs[1]: w})) for e in eqs]
    out["paper_system_equals_mine_paper_convention"] = [sp.simplify(a - b) == 0 for a, b in zip(mine, (e1, e2, e3))]
    print(json.dumps(out, indent=1, default=str))
