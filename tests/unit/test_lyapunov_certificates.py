"""Lyapunov certificates for the roots of the deflated BDF polynomials, and the controls that make them mean something.

The Lean proofs in formal/ANSE/AlixStabilityInside.lean rest on an exact rational P with C^T P C - P = -I
and a sum-of-squares P = sum_i d_i u_i u_i^T, d_i > 0. These tests re-derive that data independently of the
generator and check that the machinery says NO where it must.
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

import pytest
import sympy as sp

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

from kge_lyapunov_cert import certificate, companion, lyapunov, sos_from_last  # noqa: E402


def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def transpose(A):
    return [list(r) for r in zip(*A)]


@pytest.mark.parametrize("k", [2, 3, 4, 5, 6])
def test_exact_lyapunov_equation_and_positive_definite_sos(k):
    c = certificate(k)
    C, P, (ds, us) = c["C"], c["P"], c["sos"]
    d = c["d"]
    lhs = matmul(matmul(transpose(C), P), C)
    for i in range(d):
        for j in range(d):
            assert lhs[i][j] - P[i][j] == (-1 if i == j else 0), (k, i, j)
    assert all(x > 0 for x in ds)
    rebuilt = [[Fraction(0)] * d for _ in range(d)]
    for i in range(d):
        u = [us[i][j] if j < i else (Fraction(1) if j == i else Fraction(0)) for j in range(d)]
        for a in range(d):
            for b in range(d):
                rebuilt[a][b] += ds[i] * u[a] * u[b]
    assert rebuilt == P


@pytest.mark.parametrize("k", [7, 8])
def test_unstable_methods_have_no_positive_definite_certificate(k):
    """The control: where a root is outside the disc, no certificate may exist."""
    c = certificate(k)
    assert c["P"] is not None and c["sos"] is None


def test_a_perturbed_polynomial_breaks_the_lyapunov_equation():
    """P solves the equation for q, and must not solve it for a slightly different q."""
    c = certificate(4)
    q = c["q"][:]
    q[0] += Fraction(1, 100)
    C2 = companion(q)
    lhs = matmul(matmul(transpose(C2), c["P"]), C2)
    d = c["d"]
    assert any(lhs[i][j] - c["P"][i][j] != (-1 if i == j else 0) for i in range(d) for j in range(d))


@pytest.mark.parametrize("k", [2, 3, 4, 5, 6])
def test_the_polynomial_identity_used_in_lean_holds_symbolically(k):
    z, w = sp.symbols("z w")
    c = certificate(k)
    d = c["d"]
    R = lambda x: sp.Rational(x.numerator, x.denominator)
    q, P = [R(x) for x in c["q"]], [[R(x) for x in r] for r in c["P"]]
    e = sum(q[i] * z**i for i in range(d)) + z**d
    f = sum(q[i] * w**i for i in range(d)) + w**d
    Pform = sum(P[i][j] * w**i * z**j for i in range(d) for j in range(d))
    A = sum(P[i][d - 1] * w ** (i + 1) for i in range(d)) - P[d - 1][d - 1] * f
    B = sum(P[d - 1][j] * z ** (j + 1) for j in range(d))
    lhs = sum((z * w) ** i for i in range(d))
    assert sp.expand(lhs - ((1 - z * w) * Pform + A * e + B * f)) == 0
