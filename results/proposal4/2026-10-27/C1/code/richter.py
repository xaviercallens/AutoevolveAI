"""Reproduce Richter 2020 (arXiv 2008.01446) Table 1 smallest cases with exact rationals:
quartic N=11 (265 graphs) and cubic N=12 (85 graphs): remove each edge at the vertex of largest remeeting time."""

from __future__ import annotations

import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dbcore as d  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "data" / "richter_reproduction.json"


def run(n: int, k: int) -> dict[str, object]:
    res = subprocess.run(["/usr/bin/nauty-geng", "-cq", f"-d{k}", f"-D{k}", str(n)], capture_output=True, text=True, check=True)
    graphs = [x for x in res.stdout.splitlines() if x]
    constructors = []
    for s in graphs:
        g = d.parse_graph6(s)
        ne, ti, _ = d.neff_exact(g)
        assert ne == n
        tmax = max(ti)
        arg = [i for i in range(n) if ti[i] == tmax]
        found = []
        others = []
        for v in arg:
            for u in g[v]:
                h = d.remove_edge(g, v, u)
                if not d.is_connected(h):
                    continue
                he = d.neff_exact(h)[0]
                rec = {"removed": [v, u], "N_eff": str(he), "N_eff_float": float(he), "graph6": d.to_graph6(h)}
                (found if he > n else others).append(rec)
        if found:
            # negative control: removing an edge NOT at an argmax vertex
            nonarg = []
            for (a, b) in d.edges_of(g):
                if a in arg or b in arg:
                    continue
                h = d.remove_edge(g, a, b)
                if d.is_connected(h):
                    nonarg.append(float(d.neff_exact(h)[0]))
            constructors.append({"parent_graph6": s, "tau_max": str(tmax), "tau_max_float": float(tmax), "argmax": arg,
                                 "amplifiers": found, "argmax_nonamplifying": others,
                                 "nonargmax_removals_neff_max": max(nonarg) if nonarg else None,
                                 "nonargmax_removals_count_gt_N": sum(1 for x in nonarg if x > n)})
    return {"N": n, "k": k, "graphs": len(graphs), "constructors": constructors}


if __name__ == "__main__":
    out = {"quartic_11": run(11, 4), "cubic_12": run(12, 3)}
    OUT.write_text(json.dumps(out, indent=1))
    for key, v in out.items():
        print(key, "graphs", v["graphs"], "constructors", len(v["constructors"]))
        for c in v["constructors"]:
            print("  tau_max %.4f" % c["tau_max_float"], "amps", [round(a["N_eff_float"], 4) for a in c["amplifiers"]],
                  "nonargmax max %.4f >N:%d" % (c["nonargmax_removals_neff_max"], c["nonargmax_removals_count_gt_N"]))
