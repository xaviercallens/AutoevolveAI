"""N2 debugging aid: f_enc and fprime_enc on sample balls versus float samples (Tier X)."""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n2_certify as n  # noqa: E402
from flint import arb  # noqa: E402
F1 = n.fprime_sup()
print("F1", F1)
bad = 0
for (m, r) in ((0.5, 0.01), (3.0, 0.1), (1.0, 0.5), (10, 3), (0, 0.03), (6.2, 0.05), (2.0, 0.2), (40, 0.01), (-1.5, 0.3)):
    x = arb(m, r)
    fe, fp = n.f_enc(x), n.fprime_enc(x, F1)
    for i in range(101):
        y = m - r + 2 * r * i / 100
        fy = (1 - math.cos(y)) / y**2 if y != 0 else 0.5
        fpy = (y * math.sin(y) - 2 * (1 - math.cos(y))) / y**3 if abs(y) > 1e-3 else -y / 12
        if not (fe.contains(arb(fy)) or abs(fy - float(fe.mid())) <= float(fe.rad()) + 1e-12):
            bad += 1
        if not (abs(fpy - float(fp.mid())) <= float(fp.rad()) + 1e-12):
            bad += 1
    print(x, fe, fp)
print("sample violations:", bad)
