import sys
sys.path.insert(0, '/tmp/k2audit')
from model import logs
from encl import dlogs, cell_enc, I
from mpmath import mp, mpf
import mpmath, time
mp.dps = 30
for (T, S) in [(0.3, 30.2), (17.0, 34.0), (29.9, 37.9)]:
    dT, dS = dlogs(I(T), I(S))
    for k in range(5):
        nT = mp.diff(lambda x: logs(x, mpf(S), mp)[k], mpf(T))
        nS = mp.diff(lambda x: logs(mpf(T), x, mp)[k], mpf(S))
        print(k, mpmath.nstr(nT - dT[k].mid, 3), mpmath.nstr(nS - dS[k].mid, 3))
t0 = time.time()
cell = {"T": (0.0, 5.0), "S": (30.0, 34.0), "f": (420.0, 560.0), "TA35": (2200.0, 2300.0)}
print(cell_enc(cell, 0.0), time.time()-t0)
cell = {"T": (0.0, 0.5), "S": (30.0, 30.5), "f": (550.0, 560.0), "TA35": (2200.0, 2210.0)}
print(cell_enc(cell, 0.0), time.time()-t0)
