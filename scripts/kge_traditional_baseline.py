#!/usr/bin/env python3
"""The traditional baseline: exact polynomial regression over a monomial basis.

KGE searches for a SMALL expression that agrees with the specification at a few
sample points and then proves it. The textbook alternative for a polynomial
target is to fit a dense polynomial directly: choose a monomial basis up to some
degree, write one linear equation per sample point, and solve. In exact rational
arithmetic that recovers the coefficients exactly whenever the basis contains the
target AND the system is determined.

That last clause is the comparison. Thirty-five monomials of degree <= 3 in four
variables need at least thirty-five points to pin down; KGE's twelve points leave
a nullspace of dimension at least twenty-three, so the traditional fit is
AMBIGUOUS on the same data the search solves from, and only becomes a recovery
when given enough points. Both regimes are run and reported, because "which
method wins" depends on how much data there is, and saying so is the result.

Exactness throughout (Fractions, Gaussian elimination), so a recovery is a proof
of agreement at the points, not a least-squares approximation.

Usage:
    .venv/bin/python scripts/kge_traditional_baseline.py \
        --selection results/kge_hf_selection.json \
        --points results/python_sample_points.json \
        --out results/kge_hf_traditional_baseline.json
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

VARS = ("h", "w", "q", "p")
MAX_DEGREE = 3


def eval_prefix(text: str, env: dict[str, Fraction]) -> Fraction:
    tokens = text.replace("(", " ( ").replace(")", " ) ").split()
    pos = 0

    def walk() -> Fraction:
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        if tok == "(":
            op = tokens[pos]
            pos += 1
            a = walk()
            b = walk()
            assert tokens[pos] == ")"
            pos += 1
            return {"+": a + b, "-": a - b, "*": a * b}[op]
        if tok in env:
            return env[tok]
        return Fraction(tok)

    value = walk()
    assert pos == len(tokens)
    return value


def monomials(degree: int) -> list[tuple[int, ...]]:
    out = []
    for exps in itertools.product(range(degree + 1), repeat=len(VARS)):
        if sum(exps) <= degree:
            out.append(exps)
    return sorted(out, key=lambda e: (sum(e), e))


def monomial_value(exps: tuple[int, ...], env: dict[str, Fraction]) -> Fraction:
    value = Fraction(1)
    for var, e in zip(VARS, exps):
        value *= env[var] ** e
    return value


def solve_exact(rows: list[list[Fraction]], rhs: list[Fraction]) -> dict[str, Any]:
    """Gaussian elimination over Fractions. Returns rank, nullity and a particular
    solution with free variables set to zero, plus whether the system is
    consistent."""
    n = len(rows)
    m = len(rows[0])
    a = [row[:] + [b] for row, b in zip(rows, rhs)]
    pivots: list[int] = []
    r = 0
    for c in range(m):
        pivot = next((i for i in range(r, n) if a[i][c] != 0), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        inv = 1 / a[r][c]
        a[r] = [x * inv for x in a[r]]
        for i in range(n):
            if i != r and a[i][c] != 0:
                f = a[i][c]
                a[i] = [x - f * y for x, y in zip(a[i], a[r])]
        pivots.append(c)
        r += 1
        if r == n:
            break
    consistent = all(all(x == 0 for x in a[i][:m]) is False or a[i][m] == 0 for i in range(n))
    solution = [Fraction(0)] * m
    for i, c in enumerate(pivots):
        solution[c] = a[i][m]
    return {"rank": len(pivots), "nullity": m - len(pivots), "consistent": consistent,
            "solution": solution}


def fresh_points(count: int, seed: int, exclude: list[dict[str, Fraction]]) -> list[dict[str, Fraction]]:
    rng = random.Random(seed)
    out: list[dict[str, Fraction]] = []
    while len(out) < count:
        env = {v: Fraction(rng.randint(-9, 9), rng.randint(1, 7)) for v in VARS}
        if env not in exclude and env not in out:
            out.append(env)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--points", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--extra-points", type=int, default=28,
                        help="points added for the determined regime (12 + 28 = 40 >= 35)")
    args = parser.parse_args()

    selection = json.loads(args.selection.read_text())
    raw = json.loads(args.points.read_text())
    base_points = [{v: Fraction(s) for v, s in zip(VARS, row)} for row in raw]
    basis = monomials(MAX_DEGREE)

    results = []
    for prob in selection["selected_top"]:
        target = prob["prefix"]
        want_base = [eval_prefix(target, env) for env in base_points]
        regimes = {}
        for label, points in (
            ("12_points_same_as_kge", base_points),
            (f"{len(base_points) + args.extra_points}_points", base_points + fresh_points(args.extra_points, 99, base_points)),
        ):
            want = [eval_prefix(target, env) for env in points]
            rows = [[monomial_value(m, env) for m in basis] for env in points]
            t0 = time.perf_counter()
            sol = solve_exact(rows, want)
            elapsed = time.perf_counter() - t0
            # Check the particular solution against a fresh held-out set: exact
            # recovery means it agrees everywhere, not just at the fitting points.
            heldout = fresh_points(20, 7, points)
            agrees = all(
                sum(c * monomial_value(m, env) for c, m in zip(sol["solution"], basis)) == eval_prefix(target, env)
                for env in heldout
            )
            nonzero = sum(1 for c in sol["solution"] if c != 0)
            regimes[label] = {
                "points": len(points), "basis_size": len(basis), "rank": sol["rank"],
                "nullity": sol["nullity"], "consistent": sol["consistent"],
                "unique": sol["nullity"] == 0,
                "particular_solution_agrees_on_20_heldout": agrees,
                "nonzero_coefficients": nonzero,
                "seconds": round(elapsed, 4),
            }
        results.append({"problem": prob["problem"], "target_prefix": target,
                        "target_size": prob["size"], "regimes": regimes})
        r12 = regimes["12_points_same_as_kge"]
        r40 = regimes[[k for k in regimes if k != "12_points_same_as_kge"][0]]
        print(f"  {prob['problem']:<18} 12 pts: rank {r12['rank']}/{len(basis)} nullity {r12['nullity']:>2} "
              f"recovers={r12['particular_solution_agrees_on_20_heldout']}   "
              f"{r40['points']} pts: nullity {r40['nullity']} recovers={r40['particular_solution_agrees_on_20_heldout']} "
              f"terms={r40['nonzero_coefficients']} {r40['seconds']}s")

    report = {
        "method": f"exact polynomial regression, monomials of degree <= {MAX_DEGREE} in 4 variables ({len(basis)} features), Gaussian elimination over Fractions",
        "why_two_regimes": (
            "With 12 points the system is underdetermined (nullity >= 23) so the fit is ambiguous "
            "on the same data KGE solves from; with at least 35 points it is determined and recovers "
            "exactly. Which method wins depends on how much data there is."),
        "not_claimed": [
            "This baseline needs the target to lie in the chosen monomial basis; a target of degree 4 or with "
            "a non-polynomial form is simply absent from it. KGE's grammar has the same limitation in a "
            "different shape (no division, no transcendental functions).",
            "Recovery is checked on 20 fresh points, not proved by a kernel; the traditional method as run "
            "here has no formal acceptance step.",
        ],
        "problems": results,
    }
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
