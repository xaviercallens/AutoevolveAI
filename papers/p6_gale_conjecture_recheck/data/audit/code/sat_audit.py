"""Auditor's own SAT route: log (2-bit) encoding, PicoSAT (pycosat), CaDiCaL 3.0.1 LRAT/DRAT,
own Python LRAT checker. Edge list comes from the auditor's own geom.json."""
import json
import random
import subprocess
import sys
from itertools import combinations

import pycosat

G = json.load(open(sys.argv[1]))
WORK = sys.argv[2]
CADICAL = sys.argv[3]
MUS = json.load(open(sys.argv[4]))["mus_edge_list"]
OUT = sys.argv[5]
E = [tuple(e) for e in G["E7"]]
N = 101
res: dict = {}


def log_cnf(edges, n):
    """vertex v has bits b0 = 2v+1, b1 = 2v+2; colour c = (b1 b0). No ALO/AMO needed (4 colours exactly)."""
    cls = []
    for (u, v) in edges:
        for c in range(4):
            cl = []
            for vert in (u, v):
                for bit in range(2):
                    var = 2 * vert + 1 + bit
                    # literal that is FALSE when vert has colour c
                    cl.append(-var if (c >> bit) & 1 else var)
            cls.append(cl)
    return cls


def direct_cnf(edges, n, k):
    var = lambda v, c: v * k + c + 1
    cls = [[var(v, c) for c in range(k)] for v in range(n)]
    for (u, v) in edges:
        for c in range(k):
            cls.append([-var(u, c), -var(v, c)])
    return cls


def decode_log(model, n):
    s = set(l for l in model if l > 0)
    return [((2 * v + 2) in s) * 2 + ((2 * v + 1) in s) for v in range(n)]


def proper(col, edges):
    return all(col[u] != col[v] for u, v in edges)


def write_dimacs(path, cls, nv):
    with open(path, "w") as f:
        f.write(f"p cnf {nv} {len(cls)}\n")
        for c in cls:
            f.write(" ".join(map(str, c)) + " 0\n")


def lrat_check(cnf_cls, lrat_path):
    """Minimal LRAT checker (RUP hints only; RAT steps rejected)."""
    db = {i + 1: list(c) for i, c in enumerate(cnf_cls)}
    steps = 0
    empty = False
    for line in open(lrat_path):
        t = line.split()
        if not t:
            continue
        cid = int(t[0])
        if t[1] == "d":
            for x in t[2:-1]:
                db.pop(int(x), None)
            continue
        k = t.index("0", 1)
        lits = [int(x) for x in t[1:k]]
        hints = [int(x) for x in t[k + 1:-1]]
        if any(h < 0 for h in hints):
            return False, f"RAT hint at {cid}"
        assign = {-l for l in lits}
        ok = False
        for h in hints:
            cl = db[h]
            unassigned = [l for l in cl if -l not in assign]
            if any(l in assign for l in cl):
                return False, f"hint {h} satisfied at step {cid}"
            if len(unassigned) == 0:
                ok = True
                break
            if len(unassigned) == 1:
                assign.add(unassigned[0])
            else:
                return False, f"hint {h} not unit at step {cid}"
        if not ok:
            return False, f"no conflict at step {cid}"
        db[cid] = lits
        steps += 1
        if not lits:
            empty = True
            break
    return empty, f"{steps} lemmas checked"


# controls for the encoder: K4 (4-col), K5 (not), Moser spindle (4-col), random planted
K4 = list(combinations(range(4), 2))
K5 = list(combinations(range(5), 2))
moser = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (0, 4), (0, 5), (4, 5), (4, 6), (5, 6), (3, 6)]
rng = random.Random(7)
cols = [rng.randrange(4) for _ in range(N)]
cand = [(u, v) for u, v in combinations(range(N), 2) if cols[u] != cols[v]]
planted = rng.sample(cand, 2030)
ctl = {}
for name, ed, n, exp in [("K4", K4, 4, True), ("K5", K5, 5, False), ("Moser", moser, 7, True), ("planted101", planted, N, True)]:
    m = pycosat.solve(log_cnf(ed, n))
    sat = m != "UNSAT"
    good = (sat == exp) and (not sat or proper(decode_log(m, n), ed))
    ctl[name] = {"expected_4col": exp, "picosat_4col": sat, "pass": good}
res["controls_log_encoding"] = ctl

# headline: log encoding, PicoSAT
cls = log_cnf(E, N)
m = pycosat.solve(cls)
res["picosat_log_unsat"] = m == "UNSAT"
# also direct encoding w/o AMO, PicoSAT
m2 = pycosat.solve(direct_cnf(E, N, 4))
res["picosat_direct_noAMO_unsat"] = m2 == "UNSAT"
# 5-colourability
m5 = pycosat.solve(direct_cnf(E, N, 5))
col5 = None
if m5 != "UNSAT":
    s = set(l for l in m5 if l > 0)
    col5 = [next(c for c in range(5) if v * 5 + c + 1 in s) for v in range(N)]
res["five_colourable_validated"] = col5 is not None and proper(col5, E)

# CaDiCaL 3.0.1: DRAT and LRAT proofs on the log encoding
cnf = f"{WORK}/aud_log.cnf"
write_dimacs(cnf, cls, 2 * N)
r = subprocess.run([CADICAL, "-q", "--no-binary", cnf, f"{WORK}/aud_log.drat"], capture_output=True, text=True)
res["cadical_drat_status"] = [l for l in r.stdout.splitlines() if l.startswith("s ")]
r = subprocess.run([CADICAL, "-q", "--lrat", "--no-binary", cnf, f"{WORK}/aud_log.lrat"], capture_output=True, text=True)
res["cadical_lrat_status"] = [l for l in r.stdout.splitlines() if l.startswith("s ")]
ok, msg = lrat_check(cls, f"{WORK}/aud_log.lrat")
res["own_lrat_checker"] = {"verified": ok, "msg": msg}
# negative control for own checker: corrupt one hint line
lines = open(f"{WORK}/aud_log.lrat").read().splitlines()
idx = next(i for i, l in enumerate(lines) if " d " not in l and len(l.split()) > 6)
t = lines[idx].split()
k = t.index("0", 1)
lines[idx] = " ".join(t[:k + 1] + t[k + 2:])  # drop first hint
open(f"{WORK}/aud_log_corrupt.lrat", "w").write("\n".join(lines) + "\n")
okc, msgc = lrat_check(cls, f"{WORK}/aud_log_corrupt.lrat")
res["own_lrat_checker_corrupt_control"] = {"verified": okc, "msg": msgc}
# truncated-proof control: remove empty-clause line
lines2 = [l for l in open(f"{WORK}/aud_log.lrat").read().splitlines()]
okt, msgt = lrat_check(cls, f"{WORK}/aud_log.lrat") if False else (None, None)

# MUS (producer's 425-edge core): subset of my E, UNSAT, every single-edge deletion 4-colourable
mus = [tuple(e) for e in MUS]
res["mus_size"] = len(mus)
res["mus_subset_of_E"] = set(mus) <= set(E)
res["mus_vertices"] = len({v for e in mus for v in e})
res["mus_unsat_picosat_log"] = pycosat.solve(log_cnf(mus, N)) == "UNSAT"
alldel = True
for i in range(len(mus)):
    sub = mus[:i] + mus[i + 1:]
    mm = pycosat.solve(log_cnf(sub, N))
    if mm == "UNSAT" or not proper(decode_log(mm, N), sub):
        alldel = False
        break
res["mus_all_425_deletions_4col_validated"] = alldel
# vertex deletion of whole graph
vd = 0
for x in range(N):
    sub = [e for e in E if x not in e]
    mm = pycosat.solve(log_cnf(sub, N))
    vd += mm != "UNSAT" and proper(decode_log(mm, N), sub)
res["vertex_deletions_4col"] = vd
# weakest-edge removal / prefix check
order = [tuple(e) for e in G["order7"]]
res["prefix2029_4col"] = pycosat.solve(log_cnf(order[:2029], N)) != "UNSAT"
res["prefix2030_eq_E"] = sorted(order[:2030]) == sorted(E)
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
