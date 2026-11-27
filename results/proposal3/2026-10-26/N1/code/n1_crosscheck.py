"""N1 control: every certified enclosure must contain the independent floating-point (Tier X) value of E''(0; a)
from n1_explore.py (closed-form tau'', Gauss-Legendre Duffy rule, N = 32) at a_lo, a_c and a_hi of the run.

usage: python -I n1_crosscheck.py OUT.json RUN1.json [RUN2.json ...]
"""

from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from n1_explore import run  # noqa: E402
from n1_make_cert import bounds  # noqa: E402


def main() -> None:
    out = sys.argv[1]
    rows = []
    cache: dict[float, float] = {}
    for p in sys.argv[2:]:
        for r in json.load(open(p)):
            if r.get("engine") != "n1_certify2" or not r["ok"]:
                continue
            lo, hi = bounds(r)
            for key in ("a_lo", "a_c", "a_hi"):
                a = float(Fraction(r[key]))
                if a not in cache:
                    cache[a] = run(a, 32)["Epp_closed"]
                x = cache[a]
                rows.append({"run": [r["a_lo"], r["a_hi"]], "a": a, "tierX": x, "lo": float(lo), "hi": float(hi),
                             "contained": float(lo) <= x <= float(hi)})
    bad = [x for x in rows if not x["contained"]]
    json.dump({"n_checks": len(rows), "n_not_contained": len(bad), "rows": rows}, open(out, "w"), indent=1)
    print(f"checks {len(rows)}, not contained {len(bad)}")
    for b in bad:
        print("NOT CONTAINED", b)


if __name__ == "__main__":
    main()
