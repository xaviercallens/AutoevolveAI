"""Exact zero-stability (Dahlquist root condition) over Q, and its independent oracle.

The first version of `zero_stable_exact` demanded every non-unit root lie STRICTLY
inside the disc and so rejected weakly stable methods (simple roots on the circle,
e.g. leapfrog). The control meant to guard it -- agreement with numeric roots on
BDF1-8 -- could not catch that, because none of those eight has a weak root; only
the over-strictness check against an independent oracle did. These tests encode the
controls that would have caught it, and each can fail.
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

from kge_bdf_pilot import bdf  # noqa: E402
from kge_spec_closure_bdf import cyclotomic, oracle_bounded, poly_divmod, zero_stable_exact  # noqa: E402

F = Fraction


def test_cyclotomic_polynomials_are_exact():
    assert cyclotomic(1) == [F(-1), F(1)]                      # z - 1
    assert cyclotomic(2) == [F(1), F(1)]                       # z + 1
    assert cyclotomic(6) == [F(1), F(-1), F(1)]                # z^2 - z + 1
    # Phi_12 = z^4 - z^2 + 1
    assert cyclotomic(12) == [F(1), F(0), F(-1), F(0), F(1)]
    q, r = poly_divmod([F(-1), F(0), F(0), F(0), F(1)], cyclotomic(4))   # z^4 - 1 over z^2 + 1
    assert q == [F(-1), F(0), F(1)] and r == [F(0)]


def test_weakly_stable_leapfrog_is_accepted_and_agrees_with_the_oracle():
    leapfrog = [F(-1), F(0), F(1)]                              # rho = z^2 - 1, roots +-1
    assert zero_stable_exact(leapfrog)
    assert oracle_bounded(leapfrog)


def test_repeated_root_on_the_circle_is_rejected():
    assert not zero_stable_exact([F(1), F(-2), F(1)])          # (z-1)^2
    assert not zero_stable_exact([F(1), F(0), F(2), F(0), F(1)])  # (z^2+1)^2, repeated +-i


def test_a_root_outside_the_circle_is_rejected():
    assert not zero_stable_exact([F(-2), F(1)])                 # z - 2
    assert not zero_stable_exact([F(2), F(-3), F(1)])           # (z-1)(z-2)


def test_zero_stability_is_the_root_condition_alone_not_consistency():
    # rho = z + 1 has one simple root, at -1: it satisfies the root condition, so it is
    # zero-stable, although it is NOT consistent (rho(1) = 2 != 0). The two properties
    # are separate; consistency is carried by the order conditions (order >= 1 forces
    # rho(1) = 0), which every generated candidate already satisfies.
    inconsistent = [F(1), F(1)]
    assert zero_stable_exact(inconsistent)
    assert oracle_bounded(inconsistent)
    assert sum(inconsistent) != 0


def test_bdf_family_boundary_is_exactly_between_6_and_7():
    for k in range(1, 7):
        a, _ = bdf(k)
        assert zero_stable_exact(a), f"BDF{k} must be zero-stable"
        assert oracle_bounded(a), f"oracle must accept BDF{k}"
    for k in (7, 8):
        a, _ = bdf(k)
        assert not zero_stable_exact(a), f"BDF{k} must fail the root condition"
        assert not oracle_bounded(a), f"oracle must catch BDF{k} (the 400-step horizon did not)"
