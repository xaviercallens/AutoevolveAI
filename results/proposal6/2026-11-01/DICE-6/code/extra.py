"""Extra: (1) own search for n-cycle and (n+1)+-cycle for n=7 (X-tier search); (2) maximin 3-cycle context control for m-sided dice in [m], m=4..7."""
import itertools, json, random, time, math
import numpy as np
from fractions import Fraction

out = {}
def dice(n): return list(itertools.combinations_with_replacement(range(1, n + 1), n))
def Wmat(D, n):
    c = np.zeros((len(D), n), dtype=np.int64)
    for k, d in enumerate(D):
        for v in d: c[k, v - 1] += 1
    cum = np.cumsum(c, axis=1)
    g = n - cum
    return g @ c.T

# (2) maximin for 3-cycles, brute force over triples via threshold boolean matrices
for m in (4, 5, 6, 7):
    D = dice(m); W = Wmat(D, m); best = 0
    for t in range(m * m // 2 + 1, m * m + 1):
        B = (W >= t).astype(np.float32)
        tri = ((B @ B) * B.T).sum()
        if tri > 0: best = t
        else: break
    out[f"maximin3_m{m}"] = {"best_W": best, "prob": str(Fraction(best, m * m)), "float": best / (m * m), "golden_bound": (math.sqrt(5) - 1) / 2}
    print(m, out[f"maximin3_m{m}"])

# (1) cycles in G_7
n = 7; D = dice(n); W = Wmat(D, n); tg = n * n // 2 + 1
E = (W == tg)
adj = [np.nonzero(E[i])[0].tolist() for i in range(len(D))]
random.seed(1); t0 = time.time()
found = {}
def search(L, limit=60):
    # randomized DFS for a simple cycle of length exactly L
    for start in random.sample(range(len(D)), len(D)):
        if time.time() - t0 > limit: return None
        path = [start]; seen = {start}
        stack = [iter(random.sample(adj[start], len(adj[start])))]
        nodes = 0
        while stack and nodes < 200000:
            nodes += 1
            try: w = next(stack[-1])
            except StopIteration:
                seen.discard(path.pop()); stack.pop(); continue
            if len(path) == L:
                if w == start: return list(path)
                continue
            if w in seen or w < start and False: continue
            path.append(w); seen.add(w); stack.append(iter(random.sample(adj[w], len(adj[w]))))
    return None
for L in (7, 8, 14):
    t0 = time.time(); c = search(L)
    if c:
        cyc = [D[i] for i in c]
        ok = all(sum(1 for a in cyc[i] for b in cyc[(i + 1) % L] if a > b) == tg for i in range(L)) and len(set(cyc)) == L
        found[L] = {"cycle": [list(d) for d in cyc], "exact_check": ok}
    else: found[L] = None
    print(L, "found" if found[L] else "not found in time box", found[L] and found[L]["exact_check"])
out["n7_cycles"] = found
json.dump(out, open("../data/extra_results.json", "w"), indent=1)
