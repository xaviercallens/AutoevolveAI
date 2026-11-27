"""N2: run the n2_certify.py cell integration (unchanged Model, cell rule, tails) on a sub-domain of the initial Duffy
grid, so that one certificate can be split over two cores; n2_merge.py adds the parts exactly.

usage: python -I n2_certify_part.py POT PARAM N T0 QMAX TRIS ILO IHI OUT.json
  TRIS  comma list of triangles (0, 1);  initial cells (tri, i, j) with ILO <= i < IHI (i = s index), all j.
Totals are written as exact rational endpoints (outward), so the merge is exact.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n2_certify as n  # noqa: E402
from flint import arb  # noqa: E402


def main() -> None:
    pot, par, N, t0_s, qmax = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
    tris = tuple(int(x) for x in sys.argv[6].split(","))
    ilo, ihi, out = int(sys.argv[7]), int(sys.argv[8]), sys.argv[9]
    refine_tol = float(os.environ.get("N2_REFINE_TOL", "0.5"))
    max_depth = int(os.environ.get("N2_MAX_DEPTH", "2"))
    t_start = time.time()
    V = n.Potential(pot, par)
    model = n.Model(V, n.q_arb(t0_s), qmax)
    tot = {"g": arb(0), "lin": arb(0), "ezp": arb(0)}
    st = {"cells": 0, "refined": 0, "failed": 0, "lmin_lo": math.inf, "lminu_lo": math.inf, "qpd_lo": math.inf}
    h0 = Fraction(1, N)
    stack = [(tri, Fraction(i, N), Fraction(j, N), h0, 0) for tri in tris for i in range(ilo, ihi) for j in range(N)]
    while stack:
        tri, s0, t0_, h, depth = stack.pop()
        r = model.cell2(tri, s0, t0_, h)
        wide = (not r["ok"]) or bool(r["width"] > refine_tol * float(h * h))
        if wide and depth < max_depth:
            h2 = h / 2
            for ds in (0, 1):
                for dt in (0, 1):
                    stack.append((tri, s0 + ds * h2, t0_ + dt * h2, h2, depth + 1))
            st["refined"] += 1
            continue
        st["cells"] += 1
        if not r["ok"]:
            st["failed"] += 1
            continue
        for key in tot:
            tot[key] += 2 * r[key]
        for key in ("lmin", "lminu", "qpd"):
            st[key + "_lo"] = min(st[key + "_lo"], float(n.lower_frac(r[key])))
        if st["cells"] % 2000 == 0:
            print(f"  cells {st['cells']} stack {len(stack)} {time.time() - t_start:.0f}s "
                  f"M={float(tot['g'].mid()):.4f}+-{float(tot['g'].rad()):.4f}", flush=True)
    rec = {"potential": pot, "param": par, "N": N, "t0": t0_s, "qmax": qmax, "tris": list(tris), "ilo": ilo, "ihi": ihi,
           "refine_tol": refine_tol, "max_depth": max_depth, "n_lattice_half": len(model.ns),
           "seconds": round(time.time() - t_start, 1), "stats": st,
           "totals": {k: {"lo": str(n.lower_frac(v)), "hi": str(n.upper_frac(v)), "mid": float(v.mid()),
                          "rad": float(v.rad())} for k, v in tot.items()},
           "tails": {k: (float(v.upper()) if isinstance(v, arb) else v) for k, v in model.tails.items()}}
    for f in ("n2_certify.py", "n2_certify_part.py"):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f), "rb") as fh:
            rec[f + "_sha256"] = hashlib.sha256(fh.read()).hexdigest()
    json.dump(rec, open(out, "w"), indent=1)
    print(json.dumps({k: rec[k] for k in ("totals", "stats", "seconds")}, indent=1))


if __name__ == "__main__":
    main()
