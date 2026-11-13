#!/usr/bin/env python3
"""Lifetime learning of constants (Baldwin / Lamarck) against the plain population.

All three ladders were run with the same seeds, sample points and fitness budget,
so each rung is a PAIRED comparison: exact McNemar on the seeds where exactly one
arm solved. Both costs are reported, because lifetime learning spends dosage
passes the fitness budget does not see:

* fitness evaluations -- the budgeted currency;
* tree-point evaluations -- every evaluation of a tree at a point, including the
  passes `tune_constants` spends. A win in fitness evaluations bought with more
  tree-point work than it saves is not a win.

Also reported: how often tuning changed a genome at all, and whether Baldwin and
Lamarck differ on any seed. They are expected to coincide when exact tuning is
all-or-nothing -- a constant is set only if its required value is the same
rational at every sample point, which in practice means setting it solves the
tree -- and the per-seed comparison checks that rather than assuming it.

Usage:
    .venv/bin/python scripts/kge_lifetime_learning_analysis.py --out results/kge_lifetime_learning.json
"""

from __future__ import annotations

import argparse
import json
import statistics
from math import comb
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / "results"


def mcnemar(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def load(name: str) -> dict[str, Any]:
    return json.loads((RESULTS / f"{name}.json").read_text())


def by_seed(rung: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {a["seed"]: a for a in rung["arms"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    none = {r["rung"]: r for r in load("kge_rust_ladder")["rungs"]}
    arms = {"baldwin": load("kge_rust_ladder_baldwin"), "lamarck": load("kge_rust_ladder_lamarck")}
    if none[next(iter(none))]["seeds"] != arms["baldwin"]["rungs"][0]["seeds"]:
        raise RuntimeError("seed counts differ; the comparison would not be paired")

    rows = []
    for rung_b, rung_l in zip(arms["baldwin"]["rungs"], arms["lamarck"]["rungs"]):
        name = rung_b["rung"]
        n0, nb, nl = by_seed(none[name]), by_seed(rung_b), by_seed(rung_l)
        seeds = sorted(n0)
        b_only = sum(1 for s in seeds if nb[s]["solved"] and not n0[s]["solved"])
        n_only = sum(1 for s in seeds if n0[s]["solved"] and not nb[s]["solved"])
        differ = sum(1 for s in seeds if nb[s]["solved"] != nl[s]["solved"]
                     or nb[s]["evaluations"] != nl[s]["evaluations"])
        tuned_any = sum(1 for s in seeds if nb[s].get("constants_tuned", 0) > 0)

        def med(arm: dict[int, dict[str, Any]], key: str, solved_only: bool) -> float | None:
            vals = [arm[s][key] for s in seeds if arm[s]["solved"] or not solved_only]
            vals = [v for v in vals if v is not None]
            return statistics.median(vals) if vals else None

        tp0 = med(n0, "tree_point_evaluations", False) if "tree_point_evaluations" in n0[seeds[0]] \
            else 12 * statistics.median(n0[s]["evaluations"] for s in seeds)
        rows.append({
            "rung": name,
            "target_size": rung_b["target_size"],
            "none_rate": none[name]["solve_rate"],
            "baldwin_rate": rung_b["solve_rate"],
            "lamarck_rate": rung_l["solve_rate"],
            "baldwin_only": b_only,
            "none_only": n_only,
            "mcnemar_p": mcnemar(b_only, n_only),
            "seeds_where_baldwin_and_lamarck_differ": differ,
            "seeds_where_tuning_changed_a_genome": tuned_any,
            "median_fitness_evals_when_solved": {
                "none": med(n0, "evaluations", True), "baldwin": med(nb, "evaluations", True)},
            "median_tree_point_evals_all_runs": {
                "none": tp0, "baldwin": med(nb, "tree_point_evaluations", False)},
        })
        r = rows[-1]
        print(f"  {name:<20} none {r['none_rate']:.3f}  baldwin {r['baldwin_rate']:.3f}  "
              f"lamarck {r['lamarck_rate']:.3f}  B-only {b_only:>3} / none-only {n_only:>2}  "
              f"p={r['mcnemar_p']:.2g}  B!=L on {differ} seeds  "
              f"tree-pt {r['median_tree_point_evals_all_runs']['none']:.0f} -> "
              f"{r['median_tree_point_evals_all_runs']['baldwin']:.0f}")

    report = {
        "question": ("Does exact lifetime learning of constants (Baldwin: adapt the phenotype; "
                     "Lamarck: write the adaptation back) improve the plain population, and does "
                     "it pay for itself in total work?"),
        "design": ("Same seeds, sample points and fitness budget for all three arms; paired exact "
                   "McNemar per rung; both cost currencies reported."),
        "rungs": rows,
    }
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
