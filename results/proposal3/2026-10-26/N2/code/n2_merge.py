"""N2: merge n2_certify_part.py outputs (disjoint sub-domains covering the full initial grid) exactly, into a run
record with the same keys as n2_certify.py (cert_rationals etc.).

usage: python -I n2_merge.py OUT.json PART1.json PART2.json ...
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction


def q_up(x: Fraction, den: int = 10**12) -> Fraction:
    return Fraction(math.ceil(x * den), den)


def q_lo(x: Fraction, den: int = 10**12) -> Fraction:
    return Fraction(math.floor(x * den), den)


def main() -> None:
    out, parts = sys.argv[1], [json.load(open(p)) for p in sys.argv[2:]]
    p0 = parts[0]
    for p in parts:
        for k in ("potential", "param", "N", "t0", "qmax", "refine_tol", "max_depth", "n2_certify.py_sha256"):
            assert p[k] == p0[k], k
    N = p0["N"]
    cover = sorted((tri, i) for p in parts for tri in p["tris"] for i in range(p["ilo"], p["ihi"]))
    assert cover == sorted((tri, i) for tri in (0, 1) for i in range(N)), "parts do not tile the grid exactly once"
    tot = {}
    for k in ("g", "lin", "ezp"):
        lo = sum((Fraction(p["totals"][k]["lo"]) for p in parts), Fraction(0))
        hi = sum((Fraction(p["totals"][k]["hi"]) for p in parts), Fraction(0))
        tot[k] = (lo, hi)
    st = {"cells": sum(p["stats"]["cells"] for p in parts), "refined": sum(p["stats"]["refined"] for p in parts),
          "failed": sum(p["stats"]["failed"] for p in parts)}
    for k in ("lmin_lo", "lminu_lo", "qpd_lo"):
        st[k] = min(p["stats"][k] for p in parts)
    pd_ok = st["failed"] == 0 and st["lmin_lo"] > 0 and st["lminu_lo"] > 0 and st["qpd_lo"] > 0

    def ball(lo: Fraction, hi: Fraction) -> dict:
        return {"lo": str(q_lo(lo)), "hi": str(q_up(hi)), "lo_float": float(lo), "hi_float": float(hi),
                "mid": float((lo + hi) / 2), "rad": float((hi - lo) / 2)}

    Mlo, Mhi = tot["g"]
    rec = {"potential": p0["potential"], "param": p0["param"], "path": "shear", "N": N, "t0": p0["t0"], "qmax": p0["qmax"],
           "refine_tol": p0["refine_tol"], "max_depth": p0["max_depth"], "cell_rule_order": 2,
           "n_lattice_half": p0["n_lattice_half"], "seconds": sum(p["seconds"] for p in parts),
           "M_window_curvature_bound": ball(Mlo, Mhi), "U_lin_pp0_B2_majorant": ball(*tot["lin"]), "E0": ball(*tot["ezp"]),
           "tails": p0["tails"], "stats": st, "positivity_ok": pd_ok, "certified_not_local_min": bool(Mhi < 0) and pd_ok,
           "cert_rationals": {"M_hi": str(q_up(Mhi)), "M_lo": str(q_lo(Mlo)),
                              "lmin_lo": str(Fraction(math.floor(st["lmin_lo"] * 10**12), 10**12)),
                              "lminu_lo": str(Fraction(math.floor(st["lminu_lo"] * 10**12), 10**12)),
                              "qpd_lo": str(Fraction(math.floor(st["qpd_lo"] * 10**12), 10**12))},
           "controls": {"E0_contains_P2": bool(float(tot["ezp"][0]) <= 1.7658983 <= float(tot["ezp"][1]))
                        if (p0["potential"], p0["param"]) == ("yukawa", "1") else None, "P2_E0": "1.7658983"},
           "parts": sys.argv[2:], "script_sha256": p0["n2_certify.py_sha256"],
           "part_script_sha256": p0["n2_certify_part.py_sha256"]}
    json.dump(rec, open(out, "w"), indent=1)
    print(json.dumps({k: rec[k] for k in ("M_window_curvature_bound", "U_lin_pp0_B2_majorant", "E0", "stats",
                                          "certified_not_local_min", "controls")}, indent=1))


if __name__ == "__main__":
    main()
