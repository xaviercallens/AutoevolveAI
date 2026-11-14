"""ROOT rule, my reading of the paper's text: Sylvester resultant (nominal degree 2 in the eliminated variable)
of f,g; coefficient classes + (all monomials positive), - (all negative), * (mixed -> free in {-1,0,1}), 0.
Pass if >=1 fixed strict (+/-) coefficient and max sign variations over free assignments <= 2."""
import json
from collections import Counter
import sympy as sp
from bistab import *
from table1 import T1_TEXT

lab, reps = enumerate_all()
net27 = {tuple(sorted(parse_edge(t) for t in l.split()[1:])): l.split()[0] for l in T1_TEXT.splitlines()}
jd = json.load(open("../data/p4_jac_div.json"))
ks_sym = sp.symbols("k1:4", positive=True)


def sylv2(p, q, v):
    P = sp.Poly(p, v)
    Q = sp.Poly(q, v)
    cp = [P.coeff_monomial(v ** i) for i in (2, 1, 0)]
    cq = [Q.coeff_monomial(v ** i) for i in (2, 1, 0)]
    M = sp.Matrix([[cp[0], cp[1], cp[2], 0], [0, cp[0], cp[1], cp[2]], [cq[0], cq[1], cq[2], 0], [0, cq[0], cq[1], cq[2]]])
    return sp.expand(M.det())


def classes(Pexpr, v, params):
    P = sp.Poly(Pexpr, v)
    deg = P.degree()
    out = []
    for i in range(deg, -1, -1):
        c = sp.Poly(P.coeff_monomial(v ** i), *params)
        co = c.coeffs()
        if not co:
            out.append("0")
        elif all(t > 0 for t in co):
            out.append("+")
        elif all(t < 0 for t in co):
            out.append("-")
        else:
            out.append("*")
    return out


def max_var(seq):
    NEG = -10 ** 9
    # state: last nonzero sign (+1/-1/None) -> best variations
    best = {None: 0}
    for c in seq:
        opts = {"+": [1], "-": [-1], "0": [0], "*": [1, -1, 0]}[c]
        nb = {}
        for last, val in best.items():
            for o in opts:
                if o == 0:
                    key, nv = last, val
                else:
                    key = o
                    nv = val + (1 if (last is not None and last != o) else 0)
                if nb.get(key, NEG) < nv:
                    nb[key] = nv
        best = nb
    return max(best.values())


def root_pass(es):
    ks = list(ks_sym[: len(es)])
    f, g = fields(es, ks)
    params = [a, b, rho, *ks]
    res = {}
    for v, w in [(y, x), (x, y)]:  # eliminate v, polynomial in w
        R = sylv2(f, g, v)
        if R == 0:
            res[str(v)] = None
            continue
        cl = classes(R, w, params)
        ok = any(c in "+-" for c in cl) and max_var(cl) <= 2
        res[str(v)] = dict(classes="".join(cl), maxvar=max_var(cl), ok=bool(ok))
    return res


out = {}
cnt = Counter()
for r in reps:
    pos = r in net27 or swap_set(r) in net27
    rule = jd[str(r)]["rule"]
    if rule != "none" and not pos:
        continue
    res = {}
    for tag, e in [("rep", r), ("partner", swap_set(r))]:
        if tag == "partner" and e == r:
            res[tag] = res["rep"]
        else:
            res[tag] = root_pass(e)
    anyok = any(v and v["ok"] for t in res.values() for v in t.values())
    out[str(r)] = dict(claimed_positive=pos, root_pass=anyok, detail=res)
    cnt[(pos, anyok)] += 1
print("(claimed_positive, ROOT passes under my reading) counts:", dict(cnt))
json.dump(out, open("../data/p5_root.json", "w"))
