import json, collections, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
tab = collections.defaultdict(lambda: collections.Counter())
cpu = 0.0
for d in rows:
    tab[d["family"]][d["status"]] += 1
    cpu += d["wall_s"] * d["workers"]
for f, c in tab.items():
    ns = sorted(d["n"] for d in rows if d["family"] == f and d["status"] == "INFEASIBLE")
    fe = sorted(d["n"] for d in rows if d["family"] == f and d["status"] in ("OPTIMAL", "FEASIBLE"))
    print(f, dict(c), "INFEASIBLE n:", ns, "FEASIBLE n:", fe)
print("core-hours (wall x workers):", round(cpu / 3600, 2), "rows", len(rows))
