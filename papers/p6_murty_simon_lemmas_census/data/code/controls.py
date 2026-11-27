"""Controls for MS-CENSUS. usage: python -I controls.py MS-CENSUS_dir out.json"""
import glob
import json
import os
import random
import subprocess
import sys
from itertools import combinations

import networkx as nx
from networkx.generators.atlas import graph_atlas_g

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lemmas import _rec_wrapper, analyse, is_d2c  # noqa: E402

root = sys.argv[1]
out = {}
ok = True


def check(name: str, cond: bool) -> None:
    global ok
    out[name] = bool(cond)
    ok = ok and bool(cond)


# --- D2C predicate positive controls
pos = {"C5": nx.cycle_graph(5), "Petersen": nx.petersen_graph(), "K23": nx.complete_bipartite_graph(2, 3),
       "K33": nx.complete_bipartite_graph(3, 3), "K45": nx.complete_bipartite_graph(4, 5),
       "K1_5_star": nx.star_graph(5), "C4": nx.cycle_graph(4)}
# Figure 1 of the paper, RECONSTRUCTED from the text (edge list is not in the extracted text):
# triangle v1v3v5; v2~v1,v7 ; v4~v3,v7 ; v6~v5,v7  (consistent with the three quoted critical 2-paths)
fig1 = nx.Graph([(1, 3), (3, 5), (5, 1), (2, 1), (2, 7), (4, 3), (4, 7), (6, 5), (6, 7)])
pos["Fig1_reconstructed"] = fig1
for k, g in pos.items():
    check("pos_d2c_" + k, is_d2c(g))
# paper's statement on Fig 1: every non-edge critical, triangle edges on a critical path
r = analyse(fig1)
check("fig1_all_nonedges_critical", r["fc"] == r["nonedges"])
check("fig1_has_triangle", not r["triangle_free"])
# --- negative controls
neg = {"K3": nx.complete_graph(3), "K4": nx.complete_graph(4), "K5": nx.complete_graph(5), "C6": nx.cycle_graph(6),
       "C7": nx.cycle_graph(7), "P4": nx.path_graph(4), "K4-e": nx.complete_graph(4)}
neg["K4-e"].remove_edge(0, 1)
for k, g in neg.items():
    check("neg_notd2c_" + k, not is_d2c(g))
# --- matching enumerator vs brute force
random.seed(12345)
for t in range(40):
    n = random.randint(4, 7)
    G = nx.gnp_random_graph(n, random.choice([0.3, 0.5, 0.7]), seed=random.randint(0, 10**6))
    E = list(G.edges())
    adj = [set(G[v]) for v in range(n)]
    mine = set(_rec_wrapper(n, adj))
    brute = set()
    for mask in range(1 << len(E)):
        M = [E[i] for i in range(len(E)) if mask >> i & 1]
        vs = [x for e in M for x in e]
        if len(vs) != len(set(vs)):
            continue
        cov = set(vs)
        if all(u in cov or v in cov for u, v in E):
            brute.add(frozenset(tuple(sorted(e)) for e in M))
    if mine != brute:
        check("matching_enumerator_matches_bruteforce", False)
        break
else:
    check("matching_enumerator_matches_bruteforce", True)
# --- sanity of analyse on K33: 6 maximal matchings, equality case, strict version fails, empty-matching version fails
r = analyse(nx.complete_bipartite_graph(3, 3))
check("K33_6_maximal_matchings", r["num_maximal_matchings"] == 6)
check("K33_equality_case_triangle_free", r["equality_case"] and r["triangle_free"])
check("perturbed_strict_lt_fails_on_K33", r["strict_fail_count"] > 0)
check("perturbed_minus1_fails_on_K33", r["minus1_fail_count"] > 0)
check("perturbed_empty_matching_fails_on_K33", r["edges"] - 0 > r["nonedges"])
r = analyse(nx.petersen_graph())
check("petersen_L12_holds_not_equality", r["viol_L12"] == 0 and not r["equality_case"])
# a deliberately false variant of Theorem 1.1 must fail: bound floor(n^2/4)-1 is violated by K_{a,b}
rk = analyse(nx.complete_bipartite_graph(4, 5))
check("perturbed_bound_minus1_fails_on_K45", rk["edges"] > 81 // 4 - 1 and rk["edges"] == 81 // 4)
# --- A001349 vs geng, and D2C counts vs independent atlas / python for n<=8
A001349 = {3: 2, 4: 6, 5: 21, 6: 112, 7: 853, 8: 11117, 9: 261080, 10: 11716571, 11: 1006700565}
counts = {}
for n in range(3, 12):
    fs = sorted(glob.glob(f"{root}/logs/census_n{n}_p*.log"))
    if len(fs) != 4:
        continue
    seen = d2c = 0
    done = True
    for f in fs:
        t = open(f).read().split()
        if len(t) < 4:
            done = False
            break
        seen += int(t[1])
        d2c += int(t[3])
    if done:
        counts[n] = (seen, d2c)
out["geng_connected_and_d2c_counts"] = {str(k): v for k, v in counts.items()}
for n, (seen, d2c) in counts.items():
    check(f"A001349_matches_n{n}", seen == A001349[n])
# atlas (independent of geng): connected graphs n<=7
atlas = {}
for G in graph_atlas_g():
    n = G.number_of_nodes()
    if 3 <= n <= 7 and nx.is_connected(G):
        atlas.setdefault(n, [0, 0])
        atlas[n][0] += 1
        atlas[n][1] += int(is_d2c(G))
out["atlas_counts"] = {str(k): v for k, v in atlas.items()}
for n in atlas:
    check(f"atlas_matches_geng_C_n{n}", n in counts and tuple(atlas[n]) == counts[n])
# n=8: geng + python predicate
p = subprocess.run(["nauty-geng", "-c", "8", "-q"], capture_output=True, text=True)
cnt8 = [0, 0]
for ln in p.stdout.split():
    cnt8[0] += 1
    cnt8[1] += int(is_d2c(nx.from_graph6_bytes(ln.encode())))
out["n8_python_counts"] = cnt8
check("n8_python_matches_C", 8 in counts and tuple(cnt8) == counts[8])
out["all_controls_pass"] = ok
json.dump(out, open(sys.argv[2], "w"), indent=1, sort_keys=True)
print(json.dumps(out, indent=1, sort_keys=True))
