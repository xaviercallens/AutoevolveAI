"""JAC, DIV and ROOT rules, own implementation from the paper's wording (Sec. 2)."""
import sys, json
sys.path.insert(0, "/tmp/bistabaudit/code")
import sympy as sp
from net import catalogue, field, swap, x, y, a, b, rho, K

ids = catalogue()
PARS = [a, b, rho, *K]


def coeff_signs_nonneg(expr, vars_) -> bool:
    P = sp.Poly(sp.expand(expr), *vars_)
    return all(c >= 0 for c in P.coeffs())


def jac(es) -> bool:
    f, g = field(es, "F")
    D = sp.expand(sp.diff(f, x) * sp.diff(g, y) - sp.diff(f, y) * sp.diff(g, x))
    V = [x, y, rho, *K[:len(es)]]
    P = sp.Poly(D, *V)
    return all(c >= 0 for c in P.coeffs()) and P.coeff_monomial(rho) == 1


def div(es) -> bool:
    f, g = field(es, "F")
    Km = sp.Matrix([[x * sp.diff(f, x) - f, y * sp.diff(f, y)],
                    [x * sp.diff(g, x), y * sp.diff(g, y) - g]])
    D = sp.expand(Km.det())
    V = [x, y, a, b, rho, *K[:len(es)]]
    P = sp.Poly(D, *V)
    return all(c >= 0 for c in P.coeffs()) and P.coeff_monomial(a * b) == 1


def csign(c, m):
    if c == 0:
        return 0
    P = sp.Poly(sp.expand(c), *PARS[:3 + m])
    cs = P.coeffs()
    if all(v > 0 for v in cs):
        return 1
    if all(v < 0 for v in cs):
        return -1
    return None  # free


def maxvar(signs) -> int:
    # DP: best[s] = max variations with last nonzero sign s (0 = none yet)
    best = {0: 0}
    for s in signs:
        opts = [s] if s is not None else [-1, 0, 1]
        nb = {}
        for last, v in best.items():
            for o in opts:
                if o == 0:
                    nl, nv = last, v
                else:
                    nl, nv = o, v + (1 if last != 0 and last != o else 0)
                nb[nl] = max(nb.get(nl, -1), nv)
        best = nb
    return max(best.values())


def sylv(p, q, v, nominal: bool):
    if not nominal:
        return sp.resultant(p, q, v)
    P, Q = sp.Poly(p, v), sp.Poly(q, v)
    pc = [P.coeff_monomial(v**i) for i in (2, 1, 0)]
    qc = [Q.coeff_monomial(v**i) for i in (2, 1, 0)]
    M = sp.Matrix([pc + [0], [0] + pc, qc + [0], [0] + qc])
    return M.det(method="berkowitz")


def root_ok(es, elim, nominal) -> tuple:
    f, g = field(es, "F")
    v, t = (y, x) if elim == "y" else (x, y)
    R = sp.expand(sylv(f, g, v, nominal))
    if R == 0:
        return False, None
    P = sp.Poly(R, t)
    deg = P.degree()
    sg = [csign(P.coeff_monomial(t**i), len(es)) for i in range(deg, -1, -1)]
    fixed = any(s in (1, -1) for s in sg)
    mv = maxvar(sg)
    return (mv <= 2 and fixed), mv


if __name__ == "__main__":
    names = sorted(ids)
    J = [n for n in names if jac(ids[n])]
    rest = [n for n in names if n not in J]
    Dv = [n for n in rest if div(ids[n])]
    rest2 = [n for n in rest if n not in Dv]
    T1 = [l.split()[0] for l in open("/tmp/bistabaudit/code/a2_witness.py").read().split('T2 = """')[1].split('"""')[0].splitlines()]
    FLUX = "N0350 N0354 N0355 N0361 N0369 N0391 N0600 N0610 N0638 N0646 N0648 N0649 N0661 N0673".split()
    print("JAC", len(J), "DIV", len(Dv), "remaining", len(rest2))
    print("positives excluded by JAC/DIV:", [n for n in T1 if n in J + Dv])
    by_size = {}
    for n in names:
        s = len(ids[n]); tag = "JAC" if n in J else "DIV" if n in Dv else "REST"
        by_size.setdefault(s, {}).setdefault(tag, 0); by_size[s][tag] += 1
    print("by size", by_size)
    neg = [n for n in rest2 if n not in T1]
    print("remaining negatives", len(neg), "positives in rest", sum(1 for n in rest2 if n in T1),
          "FLUX all in rest:", all(n in neg for n in FLUX))
    res = {}
    for n in rest2:
        es = ids[n]
        r = {}
        for nominal in (False, True):
            for who, e in (("rep", es), ("swap", swap(es))):
                for elim in ("y", "x"):
                    r[f"{'nom' if nominal else 'act'}_{who}_{elim}"] = root_ok(e, elim, nominal)
        res[n] = r
    json.dump({"JAC": J, "DIV": Dv, "rest": rest2, "root": {n: {k: list(v) for k, v in r.items()} for n, r in res.items()}},
              open("/tmp/bistabaudit/a3_rules.json", "w"), indent=0)
    def cnt(pred):
        return sum(1 for n in neg if pred(res[n])), sum(1 for n in T1 if pred(res[n])), sum(1 for n in FLUX if pred(res[n]))
    for key in res[neg[0]]:
        print(key, "neg/pos/flux pass:", cnt(lambda r: r[key][0]))
    print("act any:", cnt(lambda r: any(v[0] for k, v in r.items() if k.startswith("act"))))
    print("nom any:", cnt(lambda r: any(v[0] for k, v in r.items() if k.startswith("nom"))))
    print("any:", cnt(lambda r: any(v[0] for v in r.values())))
    by = {}
    for n in neg:
        if n in FLUX:
            continue
        s = len(ids[n]); ok = any(v[0] for v in res[n].values())
        by.setdefault(s, [0, 0]); by[s][0 if ok else 1] += 1
    print("non-FLUX negatives by size [pass, fail]:", by)
