"""Decode the producer's CNF into a graph and compare with the auditor's edge set; LRAT-check
the LRAT produced by drat-trim -L from the producer's DRUP proof with the auditor's checker."""
import json
import sys

sys.path.insert(0, "/tmp/galeaudit/scripts")
G = json.load(open(sys.argv[1]))
E = sorted(tuple(e) for e in G["E7"])
cnf_path, lrat_path = sys.argv[2], sys.argv[3]
cls = []
for line in open(cnf_path):
    t = line.split()
    if not t or t[0] in ("p", "c"):
        continue
    cls.append([int(x) for x in t[:-1]])
pos = [c for c in cls if all(l > 0 for l in c)]
neg2 = [c for c in cls if len(c) == 2 and all(l < 0 for l in c)]
other = [c for c in cls if c not in pos and not (len(c) == 2 and all(l < 0 for l in c))]
print("clauses", len(cls), "positive", len(pos), "neg-binary", len(neg2), "other", len(other))
# infer mapping from ALO clauses: each positive 4-clause = one vertex
assert all(len(c) == 4 for c in pos if len(c) > 1)
alo = [c for c in pos if len(c) == 4]
vmap = {}
for v, c in enumerate(alo):
    for k, lit in enumerate(sorted(c)):
        vmap[lit] = (v, k)
amo = 0
edges = set()
bad = 0
for a, b in neg2:
    (u, cu), (w, cw) = vmap[-a], vmap[-b]
    if u == w:
        amo += 1
    elif cu == cw:
        edges.add(tuple(sorted((u, w))))
    else:
        bad += 1
# each edge must carry all 4 colour clauses
print("AMO", amo, "edges", len(edges), "bad", bad, "units", [c for c in pos if len(c) == 1])
# vertex numbering: ALO clause order assumed = vertex order
print("producer CNF graph == auditor edge set:", sorted(edges) == E)

from sat_audit_lrat import lrat_check  # noqa: E402
print("auditor LRAT checker on drat-trim LRAT of producer proof:", lrat_check(cls, lrat_path))
