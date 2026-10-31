"""The certification passes over rusty-SUNDIALS' tables must be able to FAIL.

"All entries match" is only evidence if a wrong entry would have been reported. These tests plant a
typo in an in-memory copy of each table (the real Rust files are never touched) and check that the
comparison used by the certification scripts rejects it, while the unmodified text passes.
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

from kge_bdf_pilot import bdf  # noqa: E402
from kge_certify_sundials_bdf import parse_table, product_coeffs  # noqa: E402
from kge_certify_sundials_errconst import defect, parse_err_table  # noqa: E402

BDF_L_SRC = """
const BDF_L: [[f64; 6]; 6] = [
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],             // unused (order 0)
    [1.0, 1.0, 0.0, 0.0, 0.0, 0.0],             // order 1
    [2.0 / 3.0, 1.0, 1.0 / 3.0, 0.0, 0.0, 0.0], // order 2
    [6.0 / 11.0, 1.0, 6.0 / 11.0, 1.0 / 11.0, 0.0, 0.0], // order 3
    [12.0 / 25.0, 1.0, 7.0 / 10.0, 1.0 / 5.0, 1.0 / 50.0, 0.0], // order 4
    [60.0 / 137.0, 1.0, 225.0 / 274.0, 85.0 / 274.0, 15.0 / 274.0, 1.0 / 274.0], // order 5
];
"""
ERR_SRC = "const BDF_ERR_COEFF: [f64; 6] = [0.0, 0.5, 1.0 / 3.0, 0.25, 0.2, 1.0 / 6.0];"


def rows_that_match(src: str) -> list[bool]:
    table = parse_table(src)
    out = []
    for q in range(1, len(table)):
        prod = product_coeffs(q)
        expected = [c / prod[1] for c in prod]
        out.append(table[q][: q + 1] == expected and all(x == 0 for x in table[q][q + 1:]))
    return out


def err_entries_that_match(src: str) -> list[bool]:
    stored = parse_err_table(src)
    out = []
    for k in range(1, len(stored)):
        a, b = bdf(k)
        out.append(stored[k] == abs(defect(a, b, k) / (math.factorial(k + 1) * b)))
    return out


def test_unmodified_bdf_l_table_passes():
    assert rows_that_match(BDF_L_SRC) == [True] * 5


def test_a_typo_in_a_bdf_l_numerator_is_caught():
    typo = BDF_L_SRC.replace("6.0 / 11.0, 1.0, 6.0 / 11.0", "6.0 / 11.0, 1.0, 6.0 / 12.0")
    result = rows_that_match(typo)
    assert result[2] is False and result.count(False) == 1       # only order 3 is wrong


def test_a_typo_in_a_trailing_zero_is_caught():
    typo = BDF_L_SRC.replace("[1.0, 1.0, 0.0, 0.0, 0.0, 0.0]", "[1.0, 1.0, 0.0, 0.5, 0.0, 0.0]")
    assert rows_that_match(typo)[0] is False


def test_unmodified_error_table_passes():
    assert err_entries_that_match(ERR_SRC) == [True] * 5


def test_a_typo_in_an_error_constant_is_caught():
    typo = ERR_SRC.replace("1.0 / 3.0", "1.0 / 3.5")
    result = err_entries_that_match(typo)
    assert result[1] is False and result.count(False) == 1


def test_decimal_literals_are_read_as_written_not_as_floats():
    # 0.2 as written is exactly 1/5; the nearest f64 is not. The certification is about the written value.
    assert parse_err_table(ERR_SRC)[4] == Fraction(1, 5)
    assert Fraction(0.2) != Fraction(1, 5)
