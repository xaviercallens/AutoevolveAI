import json
from collections import Counter
import sympy as sp
from bistab import *
from table1 import T1_TEXT

lab, reps = enumerate_all()
net27 = {tuple(sorted(parse_edge(t) for t in l.split()[1:])): l.split()[0] for l in T1_TEXT.splitlines()}
ks_sym = sp.symbols("k1:4", positive=True)


def tests(es):
    ks = list(ks_sym[: len(es)])
    f, g = fields(es, ks)
    J = sp.Matrix([f, g]).jacobian([x, y])
    dJ = sp.Poly(sp.expand(J.det()), x, y, rho, *ks)
    jac = bool(all(c >= 0 for c in dJ.coeffs()) and dJ.coeff_monomial(rho) > 0)  # strictly positive: rho*1 term
    K = sp.Matrix([[x * J[0, 0] - f, y * J[0, 1]], [x * J[1, 0], y * J[1, 1] - g]])
    dK = sp.Poly(sp.expand(K.det()), x, y, rho, a, b, *ks)
    div = bool(all(c >= 0 for c in dK.coeffs()) and dK.coeff_monomial(a * b) > 0)
    return jac, div


res = {}
cnt = Counter()
for r in reps:
    jr, dr = tests(r)
    jp, dp = tests(swap_set(r)) if swap_set(r) != r else (jr, dr)
    jac, div = jr or jp, dr or dp
    rule = "JAC" if jac else ("DIV" if div else "none")
    pos = r in net27 or swap_set(r) in net27
    res[str(r)] = dict(jac_rep=jr, div_rep=dr, jac_partner=jp, div_partner=dp, rule=rule, claimed_positive=pos)
    cnt[(rule, pos)] += 1
print(dict(cnt))
print("JAC", sum(v for (k, p), v in cnt.items() if k == "JAC"), "DIV after JAC", sum(v for (k, p), v in cnt.items() if k == "DIV"),
      "neither", sum(v for (k, p), v in cnt.items() if k == "none"))
bad = [k for k, v in res.items() if v["rule"] != "none" and v["claimed_positive"]]
print("claimed-positive networks wrongly excluded by JAC/DIV (must be 0):", len(bad))
# per-orientation count (representative only)
print("rep-only JAC:", sum(v["jac_rep"] for v in res.values()), "rep-only DIV|notJAC:", sum((not v["jac_rep"]) and v["div_rep"] for v in res.values()))
json.dump(res, open("../data/p4_jac_div.json", "w"))
