"""Independent exact lemma checker for Das-Fox (arXiv 2610.39032) Lemmas 1.2, 1.3, 3.1 and
intermediate Lemmas 2.4, 2.5, 2.13, 3.2, plus Theorem 1.1, on diameter-2-critical (D2C) graphs.
All integer arithmetic. D2C membership is RE-VERIFIED here with networkx (independent of the C filter).

usage: python -I lemmas.py n out.json file1.g6 [file2.g6 ...]
"""
import json
import sys
from itertools import combinations
import networkx as nx


def is_d2c(G: nx.Graph) -> bool:
    """diameter exactly 2 and deleting any edge makes diameter > 2 (or disconnects)."""
    if G.number_of_nodes() < 3 or not nx.is_connected(G):
        return False
    if nx.diameter(G) != 2:
        return False
    for u, v in list(G.edges()):
        H = G.copy()
        H.remove_edge(u, v)
        if nx.is_connected(H) and nx.diameter(H) <= 2:
            return False
    return True


def _rec_wrapper(n: int, adj: list[set[int]]):
    """Clean enumerator: decide each vertex in order: matched-to-later-free-neighbour or unmatched."""
    status = [0] * n  # 0 undecided, 1 matched, 2 declared unmatched
    M: list[tuple[int, int]] = []

    def rec(v: int):
        while v < n and status[v] != 0:
            v += 1
        if v == n:
            yield frozenset(M)
            return
        for u in sorted(adj[v]):
            if u > v and status[u] == 0:
                status[v] = status[u] = 1
                M.append((v, u))
                yield from rec(v + 1)
                M.pop()
                status[v] = status[u] = 0
        # declare v unmatched: all its neighbours must end up matched.
        # Neighbours already declared unmatched make it non-maximal.
        if any(status[w] == 2 for w in adj[v]):
            return
        status[v] = 2
        # every undecided neighbour must be matched later: forbid declaring them unmatched
        # (enforced by the check above when they are declared)
        yield from rec(v + 1)
        status[v] = 0

    yield from rec(0)


def critical_structure(n: int, adj: list[set[int]]):
    """Return (E list, F_c dict nonedge->critical path (frozenset of two edges), F_nc count)."""
    E = [(u, v) for u in range(n) for v in adj[u] if u < v]
    Fc = {}
    Fnc = 0
    for u, v in combinations(range(n), 2):
        if v in adj[u]:
            continue
        common = adj[u] & adj[v]
        if len(common) == 1:
            w = next(iter(common))
            Fc[(u, v)] = (tuple(sorted((u, w))), tuple(sorted((v, w))))
        else:
            Fnc += 1
    return E, Fc, Fnc


def components_stats(left: list, right: list, edges: list[tuple]):
    """union-find on bipartite graph; return list of (a,b,nedges) per component."""
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for l in left:
        parent[("L", l)] = ("L", l)
    for r in right:
        parent[("R", r)] = ("R", r)
    for l, r in edges:
        a, b = find(("L", l)), find(("R", r))
        if a != b:
            parent[a] = b
    comp: dict = {}
    for x in parent:
        comp.setdefault(find(x), []).append(x)
    stats = []
    for c in comp.values():
        a = sum(1 for x in c if x[0] == "L")
        b = len(c) - a
        stats.append((a, b))
    return stats


def analyse(G: nx.Graph) -> dict:
    n = G.number_of_nodes()
    G = nx.convert_node_labels_to_integers(G)
    adj = [set(G[v]) for v in range(n)]
    E, Fc, Fnc = critical_structure(n, adj)
    nE = len(E)
    nF = n * (n - 1) // 2 - nE
    assert len(Fc) + Fnc == nF
    tri = sum(1 for u, v in E if adj[u] & adj[v])  # edges lying in a triangle
    triangle_free = tri == 0
    # I edges (e ~ f)
    Iedges = []
    for f, (e1, e2) in Fc.items():
        Iedges.append((e1, f))
        Iedges.append((e2, f))
    res = dict(n=n, edges=nE, nonedges=nF, fc=len(Fc), fnc=Fnc, triangle_free=triangle_free)
    nM = 0
    viol12 = 0
    viol12_strict = 0
    viol12_minus1 = 0
    sizes = set()
    all_equal = True
    viol24 = viol25 = viol213 = viol32 = 0
    # Lemma 2.4 on I (M independent)
    for a, b in components_stats(E, list(Fc), Iedges):
        if a > b + 1:
            viol24 += 1
    maxdiff = None  # max over M of |E\M| - |F|
    comps_I = None
    for M in _rec_wrapper(n, adj):
        nM += 1
        sizes.add(len(M))
        d = nE - len(M) - nF
        maxdiff = d if maxdiff is None else max(maxdiff, d)
        if d > 0:
            viol12 += 1
        if d >= 0:
            viol12_strict += 1  # strict-version failures
        if d > -1:
            viol12_minus1 += 1
        if d != 0:
            all_equal = False
        # I' components
        Ep = [e for e in E if e not in M]
        Ipe = [(e, f) for (e, f) in Iedges if e not in M]
        stats = components_stats(Ep, list(Fc), Ipe)
        cl = 0
        right_lop = 0
        for a, b in stats:
            if a > b + 1:
                viol24 += 1
            if a == b + 1:
                cl += 1
            if a < b:
                right_lop += 1
        if cl > Fnc:
            viol213 += 1
        # Lemma 2.5: |E'|-|F| <= |C_l| - |F_nc| with equality iff no right-lopsided
        lhs = len(Ep) - nF
        rhs = cl - Fnc
        if lhs > rhs or ((lhs == rhs) != (right_lop == 0)):
            viol25 += 1
    res.update(num_maximal_matchings=nM, matching_sizes=sorted(sizes), viol_L12=viol12,
               max_diff=maxdiff, strict_fail_count=viol12_strict, minus1_fail_count=viol12_minus1,
               equality_case=all_equal, viol_L24=viol24, viol_L25=viol25, viol_L213=viol213)
    # Lemma 1.3 / 3.1 on equality cases
    res["viol_L13"] = int(all_equal and not triangle_free)
    is_star = (n >= 3 and nE == n - 1 and max(len(a) for a in adj) == n - 1)
    res["is_star"] = is_star
    res["viol_L31"] = int(all_equal and not (is_star or len(Fc) == 0))
    # Lemma 3.2 for equality cases: every component of I left-lopsided; each matching uses <=1 left vertex of a comp.
    if all_equal:
        for a, b in components_stats(E, list(Fc), Iedges):
            if not (a == b + 1):
                viol32 += 1
    res["viol_L32"] = viol32
    return res


def main() -> None:
    n = int(sys.argv[1])
    out = sys.argv[2]
    graphs = []
    for fn in sys.argv[3:]:
        with open(fn) as f:
            graphs += [ln.strip() for ln in f if ln.strip()]
    summary = dict(n=n, d2c_graphs=len(graphs), not_d2c_by_python=0, max_edges=0, extremal=[],
                   viol={k: 0 for k in ["L12", "L13", "L24", "L25", "L213", "L31", "L32"]},
                   equality_cases=[], strict_fail_graphs=0, minus1_fail_graphs=0,
                   bound_viol=0, min_edges=10**9, edge_hist={}, total_maximal_matchings=0,
                   violating_graph6=[])
    for g6 in graphs:
        G = nx.from_graph6_bytes(g6.encode())
        if not is_d2c(G):
            summary["not_d2c_by_python"] += 1
            continue
        r = analyse(G)
        m = r["edges"]
        summary["edge_hist"][m] = summary["edge_hist"].get(m, 0) + 1
        summary["min_edges"] = min(summary["min_edges"], m)
        summary["total_maximal_matchings"] += r["num_maximal_matchings"]
        if m > n * n // 4:
            summary["bound_viol"] += 1
        if m > summary["max_edges"]:
            summary["max_edges"] = m
            summary["extremal"] = []
        if m == summary["max_edges"]:
            summary["extremal"].append(g6)
        for k in summary["viol"]:
            if r["viol_" + k]:
                summary["viol"][k] += 1
                summary["violating_graph6"].append([k, g6])
        if r["strict_fail_count"]:
            summary["strict_fail_graphs"] += 1
        if r["minus1_fail_count"]:
            summary["minus1_fail_graphs"] += 1
        if r["equality_case"]:
            summary["equality_cases"].append(dict(g6=g6, edges=m, triangle_free=r["triangle_free"], star=r["is_star"]))
    # extremal graphs must be exactly K_{ceil,floor}
    ext_ok = 0
    a, b = n - n // 2, n // 2
    for g6 in summary["extremal"]:
        G = nx.from_graph6_bytes(g6.encode())
        if nx.is_isomorphic(G, nx.complete_bipartite_graph(a, b)):
            ext_ok += 1
    summary["extremal_count"] = len(summary["extremal"])
    summary["extremal_are_Kab"] = ext_ok
    summary["floor_n2_over_4"] = n * n // 4
    with open(out, "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("extremal", "equality_cases", "edge_hist", "violating_graph6")}))


if __name__ == "__main__":
    main()
