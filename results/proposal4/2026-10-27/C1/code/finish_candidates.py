"""Exact Fraction solve of every enclosure candidate. Usage: finish_candidates.py <enc.json> <out.json>"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dbcore as d  # noqa: E402


def main() -> None:
    enc = json.load(open(sys.argv[1]))
    n = enc["N"]
    rows = []
    for c in enc["candidates"]:
        g = d.parse_graph6(c["graph6"])
        ne = d.neff_exact(g)[0]
        degs = sorted(len(a) for a in g)
        rows.append({"graph6": c["graph6"], "regular": degs[0] == degs[-1], "N_eff": str(ne),
                     "class": "gt" if ne > n else ("eq" if ne == n else "lt")})
    out = {"N": n, "graphs": enc["graphs"], "excluded_certified_lt": enc["excluded_certified"], "candidates": len(rows),
           "candidates_exact": rows,
           "count_gt": sum(r["class"] == "gt" for r in rows), "count_eq": sum(r["class"] == "eq" for r in rows),
           "count_eq_nonregular": sum(r["class"] == "eq" and not r["regular"] for r in rows),
           "count_lt_total": enc["excluded_certified"] + sum(r["class"] == "lt" for r in rows),
           "top_by_float_neff_over_N": enc["top_by_float_neff"][:10], "max_eps": enc["max_eps"],
           "min_certified_gap_among_excluded": enc["min_certified_gap_among_excluded"],
           "nonregular_nearest_to_N": enc.get("nonregular_nearest_to_N"),
           "enclosure_seconds": enc["seconds"]}
    json.dump(out, open(sys.argv[2], "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "candidates_exact"}, indent=1))


if __name__ == "__main__":
    main()
