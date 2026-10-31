"""Initial velocity set for the swap search: the n smallest positive integers whose largest
prime factor is <= P, with P the smallest prime for which the n-th such integer is <= cap."""
from __future__ import annotations

import sys


def lpf(x: int) -> int:
    p, best = 2, 1
    while p * p <= x:
        while x % p == 0:
            best, x = p, x // p
        p += 1
    return max(best, x) if x > 1 else best


def smooth_set(n: int, cap: int) -> list[int]:
    for P in range(2, cap + 1):
        out = [x for x in range(1, cap + 1) if lpf(x) <= P][:n]
        if len(out) == n:
            return out
    return list(range(1, n + 1))


if __name__ == "__main__":
    n = int(sys.argv[1])
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else 2 * n + 2
    print(" ".join(map(str, smooth_set(n, cap))))
