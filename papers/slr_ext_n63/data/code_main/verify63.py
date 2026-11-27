import json
from fractions import Fraction as F

d = json.load(open("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/"
                   "results/proposal6/2026-11-07/SLR-EXT/certificates/cert_n063.json"))
v = [int(x) for x in d["v"]]
a = [int(x) for x in d["a"]]
D = int(d["D"])
n = int(d["n"])
delta = F(int(d["delta_num"]), int(d["delta_den"]))
print("n", n, "len v", len(v), "len a", len(a), "D", D, "delta", delta)
print("distinct velocities:", len(set(v)) == len(v), "all positive ints:", all(x > 0 for x in v))
print("velocity range:", min(v), max(v), "delta == 1/(n+1):", delta == F(1, n + 1))
print("shifts in [0, D):", all(0 <= x < D for x in a))
s = [F(x, D) for x in a]


def dist(x: F) -> F:
    r = x - (x.numerator // x.denominator)
    return min(r, 1 - r)


# endpoints of the open arcs {t : ||s_i + v_i t|| < delta}: v_i t = k - s_i +- delta
pts = set()
for si, vi in zip(s, v):
    for k in range(vi):
        for sign in (1, -1):
            e = (F(k) - si + sign * delta) / vi
            pts.add(e - (e.numerator // e.denominator))
print("distinct arc endpoints:", len(pts))
bad = 0
for e in pts:
    if not any(dist(si + vi * e) < delta for si, vi in zip(s, v)):
        bad += 1
print("endpoints NOT strictly inside any open arc:", bad)
print("RESULT:", "COVERED (counterexample of size %d)" % n if bad == 0 else "NOT COVERED")
# margin: smallest slack among endpoints
slack = min(max(delta - dist(si + vi * e) for si, vi in zip(s, v)) for e in pts)
print("min over endpoints of best (delta - dist):", float(slack))
