import json
from fractions import Fraction as Fr
from bistab import *
from table1 import T1_TEXT
from exact import analyse

TOK = {"N0514": [17, 100, 9, 2600, 2809], "N0524": [17, 100, 9, 650, 729],
       "N0548": [17, 100, 159, 2600, 2809], "N0554": [17, 100, 159, 2600, 2809]}
AB = {"N0514": ("3/100", "3/100"), "N0524": ("1/25", "3/100"), "N0548": ("1/50", "1/25"), "N0554": ("3/100", "3/100")}
net = {l.split()[0]: tuple(parse_edge(t) for t in l.split()[1:]) for l in T1_TEXT.splitlines()}
out = {}
for nid, t in TOK.items():
    for sizes in [(2, 2, 1), (2, 1, 2), (1, 2, 2)]:
        i, ks = 0, []
        for s in sizes:
            ks.append(Fr(t[i], t[i + 1]) if s == 2 else Fr(t[i]))
            i += s
        r = analyse(net[nid], ks, Fr(AB[nid][0]), Fr(AB[nid][1]))
        key = f"{nid}:{sizes}"
        out[key] = dict(ks=[str(k) for k in ks], sinks=r.get("n_sinks"), pos_eq=r.get("n_positive_equilibria"), undecided=r.get("undecided"))
        print(key, out[key], flush=True)
json.dump(out, open("../data/p2b_alt_parse.json", "w"), indent=1)
