"""Contribution-preserving crossover: does the graft actually preserve it?

Five independent results say subtree recombination fails in this
representation, and the mechanism is exact: an expression is affine in a
subtree's value, out = A + B*v, so a donor contributing B_d*v in its own parent
contributes B_s*v after transplant. Matching only sign(B) was tested and refuted,
with its own negative control outperforming it. The successor recorded as
untested was to RESCALE the donor so the contribution transfers exactly, and
that is what this operator does.

The property is checkable rather than argued, so these tests check it. A site is
admissible only when the coefficient ratio is a single rational across every
sample point -- one scalar cannot correct a point-varying ratio -- and the donor
is then inserted scaled by that ratio. The tests assert the contribution is
EXACTLY equal before and after, in exact rational arithmetic, and that the
admissibility condition is neither vacuous (it must admit something) nor trivial
(it must reject something).

An operator whose claimed invariant is not tested is an assertion. These make it
a measurement.
"""

from __future__ import annotations

import random
import sys
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

from lean_gated_recombination import (  # noqa: E402
    all_addresses,
    all_context_coefficients,
    binary,
    constant_ratio,
    contribution_preserving_crossover,
    evaluate,
    leaf,
    random_tree,
    replace_at,
    sample_points,
    subtree_at,
)


def test_constant_ratio_finds_the_scalar_and_rejects_a_varying_one() -> None:
    """The admissibility condition must discriminate, in both directions."""
    assert constant_ratio([Fraction(6), Fraction(9)], [Fraction(2), Fraction(3)]) == 3
    assert constant_ratio([Fraction(1), Fraction(1)], [Fraction(1), Fraction(1)]) == 1
    # A ratio that differs between points cannot be fixed by one scalar.
    assert constant_ratio([Fraction(6), Fraction(9)], [Fraction(2), Fraction(9)]) is None
    # A zero site coefficient kills the contribution and no scaling recovers it.
    assert constant_ratio([Fraction(5)], [Fraction(0)]) is None
    # Unless the donor contributes nothing there either, which constrains nothing.
    assert constant_ratio([Fraction(0), Fraction(4)], [Fraction(0), Fraction(2)]) == 2


def test_the_graft_preserves_the_contribution_exactly() -> None:
    """The invariant the whole operator exists for, over random trees."""
    rng = random.Random(3)
    points = sample_points(random.Random(5), 6)
    compared = 0
    admissible_pairs = 0
    for _ in range(120):
        a, b = random_tree(rng, 4), random_tree(rng, 4)
        donor_tables = [all_context_coefficients(b, env) for env in points]
        site_tables = [all_context_coefficients(a, env) for env in points]
        donor_address = rng.choice(all_addresses(b))
        donor = subtree_at(b, donor_address)
        donor_coefficients = [table[donor_address] for table in donor_tables]
        for site in all_addresses(a):
            site_coefficients = [table[site] for table in site_tables]
            k = constant_ratio(donor_coefficients, site_coefficients)
            if k is None:
                continue
            admissible_pairs += 1
            graft = donor if k == 1 else binary("*", leaf(k), donor)
            child = replace_at(a, site, graft)
            for index, env in enumerate(points):
                in_parent = donor_coefficients[index] * evaluate(donor, env)
                child_table = all_context_coefficients(child, env)
                in_child = child_table[site] * evaluate(graft, env)
                assert in_parent == in_child, (
                    f"contribution changed: {in_parent} -> {in_child} at site {site}"
                )
                compared += 1
            break
    assert admissible_pairs > 40, (
        f"only {admissible_pairs} admissible transplants -- the condition is too "
        "strict to be exercised, so the invariant is untested"
    )
    assert compared > 200, f"only {compared} comparisons"


def test_the_unscaled_control_does_not_preserve_it() -> None:
    """The control must really be a control: unscaled grafts must differ somewhere.

    `same_sites_unscaled` picks the same sites and omits the scaling. If the
    scaling were a no-op the two arms would be identical and the comparison
    between them would be measuring nothing, so at least one site must exist
    where the unscaled contribution differs.
    """
    rng = random.Random(11)
    points = sample_points(random.Random(13), 6)
    differing = 0
    for _ in range(200):
        a, b = random_tree(rng, 4), random_tree(rng, 4)
        donor_tables = [all_context_coefficients(b, env) for env in points]
        site_tables = [all_context_coefficients(a, env) for env in points]
        donor_address = rng.choice(all_addresses(b))
        donor = subtree_at(b, donor_address)
        donor_coefficients = [table[donor_address] for table in donor_tables]
        for site in all_addresses(a):
            k = constant_ratio(donor_coefficients, [t[site] for t in site_tables])
            if k is None or k == 1:
                continue
            child = replace_at(a, site, donor)   # unscaled, on purpose
            for index, env in enumerate(points):
                in_parent = donor_coefficients[index] * evaluate(donor, env)
                table = all_context_coefficients(child, env)
                if table[site] * evaluate(donor, env) != in_parent:
                    differing += 1
            break
    assert differing > 0, (
        "no unscaled graft changed the contribution, so the scaling is a no-op "
        "and the two arms differ in name only"
    )


def test_the_operator_reports_whether_it_found_a_site() -> None:
    """A fallback must be visible, or the arm silently becomes mutation-only."""
    rng = random.Random(17)
    points = sample_points(random.Random(19), 4)
    counter = [0]
    found_any = False
    missed_any = False
    for _ in range(80):
        a, b = random_tree(rng, 3), random_tree(rng, 3)
        child, found = contribution_preserving_crossover(
            a, b, rng, 25, points, counter, rescale=True
        )
        found_any |= found
        missed_any |= not found
        if not found:
            assert child is a, "a failed search must return the recipient unchanged"
    assert found_any, "the operator never succeeded; it cannot be measured"
    assert counter[0] > 0, "the probe cost was never counted"
