"""High-precision exp(-t) energies (direct sum, mpmath 60 digits) + Poisson cross-check, tri vs square at density rho."""
from __future__ import annotations

import mpmath as mp

mp.mp.dps = 60
N = 40
c = mp.mpf(2) / mp.sqrt(3)


def direct(kind: str, rho: mp.mpf) -> mp.mpf:
    s = mp.mpf(0)
    for j in range(-N, N + 1):
        for k in range(-N, N + 1):
            if j == 0 and k == 0:
                continue
            n2 = c * (j * j + j * k + k * k) if kind == "tri" else mp.mpf(j * j + k * k)
            s += mp.e ** (-n2 / rho)
    return s


def poisson(kind: str, rho: mp.mpf) -> mp.mpf:
    # sum_{x in L} e^{-|x|^2/rho} = pi rho sum_{w in L*} e^{-pi^2 rho |w|^2}; both lattices are self-dual up to rotation
    s = mp.mpf(0)
    for j in range(-12, 13):
        for k in range(-12, 13):
            n2 = c * (j * j + j * k + k * k) if kind == "tri" else mp.mpf(j * j + k * k)
            s += mp.e ** (-mp.pi ** 2 * rho * n2)
    return mp.pi * rho * s - 1  # minus the x = 0 term


for r in ["0.5", "2", "4"]:
    rho = mp.mpf(r)
    t, q = direct("tri", rho), direct("sq", rho)
    print(f"rho={r}: tri={mp.nstr(t, 25)} square={mp.nstr(q, 25)} diff(sq-tri)={mp.nstr(q - t, 6)} tri<square={t < q}"
          f" | poisson diff={mp.nstr(poisson('sq', rho) - poisson('tri', rho), 6)}")
