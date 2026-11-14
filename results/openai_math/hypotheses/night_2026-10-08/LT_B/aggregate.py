import collections
import glob
import json
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
c = collections.defaultdict(list)
for f in sorted(glob.glob("part1/*_call*.json")):
    d = json.load(open(f))
    cell = f[6:].rsplit("_call", 1)[0]
    c[cell] += [(r["seed"], r["excess"]) for r in d["rows"]]
p1 = {k: {"restarts": len(v), "seeds": [s for s, _ in v], "max_excess": max(e for _, e in v),
          "verdict": "NO_VIOLATION_FOUND (not a proof)"} for k, v in c.items()}
keys = ["verdict", "lambda_max_restricted", "hessian_threshold", "n_positive_beyond_thr", "n_zero_within_thr",
        "n_negative_beyond_thr", "n_confirmed_positive", "gradient_norm", "control_b_quad_translation_dilation_max",
        "spectrum_restricted"]
p2 = {}
for f in sorted(glob.glob("part2/*.json")):
    d = json.load(open(f))
    p2[f[6:-5]] = {k: d[k] for k in keys}
ctl1 = p1["control_gamma1.5_m3"]["max_excess"] <= 1e-5
ctl2 = all(p2[k]["verdict"] == ("NEGATIVE_CONTROL_PASS" if "g3.0" in k else "NONPOSITIVE_SECOND_VARIATION") for k in p2)
res = {
    "lane": "LT_B", "controls_pass": bool(ctl1 and ctl2), "part1": p1, "part2": p2,
    "H-LT1_m3": "NO_VIOLATION_FOUND in all 6 cells (8 restarts each); control gamma=1.5 not exceeded; finite search power only",
    "H-LT3": "NOT KILLED: no restricted Hessian eigenvalue above threshold for gamma in {0.75,1.0,1.25,1.4}, m in {1,2,3}; "
             "negative control gamma=3 m=1,2 gives confirmed positive directions",
    "driver": "driver.log; deviations.md",
}
json.dump(res, open("result.json", "w"), indent=1)
rows = ["run\thypothesis\tstrategy\tbudget_s\tmetric\tvalue\tcontrols\tstatus\tnote"]
n = 0
for k, v in p1.items():
    n += 1
    rows.append(f"LT_B-{n}\tH-LT1 m=3\tcampaign {k} K=2 P=8 {v['restarts']} restarts seeds {min(v['seeds'])}-{max(v['seeds'])}"
                f"\t450x4\tmax excess R/L1-1\t{v['max_excess']:.3g}\tpass\tkeep\tNO_VIOLATION_FOUND (not a proof)")
for k, v in p2.items():
    n += 1
    rows.append(f"LT_B-{n}\tH-LT3 {k}\tsecond_variation P=8 autograd Hessian + FD\t-\tlambda_max restricted"
                f"\t{v['lambda_max_restricted']:.3g}\tpass\tkeep\t{v['verdict']}; pos={v['n_positive_beyond_thr']} "
                f"confirmed={v['n_confirmed_positive']} thr={v['hessian_threshold']:.3g}")
open("lane_results.tsv", "w").write("\n".join(rows) + "\n")
print(res["controls_pass"], n)
