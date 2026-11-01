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
