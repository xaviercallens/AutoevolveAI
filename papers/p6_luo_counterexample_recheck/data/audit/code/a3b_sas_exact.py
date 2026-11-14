"""Auditor: exact SAS point + rigorous lower bound on max vol, vs analytic upper bound v3 at non-smooth points.
Also: local maximisation from that point (reproduction of 1.58865) and Luo Thm 4.2(b) consistency."""
import json
from fractions import Fraction as Fr
import mpmath as mp

mp.mp.dps = 30
I = [[1, 0, 0, 1, 0, 0], [0, 2, 0, 1, 0, 2], [1, 0, 2, 0, 2, 0]]
th = [Fr(3, 5), Fr(1, 8), Fr(11, 40), Fr(7, 5), Fr(17, 40), Fr(47, 40)]  # units of pi
res: dict = {'point_units_pi': [str(t) for t in th]}
res['tet_sums'] = [str(sum(th[0:3])), str(sum(th[3:6]))]
res['tet_ok'] = all((s - 1) % 2 == 0 for s in (sum(th[0:3]), sum(th[3:6])))
res['edge_sums'] = [str(sum(r * t for r, t in zip(row, th))) for row in I]
res['edge_ok'] = all(sum(r * t for r, t in zip(row, th)) % 2 == 0 for row in I)
res['smooth'] = all(t % 1 != 0 for t in th)
N = 2000


def lam_partial(t: Fr, n: int):
    x = mp.pi * mp.mpf(t.numerator) / t.denominator
    return sum(mp.sin(2 * k * x) / k ** 2 for k in range(1, n + 1)) / 2


partial = sum(lam_partial(t, N) for t in th)
tail = mp.mpf(6) / (2 * N)  # each |tail| < 1/(2N)
v3 = 3 * mp.clsin(2, 2 * mp.pi / 3) / 2
res['vol_partial_sum_N2000'] = mp.nstr(partial, 15)
res['rigorous_lower_bound'] = mp.nstr(partial - tail, 15)
res['vol_mpmath_clausen'] = mp.nstr(sum(mp.clsin(2, 2 * mp.pi * mp.mpf(t.numerator) / t.denominator) / 2 for t in th), 15)
res['v3'] = mp.nstr(v3, 15)
res['lower_bound_exceeds_v3'] = bool(partial - tail > v3 + mp.mpf('1e-20'))
res['margin'] = mp.nstr(partial - tail - v3, 6)


# 2-parameter family through the point: y1=-x1, x3=1-x1-x2, y2=x2+x1/2+c0, y3=1+x1-y2 (c0 from the point)
c0 = th[4] - th[1] - th[0] / 2
res['family_c0'] = str(c0)


def fam(x1, x2):
    y2 = x2 + x1 / 2 + mp.mpf(c0.numerator) / c0.denominator
    return [x1, x2, 1 - x1 - x2, -x1, y2, 1 + x1 - y2]


def fvol(x1, x2):
    return sum(mp.clsin(2, 2 * mp.pi * t) / 2 for t in fam(x1, x2))


chk = fam(mp.mpf(3) / 5, mp.mpf(1) / 8)
res['family_reproduces_point'] = mp.nstr(max(abs(a - mp.mpf(b.numerator) / b.denominator) for a, b in zip(chk, th)), 5)
# family satisfies constraints identically (symbolic): tet A sum = 1; tet B sum = -x1 + y2 + 1 + x1 - y2 = 1;
# edge a: x1 - x1 = 0; edge b: 2x2 - x1 + 2 + 2x1 - 2y2 = 2 - 2c0 ; edge c: x1 + 2 - 2x1 - 2x2 + 2y2 = 2 + 2c0
res['edge_b_c_const'] = [str(2 - 2 * c0), str(2 + 2 * c0)]
g = lambda a, b: [mp.diff(lambda s: fvol(s, b), a), mp.diff(lambda s: fvol(a, s), b)]
p = mp.findroot(g, (mp.mpf(3) / 5, mp.mpf(1) / 8))
tp = fam(p[0], p[1])
res['local_max_point_units_pi'] = [mp.nstr(t, 12) for t in tp]
res['local_max_vol'] = mp.nstr(fvol(p[0], p[1]), 15)
H = [[mp.diff(lambda a, b: fvol(a, b), (p[0], p[1]), (2, 0)), mp.diff(lambda a, b: fvol(a, b), (p[0], p[1]), (1, 1))],
     [mp.diff(lambda a, b: fvol(a, b), (p[0], p[1]), (1, 1)), mp.diff(lambda a, b: fvol(a, b), (p[0], p[1]), (0, 2))]]
res['hessian_eigs'] = [mp.nstr(e, 6) for e in mp.eig(mp.matrix(H))[0]]
res['min_abs_sin_at_max'] = mp.nstr(min(abs(mp.sin(mp.pi * t)) for t in tp), 6)
# crude global scan over the family (both components c0 and c0+1/2 give k-shift)
best = -10
for i in range(400):
    for j in range(400):
        v = fvol(mp.mpf(2 * i) / 400, mp.mpf(2 * j) / 400) if False else None
mp.mp.dps = 12
import math


def fl_vol(x1, x2, c):
    y2 = x2 + x1 / 2 + c
    s = 0.0
    for t in (x1, x2, 1 - x1 - x2, -x1, y2, 1 + x1 - y2):
        s += float(mp.clsin(2, 2 * math.pi * t)) / 2
    return s


scan = {}
for c in (float(c0), float(c0) + 0.5):
    m = max((fl_vol(2 * i / 200, 2 * j / 200, c), i, j) for i in range(200) for j in range(200))
    scan[str(c)] = m
res['coarse_scan_200x200_max'] = scan
# Luo Thm 4.2(b): z(q) = sin(q')/sin(q'') e^{iq}, with q' -> q -> q''; conv0 cyclic order x1->x2->x3
mp.mp.dps = 30
for conv in (0, 1):
    zs = []
    for t in range(2):
        a = [mp.pi * tp[3 * t + j] for j in range(3)]
        for j in range(3):
            prev, nxt = ((j - 1) % 3, (j + 1) % 3) if conv == 0 else ((j + 1) % 3, (j - 1) % 3)
            zs.append(mp.sin(a[prev]) / mp.sin(a[nxt]) * mp.expj(a[j]))
    res[f'conv{conv}_edge_products'] = [mp.nstr(mp.fprod(zs[q] ** row[q] for q in range(6)), 10) for row in I]
    sr = (lambda u: 1 / (1 - u)) if conv == 0 else (lambda u: (u - 1) / u)
    res[f'conv{conv}_shape_rule_resid'] = mp.nstr(max(abs(zs[3 * t + 1] - sr(zs[3 * t])) for t in range(2)), 5)
json.dump(res, open('/tmp/luoaudit/a3b.json', 'w'), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
