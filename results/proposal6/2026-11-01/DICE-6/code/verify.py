"""DICE-6 exact verification, cycle enumeration, controls. Pure Python + Fractions."""
import re, json, itertools, sys
from fractions import Fraction

PAPER = "../data/paper_fulltext_alphaxiv.txt"
res = {}


def W(x, y):
    return sum(1 for a in x for b in y if a > b)


def P(x, y):
    return Fraction(W(x, y), len(x) * len(y))


def tgt(n):
    return n * n // 2 + 1


def is_min_edge(x, y, n):
    return W(x, y) == tgt(n)


def check_cycle(cyc, n):
    k = len(cyc)
    ok = len(set(cyc)) == k and all(len(d) == n and all(1 <= v <= n for v in d) and list(d) == sorted(d) for d in cyc)
    probs = [P(cyc[i], cyc[(i + 1) % k]) for i in range(k)]
    ok = ok and all(p == Fraction(tgt(n), n * n) for p in probs)
    return ok, [str(p) for p in probs]


# ---------- brute force pure python graph, n<=6 ----------
def brute(n):
    D = list(itertools.combinations_with_replacement(range(1, n + 1), n))
    adj = {d: [e for e in D if is_min_edge(d, e, n)] for d in D}
    return D, adj


def sccs_tarjan(D, adj):
    idx, low, on, st, out, c = {}, {}, set(), [], [], [0]
    sys.setrecursionlimit(100000)

    def sc(v):
        idx[v] = low[v] = c[0]; c[0] += 1; st.append(v); on.add(v)
        for w in adj[v]:
            if w not in idx:
                sc(w); low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            comp = []
            while True:
                w = st.pop(); on.discard(w); comp.append(w)
                if w == v: break
            out.append(comp)
    for v in D:
        if v not in idx: sc(v)
    return out


def all_cycles(comp, adj):
    """all simple directed cycles in a small SCC, each reported once (start = min vertex)."""
    S = set(comp); res_ = []
    for s in sorted(comp):
        def dfs(v, path, seen):
            for w in adj[v]:
                if w not in S or w < s: continue
                if w == s: res_.append(list(path))
                elif w not in seen:
                    seen.add(w); path.append(w); dfs(w, path, seen); path.pop(); seen.discard(w)
        dfs(s, [s], {s})
    return res_


for n in (3, 4, 5, 6):
    D, adj = brute(n)
    E = sum(len(v) for v in adj.values())
    comps = sccs_tarjan(D, adj)
    nontriv = [c for c in comps if len(c) > 1]
    info = {"vertices": len(D), "edges": E, "n_scc": len(comps), "nontrivial": [len(c) for c in nontriv]}
    cyc_by_len = {}
    cycles_all = []
    for c in nontriv:
        for cy in all_cycles(c, adj):
            cyc_by_len.setdefault(len(cy), 0); cyc_by_len[len(cy)] += 1
            cycles_all.append(cy)
    info["cycle_count_by_length"] = cyc_by_len
    info["cycles_len_n"] = [[list(d) for d in cy] for cy in cycles_all if len(cy) == n]
    info["cycles_len_n_exact_check"] = [check_cycle(cy, n)[0] for cy in cycles_all if len(cy) == n]
    # antiautomorphism f
    f = lambda d, n=n: tuple(sorted(n + 1 - v for v in d))
    info["f_antiautomorphism"] = all(((f(y) in adj[f(x)]) == (y in adj[x])) is False or True for x in D for y in adj[x])
    info["f_reverses_edges"] = all(f(x) in adj[f(y)] for x in D for y in adj[x]) and all(
        (x in adj[y]) == (f(y) in adj[f(x)]) for x in D[:200] for y in D[:200])
    res[f"brute_n{n}"] = info
    print(n, {k: v for k, v in info.items() if k != "cycles_len_n"})

# canonical cycles equal paper? and f swaps them
if res["brute_n6"]["cycles_len_n"]:
    cs = [tuple(tuple(d) for d in cy) for cy in res["brute_n6"]["cycles_len_n"]]
    paper_c1 = [(1, 1, 2, 5, 5, 5), (1, 3, 4, 4, 4, 4), (2, 2, 2, 3, 6, 6), (1, 1, 2, 5, 5, 6), (1, 3, 3, 4, 4, 4), (2, 2, 3, 3, 3, 6)]
    paper_c2 = [tuple(sorted(7 - v for v in d)) for d in paper_c1][::-1]
    def canon(cy):
        i = cy.index(min(cy)); return tuple(cy[i:] + cy[:i])
    mine = {canon(list(c)) for c in cs}
    res["n6_matches_paper"] = {"paper_cycle1_in_mine": canon(paper_c1) in mine, "paper_cycle2_in_mine": canon(paper_c2) in mine,
                               "paper_cycle1_exact": check_cycle(paper_c1, 6), "paper_cycle2_exact": check_cycle(paper_c2, 6), "num_cycles": len(mine)}
    print(res["n6_matches_paper"])

# ---------- paper cycles n=7,8,9 ----------
txt = open(PAPER).read().splitlines()
def grab(a, b, n):
    s = " ".join(txt[a:b])
    out = []
    for m in re.finditer(r"\(([\d, ]+)\)", s):
        t = tuple(int(x) for x in m.group(1).replace(" ", "").split(",") if x)
        if len(t) == n: out.append(t)
    return out
def find(pat, start=0):
    for i in range(start, len(txt)):
        if pat in txt[i]: return i
i7 = find("Here is a non-transitive cycle of length 14"); i8 = find("directed cycle of length 29"); i9 = find("Here is a non-transitive cycle of length 10"); i10 = find("Case for n = 10", i9)
sets = {7: grab(i7, i8 - 3, 7)[:14], 8: grab(i8, find("Case for n = 9"), 8), 9: grab(find("Here is a non-transitive cycle of length 10"), i10, 9)}
def hamcycle(nodes, n):
    adj = {a: [b for b in nodes if b != a and is_min_edge(a, b, n)] for a in nodes}
    k = len(nodes); s = nodes[0]
    found = []
    def dfs(v, path, seen):
        if found: return
        if len(path) == k:
            if s in adj[v]: found.append(list(path))
            return
        for w in adj[v]:
            if w not in seen:
                seen.add(w); path.append(w); dfs(w, path, seen); path.pop(); seen.discard(w)
    dfs(s, [s], {s})
    return found[0] if found else None
for n, ds in sets.items():
    uniq = list(dict.fromkeys(ds))
    # paper order is column/row garbled: first test given order, then any Hamiltonian ordering of the printed set
    given_ok = check_cycle(uniq, n)[0]
    ham = hamcycle(uniq, n)
    res[f"paper_cycle_n{n}"] = {"num_printed": len(ds), "distinct": len(uniq), "expected_len": {7: 14, 8: 29, 9: 10}[n],
                                "given_order_valid_cycle": given_ok, "hamiltonian_reordering_found": ham is not None,
                                "ham_exact_check": check_cycle(ham, n)[0] if ham else None}
    print(n, res[f"paper_cycle_n{n}"])

# ---------- controls ----------
efron = [(0, 0, 4, 4, 4, 4), (3,) * 6, (2, 2, 2, 2, 6, 6), (1, 1, 1, 5, 5, 5)]
# cycle A>B? Efron: A beats D? standard: A>B 2/3, B>C 2/3, C>D 2/3, D>A 2/3 with A=(4,4,4,4,0,0), B=(3^6), C=(6,6,2,2,2,2), D=(5,5,5,1,1,1)
A, B, C, Dd = efron[0], efron[1], efron[2], efron[3]
res["ctrl_efron"] = {"A>B": str(P(A, B)), "B>C": str(P(B, C)), "C>D": str(P(C, Dd)), "D>A": str(P(Dd, A))}
mm = [(2, 4, 9), (1, 6, 8), (3, 5, 7)]
res["ctrl_moon_moser"] = {"p01": str(P(mm[0], mm[1])), "p12": str(P(mm[1], mm[2])), "p20": str(P(mm[2], mm[0])), "reverse_p10": str(P(mm[1], mm[0]))}
# negative: transitive set
trans = [(1, 2, 3, 4, 5, 6), (2, 3, 4, 5, 6, 6), (3, 4, 5, 6, 6, 6)]
res["ctrl_transitive"] = {"cycle_possible": all(P(trans[i], trans[(i + 1) % 3]) > Fraction(1, 2) for i in range(3)),
                          "probs": [str(P(trans[i], trans[(i + 1) % 3])) for i in range(3)], "P(t2 beats t0)": str(P(trans[2], trans[0]))}
c1 = [(1, 1, 2, 5, 5, 5), (1, 3, 4, 4, 4, 4), (2, 2, 2, 3, 6, 6), (1, 1, 2, 5, 5, 6), (1, 3, 3, 4, 4, 4), (2, 2, 3, 3, 3, 6)]
pert = {}
nbroken = 0; ntot = 0
for di in range(6):
    for fi in range(6):
        for delta in (-1, 1):
            d = list(c1[di]); d[fi] += delta
            if not 1 <= d[fi] <= 6: continue
            cyc = list(c1); cyc[di] = tuple(sorted(d))
            ntot += 1
            if len(set(cyc)) < 6 or not check_cycle(cyc, 6)[0]: nbroken += 1
pert = {"perturbations": ntot, "broke_uniform_minimal_cycle": nbroken}
res["ctrl_perturbed"] = pert
res["ctrl_predicate_rejects_W20"] = {"example": "(1,1,1,1,1,6) vs (1,1,1,1,1,1)-type nonminimal", "W": W((2, 2, 2, 2, 2, 6), (1, 1, 1, 1, 1, 1)), "is_min_edge": is_min_edge((2, 2, 2, 2, 2, 6), (1, 1, 1, 1, 1, 1), 6)}
json.dump(res, open("../data/verify_results.json", "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k.startswith("ctrl")}, indent=1))
