"""Independent exact audit of cert_n063 (auditor, not producer)."""
import json, sys
from fractions import Fraction as F
from math import lcm, floor
import numpy as np


def load(p: str):
    d = json.load(open(p))
    return d['v'], d['a'], d['D']


def strict_cover(v, s, r):
    """Exact integer interval union: open arcs {t: ||s_i+v_i t|| < r} cover [0,1] (hence R/Z)?
    Interval for runner i, integer k: t in ((k - s_i - r)/v_i, (k - s_i + r)/v_i)."""
    L = 1
    for q in [x.denominator for x in s] + [r.denominator]:
        L = lcm(L, q)
    L0 = L
    for vi in v:
        L = lcm(L, L0 * vi)
    iv = []
    for vi, si in zip(v, s):
        for k in range(-vi - 2, 2 * vi + 3):
            lo = (k - si - r) / vi * L
            hi = (k - si + r) / vi * L
            assert lo.denominator == 1 and hi.denominator == 1
            lo, hi = lo.numerator, hi.numerator
            if hi > -L and lo < 2 * L:
                iv.append((lo, hi))
    iv.sort()
    reach = None
    for lo, hi in iv:
        if reach is None:
            if lo < 0:
                reach = hi
            continue
        if reach > L:
            return True, None
        if lo >= reach:  # point 'reach' is uncovered (open intervals)
            return False, F(reach, L)
        reach = max(reach, hi)
    return (reach is not None and reach > L), None


def dist(x):
    x = x - floor(x)
    return min(x, 1 - x)


def gamma(v, a, D):
    n = len(v)
    V = np.array(v, dtype=np.float64)
    A = np.array(a, dtype=np.float64) / D
    cands = []
    for i in range(n):
        for j in range(i + 1, n):
            for e in (1, -1):
                w = v[i] - e * v[j]
                if w == 0:
                    continue
                aw = abs(w)
                for k in range(-2 * aw - 2, 2 * aw + 3):
                    num = (e * a[j] - a[i]) + D * k
                    den = D * w
                    t = num / den
                    if 0 <= t < 1:
                        cands.append((t, num, den))
    T = np.array([c[0] for c in cands])
    vals = np.empty(len(T))
    for c0 in range(0, len(T), 20000):
        tt = T[c0:c0 + 20000][:, None]
        x = A[None, :] + V[None, :] * tt
        x = x - np.floor(x)
        vals[c0:c0 + 20000] = np.minimum(x, 1 - x).min(axis=1)
    top = vals.max()
    idx = np.nonzero(vals >= top - 1e-9)[0]
    s = [F(ai, D) for ai in a]
    exact = []
    for q in idx:
        t = F(cands[q][1], cands[q][2])
        exact.append((min(dist(si + vi * t) for si, vi in zip(s, v)), t))
    exact.sort(reverse=True)
    return exact[0], len(T), top, len(idx)


if __name__ == '__main__':
    v, a, D = load(sys.argv[1])
    n = len(v)
    s = [F(ai, D) for ai in a]
    print('n', n, 'distinct', len(set(v)) == n, 'pos', min(v) > 0, 'max v', max(v),
          'shifts in [0,1)', all(0 <= x < 1 for x in s))
    print('cover r=1/(n+1):', strict_cover(v, s, F(1, n + 1)))
    print('cover r=1/(n+2):', strict_cover(v, s, F(1, n + 2)))
    (g, tstar), nc, top, ntop = gamma(v, a, D)
    print('candidates', nc, 'float max', top, 'near-top', ntop)
    print('gamma exact', g, float(g), 't*', tstar, 'gap 1/(n+1)-gamma', F(1, n + 1) - g, float(F(1, n + 1) - g))
    print('cover r=gamma (tangent):', strict_cover(v, s, g))
    print('cover r=gamma+1e-12:', strict_cover(v, s, g + F(1, 10**12)))
    broke = 0
    for i in range(n):
        for sg in (1, -1):
            s2 = list(s)
            s2[i] = (s2[i] + sg * F(1, 2 * D)) % 1
            if not strict_cover(v, s2, F(1, n + 1))[0]:
                broke += 1
    print('perturb +-1/(2D): broke', broke, 'of', 2 * n)
    v2 = list(v)
    v2[-1] = v2[-2]
    print('duplicate velocity distinct?', len(set(v2)) == n)
