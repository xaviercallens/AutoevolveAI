"""C1b aggregation of the N = 11 census parts + exact Fraction finish.

Usage: aggregate_census.py <mod> <out.json> [--partial]

- Reads data/parts/part_<res>of<mod>.json for res = 0..mod-1; every part must pass its count check (graphs == geng count,
  bad_lines == 0). Without --partial, every part must be present and the total must equal OEIS A001349(11) = 1,006,700,565.
- Exact (Fraction) solve of Allen eqs. (5),(6),(9) (dbcore.neff_exact, C1 code) for: every candidate (not certified-excluded:
  all regular graphs and anything the inequality could not exclude), every 'near' graph (certified-excluded but with upper bound
  >= N - near_margin), and the 10 non-regular graphs with the smallest certified gap over all parts.
- Amplifiers (exact N_eff > 11) are listed with graph6, exact N_eff and nauty-labelg canonical form; Richter's graph is
  canonicalised the same way and compared.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dbcore as d  # noqa: E402

ROOT = HERE.parent
PARTS = ROOT / "data" / "parts"
C1DATA = ROOT.parent / "C1" / "data"
A001349_11 = 1006700565
A005177_11 = 539
N = 11


def canon(g6s: list[str]) -> list[str]:
    if not g6s:
        return []
    p = subprocess.run(["taskset", "-c", "2,3", "nauty-labelg", "-q"], input="\n".join(g6s) + "\n", capture_output=True, text=True,
                       check=True)
    return p.stdout.split()


def main() -> None:
    mod, out = int(sys.argv[1]), sys.argv[2]
    partial = "--partial" in sys.argv
    t0 = time.time()
    total = excluded = regular = guard = chol = 0
    missing: list[int] = []
    bad: list[int] = []
    cands: dict[str, dict] = {}
    near: dict[str, dict] = {}
    nearest: list[dict] = []
    top: list[list] = []
    max_eps = 0.0
    cpu = wall = 0.0
    done = []
    for r in range(mod):
        p = PARTS / f"part_{r:04d}of{mod}.json"
        if not p.exists():
            missing.append(r)
            continue
        dd = json.load(open(p))
        if not dd.get("count_check_ok"):
            bad.append(r)
            continue
        done.append(r)
        total += dd["graphs"]
        excluded += dd["excluded_certified"]
        regular += dd["regular"]
        guard += dd["guard_fail"]
        chol += dd["chol_fail"]
        max_eps = max(max_eps, dd["max_eps"])
        cpu += dd["cpu_seconds"]
        wall += dd["wall_seconds_part"]
        if dd["n_candidates"] != len(dd["candidates"]) or dd["n_near"] != len(dd["near"]):
            raise SystemExit(f"part {r}: truncated candidate/near list")
        for c in dd["candidates"]:
            cands[c["graph6"]] = c
        for c in dd["near"]:
            near[c["graph6"]] = c
        nearest += dd["nonregular_nearest_to_N"]
        top += dd["top_by_float_neff"]
    if bad or (missing and not partial):
        raise SystemExit(f"missing parts {missing[:10]}... ({len(missing)}), failed parts {bad}")
    nearest.sort(key=lambda x: x["gap_lower"])
    top.sort(key=lambda x: -x[0])
    exact_rows = []
    to_solve = list(cands) + [g for g in near if g not in cands]
    lead = [x["graph6"] for x in nearest[:10]]
    to_solve += [g for g in lead if g not in cands and g not in near]
    for g in to_solve:
        adj = d.parse_graph6(g)
        ne = d.neff_exact(adj)[0]
        degs = sorted(len(a) for a in adj)
        exact_rows.append({"graph6": g, "source": "candidate" if g in cands else ("near" if g in near else "nearest_leader"),
                           "regular": degs[0] == degs[-1], "degrees": degs, "edges": sum(degs) // 2, "N_eff": str(ne),
                           "N_eff_float": float(ne), "class": "gt" if ne > N else ("eq" if ne == N else "lt")})
    amps = [x for x in exact_rows if x["class"] == "gt"]
    ca = canon([x["graph6"] for x in amps])
    for x, c in zip(amps, ca):
        x["canonical_labelg"] = c
    r11 = (C1DATA / "richter_n11_amplifier.g6").read_text().strip()
    cr = canon([r11])[0]
    cand_rows = [x for x in exact_rows if x["source"] == "candidate"]
    nonreg_lt = sorted((x for x in exact_rows if x["class"] == "lt" and not x["regular"]), key=lambda x: -Fraction(x["N_eff"]))
    res = {
        "N": N, "mod": mod, "parts_done": len(done), "parts_missing": len(missing), "partial": bool(missing),
        "graphs": total, "A001349_11": A001349_11, "count_equals_A001349": total == A001349_11,
        "excluded_certified_lt": excluded, "candidates": len(cands), "near_graphs": len(near),
        "regular_graphs": regular, "A005177_11": A005177_11, "regular_equals_A005177": regular == A005177_11,
        "guard_fail": guard, "chol_fail": chol, "max_eps": max_eps,
        "exact_candidates_gt": sum(x["class"] == "gt" for x in cand_rows),
        "exact_candidates_eq": sum(x["class"] == "eq" for x in cand_rows),
        "exact_candidates_eq_nonregular": sum(x["class"] == "eq" and not x["regular"] for x in cand_rows),
        "exact_candidates_lt": sum(x["class"] == "lt" for x in cand_rows),
        "count_gt_total": len(amps),
        "count_eq_total": sum(x["class"] == "eq" for x in cand_rows),
        "count_lt_total": excluded + sum(x["class"] == "lt" for x in cand_rows),
        "amplifiers": amps, "richter_graph6": r11, "richter_canonical": cr,
        "amplifier_canonical_classes": sorted(set(ca)), "richter_among_amplifiers": cr in ca,
        "only_richter": len(set(ca)) == 1 and cr in ca,
        "nearest_nonamplifiers_exact": nonreg_lt[:10],
        "nonregular_nearest_to_N_certified": nearest[:25], "top_by_float_neff": top[:25],
        "census_cpu_seconds_sum": round(cpu, 1), "census_part_wall_seconds_sum": round(wall, 1),
        "exact_rows": exact_rows, "aggregate_seconds": round(time.time() - t0, 1),
    }
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("exact_rows", "top_by_float_neff", "nonregular_nearest_to_N_certified")},
                     indent=1)[:6000])


if __name__ == "__main__":
    main()
