import json, time
from fractions import Fraction as Fr
from bistab import *
from table1 import T1_TEXT, T2
from exact import analyse

res = {}
for line in T1_TEXT.splitlines():
    p = line.split()
    nid = p[0]
    es = tuple(parse_edge(t) for t in p[1:])
    v = [Fr(s) for s in T2[nid]]
    t0 = time.time()
    r = analyse(es, v[2:], v[0], v[1])
    r["secs"] = round(time.time() - t0, 2)
    res[nid] = dict(params=T2[nid], **r)
    print(nid, r.get("status"), "pos_eq", r.get("n_positive_equilibria"), "sinks", r.get("n_sinks"), "saddles", r.get("n_saddles"),
          "undecided", r.get("undecided"), "degP", r.get("degP"), r["secs"], flush=True)
json.dump(res, open("../data/p2_witnesses.json", "w"), indent=1, default=str)
ok = [k for k, v in res.items() if v.get("n_sinks", 0) == 2 and v["undecided"] == 0]
print("27 witnesses with exactly 2 certified sinks:", len(ok))
print("failing:", [k for k in res if k not in ok])
