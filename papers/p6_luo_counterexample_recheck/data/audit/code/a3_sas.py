"""Auditor: SAS(T) for Guo's triangulation. Rational-multiple-of-pi grid, exact constraint check, mpmath volume.
Analytic bound: a partially flat tetrahedron contributes 0 volume, so vol <= 3*Lambda(pi/3) at every non-smooth point."""
import itertools, json
from fractions import Fraction as Fr
import mpmath as mp

mp.mp.dps = 50
I = [[1, 0, 0, 1, 0, 0], [0, 2, 0, 1, 0, 2], [1, 0, 2, 0, 2, 0]]


def Lam(theta):
    return mp.clsin(2, 2 * theta) / 2


def in_sas(th: list) -> bool:
    """th = angles as Fractions (units of pi). Exact check of Luo's SAS conditions."""
    ok = (th[0] + th[1] + th[2] - 1) % 2 == 0 and (th[3] + th[4] + th[5] - 1) % 2 == 0
    for row in I:
        ok = ok and sum(r * t for r, t in zip(row, th)) % 2 == 0
    return ok


def vol(th: list):
    return sum(Lam(mp.pi * mp.mpf(t.numerator) / t.denominator) for t in th)


N = 72
best = None
count = 0
nonsmooth_max = mp.mpf(-10)
for a, b, c in itertools.product(range(2 * N), repeat=3):
    x1, x2, y2 = Fr(a, N), Fr(b, N), Fr(c, N)
    y1 = (-x1) % 2  # edge a: x1 + y1 = 0 mod 2
    x3 = (1 - x1 - x2) % 2
    y3 = (1 - y1 - y2) % 2
    th = [x1, x2, x3, y1, y2, y3]
    if not in_sas(th):
        continue
    count += 1
    v = sum(float(Lam(float(t) * 3.141592653589793)) for t in th) if False else None
    smooth = all(t % 1 != 0 for t in th)
    import math
    vf = sum(-0.0 for _ in ())
    vf = sum(float(mp.clsin(2, 2 * math.pi * float(t), pi=False)) / 2 for t in th) if False else None
    key = th
    if best is None or True:
        pass
    if smooth:
        if best is None:
            best = [th]
        else:
            best.append(th)
    else:
        nonsmooth_max = max(nonsmooth_max, vol(th))
# evaluate smooth candidates at low precision first to pick the best, then high precision
mp.mp.dps = 15
scored = sorted(best, key=lambda th: -vol(th))[:8]
mp.mp.dps = 50
res = {'grid_N': N, 'n_sas_grid_points': count, 'n_smooth': len(best),
       'best_smooth': [[str(t) for t in th] for th in scored],
       'best_smooth_vol': [mp.nstr(vol(th), 20) for th in scored],
       'max_nonsmooth_grid_vol': mp.nstr(nonsmooth_max, 20),
       'regular_tet_vol_3Lam_pi3': mp.nstr(3 * Lam(mp.pi / 3), 20)}
# continuous refinement of the best point in the 2-parameter family through it (local search on x1, x2 keeping integers)
top = scored[0]
x1, x2, y2 = top[0], top[1], top[4]
# family: y1=-x1, x3=1-x1-x2, y3=1-y1-y2; edge b: 2x2+y1+2y3 = 0 mod 2, edge c: x1+2x3+2y2 = 0 mod 2
# => edge b: 2x2 - x1 + 2 + 2x1 - 2y2 = 2x2 + x1 - 2y2 (mod 2) ; edge c: x1 + 2 - 2x1 - 2x2 + 2y2 = -x1 - 2x2 + 2y2 (mod 2)
# both: x1 + 2x2 - 2y2 = 0 mod 2, so y2 = x2 + x1/2 + k  -> 2-parameter family (x1, x2), k in {0,1}
k = (y2 - x2 - x1 / 2) % 1
res['family_offset_check'] = str((y2 - x2 - x1 / 2))


def fam(p):
    X1, X2 = p
    Y2 = X2 + X1 / 2 + mp.mpf(y2 - x2 - x1 / 2)
    th = [X1, X2, 1 - X1 - X2, -X1, Y2, 1 + X1 - Y2]
    return th


def fvol(p):
    return sum(Lam(mp.pi * t) for t in fam(p))


mp.mp.dps = 30
p = mp.findroot(lambda u, v: [mp.diff(lambda s: fvol([s, v]), u), mp.diff(lambda s: fvol([u, s]), v)],
                (mp.mpf(x1.numerator) / x1.denominator, mp.mpf(x2.numerator) / x2.denominator))
thp = fam(p)
res['refined_point_units_pi'] = [mp.nstr(t, 15) for t in thp]
res['refined_vol'] = mp.nstr(fvol(p), 20)
# exact SAS check of refined point in floating form
res['refined_constraint_residuals'] = [mp.nstr(((thp[0] + thp[1] + thp[2] - 1) / 2) % 1, 5),
                                       mp.nstr(((thp[3] + thp[4] + thp[5] - 1) / 2) % 1, 5)] + \
    [mp.nstr((sum(r * t for r, t in zip(row, thp)) / 2) % 1, 5) for row in I]
# Luo Thm 4.2(b): smooth critical point -> generalized Thurston solution z(q) = sin(q')/sin(q'') e^{i q}, q' -> q -> q''
for conv in (0, 1):
    zs = []
    for t in range(2):
        a = [mp.pi * thp[3 * t + j] for j in range(3)]
        for j in range(3):
            prev, nxt = ((j - 1) % 3, (j + 1) % 3) if conv == 0 else ((j + 1) % 3, (j - 1) % 3)
            zs.append(mp.sin(a[prev]) / mp.sin(a[nxt]) * mp.expj(a[j]))
    prods = [mp.fprod(zs[q] ** row[q] for q in range(6)) for row in I]
    res[f'gen_thurston_edge_products_conv{conv}'] = [mp.nstr(pr, 12) for pr in prods]
    # check shape relation z' = 1/(1-z) in conv0 ordering
    res[f'shape_rel_resid_conv{conv}'] = mp.nstr(max(abs(zs[3 * t + 1] - 1 / (1 - zs[3 * t])) for t in range(2)), 5)
json.dump(res, open('/tmp/luoaudit/a3.json', 'w'), indent=1)
print(json.dumps(res, indent=1))
