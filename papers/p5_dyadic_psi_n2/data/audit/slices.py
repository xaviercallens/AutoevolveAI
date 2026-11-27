import json
import subprocess

G = "/tmp/dhaudit/gauge_enum"
P = "/tmp/dhaudit/psi_exhaust_rebuilt"
res = []
for a in (0, 1, 7000, 12345, 21845, 30000, 32767):
    for haar, wlist in ((1, (1, 3, 4)), (0, (1, 3))):
        g = json.loads(subprocess.run(["taskset", "-c", "5", G, str(haar), "slice", str(a), str(a + 1)], capture_output=True, text=True, check=True).stdout)
        for w in wlist:
            p = json.loads(subprocess.run(["taskset", "-c", "5", P, str(w), str(haar), str(a), str(a + 1)], capture_output=True, text=True, check=True).stdout)
            m = g["modes"][f"wT={w}"]
            res.append({"F0code": a, "haar": haar, "wT": w, "max_mine": m["max_S"], "max_prod": p["max_S"],
                        "gt192_mine": m["pairs_gt192"], "gt192_prod": p["violating_pairs_gt192"],
                        "hist_equal": {k: int(v) for k, v in m["hist"].items()} == {k: int(v) for k, v in p["hist"].items()}})
print(json.dumps(res))
print("all_equal", all(r["hist_equal"] for r in res), "n", len(res))
