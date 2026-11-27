"""Auditor: shape-rule check at the SAS maximum for Luo's z(q) = sin(q')/sin(q'') e^{iq}."""
import cmath, math

for A in [(0.61456669565, 0.128477768117, 0.256955536233), (-0.61456669565, 0.435761115942, 1.17880557971)]:
    a = [math.pi * x for x in A]
    z = [math.sin(a[(j - 1) % 3]) / math.sin(a[(j + 1) % 3]) * cmath.exp(1j * a[j]) for j in range(3)]
    print('next=1/(1-z):', [round(abs(z[(j + 1) % 3] - 1 / (1 - z[j])), 12) for j in range(3)],
          'prev=1/(1-z):', [round(abs(z[(j - 1) % 3] - 1 / (1 - z[j])), 12) for j in range(3)])
