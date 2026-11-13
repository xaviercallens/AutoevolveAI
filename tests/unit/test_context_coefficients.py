"""Reverse-mode context coefficients: exactly the quantity they replace.

A subtree's contribution to an expression is `B` in `output = A + B * v`, and B
is the measured reason subtree crossover behaves as a macromutation: a donor
contributing `B_donor * v` in its own parent contributes `B_site * v` after
transplant, so unless the coefficients agree its contribution is rescaled or
sign-flipped even though its syntax arrived intact.

Computing B per address by the definition costs two whole-tree evaluations each,
O(size^2) per sample point, which measured at 5.5x the tree-point evaluations of
a plain arm -- a hidden cost big enough to make any win on fitness evaluations
meaningless. Reverse mode gives every address's B in one forward and one
backward pass.

An optimisation of a measurement is only admissible if it computes the SAME
number, so that is what these tests check: exact agreement with the definition
on random trees, including the cases that carry the whole point (a `-` must
negate the right branch's coefficient, a `*` must scale each child by its
sibling's value). Exact rational arithmetic throughout, so agreement means
equality and not closeness.
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
    context_coefficient,
    leaf,
    random_tree,
    sample_points,
)


def test_agrees_with_the_definition_on_random_trees() -> None:
    """Exact equality with B = f(v=1) - f(v=0), over every address and point."""
    rng = random.Random(7)
    points = sample_points(random.Random(11), 4)
    checked = 0
    for _ in range(40):
        tree = random_tree(rng, 4)
        for env in points:
            table = all_context_coefficients(tree, env)
            for address in all_addresses(tree):
                direct = context_coefficient(tree, address, [env], [0])[0]
                assert table[address] == direct, (
                    f"reverse mode disagrees at {address}: "
                    f"{table[address]} vs {direct}"
                )
                checked += 1
    assert checked > 500, f"only {checked} comparisons -- too few to mean anything"


def test_minus_negates_the_right_branch() -> None:
    """The case the whole mechanism rests on: `-` inverts a donor's direction."""
    q, p = leaf("q"), leaf("p")
    tree = binary("-", q, p)          # q - p
    env = {"h": Fraction(1), "w": Fraction(1), "q": Fraction(3), "p": Fraction(5)}
    table = all_context_coefficients(tree, env)
    assert table[()] == 1
    assert table[(0,)] == 1, "left of a minus keeps its sign"
    assert table[(1,)] == -1, "right of a minus must be inverted"


def test_times_scales_each_child_by_its_sibling() -> None:
    """And the other half: `*` rescales a donor by whatever it lands beside."""
    h, w = leaf("h"), leaf("w")
    tree = binary("*", h, w)          # h * w
    env = {"h": Fraction(2), "w": Fraction(7), "q": Fraction(0), "p": Fraction(0)}
    table = all_context_coefficients(tree, env)
    assert table[(0,)] == Fraction(7), "h's coefficient is w's value"
    assert table[(1,)] == Fraction(2), "w's coefficient is h's value"


def test_a_nested_product_under_a_minus_composes_both_effects() -> None:
    """Composition is where a hand-rolled rule would most plausibly go wrong."""
    h, w, q = leaf("h"), leaf("w"), leaf("q")
    tree = binary("-", q, binary("*", h, w))    # q - h*w
    env = {"h": Fraction(2), "w": Fraction(5), "q": Fraction(1), "p": Fraction(0)}
    table = all_context_coefficients(tree, env)
    assert table[(0,)] == 1
    assert table[(1,)] == -1, "the product sits on the right of a minus"
    assert table[(1, 0)] == Fraction(-5), "h: -1 * value(w)"
    assert table[(1, 1)] == Fraction(-2), "w: -1 * value(h)"
    # Cross-check every one against the definition.
    for address in all_addresses(tree):
        assert table[address] == context_coefficient(tree, address, [env], [0])[0]
