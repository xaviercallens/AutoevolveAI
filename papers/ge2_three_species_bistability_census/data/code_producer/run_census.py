"""GE-2 census driver, resumable (jsonl log per shard). usage: run_census.py n shard nshards npairs [stage]"""
from __future__ import annotations
import json
import os
import sys
import time
from fractions import Fraction as Fr
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import ge2lib as G

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)


def sfr(x: Fr) -> str:
    return f"{x.numerator}/{x.denominator}"


def row_edges(edges):
    return [f"{G.cname(a)}->{G.cname(b)}" for a, b in edges]


def main() -> None:
    n, shard, nsh, npairs = (int(v) for v in sys.argv[1:5])
    stage = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    tag = f"n{n}"
    E = G.edge_list(n)
    labelled, orbits, burn = G.enumerate_orbits(n)
    reps = sorted(orbits)
    if shard == 0 and stage == 1:
        json.dump(dict(n=n, labelled=labelled, orbits=len(reps), burnside=burn,
                       orbit_size_sum=sum(orbits.values())), open(f"{OUT}/logs/enum_{tag}.json", "w"))
    log = f"{OUT}/logs/census_{tag}_s{shard}.jsonl"
    done: dict = {}
    if os.path.exists(log):
        for line in open(log):
            r = json.loads(line)
            done[(r["id"], r["stage"])] = r
    os.makedirs(f"{OUT}/witnesses", exist_ok=True)
    f = open(log, "a")
    for idx, rep in enumerate(reps):
        if idx % nsh != shard:
            continue
        nid = ("G%05d" if n == 3 else "P%04d") % idx
        if (nid, stage) in done:
            continue
        edges = [E[e] for e in rep]
        if stage == 3:
            # amendment: stage-1 search could not sample networks with a species never changed by internal reactions
            prev = [rr for (i2, s2), rr in done.items() if i2 == nid and s2 == 1]
            S0 = [sum(abs(b[i] - a[i]) for a, b in edges) for i in range(n)]
            if not prev or prev[0]["verdict"] not in ("UNDECIDED", "MULTISTATIONARY_CERT") or all(S0):
                continue
        t0 = time.process_time()
        row = dict(id=nid, idx=idx, stage=stage, edges=row_edges(rep and edges), m=len(edges),
                   orbit_size=orbits[rep], bucket=G.bucket(edges, n))
        jac = G.jac_rule(edges, n)
        sgn = G.sign_rule(edges, n)
        row.update(jac=jac, sign=sgn)
        if jac or sgn:
            row.update(verdict="MONOSTATIONARY_JAC" if jac else "MONOSTATIONARY_SIGN", cert="exclusion")
        else:
            rng = np.random.default_rng([20261111, n, idx, stage])
            res = G.search(edges, n, rng, npairs)
            row.update(pairs=res["pairs"], n_stable_cand=len(res["stable"]), n_multi_cand=len(res["multi"]))
            w = G.find_witness(edges, n, res["stable"], "stable") if res["stable"] else None
            if w is not None:
                row.update(verdict="BISTABLE_CERT", cert="exact_rational_witness")
                json.dump(dict(id=nid, edges=row_edges(edges), species=n,
                               parameters=dict(a=[sfr(x) for x in w["a"]], rho=[sfr(x) for x in w["rho"]],
                                               k=[sfr(x) for x in w["k"]]),
                               equilibrium_p=[sfr(x) for x in w["p"]], equilibrium_q=[sfr(x) for x in w["q"]],
                               enclosure_p=[[sfr(x), sfr(x)] for x in w["p"]],
                               enclosure_q=[[sfr(x), sfr(x)] for x in w["q"]],
                               hurwitz={k_: {a_: (sfr(b_) if isinstance(b_, Fr) else b_) for a_, b_ in v_.items()}
                                        for k_, v_ in (("p", w["cert"]["hurwitz_p"]), ("q", w["cert"]["hurwitz_q"]))},
                               convention="Hurwitz data for A=-J: a1=tr, a2=sum 2x2 minors, a3=det, h=a1*a2-a3"),
                          open(f"{OUT}/witnesses/{nid}.json", "w"), indent=1)
            else:
                w2 = G.find_witness(edges, n, res["multi"], "multi") if res["multi"] else None
                if w2 is not None:
                    row.update(verdict="MULTISTATIONARY_CERT", cert="exact_two_equilibria",
                               multi_p=[sfr(x) for x in w2["p"]], multi_q=[sfr(x) for x in w2["q"]])
                else:
                    row.update(verdict="UNDECIDED", cert="none")
        row["cpu_s"] = round(time.process_time() - t0, 3)
        f.write(json.dumps(row) + "\n")
        f.flush()
    f.close()


if __name__ == "__main__":
    main()
