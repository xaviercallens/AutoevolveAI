import json, re, itertools, sys
B = sys.argv[1]
txt = open(B + '/logs/aggregate_out.txt').read()
i = txt.index('"bistable_minimal"'); j = txt.index('"bistable_nonminimal"')
pm = set(re.findall(r'G\d+', txt[i:j])); print("producer minimal", len(pm))
rows = [json.loads(l) for l in open(B + '/census.jsonl')]
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
    m = dict(zip("XYZ", p)); return "".join(m.get(c, c) for c in e)
def canon(ed): return min(tuple(sorted(ren(e, p) for e in ed)) for p in perms)
V = {canon(r['edges']): r for r in rows}
bis = {k for k, r in V.items() if r['verdict'] == 'BISTABLE_CERT'}
byid = {r['id']: r for r in rows}
mine = {g for g, r in byid.items() if r['verdict'] == 'BISTABLE_CERT' and not any(canon(s) in bis for m in range(1, len(r['edges'])) for s in itertools.combinations(r['edges'], m))}
print(len(mine), len(pm & mine), len(pm - mine), len(mine - pm))
for g in sorted(mine - pm)[:4]:
    r = byid[g]; print(g, r['edges'], r['stage'], r['bucket'])
for g in sorted(pm - mine)[:4]:
    r = byid[g]; print("prod-only", g, r['edges'])
