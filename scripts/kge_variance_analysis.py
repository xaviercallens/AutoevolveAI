#!/usr/bin/env python3
"""Test the prediction H12 registered, and the intervention it implies.

H12 (proved, formal/ANSE/AlixPopulationGenetics.lean) says one round of selection
raises mean fitness by exactly Var(w)/wbar. Registered before these runs, as an
untested prediction for KGE: stalled runs should be those whose population fitness
variance has collapsed; and restoring variance should help.

Pre-registered definitions, fixed in the crate before the runs:
* COLLAPSE: at a generation boundary the population holds at most two distinct
  fitness values;
* INTERVENTION (--immigration): on collapse, replace the worst half with fresh
  random trees, each evaluated out of the same fitness budget.

Three outputs:
1. A control: the instrumented no-immigration run must reproduce the earlier
   Baldwin solve counts exactly, or measuring perturbed the search.
2. The descriptive prediction: collapse fraction (collapsed / observed
   generations) in unsolved versus solved runs, with a rank-sum test.
3. The intervention: paired exact McNemar against the same seeds without
   immigration, with both cost currencies.
"""

from __future__ import annotations

import argparse
import json
import statistics
from math import comb, erf, sqrt
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
R = REPO / "results"


def mcnemar(b: int, c: int) -> float:
    n = b + c
    return 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def ranksum(x: list[float], y: list[float]) -> tuple[float, float]:
    """Mann-Whitney U for x > y, normal approximation; (U, two-sided p)."""
    if not x or not y:
        return float("nan"), 1.0
    u = sum((a > b) + 0.5 * (a == b) for a in x for b in y)
    n1, n2 = len(x), len(y)
    z = (u - n1 * n2 / 2) / sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    return u, 2 * (1 - 0.5 * (1 + erf(abs(z) / sqrt(2))))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    earlier = {r["rung"]: r["solved"] for r in json.loads((R / "kge_rust_ladder_baldwin.json").read_text())["rungs"]}
    base = json.loads((R / "kge_rust_ladder_baldwin_instrumented.json").read_text())
    imm = json.loads((R / "kge_rust_ladder_baldwin_immigration.json").read_text())
    rows = []
    for rb, ri in zip(base["rungs"], imm["rungs"]):
        name = rb["rung"]
        b = {x["seed"]: x for x in rb["arms"]}
        m = {x["seed"]: x for x in ri["arms"]}
        frac = {s: x["collapsed_generations"] / x["generations_observed"] if x["generations_observed"] else 0.0
                for s, x in b.items()}
        solved = [frac[s] for s in b if b[s]["solved"]]
        unsolved = [frac[s] for s in b if not b[s]["solved"]]
        u, p_rs = ranksum(unsolved, solved)
        i_only = sum(1 for s in b if m[s]["solved"] and not b[s]["solved"])
        b_only = sum(1 for s in b if b[s]["solved"] and not m[s]["solved"])
        row = {
            "rung": name,
            "control_reproduces_earlier_baldwin": rb["solved"] == earlier.get(name),
            "baldwin_solved": rb["solved"], "earlier_baldwin_solved": earlier.get(name),
            "immigration_solved": ri["solved"],
            "immigration_only": i_only, "baldwin_only": b_only, "mcnemar_p": mcnemar(i_only, b_only),
            "median_collapse_fraction_unsolved": statistics.median(unsolved) if unsolved else None,
            "median_collapse_fraction_solved": statistics.median(solved) if solved else None,
            "unsolved_runs_ending_collapsed": sum(1 for s in b if not b[s]["solved"] and b[s]["final_distinct_fitness"] <= 2),
            "unsolved_runs": len(unsolved),
            "ranksum_unsolved_gt_solved_p": p_rs,
            "median_tree_points": {
                "baldwin": statistics.median(x["tree_point_evaluations"] for x in rb["arms"]),
                "immigration": statistics.median(x["tree_point_evaluations"] for x in ri["arms"])},
            "median_immigration_events": statistics.median(x["immigration_events"] for x in ri["arms"]),
        }
        # The UNCONFOUNDED test. Solved runs stop early, so comparing collapse
        # fractions between solved and unsolved runs is biased by construction.
        # Instead: solves per generation of exposure in each state. A run is
        # uncollapsed from generation 1 until its first collapse and collapsed
        # afterwards (collapse is treated as absorbing; a run can re-diversify,
        # which biases AGAINST finding a difference). A solve at the run's last
        # generation is credited to the state it happened in. Under equal rates
        # the uncollapsed share of solves is Binomial(k, E_u / (E_u + E_c)).
        if all("first_collapse_generation" in x for x in rb["arms"]):
            e_u = e_c = k_u = k_c = 0
            for x in rb["arms"]:
                g = max(1, x["generations_observed"])
                f = x["first_collapse_generation"]
                if f is None:
                    e_u += g
                    k_u += int(x["solved"])
                else:
                    e_u += f - 1
                    e_c += g - (f - 1)
                    k_c += int(x["solved"])
            k = k_u + k_c
            share = e_u / (e_u + e_c) if e_u + e_c else 0.0
            pmf = [comb(k, j) * share ** j * (1 - share) ** (k - j) for j in range(k + 1)]
            p_obs = pmf[k_u] if k else 1.0
            p_hz = min(1.0, sum(q for q in pmf if q <= p_obs * (1 + 1e-12))) if k else 1.0
            row["hazard"] = {
                "exposure_uncollapsed": e_u, "exposure_collapsed": e_c,
                "solves_uncollapsed": k_u, "solves_collapsed": k_c,
                "rate_uncollapsed": k_u / e_u if e_u else None,
                "rate_collapsed": k_c / e_c if e_c else None,
                "exact_binomial_p": p_hz,
            }
            hz = row["hazard"]
            print(f"  {name:<20} HAZARD  uncollapsed {k_u}/{e_u} gens = {hz['rate_uncollapsed'] or 0:.4f}   "
                  f"collapsed {k_c}/{e_c} gens = {hz['rate_collapsed'] or 0:.4f}   p={p_hz:.2g}")
        rows.append(row)
        print(f"  {name:<20} control={'OK' if row['control_reproduces_earlier_baldwin'] else 'MISMATCH'}  "
              f"baldwin {rb['solved']:>3}  +immigration {ri['solved']:>3}  ({i_only} vs {b_only}, p={row['mcnemar_p']:.2g})  "
              f"collapse frac unsolved {row['median_collapse_fraction_unsolved']} vs solved {row['median_collapse_fraction_solved']} "
              f"(p={p_rs:.2g}); unsolved ending collapsed {row['unsolved_runs_ending_collapsed']}/{len(unsolved)}")
    a.out.write_text(json.dumps({
        "prediction_registered_before_runs": "stalled runs are those whose population fitness variance has collapsed; restoring variance should help",
        "collapse_definition": "at most two distinct fitness values in the population at a generation boundary",
        "intervention": "on collapse, replace the worst half with fresh random trees, paid from the same budget",
        "rungs": rows}, indent=2) + "\n")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
