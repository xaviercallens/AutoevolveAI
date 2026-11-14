"""Regular (first-order neutral, N_eff = N) graphs are NOT decided by the weak-selection criterion.
Exploratory check: certified sign of rho_G(r) - rho_K(r) at r = 999/1000 and 1001/1000 for every connected
non-complete regular graph with 4 <= N <= 10 (nauty geng -d k -D k). Usage: regular_check.py <out.json>"""

from __future__ import annotations

import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dbcore as d  # noqa: E402
import fixation_cert as fc  # noqa: E402

RS = [Fraction(999, 1000), Fraction(1001, 1000)]


def main() -> None:
    rows = []
    for n in range(4, 11):
        for k in range(2, n - 1):
            res = subprocess.run(["/usr/bin/nauty-geng", "-cq", f"-d{k}", f"-D{k}", str(n)], capture_output=True, text=True, check=False)
            for s in [x for x in res.stdout.splitlines() if x]:
                adj = d.parse_graph6(s)
                rec = {"N": n, "k": k, "graph6": s}
                for r in RS:
                    c = fc.certify(adj, r)
                    rec[c["r"]] = {"verdict": c["verdict"], "diff_interval": c["diff_interval"]}
                rows.append(rec)
                print(json.dumps(rec), flush=True)
    summary = {"graphs": len(rows),
               "below_K_at_both": sum(all(r[key]["verdict"] == "G_below_K" for key in ("999/1000", "1001/1000")) for r in rows),
               "any_above_K": [r["graph6"] for r in rows if any(r[key]["verdict"] == "G_above_K" for key in ("999/1000", "1001/1000"))],
               "undecided": [r["graph6"] for r in rows if any(r[key]["verdict"] == "undecided" for key in ("999/1000", "1001/1000"))],
               "rows": rows}
    json.dump(summary, open(sys.argv[1], "w"), indent=1)
    print({k: v for k, v in summary.items() if k != "rows"})


if __name__ == "__main__":
    main()
