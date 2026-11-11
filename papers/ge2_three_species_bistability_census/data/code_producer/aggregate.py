"""GE-2 aggregation: census.jsonl, counts, minimality, result.json with sha256."""
from __future__ import annotations
import glob
import hashlib
import itertools
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
import ge2lib as G

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)


def sha(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main() -> None:
    rows: dict = {}
    for f in sorted(glob.glob(f"{OUT}/logs/census_n3_s*.jsonl")):
        for line in open(f):
            r = json.loads(line)
            key = r["id"]
            if key not in rows or r["stage"] >= rows[key]["stage"]:
                rows[key] = r
    rows_l = sorted(rows.values(), key=lambda r: r["idx"])
    with open(f"{OUT}/census.jsonl", "w") as fo:
        for r in rows_l:
            fo.write(json.dumps(r) + "\n")
    tab: dict = defaultdict(Counter)
    tabw: dict = defaultdict(Counter)
    for r in rows_l:
        tab[r["bucket"]][r["verdict"]] += 1
        tabw[r["bucket"]][r["verdict"]] += r["orbit_size"]
    # minimality via canonical subsets
    E = G.edge_list(3)
    idx = {f"{G.cname(a)}->{G.cname(b)}": i for i, (a, b) in enumerate(E)}
    maps = G.perm_edge_map(3)
    verd = {tuple(sorted(idx[e] for e in r["edges"])): r["verdict"] for r in rows_l}  # reps are canonical

    def canon(s: tuple) -> tuple:
        return min(tuple(sorted(mp[e] for e in s)) for mp in maps)
    bis = [r for r in rows_l if r["verdict"] == "BISTABLE_CERT"]
    minimal, nonminimal = [], []
    for r in bis:
        s = tuple(sorted(idx[e] for e in r["edges"]))
        sub_bis = False
        for m in range(1, len(s)):
            for sub in itertools.combinations(s, m):
                if verd.get(canon(sub)) == "BISTABLE_CERT":
                    sub_bis = True
        (nonminimal if sub_bis else minimal).append(r["id"])
    cpu = {"n3_stage1_cpu_s": round(sum(r["cpu_s"] for r in rows_l if r["stage"] == 1), 1)}
    n2 = [json.loads(l) for f in glob.glob(f"{OUT}/logs/census_n2_s*.jsonl") for l in open(f)]
    cpu["n2_control_cpu_s"] = round(sum(r["cpu_s"] for r in n2), 1)
    cpu["total_core_hours_census_rows"] = round((cpu["n3_stage1_cpu_s"] + cpu["n2_control_cpu_s"]) / 3600, 3)
    enum = json.load(open(f"{OUT}/logs/enum_n3.json"))
    summary = dict(enumeration=enum, rows=len(rows_l), table_orbits={b: dict(c) for b, c in tab.items()},
                   table_labelled={b: dict(c) for b, c in tabw.items()}, bistable_total=len(bis),
                   bistable_minimal=minimal, bistable_nonminimal=len(nonminimal), cpu=cpu,
                   bistable_by_m={f"{b}/m{m}": c for (b, m), c in Counter((r["bucket"], r["m"]) for r in bis).items()})
    json.dump(summary, open(f"{OUT}/logs/summary.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print("MINIMAL:")
    for r in rows_l:
        if r["id"] in minimal:
            print(r["id"], r["bucket"], r["edges"])


if __name__ == "__main__":
    main()
