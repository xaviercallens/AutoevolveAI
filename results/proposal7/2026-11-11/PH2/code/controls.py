"""Controls (PREREG_ITEM.md): positive, negative, broken-method.  usage: sage --python3 controls.py OUT.json"""
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))) if False else None
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from ph2_enclose import *


def contained(X, E):
    d = (R(X.mid()) - R(E.mid())).abs()
    return bool((R(d.upper()) + R(X.rad())).upper() <= R(E.rad()).lower())


def disjoint(X, E):
    d = (R(X.mid()) - R(E.mid())).abs()
    return bool(R(d.lower()) - R(X.rad()) - R(E.rad()).upper() > 0) if False else bool((R(d).lower() - R(X.rad()).upper() - R(E.rad()).upper()) > 0)


def exact_lin(t):
    t = B(QQ(t)); C = B(QQ(1)) / (1 - B(QQ(10000)))
    e1 = (-t).exp(); e4 = (-10000 * t).exp()
    return [(1 - C) * e1 + C * e4, e4]


def exact_log(t):
    t = B(QQ(t))
    return [1 / (1 + 9 * (-t).exp()), (-2 * t).exp()]


LIN = Quad([0, 0], [[-1, 1], [0, -10000]], [[[0, 0], [0, 0]], [[0, 0], [0, 0]]])
LOG = Quad([0, 0], [[1, 0], [0, -2]], [[[-1, 0], [0, 0]], [[0, 0], [0, 0]]])
out = {}
cases = [("lin", LIN, [1, 1], ["1/10", "1", "10"], exact_lin), ("log", LOG, [QQ(1) / 10, 1], ["1", "5", "10"], exact_log)]
for p, tau, tag in [(24, 1e-22, "p24"), (6, 1e-6, "p6")]:
    for name, S, y0, ts, ex in cases:
        res = run(S, y0, [QQ(x) for x in ts], p=p, tau=tau)
        rows = []
        for o in res["outputs"]:
            E = [box_ball(b) for b in o["box"]]
            X = ex(QQ(o["t"]))
            rows.append(dict(t=o["tf"], contained=[contained(X[i], E[i]) for i in range(2)],
                             rel_width=[float((R(E[i].rad()) * 2 / R(E[i].mid()).abs()).upper()) for i in range(2)],
                             exact_x1_plus_1e6_disjoint=[disjoint(X[i] * (1 + B(QQ(1) / 10 ** 6)), E[i]) for i in range(2)]))
        out[f"{name}_{tag}_intact"] = dict(steps=res["steps"], rows=rows, failed=res.get("failed"))
        print(name, tag, "intact", res["steps"], [(r["t"], r["contained"], r["rel_width"]) for r in rows], flush=True)
# broken: p=6, defect dropped, same tau (same step control)
for name, S, y0, ts, ex in cases:
    res = run(S, y0, [QQ(x) for x in ts], p=6, tau=1e-6, drop_defect=True)
    rows = []
    for o in res["outputs"]:
        E = [box_ball(b) for b in o["box"]]
        X = ex(QQ(o["t"]))
        rows.append(dict(t=o["tf"], contained=[contained(X[i], E[i]) for i in range(2)]))
    out[f"{name}_p6_broken"] = dict(steps=res["steps"], rows=rows, failed=res.get("failed"))
    print(name, "p6 BROKEN", res["steps"], [(r["t"], r["contained"]) for r in rows], flush=True)
json.dump(out, open(sys.argv[1], "w"), indent=1)
