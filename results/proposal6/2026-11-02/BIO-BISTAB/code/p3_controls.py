import json
from fractions import Fraction as Fr
import sympy as sp
from bistab import *
from table1 import T1_TEXT, T2
from exact import analyse

out = {}
net = {l.split()[0]: tuple(parse_edge(t) for t in l.split()[1:]) for l in T1_TEXT.splitlines()}

# Positive control: Section 4 baseline of the paper, checked by direct substitution (not by my solver) and by the solver
es = tuple(parse_edge(t) for t in ["Y->2X", "2X->X+Y", "X+Y->Y"])
ks = [sp.Integer(10), sp.Rational(50, 9), sp.Integer(10)]
f, g = fields(es, ks, sp.Rational(4, 99), sp.Rational(1, 90), sp.Integer(1))
J = sp.Matrix([f, g]).jacobian([x, y])
rows = []
for x0 in [sp.Rational(1, 10), sp.Rational(1, 5), sp.Rational(3, 5)]:
    y0 = (sp.Rational(1, 90) + sp.Rational(50, 9) * x0 ** 2) / 11
    sub = {x: x0, y: y0}
    rows.append(dict(x=str(x0), y=str(y0), f=str(f.subs(sub)), g=str(g.subs(sub)), det=str(J.subs(sub).det()), tr=str(J.subs(sub).trace())))
out["baseline_sec4_direct"] = rows
r = analyse(es, [Fr(10), Fr(50, 9), Fr(10)], Fr(4, 99), Fr(1, 90))
out["baseline_sec4_solver"] = {k: r[k] for k in ["n_positive_equilibria", "n_sinks", "n_saddles", "undecided"]}
print(rows)
print(out["baseline_sec4_solver"])

# Negative controls: monostable / complex-balanced / linear
neg = {}
cases = {
    "empty": ([], []),
    "X->Y (linear)": (["X->Y"], [Fr(3)]),
    "X<->Y (reversible linear, detailed balance)": (["X->Y", "Y->X"], [Fr(2), Fr(5)]),
    "X+Y<->2X (reversible bimolecular, deficiency-zero-like piece)": (["X+Y->2X", "2X->X+Y"], [Fr(2), Fr(5)]),
    "N0056 X->X+Y, X+Y->2X (paper's multistationary, <=2 eq expected)": (["X->X+Y", "X+Y->2X"], [Fr(1), Fr(1, 2)]),
}
for name, (ed, kk) in cases.items():
    r = analyse(tuple(parse_edge(t) for t in ed), kk, Fr(1, 50), Fr(1, 30), Fr(1))
    neg[name] = {k: r.get(k) for k in ["status", "n_positive_equilibria", "n_sinks", "n_saddles", "undecided"]}
    print(name, neg[name])
out["negative_controls"] = neg

# Perturbation of each witness: scale a upward until fewer than 2 sinks; and scale all k by tiny
pert = {}
for nid, e in net.items():
    v = [Fr(s) for s in T2[nid]]
    row = {}
    for m in [1, 2, 5, 20, 100, 1000]:
        r = analyse(e, v[2:], v[0] * m, v[1])
        row[f"a x{m}"] = (r["n_sinks"], r["n_positive_equilibria"])
    for m in [Fr(1, 100), Fr(100)]:
        r = analyse(e, [k * m for k in v[2:]], v[0], v[1])
        row[f"all k x{m}"] = (r["n_sinks"], r["n_positive_equilibria"])
    pert[nid] = row
out["perturbation"] = pert
lost = sum(1 for r in pert.values() if any(v[0] < 2 for k, v in r.items() if k.startswith("a x")))
print("witnesses that lose bistability when a is scaled up (some factor in list):", lost, "/ 27")
print("witnesses bistable at a x1:", sum(1 for r in pert.values() if r["a x1"][0] == 2), "/27")
json.dump(out, open("../data/p3_controls.json", "w"), indent=1, default=str)
