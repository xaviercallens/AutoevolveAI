"""Apply the n=63 template with delta = 1/(N+k) (k=-1,0,1,2) for N = 64..129; report which N are covered at radius 1/(n+1)."""
from fractions import Fraction as F

from slr_exact import covers_open
from template import N63


def run(N: int, k: int):
    d = F(1, N + k)
    vel = {2 * j: F(0) for j in range(1, N + 1)}
    for r in N63["removed"]:
        vel.pop(r, None)
    for v, (c, beta) in {**N63["reph"], **N63["added"]}.items():
        vel[v] = F(c, 4) + beta * d
    vs = sorted(vel)
    D = 32 * (N + k)
    a = [int((vel[x] * D) % D) for x in vs]
    n = len(vs)
    return n, covers_open(vs, a, D, 1, n + 1)[0]


if __name__ == "__main__":
    for k in (-1, 0, 1, 2):
        print("k", k, "covered N:", [N for N in range(64, 130) if run(N, k)[1]])
