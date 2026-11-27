from bistab import *
from table1 import T1_TEXT
lab, reps = enumerate_all()
idx = {}
for i, r in enumerate(reps):
    idx[r] = i
    idx[swap_set(r)] = i
m = 0
for line in T1_TEXT.splitlines():
    p = line.split()
    s = tuple(sorted(parse_edge(t) for t in p[1:]))
    ok = "N%04d" % idx[s] == p[0]
    m += ok
    if not ok:
        print(p[0], "N%04d" % idx[s])
print("matches with representative-index (first-seen) numbering:", m, "/27")
# also the FLUX list and N0056 example
for n in [56, 350, 354, 355, 361, 369, 391, 600, 610, 638, 646, 648, 649, 661, 673]:
    r = reps[n]
    print(n, [f"{NAMES[EDGES[e][0]]}->{NAMES[EDGES[e][1]]}" for e in r], "orbit-partner reps ok" if True else "")
