"""Certified witness check with Arb ball arithmetic (python-flint), not Sturm/rational intervals."""
import sys, json
sys.path.insert(0, "/tmp/bistabaudit/code")
import sympy as sp
import flint
from flint import arb, acb, fmpq, fmpz_poly
from net import catalogue, field, x, y, a, b, rho, K

flint.ctx.prec = 400
T2 = """N0438 1/50 1/50 401/202 25/10201 5025/10201
N0440 1/50 3/100 601/202 25/10201 5025/10201
N0442 1/50 3/100 43/29 100/41209 2525/2601
N0443 1/50 1/50 401/202 25/10201 5025/10201
N0448 3/100 1/50 401/202 25/10201 10050/20503
N0450 3/100 3/100 601/202 25/10201 20100/41209
N0452 3/100 3/100 43/29 100/41209 10100/10609
N0453 3/100 1/50 401/202 25/10201 20100/41209
N0459 1/50 3/100 601/202 25/10201 20100/41209
N0467 3/100 3/100 601/202 25/10201 1675/3468
N0474 1/100 1/25 601/202 25/10201 5025/10201
N0476 1/100 1/25 43/29 50/10353 2525/2601
N0477 1/100 3/100 401/202 25/10201 5025/10201
N0480 1/50 3/100 601/202 25/10201 5025/10201
N0482 1/50 3/100 43/29 50/10353 2525/2601
N0483 1/50 1/50 401/202 25/10201 5025/10201
N0489 1/50 3/100 601/202 50/20503 20100/41209
N0510 3/100 1/50 101/2 25 5050/103
N0514 3/100 3/100 17 100/9 2600/2809
N0515 3/100 1/50 101/2 25 10100/10609
N0520 1/25 1/50 101/2 25 2525/52
N0524 1/25 3/100 17 100/9 650/729
N0525 1/25 1/50 101/2 25 2525/2704
N0548 1/50 1/25 17 100/159 2600/2809
N0549 1/50 3/100 101/2 50/103 10100/10609
N0554 3/100 3/100 17 100/159 2600/2809
N0555 3/100 1/50 101/2 50/103 10100/10609"""


def to_arb(q) -> arb:
    q = sp.Rational(q)
    return arb(fmpq(int(q.p), int(q.q)))


def ev(poly: sp.Poly, X: arb, Y: arb):
    s = arb(0)
    for (i, j), c in poly.terms():
        s += to_arb(c) * X**i * Y**j
    return s


def sign(v: arb) -> int:
    if v > 0:
        return 1
    if v < 0:
        return -1
    return 0  # undecided


def check(es: tuple, pars: list, r=1) -> dict:
    sub = {a: pars[0], b: pars[1], rho: r}
    sub.update({K[i]: pars[2 + i] for i in range(len(es))})
    f, g = field(es, "F")
    f, g = sp.expand(f.subs(sub)), sp.expand(g.subs(sub))
    R = sp.Poly(sp.resultant(f, g, y), x)
    R = sp.Poly(sp.sqf_part(R.as_expr()), x)
    den = sp.ilcm(*[sp.Rational(c).q for c in R.all_coeffs()])
    Z = fmpz_poly([int(c * den) for c in reversed(R.all_coeffs())])
    fP, gP = sp.Poly(f, x, y), sp.Poly(g, x, y)
    fx, fy, gx, gy = [sp.Poly(sp.diff(p, v), x, y) for p in (f, g) for v in (x, y)]
    gy_poly = sp.Poly(g, y)
    eqs, undecided = [], 0
    for root, mult in Z.complex_roots():
        if root.imag != 0 or not (root.real > 0):
            if root.imag == 0 and not (root.real < 0) and not (root.real > 0):
                undecided += 1
            continue
        X0 = root.real
        cs = [ev(sp.Poly(c, x, y), X0, arb(1)) for c in gy_poly.all_coeffs()]
        if len(cs) == 3:
            A, B, Cc = cs
            disc = B * B - 4 * A * Cc
            if disc < 0:
                continue
            if not disc > 0:
                undecided += 1
                continue
            ys = [(-B + disc.sqrt()) / (2 * A), (-B - disc.sqrt()) / (2 * A)]
        elif len(cs) == 2:
            ys = [-cs[1] / cs[0]]
        else:
            undecided += 1
            continue
        for Y0 in ys:
            fv = ev(fP, X0, Y0)
            if fv != 0 and (fv > 0 or fv < 0):
                continue  # certified non-solution
            # certified that f contains 0; uniqueness: the other y must be certified non-solution
            ysg = sign(Y0)
            tr = ev(fx, X0, Y0) + ev(gy, X0, Y0)
            det = ev(fx, X0, Y0) * ev(gy, X0, Y0) - ev(fy, X0, Y0) * ev(gx, X0, Y0)
            eqs.append({"x": float(X0.mid()), "y": float(Y0.mid()), "ysign": ysg,
                        "tr": sign(tr), "det": sign(det)})
    pos = [e for e in eqs if e["ysign"] == 1]
    und = undecided + sum(1 for e in eqs if 0 in (e["ysign"], e["tr"], e["det"]))
    return {"degR": R.degree(), "n_pos": len(pos),
            "sinks": sum(1 for e in pos if e["tr"] == -1 and e["det"] == 1),
            "saddles": sum(1 for e in pos if e["det"] == -1), "undecided": und, "eqs": pos}


if __name__ == "__main__":
    ids = catalogue()
    out = {}
    for line in T2.splitlines():
        n, *ps = line.split()
        r = check(ids[n], [sp.Rational(p) for p in ps])
        out[n] = r
        print(n, r["degR"], "pos", r["n_pos"], "sinks", r["sinks"], "saddles", r["saddles"],
              "und", r["undecided"], [round(e["x"], 5) for e in r["eqs"]])
    ok = sum(1 for r in out.values() if r["n_pos"] == 3 and r["sinks"] == 2 and r["saddles"] == 1 and r["undecided"] == 0)
    print("PASS 3 pos = 2 sinks + 1 saddle:", ok, "/27")
    # producer param comparison
    prod = json.load(open("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal6/2026-11-02/BIO-BISTAB/data/p2_witnesses.json"))
    diff = [n for line in T2.splitlines() for n in [line.split()[0]]
            if [sp.Rational(p) for p in prod[n]["params"]] != [sp.Rational(p) for p in line.split()[1:]]]
    print("param rows differing from producer:", diff)
    json.dump(out, open("/tmp/bistabaudit/a2_witness.json", "w"), indent=1)
