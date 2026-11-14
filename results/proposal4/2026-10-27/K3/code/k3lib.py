"""K3 library: linear carbon-cycle IRF h(t) = a0 + sum a_i exp(-t/tau_i), interval arithmetic (mpmath iv).

Emission paths are piecewise linear with optional jumps:  m(z) = sum_j c_j [z>=z_j] + sum_j s_j (z-z_j)_+ .
Concentration excess u(t) = int_0^t m(z) h(t-z) dz = sum_j c_j H(t-z_j) + sum_j s_j K(t-z_j),
H(x) = int_0^x h, K(x) = int_0^x H.  All inputs are exact Fractions; evaluation is outward-rounded.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Sequence

import mpmath
from mpmath import iv

iv.dps = 60
mpmath.mp.dps = 60

# Joos et al. 2013, ACP 13, 2793, Table 5, row IRFCO2 (exact decimals as printed).
JOOS_A: tuple[Fraction, ...] = (Fraction("0.2173"), Fraction("0.2240"), Fraction("0.2824"), Fraction("0.2763"))
JOOS_TAU: tuple[Fraction, ...] = (Fraction("394.4"), Fraction("36.54"), Fraction("4.304"))


class IRF:
    def __init__(self, a0: Fraction, a: Sequence[Fraction], tau: Sequence[Fraction]) -> None:
        self.a0, self.a, self.tau = a0, tuple(a), tuple(tau)
        assert len(self.a) == len(self.tau)

    @staticmethod
    def joos() -> "IRF":
        return IRF(JOOS_A[0], JOOS_A[1:], JOOS_TAU)

    def nonneg(self) -> bool:
        return self.a0 >= 0 and all(x >= 0 for x in self.a)

    # --- interval evaluation -------------------------------------------------------------------
    def h(self, x: Fraction):
        r = _iv(self.a0)
        for ai, ti in zip(self.a, self.tau):
            r += _iv(ai) * iv.exp(-_iv(x) / _iv(ti))
        return r

    def H(self, x: Fraction):
        if x <= 0:
            return iv.mpf(0)
        r = _iv(self.a0) * _iv(x)
        for ai, ti in zip(self.a, self.tau):
            r += _iv(ai) * _iv(ti) * (1 - iv.exp(-_iv(x) / _iv(ti)))
        return r

    def K(self, x: Fraction):
        if x <= 0:
            return iv.mpf(0)
        r = _iv(self.a0) * _iv(x) ** 2 / 2
        for ai, ti in zip(self.a, self.tau):
            T = _iv(ti)
            r += _iv(ai) * T * (_iv(x) - T * (1 - iv.exp(-_iv(x) / T)))
        return r


def _iv(q: Fraction):
    return iv.mpf(q.numerator) / iv.mpf(q.denominator)


class Path:
    """m = sum c_j [z>=z_j] + sum s_j (z-z_j)_+ ."""

    def __init__(self, steps: Sequence[tuple[Fraction, Fraction]] = (), kinks: Sequence[tuple[Fraction, Fraction]] = ()) -> None:
        self.steps = tuple(steps)  # (z_j, c_j)
        self.kinks = tuple(kinks)  # (z_j, s_j)

    def m(self, z: Fraction) -> Fraction:
        r = Fraction(0)
        for zj, c in self.steps:
            if z >= zj:
                r += c
        for zj, s in self.kinks:
            if z > zj:
                r += s * (z - zj)
        return r

    def u(self, irf: IRF, t: Fraction):
        r = iv.mpf(0)
        for zj, c in self.steps:
            if t > zj:
                r += _iv(c) * irf.H(t - zj)
        for zj, s in self.kinks:
            if t > zj:
                r += _iv(s) * irf.K(t - zj)
        return r

    def u_float(self, irf: IRF, t: float) -> float:
        import math
        def Hf(x: float) -> float:
            if x <= 0: return 0.0
            return float(irf.a0) * x + sum(float(a) * float(T) * (1 - math.exp(-x / float(T))) for a, T in zip(irf.a, irf.tau))
        def Kf(x: float) -> float:
            if x <= 0: return 0.0
            return float(irf.a0) * x * x / 2 + sum(float(a) * float(T) * (x - float(T) * (1 - math.exp(-x / float(T)))) for a, T in zip(irf.a, irf.tau))
        r = 0.0
        for zj, c in self.steps:
            r += float(c) * Hf(t - float(zj))
        for zj, s in self.kinks:
            r += float(s) * Kf(t - float(zj))
        return r

    def is_unimodal(self, grid: Sequence[Fraction]) -> bool:
        """Nondecreasing then nonincreasing (checked on a grid containing all breakpoints and one point after each)."""
        vals = [self.m(g) for g in grid]
        seen_down = False
        for p, q in zip(vals, vals[1:]):
            if q < p:
                seen_down = True
            elif q > p and seen_down:
                return False
        return vals[0] >= 0 and all(v >= 0 for v in vals)


def from_nodes(nodes: Sequence[tuple[Fraction, Fraction]]) -> Path:
    """Continuous piecewise-linear emission through (z, m) nodes; m is 0 after the last node (which must have m=0
    or be followed by a drop; a final kink returns the slope to 0 and a step removes any remaining level)."""
    kinks: list[tuple[Fraction, Fraction]] = []
    steps: list[tuple[Fraction, Fraction]] = []
    z0, m0 = nodes[0]
    if m0 != 0:
        steps.append((z0, m0))
    prev = Fraction(0)
    for (za, ma), (zb, mb) in zip(nodes, nodes[1:]):
        s = (mb - ma) / (zb - za)
        kinks.append((za, s - prev))
        prev = s
    kinks.append((nodes[-1][0], -prev))
    zl, ml = nodes[-1]
    if ml != 0:
        steps.append((zl, -ml))
    return Path(steps=steps, kinks=kinks)
