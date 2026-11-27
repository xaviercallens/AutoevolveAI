"""Inheritance consistency check on census.jsonl (read-only, standard library)."""
import json, sys, itertools, collections
rows = [json.loads(l) for l in open(sys.argv[1])]
perms = list(itertools.permutations("XYZ"))


def ren(e, p):
    m = dict(zip("XYZ", p))
    def cx(c):
        toks = []
        for t in c.split("+"):
            toks.append(t[:-1] + m[t[-1]])
        return "+".join(sorted(toks, key=lambda t: t[-1]))
    a, b = e.split("->")
    return cx(a) + "->" + cx(b)

def ren_old(e, p):
    m = dict(zip("XYZ", p))
    return "".join(m.get(c, c) for c in e)


def canon(edges):
    return min(tuple(sorted(ren(e, p) for e in edges)) for p in perms)


V = {canon(r["edges"]): r for r in rows}
assert len(V) == len(rows) == 10523
bis = {k for k, r in V.items() if r["verdict"] == "BISTABLE_CERT"}
print("bistable", len(bis))
minimal = [k for k in bis if not any(canon(s) in bis for m in range(len(k)) for s in itertools.combinations(k, m))]
cC = [k for k in bis if V[k]["bucket"] == "C"]
print("bistable C", len(cC), "minimal total", len(minimal), "minimal C", sum(1 for k in minimal if V[k]["bucket"] == "C"))
print(collections.Counter((V[k]["m"], V[k]["bucket"]) for k in bis))
c3 = [k for k in cC if len(k) == 3]
withsub = [k for k in c3 if any(canon(s) in bis for s in itertools.combinations(k, 2))]
print("C m=3 bistable", len(c3), "with bistable proper subnetwork", len(withsub), "without", len(c3) - len(withsub))
pred = [k for k, r in V.items() if r["m"] == 3 and any(canon(s) in bis for s in itertools.combinations(k, 2))]
print("m=3 orbits with bistable 2-subnet", len(pred), collections.Counter(V[k]["verdict"] for k in pred))


def reactants(k):
    s = set()
    for e in k:
        s |= set(c for c in e.split("->")[0] if c in "XYZ")
    return s


mc = [k for k in minimal if V[k]["bucket"] == "C"]
nr = [k for k in mc if len(reactants(k)) < 3]
print("minimal C never-reactant", len(nr), "irreducible", len(mc) - len(nr))
print("bistable C never-reactant all", len([k for k in cC if len(reactants(k)) < 3]))
two = sorted(k for k in cC if len(k) == 2)
print(len(two))
for k in two:
    print(k, V[k]["id"])
print("m=2 verdicts C", collections.Counter(V[k]["verdict"] for k in V if len(k) == 2 and V[k]["bucket"] == "C"))
print("stages", collections.Counter(r["stage"] for r in rows))
