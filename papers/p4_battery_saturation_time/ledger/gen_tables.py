"""Generate table_cert.tex and tables_check.json from data/data/certified_t_star.json (the post-fix, outward-rounded run).

Also recomputes, for every case, the relative size of the exponential correction to the long-time formula
t = (R^2/(3D)) [ (x*-x0)/(C beta) - 1/5 ]  (first term 2 exp(-a1^2 tau)/(a1^2 F), mpmath 40 digits; Tier X reading of the table).
Run (any python3 with mpmath):  python3 -I ledger/gen_tables.py
"""
from __future__ import annotations

import json
from pathlib import Path

import mpmath as mp

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
mp.mp.dps = 40


def main() -> int:
    recs = json.loads((PAPER / "data" / "data" / "certified_t_star.json").read_text())
    a1 = mp.findroot(lambda a: mp.tan(a) - a, 4.4934)
    rows = []
    corr = []
    for r in recs:
        p, q = map(int, r["tau_lo"].split("/"))
        tau = mp.mpf(p) / q
        f = 3 * tau + mp.mpf(1) / 5
        c = 2 * mp.e ** (-a1**2 * tau) / a1**2 / f
        corr.append(float(c))
        lo, hi = float(r["t_lo_s"]), float(r["t_hi_s"])
        rows.append((r["C"], r["x0"], r["x_star"], lo, hi, float(r["rel_width"]), float(c)))
    tex = [r"\begin{tabular}{rrrrrr}", r"\toprule",
           r"$C$ & $x_0$ & $x^*$ & $t^*$ (s), certified & rel.\ width & corr.\ to long-time formula \\", r"\midrule"]
    for C, x0, xs, lo, hi, w, c in rows:
        xs_t = "1" if xs == "1.0" else "0.9014"
        tex.append(f"{C} & {x0} & {xs_t} & {(lo + hi) / 2:.3f} & {w:.1e} & {c:.1e} \\\\")
    tex += [r"\bottomrule", r"\end{tabular}"]
    (PAPER / "table_cert.tex").write_text("\n".join(tex) + "\n")
    summary = {"n": len(rows), "corr_min": min(corr), "corr_max": max(corr), "corr_below_1e-12": sum(1 for c in corr if c < 1e-12),
               "max_rel_width": max(r[5] for r in rows)}
    (HERE / "tables_check.json").write_text(json.dumps(summary, indent=1))
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
