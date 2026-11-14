"""Describe each graph in a graph6 file: degree sequence, edges, exact N_eff (dbcore), tau_i, bridges/cut vertices, nauty
canonical form, and whether it is isomorphic to Richter's graph. Usage: describe_amplifiers.py <g6 file> <out.json>"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dbcore as d  # noqa: E402

C1DATA = HERE.parents[1] / "C1" / "data"


def canon(g6s: list[str]) -> list[str]:
    p = subprocess.run(["nauty-labelg", "-q"], input="\n".join(g6s) + "\n", capture_output=True, text=True, check=True)
    return p.stdout.split()


def main() -> None:
    g6s = [x.strip() for x in open(sys.argv[1]) if x.strip()]
    r11 = (C1DATA / "richter_n11_amplifier.g6").read_text().strip()
    cs = canon(g6s + [r11])
    rows = []
    for g, c in zip(g6s, cs[:-1]):
        adj = d.parse_graph6(g)
        ne, ti, _ = d.neff_exact(adj)
        G = nx.Graph(d.edges_of(adj))
        nx_iso = nx.is_isomorphic(G, nx.Graph(d.edges_of(d.parse_graph6(r11))))
        rows.append({"graph6": g, "canonical_labelg": c, "isomorphic_to_richter_labelg": c == cs[-1],
                     "isomorphic_to_richter_networkx": nx_iso, "N_eff": str(ne), "N_eff_float": float(ne),
                     "N_eff_minus_N": float(ne - len(adj)), "degrees": [len(a) for a in adj], "edges": d.edges_of(adj),
                     "m": G.number_of_edges(), "bridges": sorted(map(list, nx.bridges(G))),
                     "cut_vertices": sorted(nx.articulation_points(G)), "diameter": nx.diameter(G),
                     "tau_i_float": [float(t) for t in ti]})
    canon_set = sorted({r["canonical_labelg"] for r in rows})
    out = {"graphs": rows, "richter_graph6": r11, "richter_canonical": cs[-1], "distinct_canonical_forms": len(canon_set),
           "pairwise_noniso_networkx": all(not nx.is_isomorphic(nx.Graph(rows[a]["edges"]), nx.Graph(rows[b]["edges"]))
                                           for a in range(len(rows)) for b in range(a + 1, len(rows)))}
    json.dump(out, open(sys.argv[2], "w"), indent=1)
    for r in rows:
        print(r["graph6"], r["N_eff"], round(r["N_eff_float"], 6), "m", r["m"], "deg", sorted(r["degrees"]), "bridges", r["bridges"],
              "cut", r["cut_vertices"], "richter", r["isomorphic_to_richter_labelg"], r["isomorphic_to_richter_networkx"])
    print("distinct canonical", len(canon_set), "pairwise non-iso (networkx)", out["pairwise_noniso_networkx"])


if __name__ == "__main__":
    main()
