"""Poliakova (arXiv 2609.23952) 9->8 rule instantiated at scale b on base 2,4,..,2N; test with exact checker."""
from fractions import Fraction as F
from slr_exact import covers_open


def build(N, variant, b=1):
    D = 4 * (N + 1)
    d = F(1, N + 1)
    vel = {2 * j: F(0) for j in range(1, N + 1)}
    half = (1 + d) / 2
    reph = {12: half, 24: half,
            48: half if variant == 0 else (1 - d) / 2,
            96: half if variant == 0 else (1 - d) / 2,
            16: -d, 64: -d if variant == 0 else d}
    add = {3: F(1, 4), 9: F(1, 4)}
    for r in (8, 32, 192):
        vel.pop(r * b, None)
    for k, s in reph.items():
        if k * b <= 2 * N:
            vel[k * b] = s
    for k, s in add.items():
        vel[k * b] = s
    return vel, D


def test(N, variant, b=1):
    vel, D = build(N, variant, b)
    v = sorted(vel)
    n = len(v)
    assert all((vel[x] * D).denominator == 1 for x in v)
    a = [int((vel[x] * D) % D) for x in v]
    return {"n": n, "N": N, "cov_1/(N+1)": covers_open(v, a, D, 1, N + 1)[0],
            "cov_1/(n+1)": covers_open(v, a, D, 1, n + 1)[0]}


if __name__ == "__main__":
    for N in [96, 97, 100, 110]:
        for var in (0, 1):
            print(N, var, test(N, var))
