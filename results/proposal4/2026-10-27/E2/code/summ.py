import json
d = json.load(open("results/proposal4/2026-10-27/E2/data/pybamm_compare.json"))
rows = [r for r in d["rows"] if r["status"] == "ok"]
print(len(d["rows"]), len(rows))
for mesh in (20, 100):
    for m in ("SPM", "SPMe"):
        x = [abs(r["rel_diff_avg"]) for r in rows if r["model"] == m and r["r_n"] == mesh]
        print(m, mesh, len(x), max(x))
inside = [r for r in rows if r["r_n"] == 100 and r["model"] == "SPM"]
print(max(abs(r["t_cross_avg"] - 0.5*(r["t_cert_lo"]+r["t_cert_hi"])) for r in inside))
print(d["N4"])
