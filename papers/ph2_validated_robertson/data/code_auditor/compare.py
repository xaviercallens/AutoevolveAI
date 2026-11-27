"""Compare auditor's MPFI/Lohner boxes with the producer's enclosures.json (exact rationals)."""
import json, sys
from fractions import Fraction as F

prod = {F(e["t_exact"]): e for e in json.load(open(sys.argv[1]))}
aud = json.load(open(sys.argv[2]))
for row in aud:
    t = F(row["t"])
    # producer output times are the doubles 0.1/0.4 etc.; 1, 10, 40 are exact integers
    e = prod.get(t)
    if e is None:
        print("no producer box at", t); continue
    for i, c in enumerate(e["comps"]):
        pm, pr = F(c["mid"]), F(c["rad"])
        lo, hi = F(row["box"][i][0]), F(row["box"][i][1])
        am, ar = (lo + hi) / 2, (hi - lo) / 2
        overlap = max(lo, pm - pr) <= min(hi, pm + pr)
        print(f"t={float(t):g} {c['name']}: prod mid={float(pm):.16e} rad={float(pr):.2e} | aud mid={float(am):.16e} rad={float(ar):.2e} "
              f"| |dmid|={float(abs(pm-am)):.2e} overlap={overlap} audmid_in_prod={abs(am-pm)<=pr} prodmid_in_aud={abs(am-pm)<=ar} aud_in_prod={pm-pr<=lo and hi<=pm+pr}")
