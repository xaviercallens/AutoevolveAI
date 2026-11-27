"""Parametrised Poliakova-type move at odd scale b, exact check.  Shifts are alpha + beta*delta (+ gamma/4) with delta = 1/(N+1).
A template = (removed, rephased {v: (num4, beta)}, added {v: (num4, beta)}) with shift = num4/4 + beta*delta/2? kept simple:
shift = num4/4 + beta*delta where beta is a Fraction.  Radius tested: 1/(n+1)."""
from fractions import Fraction as F
from slr_exact import covers_open

POL = dict(removed=[8, 32, 192],
           reph={12: (2, F(1, 2)), 24: (2, F(1, 2)), 48: (2, F(1, 2)), 96: (2, F(1, 2)), 16: (0, F(-1)), 64: (0, F(-1))},
           added={3: (1, F(0)), 9: (1, F(0))})
# the n=63 member, read from certificates/cert_n063.json (N = 64, delta = 1/65): shift num/520, 520 = 8*65
N63 = dict(removed=[4, 8, 32, 72, 96, 108],
           reph={12: (2, F(1, 2)), 24: (2, F(1, 2)), 36: (2, F(1, 2)), 48: (2, F(-1, 2)), 16: (0, F(-1)), 128: (0, F(-1)), 64: (0, F(1))},
           added={1: (3, F(-5, 8)), 3: (3, F(0)), 9: (3, F(-1, 4)), 27: (3, F(1, 8)), 81: (3, F(1, 8))})


def apply(tpl: dict, N: int, b: int = 1, radius_den: int | None = None) -> dict:
    d = F(1, N + 1)
    vel = {2 * j: F(0) for j in range(1, N + 1)}
    for r in tpl["removed"]:
        vel.pop(r * b, None)
    for v, (c, beta) in {**tpl["reph"], **tpl["added"]}.items():
        vel[v * b] = F(c, 4) + beta * d
    vs = sorted(vel)
    n = len(vs)
    D = 8 * (N + 1) * 4
    assert all((vel[x] * D).denominator == 1 for x in vs)
    a = [int((vel[x] * D) % D) for x in vs]
    q = radius_den or n + 1
    return {"n": n, "covered": covers_open(vs, a, D, 1, q)[0]}


if __name__ == "__main__":
    print("N63 template at N=64:", apply(N63, 64))
    for N in (65, 66, 70, 80, 95):
        print("N63 template at N =", N, apply(N63, N))
    for N in (96, 97, 100, 109):
        print("POL at N =", N, apply(POL, N))
