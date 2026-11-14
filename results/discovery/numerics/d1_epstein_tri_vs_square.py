"""Verifier numerics for D1: Riesz energies of triangular vs square lattice at density 1."""
import random
import numpy as np
from mpmath import mp, mpf, sqrt, zeta, dirichlet, pi

mp.dps = 30

# closed form of ||p(j,k)||^2 from upstream's coordinates p = (sqrt b)^{-1} (j + k/2, k b), b = sqrt3/2
b = sqrt(3) / 2
rng = random.Random(0)
maxerr = mpf(0)
for _ in range(1000):
    j, k = rng.randint(-50, 50), rng.randint(-50, 50)
    x = (j + mpf(k) / 2) / sqrt(b)
    y = k * b / sqrt(b)
    maxerr = max(maxerr, abs(x * x + y * y - (2 / sqrt(3)) * (j * j + j * k + k * k)))
print("max |norm^2 - (2/sqrt3)Q| over 1000 random (j,k):", mp.nstr(maxerr, 5))
print("covolume (1/sqrt b)^2 * b =", mp.nstr(b / b, 5))


def tri_closed(s: float) -> mpf:
    sig = mpf(s) / 2
    return (2 / sqrt(3)) ** (-sig) * 6 * zeta(sig) * dirichlet(sig, [0, 1, -1])


def sq_closed(s: float) -> mpf:
    sig = mpf(s) / 2
    return 4 * zeta(sig) * dirichlet(sig, [0, 1, 0, -1])


def direct(s: float, kind: str, N: int = 1200) -> float:
    j = np.arange(-N, N + 1, dtype=np.float64)
    J, K = np.meshgrid(j, j, indexing="ij")
    if kind == "tri":
        r2 = (2 / np.sqrt(3)) * (J * J + J * K + K * K)
    else:
        r2 = J * J + K * K
    R = 0.8 * N if kind == "sq" else 0.8 * N * np.sqrt(np.sqrt(3) / 2) * 1.0
    m = (r2 > 0) & (r2 <= R * R)
    tail = 2 * np.pi * R ** (2 - s) / (s - 2)  # density-1 integral tail
    return float(np.sum(r2[m] ** (-s / 2)) + tail)


for s in (3, 4, 6):
    t, q = tri_closed(s), sq_closed(s)
    print(f"s={s}: tri closed={mp.nstr(t, 12)} direct={direct(s, 'tri'):.9f} | "
          f"sq closed={mp.nstr(q, 12)} direct={direct(s, 'sq'):.9f} | sq-tri={mp.nstr(q - t, 8)}")

# s = 2 divergence: partial sums over |x| <= R grow like 2*pi*log R
for R in (50, 100, 200, 400):
    N = int(R * 1.2) + 2
    jj = np.arange(-N, N + 1, dtype=np.float64)
    J, K = np.meshgrid(jj, jj, indexing="ij")
    r2 = (2 / np.sqrt(3)) * (J * J + J * K + K * K)
    m = (r2 > 0) & (r2 <= R * R)
    S = float(np.sum(1.0 / r2[m]))
    print(f"s=2 partial sum R={R}: {S:.4f}  S - 2*pi*log R = {S - 2*np.pi*np.log(R):.4f}")
