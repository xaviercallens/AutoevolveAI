import sys
import numpy as np
sys.argv = ["x", "0", "1", "3000", "5"]
src = open("p6_search.py").read().split("results = {}")[0]
exec(src)
r = (0, 15, 19)
m = 3
rng = np.random.default_rng(3)
P = {"a": 10 ** rng.uniform(LO, HI, 3000), "b": 10 ** rng.uniform(LO, HI, 3000), "rho": 10 ** rng.uniform(LO, HI, 3000)}
for i in range(m):
    P[f"k{i}"] = 10 ** rng.uniform(LO, HI, 3000)
nd, h = crossings(r, P)
j = np.where(nd >= 2)[0][0]
print({k: v[j] for k, v in P.items()})
hh = h[j]
idx = np.where(np.diff(np.sign(hh)) != 0)[0]
print(XS[idx], hh[idx], hh[idx + 1])
vals = {k: Fr(float(f"{v[j]:.8g}")) for k, v in P.items()}
res = analyse(r, [vals[f"k{i}"] for i in range(m)], vals["a"], vals["b"], vals["rho"], eps=Fr(1, 10 ** 20))
print({k: v for k, v in res.items() if k != "equilibria"})
print(res.get("equilibria"))
