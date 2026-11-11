"""Negative control for my exact verifier + reducible count among the 175 minimal."""
import json, sys, os, itertools
from fractions import Fraction as F
sys.argv = [sys.argv[0], sys.argv[1]]
BASE = sys.argv[1]
src = open("/tmp/ge2audit/verify.py").read().split("census = {")[0]
exec(src)
w = json.load(open(os.path.join(BASE, "witnesses", "G01312.json")))
E = [parse_edge(e, 3) for e in w["edges"]]
a = [F(s) for s in w["parameters"]["a"]]; rho = [F(s) for s in w["parameters"]["rho"]]; k = [F(s) for s in w["parameters"]["k"]]
p = [F(s) for s in w["equilibrium_p"]]
print("good f(p)==0:", all(v == 0 for v in rhs(E, a, rho, k, p)))
p2 = list(p); p2[0] += F(1, 1000)
print("perturbed p f==0:", all(v == 0 for v in rhs(E, a, rho, k, p2)))
rho2 = list(rho); rho2[1] *= F(11, 10)
print("rho*1.1 f==0:", all(v == 0 for v in rhs(E, a, rho2, k, p)))
# Hurwitz negative: a known saddle is the 3rd root; check Hurwitz on a non-stable matrix
print("Hurwitz of +I (unstable) accepted:", hurwitz_ok([[F(1), 0, 0], [0, F(1), 0], [0, 0, F(1)]]))
print("Hurwitz of -I accepted:", hurwitz_ok([[F(-1), 0, 0], [0, F(-1), 0], [0, 0, F(-1)]]))
# reducible among the 2+3-edge bucket-C bistables that are minimal (re-derived via subset lookup on labelled sets)
rows = [json.loads(l) for l in open(os.path.join(BASE, "census.jsonl"))]
perms = list(itertools.permutations(range(3)))
def canon(es):
    return min(tuple(sorted(e.translate(str.maketrans("XYZ", "".join("XYZ"[s[i]] for i in range(3)))) for e in es)) for s in perms)
# canonical by string after relabel; complexes like 'Y+X' must be normalised
def norm(e):
    def nc(c):
        parts = sorted(c.split("+"), key=lambda t: t.lstrip("2"))
        if len(parts) == 2 and parts[0] == parts[1]: return "2" + parts[0]
        return "+".join(parts)
    l, r = e.split("->"); return nc(l) + "->" + nc(r)
def canon2(es):
    best = None
    for s in perms:
        m = str.maketrans("XYZ", "".join("XYZ"[s[i]] for i in range(3)))
        t = tuple(sorted(norm(e.translate(m)) for e in es))
        best = t if best is None or t < best else best
    return best
bis = {canon2(r["edges"]): r for r in rows if r["verdict"] == "BISTABLE_CERT"}
cnt = [0, 0]
for c, r in bis.items():
    if r["bucket"] != "C": continue
    if any(canon2(list(s)) in bis for m in range(len(c)) for s in itertools.combinations(c, m)): continue
    E2 = [parse_edge(e, 3) for e in r["edges"]]
    red = any(not any(al[i] for al, be in E2) or all(al[i] == be[i] for al, be in E2) for i in range(3))
    cnt[red] += 1
print("minimal bucket-C bistable: irreducible", cnt[0], "reducible (a species never reactant or never changed)", cnt[1])
