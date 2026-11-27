"""GE-2 controls: negative networks, corrupted witness, positive-control comparison with Peng Table 1 (2-species)."""
from __future__ import annotations
import glob
import json
import os
import sys
from collections import Counter
from fractions import Fraction as Fr
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import ge2lib as G

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
PENG = "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal6/2026-11-02/BIO-BISTAB/code"


def parse(n: int, s: str) -> G.Edge:
    names = {G.cname(c): c for c in G.complexes(n)}
    a, b = s.replace(" ", "").split("->")
    return names[a], names[b]


def main() -> None:
    out: dict = {}
    # negative controls (n, edges)
    negs = {
        "empty_n3": (3, []),
        "X->Y_n3": (3, ["X->Y"]),
        "cycle_X<->Y<->Z_n3 (deficiency-zero weakly reversible)": (3, ["X->Y", "Y->X", "Y->Z", "Z->Y"]),
    }
    # cycle has 4 edges (> class bound 3) and is allowed here only as an external negative control
    for name, (n, es) in negs.items():
        edges = [parse(n, e) for e in es]
        jac = G.jac_rule(edges, n) if edges else True
        sgn = G.sign_rule(edges, n)
        verdict = "none"
        if edges:
            rng = np.random.default_rng([7, n, len(es)])
            res = G.search(edges, n, rng, 200000)
            w = G.find_witness(edges, n, res["stable"], "stable") if res["stable"] else None
            verdict = "BISTABLE_CERT" if w else ("multi_candidates=%d" % len(res["multi"]))
        out[name] = dict(jac=jac, sign=sgn, verdict=verdict, passed=(verdict != "BISTABLE_CERT"))
    # corrupted witness
    ws = sorted(glob.glob(f"{OUT}/witnesses/P*.json"))
    corr = {}
    if ws:
        w = json.load(open(ws[0]))
        n = w["species"]
        edges = [parse(n, e) for e in w["edges"]]
        F = lambda L: [Fr(x) for x in L]
        a, rho, k = F(w["parameters"]["a"]), F(w["parameters"]["rho"]), F(w["parameters"]["k"])
        p, q = F(w["equilibrium_p"]), F(w["equilibrium_q"])
        good = G.certify(edges, n, a, rho, k, p, q)
        p2 = [p[0] + Fr(1, 1000)] + p[1:]
        bad_p = G.certify(edges, n, a, rho, k, p2, q)
        rho2 = [rho[0] * Fr(11, 10)] + rho[1:]
        bad_rho = G.certify(edges, n, a, rho2, k, p, q)
        corr = dict(witness=os.path.basename(ws[0]), good_ok=good["ok_bistable"], perturbed_p_ok=bad_p["ok_bistable"],
                    changed_rho_ok=bad_rho["ok_bistable"],
                    passed=bool(good["ok_bistable"] and not bad_p["ok_bistable"] and not bad_rho["ok_bistable"]))
    out["corrupted_witness"] = corr
    # positive control: n=2 census vs Peng Table 1
    rows = [json.loads(l) for f in glob.glob(f"{OUT}/logs/census_n2_s*.jsonl") for l in open(f)]
    rows = [r for r in rows if r["stage"] == 1]
    sys.path.insert(0, PENG)
    from table1 import T1_TEXT  # Peng Table 1 edge lists (read from our recheck lane)
    maps = G.perm_edge_map(2)
    E2 = G.edge_list(2)
    idx = {f"{G.cname(a)}->{G.cname(b)}": i for i, (a, b) in enumerate(E2)}

    def canon(names: list[str]) -> tuple:
        s = [idx[x] for x in names]
        return min(tuple(sorted(mp[e] for e in s)) for mp in maps)
    peng = {canon([t.replace("X+Y", "X+Y") for t in l.split()[1:]]) for l in T1_TEXT.splitlines()}
    mine = {canon(r["edges"]) for r in rows if r["verdict"] == "BISTABLE_CERT"}
    c = Counter(r["verdict"] for r in rows)
    out["positive_control_n2"] = dict(rows=len(rows), verdicts=dict(c), n_bistable=len(mine), peng_n=len(peng),
                                      same_set=(mine == peng), only_mine=len(mine - peng), only_peng=len(peng - mine),
                                      jac_excluded=sum(1 for r in rows if r["jac"]),
                                      sign_excluded_not_jac=sum(1 for r in rows if r["sign"] and not r["jac"]),
                                      passed=bool(len(mine) == 27 and mine == peng and len(rows) == 681))
    json.dump(out, open(f"{OUT}/logs/controls.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
