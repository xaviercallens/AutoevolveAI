#!/usr/bin/env python3
"""Why does every operator fail at the same rung? Characterise the landscape.

Eight variation operators -- mutation, random crossover, homologous,
anti-homologous, contribution-preserving, same-sites-unscaled, semantic
backpropagation and its matched decoy -- all collapse between target rung L3
(size 9, solve rates 0.3-0.6) and L4 (size 11, at most 1 of 12). A cliff that
every mechanism hits in the same place is not a property of any mechanism, so
this measures the thing they share: the fitness landscape.

THE DISCRIMINATING QUESTION. Search needs a gradient. If a single mutation away
from an exact solution already yields a tree indistinguishable from a random
one, there is nothing to climb and no operator can help; if fitness degrades
gradually, the solution sits in a basin and failure is about budget or operator
quality instead. So we walk AWAY from known solutions and ask how fast the
signal disappears.

For each rung we take the exact target tree, apply k random mutations for
k = 1..5, and compare the resulting fitness distribution against random trees of
the same depth. The statistic of interest is the smallest k at which the
perturbed median is no better than the random median -- the width of the basin
in mutations. We also report neutrality, the fraction of single mutations that
leave fitness exactly unchanged, because a wide plateau and a narrow basin are
different problems with different remedies.

Two things make this a measurement rather than an illustration:

* **The random baseline is drawn the same way the search draws its population**
  (`random_tree` at the same depth), so "no better than random" means no better
  than what the search starts with, not better than an arbitrary reference.
* **Fitness is the same exact-rational function the search optimises**, so the
  landscape measured is the landscape searched, not a proxy for it.

Usage:
    .venv/bin/python scripts/gp_landscape_cliff.py --samples 300 \
        --out results/gp_landscape_cliff.json
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from fractions import Fraction
from pathlib import Path
from typing import Callable, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from lean_gated_recombination import (  # noqa: E402
    Node,
    evaluate,
    fitness,
    mutate,
    random_tree,
    sample_points,
    target_ladder,
)

MAX_SIZE = 25
START_DEPTH = 3


def perturb(tree: Node, steps: int, rng: random.Random) -> Node:
    """Apply `steps` independent random mutations, the search's own operator."""
    out = tree
    for _ in range(steps):
        out = mutate(out, rng, MAX_SIZE)
    return out


def summarise(values: Sequence[Fraction]) -> dict[str, object]:
    """Fitness distribution, as floats for reporting only."""
    floats = sorted(float(v) for v in values)
    if not floats:
        return {"n": 0}
    return {
        "n": len(floats),
        "median": floats[len(floats) // 2],
        "min": floats[0],
        "q1": floats[len(floats) // 4],
        "q3": floats[(3 * len(floats)) // 4],
        "zero_fraction": sum(1 for v in floats if v == 0.0) / len(floats),
    }


def measure_rung(
    name: str,
    target: Node,
    points: Sequence[dict[str, Fraction]],
    spec: Callable[[dict[str, Fraction]], Fraction],
    samples: int,
    seed: int,
) -> dict[str, object]:
    rng = random.Random(seed)

    assert fitness(target, points, spec) == 0, f"{name}: target is not a solution"

    # The baseline the search actually starts from.
    random_fitness = [
        fitness(random_tree(rng, START_DEPTH), points, spec) for _ in range(samples)
    ]
    random_median = statistics.median(float(v) for v in random_fitness)

    walks: list[dict[str, object]] = []
    basin_width: int | None = None
    for steps in range(1, 6):
        perturbed = [
            fitness(perturb(target, steps, rng), points, spec) for _ in range(samples)
        ]
        stats = summarise(perturbed)
        median = float(stats["median"])
        # "Still informative" means the perturbed median beats the random median.
        informative = median < random_median
        walks.append({
            "mutations_from_solution": steps,
            **stats,
            "beats_random_median": informative,
            "ratio_to_random_median": (median / random_median) if random_median else None,
        })
        if basin_width is None and not informative:
            basin_width = steps

    # Neutrality at the solution: single mutations that keep fitness exactly 0.
    singles = [fitness(perturb(target, 1, rng), points, spec) for _ in range(samples)]
    neutral = sum(1 for v in singles if v == 0) / len(singles)

    return {
        "rung": name,
        "target_size": target.size(),
        "random_baseline": summarise(random_fitness),
        "walk_away_from_solution": walks,
        "basin_width_in_mutations": basin_width,
        "neutrality_at_solution": neutral,
        "reading": (
            "basin_width_in_mutations is the smallest k whose perturbed median is no "
            "better than a random tree's. A width of 1 means a single mutation "
            "destroys all signal, so there is no gradient for any operator to climb."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=300)
    parser.add_argument("--points", type=int, default=12)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    points = sample_points(random.Random(20261024), args.points)
    rows: list[dict[str, object]] = []
    for index, (name, node) in enumerate(target_ladder()):
        def spec(env: dict[str, Fraction], n: Node = node) -> Fraction:
            return evaluate(n, env)

        row = measure_rung(name, node, points, spec, args.samples, seed=1000 + index)
        rows.append(row)
        widths = row["basin_width_in_mutations"]
        print(
            f"  {name:<20} size={row['target_size']:>2}  "
            f"basin={widths if widths is not None else '>5':<3}  "
            f"neutrality={row['neutrality_at_solution']:.3f}  "
            f"random_median={row['random_baseline']['median']:.3g}"
        )
        for walk in row["walk_away_from_solution"]:
            ratio = walk["ratio_to_random_median"]
            print(
                f"      k={walk['mutations_from_solution']}  "
                f"median={walk['median']:<12.4g} "
                f"ratio_to_random={ratio:.3f}  "
                f"still_solution={walk['zero_fraction']:.3f}  "
                f"{'informative' if walk['beats_random_median'] else 'NO SIGNAL'}"
            )

    report = {
        "question": (
            "Eight operators collapse between L3 (size 9) and L4 (size 11). Is the "
            "cliff a property of the landscape rather than of any operator?"
        ),
        "method": (
            "Walk away from each rung's exact solution with k = 1..5 applications of "
            "the search's own mutation operator, and compare the fitness distribution "
            "against random trees drawn exactly as the search's initial population is. "
            "The basin width is the smallest k whose median is no better than random."
        ),
        "why_this_is_the_landscape_and_not_a_proxy": (
            "Fitness here is the same exact-rational function the search optimises, and "
            "the baseline is drawn by the same random_tree at the same depth the search "
            "starts from, so 'no better than random' means no better than the search's "
            "own starting point."
        ),
        "parameters": {
            "samples_per_cell": args.samples, "sample_points": args.points,
            "max_size": MAX_SIZE, "start_depth": START_DEPTH,
        },
        "rungs": rows,
        "not_established": [
            "Basin width is measured along the mutation operator's own moves, so it "
            "describes the landscape AS THAT OPERATOR SEES IT. A different "
            "neighbourhood could have a different width; that is a feature for "
            "explaining mutation's behaviour and a limit on generalising further.",
            "A narrow basin explains why search fails but not why the basin narrows "
            "with target size. That would need a count of how many distinct trees "
            "realise each target, which is not attempted here.",
        ],
    }
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
