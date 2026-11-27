"""E3link + numeric monotonicity grid. Root form vs transcription of Eq. (13) of arXiv 1802.09806v4."""
import random
import mpmath as mp

mp.mp.dps = 60


def root_form(c, P, z):
    s = mp.sqrt(1 - P)
    K = 2 / (1 - s)
    A = K / c - (1 + z) ** 2 / 4
    B = (1 - z * z) / 2
    C = (1 - z) ** 2 / 4 + K * (1 - c) / c
    w = (B + mp.sqrt(B * B + 4 * A * C)) / (2 * A)
    return (1 - w * w) / c


def eq13(c, P, z, flip=False):
    s = mp.sqrt(1 - P)
    a = 1 + s
    d = (1 + z) ** 2 / 4
    D = a * a + (1 - d * c) * P
    zz = -z if flip else z
    inner = (c / 2) * (d * c - zz) * (1 - s) + 1 - c
    return a * a / D + (1 - z * z) * P * a / D ** 2 * (1 - mp.sqrt(inner) - ((1 + z) / 4) * c * (1 - s))


def eq1(c, P):
    s = mp.sqrt(1 - P)
    return 1 - (1 - c) * P / (2 * (1 + s) - c * P)


random.seed(20261031)
worst = 0
worst_flip = 0
n = 0
viol = 0
for _ in range(3000):
    c = mp.mpf(random.uniform(0.001, 0.999))
    P = mp.mpf(random.uniform(0.001, 1.0))
    z = mp.mpf(random.uniform(-1, 1))
    r = root_form(c, P, z)
    e = eq13(c, P, z)
    f = eq13(c, P, z, True)
    worst = max(worst, abs(r - e))
    worst_flip = max(worst_flip, abs(r - f))
    n += 1
    if r > eq1(c, P) + mp.mpf(10) ** -40:
        viol += 1
print("E3link: points", n, "max |root - Eq13|", mp.nstr(worst, 5), " N4 flipped max diff", mp.nstr(worst_flip, 5), " Eq1 violations", viol)
bad = 0
tot = 0
for ci in range(1, 40):
    c = mp.mpf(ci) / 40
    for pi in range(1, 41):
        P = mp.mpf(pi) / 40
        prev = None
        for zi in range(0, 81):
            z = -1 + mp.mpf(zi) / 40
            u = root_form(c, P, z)
            if prev is not None:
                tot += 1
                if not u > prev:
                    bad += 1
            prev = u
print("grid consecutive-zeta pairs", tot, "non-increasing pairs", bad)
for c in [mp.mpf(1) / 10, mp.mpf(1) / 2, mp.mpf(9) / 10]:
    print("P=1 c=", c, "zeta=-1:", mp.nstr(root_form(c, 1, -1), 20), "zeta=1:", mp.nstr(root_form(c, 1, 1), 20), "1/(2-c)=", mp.nstr(1 / (2 - c), 20))
print("N1 perturbed (zeta->-zeta) c=.5 P=.5 at zeta=-1,0,1:", [mp.nstr(root_form(mp.mpf(1) / 2, mp.mpf(1) / 2, -mp.mpf(z)), 8) for z in (-1, 0, 1)])
