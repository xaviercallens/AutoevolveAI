"""Power-sum instability certificates for BDF-k, and the controls that give them meaning.

A certificate is an index m with |s_m| > k, where s_m is the m-th power sum of the roots of the
characteristic polynomial. Its existence proves a root outside the unit disc. These tests pin the
indices the Lean proofs rely on and, more importantly, check that the machinery can say NO.
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

from kge_bdf_pilot import bdf  # noqa: E402
from kge_gen_stability_lean import find_certificate, power_sums  # noqa: E402


def test_certificate_indices_match_the_lean_proofs():
    m7, s7 = find_certificate(bdf(7)[0])
    m8, s8 = find_certificate(bdf(8)[0])
    assert (m7, m8) == (59, 8)
    assert abs(s7[-1]) > 7 and abs(s8[-1]) > 8
    assert abs(float(s7[-1]) - 8.0379) < 1e-3
    assert abs(float(s8[-1]) - 8.7147) < 1e-3
    # Minimality: no earlier index certifies, so the Lean proof cannot be using a lucky m.
    assert all(abs(v) <= 7 for v in s7[:-1]) and all(abs(v) <= 8 for v in s8[:-1])


@pytest.mark.parametrize("k", [1, 2, 3, 4, 5, 6])
def test_stable_methods_have_no_certificate(k):
    """The control: for methods whose roots are inside the disc the certificate must NOT exist."""
    with pytest.raises(ValueError):
        find_certificate(bdf(k)[0], horizon=400)


@pytest.mark.parametrize("k", [3, 6, 7, 8])
def test_newton_power_sums_agree_with_the_actual_roots(k):
    """Independent check of the exact arithmetic the Lean numerals come from."""
    a, _ = bdf(k)
    roots = np.roots([float(x) for x in reversed(a)])
    s = power_sums(a, 12)
    for m in range(1, 13):
        numeric = np.sum(roots ** m)
        assert abs(numeric.imag) < 1e-8
        assert abs(numeric.real - float(s[m])) < 1e-8 * max(1.0, abs(float(s[m]))), (k, m)


def test_power_sums_satisfy_the_recurrence_exactly():
    for k in (5, 7, 8):
        a, _ = bdf(k)
        s = power_sums(a, 80)
        assert all(sum(a[j] * s[m + j] for j in range(k + 1)) == 0 for m in range(80 - k))


def test_a_polynomial_with_all_roots_inside_stays_bounded():
    """(z - 1/2)(z + 1/3): every power sum must satisfy |s_m| <= 2."""
    a = [Fraction(-1, 6), Fraction(-1, 6), Fraction(1)]
    assert all(abs(v) <= 2 for v in power_sums(a, 60))
