import sys
sys.path.insert(0, "/tmp/bistabaudit/code")
import sympy as sp
from a2_witness import check, T2
from net import catalogue, field, x, y, a, b, rho, K

ids = catalogue()
R = sp.Rational
base = ((1, 2), (2, 3), (3, 1))  # Y->2X, 2X->X+Y, X+Y->Y (displayed order of Sec. 4)
pars = [R(4, 99), R(1, 90), R(10), R(50, 9), R(10)]
r = check(base, pars)
print("baseline:", r["n_pos"], r["sinks"], r["saddles"], r["undecided"], [round(e["x"], 6) for e in r["eqs"]])
f, g = field(base, "E", ks=pars[2:])
f, g = f.subs({a: pars[0], b: pars[1]}), g.subs({a: pars[0], b: pars[1]})
for xv in (R(1, 10), R(1, 5), R(3, 5)):
    ys = [s for s in sp.solve(g.subs(x, xv), y) if s.is_positive and sp.simplify(f.subs({x: xv, y: s})) == 0]
    Jm = sp.Matrix([[sp.diff(f, x), sp.diff(f, y)], [sp.diff(g, x), sp.diff(g, y)]]).subs({x: xv, y: ys[0]})
    print(" x", xv, "y", ys[0], "det", sp.nsimplify(Jm.det()), "tr", Jm.trace())
aplus = R(1, 99) + 7 * sp.sqrt(21) / 891
for av in (R(4610, 100000), R(4611, 100000)):
    rr = check(base, [av] + pars[1:])
    print(" a =", av, "vs a+ =", sp.N(aplus, 10), "sinks", rr["sinks"], "pos", rr["n_pos"])
for nm, es in (("empty", ()), ("X->Y", ((0, 1),)), ("X<->Y", ((0, 1), (1, 0))), ("X+Y<->2X", ((2, 3), (3, 2))), ("N0056", ids["N0056"])):
    rr = check(es, [R(1, 3), R(2, 7)] + [R(3, 2), R(5, 4)][:len(es)])
    print("neg control", nm, "pos eq", rr["n_pos"], "sinks", rr["sinks"])
lost = 0
for line in T2.splitlines():
    n, *ps = line.split()
    p = [R(q) for q in ps]
    res = [check(ids[n], [p[0] * s] + p[1:])["sinks"] for s in (2, 5, 20, 100, 1000)]
    lost += any(s < 2 for s in res)
print("witnesses losing bistability under a-scaling (x2..x1000):", lost, "/27")
