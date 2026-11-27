import json
from collections import Counter
from bistab import *
from table1 import T1_TEXT

lab, reps = enumerate_all()
print("labelled", len(lab), "orbits", len(reps), sorted(Counter(len(r) for r in reps).items()))
fixed = [s for s in lab if swap_set(s) == s]
print("fixed by exchange:", len(fixed), sorted(Counter(len(s) for s in fixed).items()))
off = {0: 0, 1: 1, 2: 21, 3: 211}
bysize = {m: [t for t in lab if len(t) == m] for m in range(4)}


def nid(s):
    return off[len(s)] + bysize[len(s)].index(s)


out = []
for line in T1_TEXT.splitlines():
    p = line.split()
    disp = tuple(parse_edge(t) for t in p[1:])
    s = tuple(sorted(disp))
    out.append(dict(id=p[0], disp=disp, set=s, lexid="N%04d" % nid(s), match=("N%04d" % nid(s)) == p[0],
                    disp_sorted=(disp == s)))
print("IDs matching my lexicographic index:", sum(o["match"] for o in out), "/27")
print("displayed in sorted edge order:", sum(o["disp_sorted"] for o in out), "/27")
orbs = {min(o["set"], swap_set(o["set"])) for o in out}
print("distinct orbits among Table 1 sets:", len(orbs))
print("mismatches:", [(o["id"], o["lexid"]) for o in out if not o["match"]][:10])
json.dump(dict(labelled=len(lab), orbits=len(reps), by_size=sorted(Counter(len(r) for r in reps).items()),
               fixed=len(fixed), table1=out), open("../data/p1_enum.json", "w"))
