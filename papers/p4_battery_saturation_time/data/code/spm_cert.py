"""E2: certified enclosures of the SPM surface-saturation time (Arb ball arithmetic).

F(tau) = 3 tau + 1/5 - 2 sum_n exp(-a_n^2 tau)/a_n^2, a_n positive roots of tan a = a.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Callable

from flint import arb, ctx, fmpq

ctx.prec = 300
PI = arb.pi()

_ROOT_CACHE: dict[int, tuple[arb, arb]] = {}


def g_sign(a: arb) -> int:
    """Rigorous sign of g(a)=sin a - a cos a at an exact point (0 if undecided)."""
    v = a.sin() - a * a.cos()
    if v > 0:
        return 1
    if v < 0:
        return -1
    return 0


def certify_bracket(lo: arb, hi: arb) -> bool:
    """True iff g has opposite rigorous signs at lo and hi. On (n pi, n pi + pi/2) g is
    monotone (g' = a sin a keeps its sign), so this certifies exactly one root of tan a = a
    inside [lo, hi]."""
    s1, s2 = g_sign(lo), g_sign(hi)
    return s1 != 0 and s2 != 0 and s1 != s2


def root_bracket(n: int, width_exp: int = 140) -> tuple[arb, arb]:
    """Certified enclosure of alpha_n in (n pi, n pi + pi/2), width about 2^-width_exp."""
    if n in _ROOT_CACHE:
        return _ROOT_CACHE[n]
    npi = PI * n
    # nudge inwards so that exact (zero radius) endpoints lie inside [n pi, n pi + pi/2]
    eps = arb(2) ** (-100)
    lo_a = arb((npi + eps).mid())
    hi_a = arb((npi + PI / 2 - eps).mid())
    if not certify_bracket(lo_a, hi_a):
        raise RuntimeError(f"bracket for root {n} not certified")
    for _ in range(width_exp):
        mid = arb(((lo_a + hi_a) / 2).mid())
        s = g_sign(mid)
        if s == 0:
            raise RuntimeError("undecided sign in bisection")
        if s == g_sign(lo_a):
            lo_a = mid
        else:
            hi_a = mid
    assert certify_bracket(lo_a, hi_a)
    _ROOT_CACHE[n] = (lo_a, hi_a)
    return lo_a, hi_a


def root_ball(n: int) -> arb:
    lo, hi = root_bracket(n)
    return arb(((lo + hi) / 2).mid(), (hi - lo).upper())


def tail_bound(tau: arb, N: int) -> arb:
    """Upper bound of sum_{n>N} exp(-a_n^2 tau)/a_n^2 using a_n >= n pi."""
    m = N + 1
    first = (-(PI * m) ** 2 * tau).exp() / (PI * m) ** 2
    ratio = (-(2 * m) * PI**2 * tau).exp()
    return first / (1 - ratio)


def choose_N(tau: arb, target_exp: int = 100) -> int:
    t = float(tau.mid())
    import math

    need = target_exp * math.log(2)
    n = int(math.sqrt(need / (math.pi**2 * t))) + 2
    return max(n, 5)


def F_ball(tau: arb, roots: Callable[[int], arb] | None = None, c3: int = 3) -> arb:
    """Ball containing F(tau); `roots` lets controls plant wrong roots; c3 the secular factor."""
    rf = roots or root_ball
    N = choose_N(tau)
    s = arb(0)
    for n in range(1, N + 1):
        a = rf(n)
        s += (-(a * a) * tau).exp() / (a * a)
    tb = tail_bound(tau, N)
    tail = arb(tb.upper() / 2, tb.upper() / 2)  # contains [0, tb]
    return c3 * tau + arb(1) / 5 - 2 * (s + tail)


def enclose_tau(T: arb, roots: Callable[[int], arb] | None = None, c3: int = 3,
                rel: float = 1e-13) -> tuple[fmpq, fmpq] | None:
    """Certified [lo,hi] (exact rationals) with F(lo) < T < F(hi). None if T <= 0 (unreachable)."""
    if T.upper() <= 0:
        return None
    hi = fmpq(int(((T / c3).upper() * 2**60).ceil().unique_fmpz()) + 1, 2**60)
    if c3 == 3:
        # 3 tau <= F(tau) <= 3 tau + 1/5 (sum rule), so the root lies in [(T-1/5)/3, T/3]
        lo_i = int((((T - arb(1) / 5) / c3).lower() * 2**60).floor().unique_fmpz())
        lo = fmpq(max(lo_i, 0), 2**60)
    else:
        lo = fmpq(0)
    # certify the bracket numerically (F increasing): F(hi) > T, and F(lo) < T if lo > 0
    while not (F_ball(arb(hi), roots, c3).lower() > T.upper()):
        hi = hi * 2
    if lo > 0 and not (F_ball(arb(lo), roots, c3).upper() < T.lower()):
        lo = fmpq(0)
    while (hi - lo) > fmpq(1, 10**13) * hi:
        mid = (lo + hi) / 2
        f = F_ball(arb(mid), roots, c3)
        if f.upper() < T.lower():
            lo = mid
        elif f.lower() > T.upper():
            hi = mid
        else:
            break  # undecided (parameter-ball width): stop, keep certified bracket
    return lo, hi
