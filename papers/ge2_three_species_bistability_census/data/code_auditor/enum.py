"""Independent enumeration, Burnside, buckets, minimality, Peng control, reduction screen."""
import json, sys, os, itertools, collections
from math import comb
BASE = sys.argv[1]; PENGF = sys.argv[2]

def cplxs(n):
    out = []
    for v in itertools.product(range(3), repeat=n):
        if 1 <= sum(v) <= 2: out.append(v)
    return out

def name(v):
    sp = "XYZ"; parts = []
    for i, c in enumerate(v):
        if c == 1: parts.append(sp[i])
        elif c == 2: parts.append("2" + sp[i])
    return "+".join(parts)

def parse(s, n):
    v = [0] * n
    for t in s.split("+"):
        c = 1
        if t[0].isdigit(): c = int(t[0]); t = t[1:]
        v["XYZ".index(t)] += c
    return tuple(v)

def run(n):
    C = cplxs(n); E = [(a, b) for a in C for b in C if a != b]
    perms = list(itertools.permutations(range(n)))
    def pe(e, s): return tuple(tuple(c[s[i]] for i in range(n)) for c in e)
    eidx = {e: i for i, e in enumerate(E)}
    nets = [frozenset(c) for m in range(4) for c in itertools.combinations(range(len(E)), m)]
    def canon(S):
        return min(tuple(sorted(eidx[pe(E[i], s)] for i in S)) for s in perms)
    orbits = collections.Counter(canon(S) for S in nets)
    # Burnside
    fix = 0
    for s in perms:
        fix += sum(1 for S in nets if frozenset(eidx[pe(E[i], s)] for i in S) == S)
    return C, E, eidx, canon, len(nets), orbits, fix / len(perms)

def bucket(edges, n):
    sup = set(); adj = collections.defaultdict(set)
    for a, b in edges:
        s = {i for i in range(n) if a[i] or b[i]}
        sup |= s
        for i in s: adj[i] |= s
    if len(sup) <= 2: return "A"
    seen = {0}; st = [0]
    while st:
        u = st.pop()
        for v in adj[u]:
            if v not in seen: seen.add(v); st.append(v)
    return "C" if len(seen) == 3 else "B"

for n in (2, 3):
    C, E, eidx, canon, nl, orb, burn = run(n)
    print(f"n={n}: complexes={len(C)} edges={len(E)} labelled={nl} (formula {sum(comb(len(E),m) for m in range(4))}) orbits={len(orb)} burnside={burn}")
    if n == 3:
        rows = [json.loads(l) for l in open(os.path.join(BASE, "census.jsonl"))]
        mine = {}
        bmis = 0; osz = 0
        for r in rows:
            ed = [tuple(parse(x, n) for x in e.split("->")) for e in r["edges"]]
            c = canon([eidx[e] for e in ed])
            mine[c] = r
            if bucket(ed, n) != r["bucket"]: bmis += 1
            if orb[c] != r["orbit_size"]: osz += 1
        print("census rows", len(rows), "distinct canon", len(mine), "covers all orbits", set(mine) == set(orb), "bucket mismatches", bmis, "orbit size mismatches", osz)
        bc = collections.Counter((r["bucket"], r["verdict"]) for r in rows)
        print(sorted(bc.items()))
        # minimality among bistable bucket C
        bis = {c for c, r in mine.items() if r["verdict"] == "BISTABLE_CERT"}
        minimal = []
        for c in bis:
            if mine[c]["bucket"] != "C": continue
            subs = [canon(list(s)) for m in range(len(c)) for s in itertools.combinations(c, m)]
            if not any(s in bis for s in subs): minimal.append(c)
        print("bucket C bistable", sum(1 for c in bis if mine[c]["bucket"] == "C"), "minimal", len(minimal),
              "2-edge", sum(1 for c in bis if mine[c]["bucket"] == "C" and len(c) == 2))
        # reduction screen on bucket-C bistables
        red = collections.Counter(); ex = []
        for c in bis:
            if mine[c]["bucket"] != "C": continue
            ed = [E[i] for i in c]
            flags = []
            for i in range(3):
                reactant = any(a[i] for a, b in ed)
                changed = any(a[i] != b[i] for a, b in ed)
                if not reactant: flags.append(f"{'XYZ'[i]}:never-reactant")
                if not changed: flags.append(f"{'XYZ'[i]}:never-changed")
            key = "reducible" if flags else "irreducible"
            red[(key, len(c))] += 1
            if len(c) == 2 or (flags and len(ex) < 6): ex.append(([name(a)+"->"+name(b) for a, b in ed], flags))
        print("reduction screen", sorted(red.items()))
        for e in ex: print(e)
    if n == 2:
        rows = [json.loads(l) for l in open(os.path.join(BASE, "logs", "census_n2_s0.jsonl"))]
        allr = []
        for s in range(6):
            allr += [json.loads(l) for l in open(os.path.join(BASE, "logs", f"census_n2_s{s}.jsonl"))]
        best = {}
        for r in allr:
            if r["id"] not in best or r.get("stage", 0) >= best[r["id"]].get("stage", 0): best[r["id"]] = r
        bis2 = {canon([eidx[tuple(parse(x, 2) for x in e.split("->"))] for e in r["edges"]]) for r in best.values() if r["verdict"] == "BISTABLE_CERT"}
        txt = open(PENGF).read().split('T1_TEXT = """')[1].split('"""')[0]
        peng = {canon([eidx[tuple(parse(x, 2) for x in e.split("->"))] for e in l.split()[1:]]) for l in txt.splitlines()}
        wP = set()
        for fn in os.listdir(os.path.join(BASE, "witnesses")):
            if fn.startswith("P"):
                w = json.load(open(os.path.join(BASE, "witnesses", fn)))
                wP.add(canon([eidx[tuple(parse(x, 2) for x in e.split("->"))] for e in w["edges"]]))
        print("n2 rows", len(best), "bistable", len(bis2), "peng", len(peng), "same", bis2 == peng, "P-witness set == peng", wP == peng)
