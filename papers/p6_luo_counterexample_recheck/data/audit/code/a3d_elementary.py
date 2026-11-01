"""Auditor: elementary bound |Lambda| <= Lambda(pi/6) (Lambda' = -log|2 sin|, so max at pi/6), tail-bounded;
and a non-smooth SAS point attaining v3."""
from fractions import Fraction as Fr
import mpmath as mp

mp.mp.dps = 30
N = 2000
x = mp.pi / 6
lam_pi6_partial = sum(mp.sin(2 * k * x) / k ** 2 for k in range(1, N + 1)) / 2
upper_lam_pi6 = lam_pi6_partial + mp.mpf(1) / (2 * N)
print('Lambda(pi/6) partial', mp.nstr(lam_pi6_partial, 12), 'upper', mp.nstr(upper_lam_pi6, 12),
      'clausen', mp.nstr(mp.clsin(2, mp.pi / 3) / 2, 12))
print('nonsmooth upper bound 3*Lambda(pi/6) <=', mp.nstr(3 * upper_lam_pi6, 12))
lower_smooth = mp.mpf('1.5852855299645')  # from a3b.json rigorous_lower_bound
print('smooth certified lower bound', lower_smooth, 'margin', mp.nstr(lower_smooth - 3 * upper_lam_pi6, 6))
I = [[1, 0, 0, 1, 0, 0], [0, 2, 0, 1, 0, 2], [1, 0, 2, 0, 2, 0]]
th = [Fr(2, 3), Fr(0), Fr(1, 3), Fr(-2, 3), Fr(1, 3), Fr(4, 3)]
print('tet sums', sum(th[:3]), sum(th[3:]), 'edge sums', [sum(r * t for r, t in zip(row, th)) for row in I])
ok = all((s - 1) % 2 == 0 for s in (sum(th[:3]), sum(th[3:]))) and all(sum(r * t for r, t in zip(row, th)) % 2 == 0 for row in I)
print('in SAS', ok, 'nonsmooth', any(t % 1 == 0 for t in th))
v = sum(mp.clsin(2, 2 * mp.pi * mp.mpf(t.numerator) / t.denominator) / 2 for t in th)
print('vol', mp.nstr(v, 15), 'v3', mp.nstr(3 * mp.clsin(2, 2 * mp.pi / 3) / 2, 15))
