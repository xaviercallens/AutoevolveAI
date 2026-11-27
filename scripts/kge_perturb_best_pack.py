#!/usr/bin/env python3
"""Pack the per-seed arm files of the perturb-the-best experiment into a compact, committed table.

The raw arm files are ~100 MB (each carries Lean text for every solved seed). This keeps, per arm / rung / seed,
only the fields the analysis reads, gzipped; nothing is recomputed or altered.
"""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

KEEP = ("seed", "solved", "evaluations", "tree_point_evaluations", "generations_observed", "collapsed_generations",
        "first_collapse_generation", "immigration_events", "inserted_total", "admitted_total",
        "inserted_equal_to_best_fitness", "dedup_fail", "var_fitness_post10")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    out = {}
    for f in sorted(a.dir.glob("A?.json")):
        d = json.loads(f.read_text())
        out[f.stem] = {r["rung"]: [{k: x.get(k) for k in KEEP} | {"survival_gens": x.get("survival_gens", [])} for x in r["arms"]]
                       for r in d["rungs"]}
    with gzip.open(a.out, "wt") as g:
        json.dump(out, g, separators=(",", ":"))
    print(f"wrote {a.out}: arms {sorted(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
