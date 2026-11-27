"""Tests for the w = +1 Gross stratum test of scripts/three_breakthroughs/paper_c_v2_experiment.py.

The w = -1 half of Paper C's P3 is forced (Frobenius fixes e_{E_0} at j = 1728, and w = -1
forces an odd functional equation), so its permutation test cannot fail and carries no
evidence. `w_plus_stratum_test` is the replacement that can: these tests pin its exact
p-value against a hand computation and, crucially, show it reports a LARGE p-value when the
association it measures is absent. A control that cannot come out non-significant is the
defect this test exists to prevent.
"""

from __future__ import annotations

import copy
import importlib.util
import math
import sys
from pathlib import Path
from typing import Any

from hypothesis import given, settings
from hypothesis import strategies as st

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "three_breakthroughs" / "paper_c_v2_experiment.py"
_spec = importlib.util.spec_from_file_location("paper_c_v2_experiment", _SCRIPT)
assert _spec is not None and _spec.loader is not None
X = importlib.util.module_from_spec(_spec)
sys.modules["paper_c_v2_experiment"] = X
_spec.loader.exec_module(X)


def _cls(p: int, charpoly: str, visible: int, invisible: int, nonvanishing: int,
         vanishing: int) -> dict[str, Any]:
    """One w = +1 Hecke class as `gross_lvalues.classes` records it."""
    return {"p": p, "a2_charpoly": charpoly, "root_number": 1, "graph_visible": visible,
            "graph_invisible": invisible, "L_nonvanishing": nonvanishing, "L_vanishing": vanishing}


def _concordant(p: int, charpoly: str, visible: bool) -> dict[str, Any]:
    """A singleton class on which visibility and L-nonvanishing agree."""
    return _cls(p, charpoly, int(visible), int(not visible), int(visible), int(not visible))


def test_perfect_agreement_gives_the_hand_computed_exact_p_value() -> None:
    """Two primes, each with one visible and one invisible orbit -> p = 1/(2*2) = 1/4."""
    rows = [_concordant(227, "x - 1", True), _concordant(227, "x + 1", False),
            _concordant(431, "x - 2", True), _concordant(431, "x + 2", False)]
    got = X.w_plus_stratum_test(rows, [])
    assert got["orbits_total"] == 4
    assert got["orbits_concordant"] == 4
    assert got["agrees_everywhere"] is True
    assert got["within_prime_exact_p_value_exact"] == "1/4"
    assert got["orbits_free_under_null"] == 4
    assert got["orbits_constant_under_null"] == 0


def test_a_prime_with_only_visible_orbits_is_constant_under_the_null() -> None:
    """Nothing to permute where every w = +1 orbit is visible, so it must not buy significance."""
    rows = [_concordant(307, "x - 1", True), _concordant(307, "x - 2", True),
            _concordant(431, "x - 3", True), _concordant(431, "x + 2", False)]
    got = X.w_plus_stratum_test(rows, [])
    assert got["orbits_constant_under_null"] == 2
    assert got["orbits_free_under_null"] == 2
    assert got["within_prime_exact_p_value_exact"] == "1/2"
    assert got["informative_primes"] == [{"p": 431, "visible": 1, "invisible": 1}]


def test_discordance_raises_the_p_value_so_the_test_can_fail() -> None:
    """The property control (iv) lacks: breaking the association must lose significance."""
    rows = [_concordant(p, "x - 1", True) for p in (227, 307, 431, 503, 571)]
    rows += [_concordant(p, "x + 1", False) for p in (227, 307, 431, 503, 571)]
    clean = X.w_plus_stratum_test(rows, [])
    assert clean["within_prime_exact_p_value_exact"] == "1/32"

    broken = copy.deepcopy(rows)
    for r in broken:  # swap visibility on every class, destroying the association
        r["graph_visible"], r["graph_invisible"] = r["graph_invisible"], r["graph_visible"]
    got = X.w_plus_stratum_test(broken, [])
    assert got["orbits_concordant"] == 0
    assert got["within_prime_exact_p_value"] == 1.0
    assert got["agrees_everywhere"] is False
    assert got["within_prime_exact_p_value"] > clean["within_prime_exact_p_value"]


def test_one_discordant_prime_is_already_detected() -> None:
    """Sensitivity: a single flipped prime out of five must move the p-value by a factor of 2+."""
    rows = [_concordant(p, "x - 1", True) for p in (227, 307, 431, 503, 571)]
    rows += [_concordant(p, "x + 1", False) for p in (227, 307, 431, 503, 571)]
    one_bad = copy.deepcopy(rows)
    for r in one_bad:
        if r["p"] == 227:
            r["graph_visible"], r["graph_invisible"] = r["graph_invisible"], r["graph_visible"]
    got = X.w_plus_stratum_test(one_bad, [])
    assert got["orbits_concordant"] == 8
    assert got["within_prime_exact_p_value"] > X.w_plus_stratum_test(rows, [])["within_prime_exact_p_value"]
    assert got["agrees_everywhere"] is False


def test_w_minus_one_classes_are_excluded_entirely() -> None:
    """The forced stratum must not leak in: it would restore the defect being removed."""
    rows = [_concordant(227, "x - 1", True), _concordant(227, "x + 1", False)]
    forced = [{"p": p, "a2_charpoly": "x - 1", "root_number": -1, "graph_visible": 0,
               "graph_invisible": 5, "L_nonvanishing": 0, "L_vanishing": 5} for p in (227, 311, 431)]
    assert X.w_plus_stratum_test(rows, []) == X.w_plus_stratum_test(rows + forced, [])


def test_a_class_mixed_on_both_sides_is_reported_not_resolved() -> None:
    """Where the counts do not determine the pairing, say so instead of guessing."""
    rows = [_cls(503, "x - 1", 1, 1, 1, 1), _concordant(431, "x - 2", True),
            _concordant(431, "x + 2", False)]
    got = X.w_plus_stratum_test(rows, [])
    assert len(got["classes_ambiguous"]) == 1
    assert got["classes_ambiguous"][0]["p"] == 503
    assert len(X.w_plus_stratum_test(rows[1:], [])["classes_ambiguous"]) == 0


def test_analytic_rank_two_orbits_are_counted_from_the_vanishing_factor() -> None:
    """w = +1 with L(f,1) = 0 means even analytic rank >= 2, the cases the FE does not force."""
    rows = [_concordant(227, "x - 1", True), _concordant(227, "x + 1", False)]
    exc = [{"p": 571, "a2_charpoly": "x - 1", "dim": 1, "vanishing_factor": ["L(f,1)"]},
           {"p": 503, "a2_charpoly": "x + 1", "dim": 1, "vanishing_factor": ["L(f x chi_-4,1)"]},
           {"p": 307, "a2_charpoly": "x - 2", "dim": 1, "vanishing_factor": ["none"]}]
    got = X.w_plus_stratum_test(rows, exc)
    assert got["analytic_rank_at_least_2_orbits"] == 1
    assert got["analytic_rank_at_least_2_detail"][0]["p"] == 571


@settings(max_examples=60, deadline=None)
@given(st.lists(st.tuples(st.integers(min_value=1, max_value=3),
                          st.integers(min_value=1, max_value=3)),
                min_size=1, max_size=5))
def test_perfect_agreement_p_value_is_the_product_of_inverse_binomials(
        shape: list[tuple[int, int]]) -> None:
    """Under perfect agreement the exact p-value must be prod 1/C(v+i, i) over the primes."""
    rows, want = [], 1
    for n, (vis, inv) in enumerate(shape):
        p = 227 + 4 * n
        rows += [_concordant(p, f"x - {j}", True) for j in range(vis)]
        rows += [_concordant(p, f"x + {j}", False) for j in range(inv)]
        want *= math.comb(vis + inv, inv)
    got = X.w_plus_stratum_test(rows, [])
    assert got["agrees_everywhere"] is True
    assert got["within_prime_exact_p_value_exact"] == f"1/{want}"
