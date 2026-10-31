import sys
sys.path.insert(0, '/tmp/k2audit')
from model import *
a = logs(mpf(25), mpf(35), mp)
print("checkvals", [mpmath.nstr(x, 8) for x in a], "expect -3.5617 -5.8472 -8.9660 -19.7964 -30.434")
for pt in [(0, 30, 560, 2200), (30, 38, 280, 2400), (15, 35, 420, 2300)]:
    e, h, c = eta_point(*pt)
    T, S, f, TA35 = pt
    f = mpf(f)
    TA = mpf(S)/35*TA35*mpf('1e-6')
    d = mp.diff(lambda x: DIC_of_h(solve_h(c, f, x), c, f), TA)
    print(pt, mpmath.nstr(e, 15), mpmath.nstr(d, 15), 'pH', mpmath.nstr(-mp.log10(h), 6))
