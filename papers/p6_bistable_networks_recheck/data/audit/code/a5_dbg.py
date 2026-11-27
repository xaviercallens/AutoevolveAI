import sys
sys.path.insert(0, "/tmp/bistabaudit/code")
import numpy as np, sympy as sp

from a2_witness import check
from net import field, label

n = sys.argv[1]; sys.argv = sys.argv[:1]
import a5_search as S
S.NS = 300
S.rng = np.random.default_rng(1)
es = S.ids[n]
print(n, label(es))
# reproduce run with captured params

cap = {}
def uni(*args, **kw):
    v = orig(*args, **kw); cap["th"] = 10 ** v; return v

hits, distinct = S.run(n)
idx = np.nonzero(distinct >= 2)[0][:3]
f, g = field(es, "F")
for i in idx:
    th = S.LAST_TH[:, i]
    pars = [sp.Rational(float(t)).limit_denominator(10**8) for t in th]
    r = check(es, [pars[0], pars[1]] + pars[3:], r=pars[2])
    print("sample", i, [float(t) for t in th], "exact:", r["n_pos"], r["sinks"], r["saddles"], r["undecided"], [(round(e["x"], 6), round(e["y"], 6)) for e in r["eqs"]])
