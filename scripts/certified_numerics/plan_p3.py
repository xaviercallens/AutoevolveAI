#!/usr/bin/env python3
"""Untrusted planner for P3 (H0 >= 73 exclusion): box layout by the preregistered bisection rule.

For a box Om in [a,b] x omega_b in [c,d] (inside Om band [0.255, 0.35] and omega_b in mu +- 7 sigma):
  K0 = c_light / (100 * 0.73 * r_d(omega_cb(0.73, b), d)) * (1 + 1e-9)    (largest K of any H0 >= 73 point)
  pass if  B_lo(K0) >= 0, A_lo >= 0  and  c_lo(K0) + priorMin(c, d) > threshold.
The environment of each Om slab comes from P1/P2-style tables at its edges (exact mirror of Lean's ieval).
Output: results/certified_numerics/P3_h0/plan.json.
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import emit_p2_cases as E  # noqa: E402
from emit_p2 import lean_table  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "results" / "certified_numerics" / "P3_h0"
MU, SIG = Fraction(2218, 100000), Fraction(55, 100000)
NU = Fraction(107, 10000) * Fraction(6, 100)
C_LIGHT = Fraction(299792458, 1000)


def rd_float(wcb: float, wb: float) -> float:
    return 55.154 * math.exp(-72.3 * (float(NU) + 0.0006) ** 2) / (wcb**0.25351 * wb**0.12807)


def prior_min(c: Fraction, d: Fraction) -> Fraction:
    if d < MU:
        return ((d - MU) / SIG) ** 2
    if MU < c:
        return ((c - MU) / SIG) ** 2
    return Fraction(0)


def main() -> int:
    import argparse
    import shutil
    import emit_p2
    ap = argparse.ArgumentParser()
    ap.add_argument("threshold", nargs="?", default="35.30")
    ap.add_argument("--hmin", default="73/100", help="lower end of the excluded h range")
    ap.add_argument("--mu", default="2218/100000", help="BBN prior mean (negative control C10)")
    ap.add_argument("--scratch", help="write tables/plan into this directory (controls), not the repo")
    ap.add_argument("--max-boxes", type=int, default=400)
    args = ap.parse_args()
    threshold = Fraction(args.threshold)
    hmin = Fraction(args.hmin)
    global MU
    MU = Fraction(args.mu)
    out_dir = OUT
    if args.scratch:
        sd = Path(args.scratch)
        (sd / "lean").mkdir(parents=True, exist_ok=True)
        for f in E.RES.glob("table_*.json"):
            shutil.copy(f, sd / f.name)
        shutil.copy(E.RES / "data.json", sd / "data.json")
        for f in E.LEAN_DIR.glob("T_*.lean"):
            (sd / "lean" / f.name).touch()
        E.RES = sd
        E.LEAN_DIR = sd / "lean"
        emit_p2.RES = sd
        emit_p2.LEAN_DIR = sd / "lean"
        out_dir = sd
    elist = json.loads((REPO / "scripts/certified_numerics/p2_edges.json").read_text())["edges"]
    edges = {Fraction(p, q): n for n, p, q in elist}
    raw = {n: (p, q) for n, p, q in elist}
    for f in (E.RES).glob("table_R*.json"):
        t = json.loads(f.read_text())
        x = Fraction(t["p"], t["q"])
        edges.setdefault(x, t["name"])
        raw.setdefault(t["name"], (t["p"], t["q"]))
    d, P = E.load_PD("Data")
    new_tables: list[str] = []

    def edge(x: Fraction) -> str:
        if x not in edges:
            name = f"R{x.numerator}_{x.denominator}"
            if not (E.LEAN_DIR / f"T_{name}.lean").exists():
                lean_table(name, x.numerator, x.denominator, 2000, False)
                new_tables.append(name)
            edges[x] = name
            raw[name] = (x.numerator, x.denominator)
        return edges[x]

    T = E.tables()
    stack = [(Fraction(51, 200), Fraction(35, 100), MU - 7 * SIG, MU + 7 * SIG)]
    leaves = []
    while stack:
        a, b, c, dd = stack.pop()
        ta, tb = edge(a), edge(b)
        T = E.tables()
        env = [(E.iv_from(T[tb], kind, n)[0], E.iv_from(T[ta], kind, n)[1]) for kind, n in E.ROWS]
        wcb_hi = float(b) * float(hmin) ** 2 - float(NU)
        K0f = float(C_LIGHT) / (100 * float(hmin) * rd_float(wcb_hi, float(dd))) * (1 + 1e-9)
        K0 = Fraction(math.ceil(K0f * 10**9), 10**9)
        A = E.a_iv(P, env)
        B = E.b_iv(P, d, K0, env)
        Cc = E.c_iv(P, d, K0, env)
        L = E.round_down(Cc[0], 2)
        pm = prior_min(c, dd)
        ok = B[0] >= 0 and A[0] >= 0 and L + pm > threshold
        rec = {"Om": [str(a), str(b)], "wb": [str(c), str(dd)], "K0": str(K0), "B_lo": float(B[0]), "c_lo": float(L),
               "prior_min": float(pm), "total": float(L + pm), "pass": bool(ok)}
        if ok:
            leaves.append(rec)
            continue
        if len(leaves) + len(stack) > args.max_boxes:
            rec["aborted_budget"] = True
            leaves.append(rec)
            break
        om_rel, wb_rel = (b - a) / Fraction(1, 100), (dd - c) / SIG
        if b - a <= Fraction(1, 800) and dd - c <= SIG / 8:
            rec["minimal"] = True
            leaves.append(rec)
            continue
        if om_rel >= wb_rel and b - a > Fraction(1, 800):
            m = (a + b) / 2
            stack += [(a, m, c, dd), (m, b, c, dd)]
        else:
            m = (c + dd) / 2
            stack += [(a, b, c, m), (a, b, m, dd)]
    out_dir.mkdir(parents=True, exist_ok=True)
    fails = [l for l in leaves if not l["pass"]]
    (out_dir / "plan.json").write_text(json.dumps({"threshold": str(threshold), "leaves": leaves, "new_tables": new_tables}, indent=1) + "\n")
    print(json.dumps({"threshold": float(threshold), "boxes": len(leaves), "failed_minimal": len(fails), "new_tables": len(new_tables),
                      "worst_pass_total": min((l["total"] for l in leaves if l["pass"]), default=None),
                      "fails": fails[:6]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
