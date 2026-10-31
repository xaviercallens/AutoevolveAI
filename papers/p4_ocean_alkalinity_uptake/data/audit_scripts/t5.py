import sys, time
sys.path.insert(0, '/tmp/k2audit')
import encl9 as E
for n in ("K0", "K1", "K2", "KB", "KW"):
    E.BOX["d"+n] = (-E.SIG[n], E.SIG[n])
base = {"T": (0.0, 5.0), "S": (30.0, 34.0), "f": (420.0, 560.0), "TA35": (2200.0, 2300.0)}
for frac in (1.0, 0.5, 0.1, 0.0):
    cell = dict(base)
    for n in ("K0", "K1", "K2", "KB", "KW"):
        cell["d"+n] = (-frac*E.SIG[n], frac*E.SIG[n]) if frac else (0.0, 0.0)
    t0 = time.time()
    print(frac, E.cell_enc(cell, 1.0), time.time()-t0)
import encl
print("encl ns=0", encl.cell_enc(base, 0.0), "ns=1", encl.cell_enc(base, 1.0))
