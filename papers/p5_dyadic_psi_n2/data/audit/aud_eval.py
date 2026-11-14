"""Auditor's exact evaluator of Lambda, T, H, R, Psi for step inputs, written from eq. (LI) of
doi:10.5281/zenodo.23232389 (integral definition), NOT from eq. (trace) or producer code.

Inputs: three n x n integer/rational matrices, n = 2^N, F_v constant on cells of side 1/n of [0,1)^2.
Integration is done literally on a refined grid of side 1/(2n) (so Haar functions of every scale down
to 2^-N are constant on refined cells), summing exact Fractions. Scales k >= 1 are summed in closed form
after checking k = 1..3 literally; the scale k = -N is evaluated literally and must vanish.
"""
from __future__ import annotations

import itertools
import random
import sys
from fractions import Fraction
from typing import Callable

Mat = list[list[int]]


def haar(k: int, idx: int, x: Fraction) -> int:
    """h_I(x) for I = [2^k idx, 2^k (idx+1)): +1 on left half, -1 on right half, 0 outside."""
    lo = Fraction(2) ** k * idx
    ln = Fraction(2) ** k
    if x < lo or x >= lo + ln:
        return 0
    return 1 if x < lo + ln / 2 else -1


def L_I(F: list[Mat], k: int, I: tuple[int, int, int], n: int, variant: str = "") -> Fraction:
    """2^-k * int_{I0xI1xI2} F0(x0,x1)F1(x1,x2)F2(x2,x0) h h h, exact, on refined grid of side 1/(2n)."""
    M = 2 * n
    vol = Fraction(1, M**3)
    tot = Fraction(0)
    mids = [Fraction(2 * a + 1, 2 * M) for a in range(M)]
    hv = [[haar(k, I[v], mids[a]) for a in range(M)] for v in range(3)]
    if variant == "coarse_haar_at_level1" and k == -1:
        hv = [[(1 if mids[a] < Fraction(1, 2) else -1) if haar(k, I[v], mids[a]) != 0 else 0 for a in range(M)] for v in range(3)]
    for a0 in range(M):
        if hv[0][a0] == 0:
            continue
        for a1 in range(M):
            if hv[1][a1] == 0:
                continue
            for a2 in range(M):
                if hv[2][a2] == 0:
                    continue
                c0, c1, c2 = a0 // 2, a1 // 2, a2 // 2  # cell of side 1/n
                tot += F[0][c0][c1] * F[1][c1][c2] * F[2][c2][c0] * hv[0][a0] * hv[1][a1] * hv[2][a2]
    pre = Fraction(2) ** (-k)
    if variant == "level1_weight1" and k == -1:
        pre = Fraction(1)
    return pre * tot * vol


def T_of(F: list[Mat], n: int) -> Fraction:
    s = sum(F[0][i][j] * F[1][j][kk] * F[2][kk][i] for i in range(n) for j in range(n) for kk in range(n))
    return Fraction(s, n**3)


def parts(F: list[Mat], N: int, variant: str = "") -> dict[str, Fraction]:
    n = 2**N
    T = T_of(F, n)
    H = Fraction(0)
    zero_check = Fraction(0)
    for k in range(-N, 4):
        ln = Fraction(2) ** k
        nint = max(1, int(Fraction(1) / ln)) if k <= 0 else 1  # intervals of D_k meeting [0,1)
        for I in itertools.product(range(nint), repeat=3):
            xor = I[0] ^ I[1] ^ I[2]
            if variant == "odd_class" and k == -1:
                if xor != 1:
                    continue
            elif xor != 0:
                continue
            v = L_I(F, k, I, n, variant)
            if k == -N:
                zero_check += abs(v)
            elif k <= 0:
                H += abs(v)
            else:
                assert v == T / 2**k, (k, v, T)  # literal check of the k >= 1 scales
    assert zero_check == 0, "scale 2^-N must vanish"
    lam = abs(T) + H  # sum_{k>=1} 2^-k |T| = |T| in closed form
    return {"T": T, "H": H, "R": lam, "Psi": H + 3 * abs(T)}


def S_units(F: list[Mat], N: int, wT: int, haar_free: bool = False, variant: str = "") -> Fraction:
    """64*(wT|T| + H) for N=2 in units of 1/n^3 (returns Fraction; integral expected)."""
    if haar_free:
        raise ValueError("use S_haar_free")
    p = parts(F, N, variant)
    return (wT * abs(p["T"]) + p["H"]) * (2**N) ** 3


def S_haar_free(F: list[Mat], N: int, wT: int) -> Fraction:
    """Haar-free form: every h_I replaced by +1 on I, level weights 2^l unchanged, T weight wT."""
    n = 2**N
    T = T_of(F, n)
    H = Fraction(0)
    for l in range(N):
        m = 2**l
        b = n // m
        for p in range(m):
            for q in range(m):
                r = p ^ q
                s = sum(F[0][i][j] * F[1][j][kk] * F[2][kk][i]
                        for i in range(p * b, (p + 1) * b) for j in range(q * b, (q + 1) * b) for kk in range(r * b, (r + 1) * b))
                H += abs(Fraction(m * s, n**3))
    return (wT * abs(T) + H) * n**3


def rand_sign(n: int, rng: random.Random) -> Mat:
    return [[rng.choice((-1, 1)) for _ in range(n)] for _ in range(n)]


if __name__ == "__main__":
    print("module ok", file=sys.stderr)
