#!/usr/bin/env python3
"""Collect box results into data/summary.json and result.json (sha256 of every file)."""
import os, json, hashlib, glob
from math import comb
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


boxes = []
for lab, files in [("primary", glob.glob(os.path.join(root, "logs", "primary_n*_N*.json"))),
                   ("ext", glob.glob(os.path.join(root, "logs", "ext_n*_N*.json"))),
                   ("ext2", glob.glob(os.path.join(root, "logs", "ext2_n*_N*.json")))]:
    for f in sorted(files):
        b = os.path.basename(f)
        if b.endswith("_verify.json") or "_W9" in b:
            continue
        try:
            d = json.loads(open(f).read())
        except Exception:
            continue
        n, N = d["n"], d["N"]
        tuples = sum(int(l.split("tuples=")[1].split()[0]) for l in d["logs"])
        vf = os.path.join(root, "logs", b.replace(".json", "_verify.json"))
        v = json.loads(open(vf).read()) if os.path.exists(vf) else None
        boxes.append({"group": lab, "n": n, "N": N, "tuples_enumerated": tuples, "equals_C(N,n)": tuples == comb(N, n),
                      "wall_s": d["wall_s"], "core_s_upper": d["core_s_approx"], "primitive_neartight": d["primitive_neartight"],
                      "k_counts": v["k_counts"] if v else None, "k_gt_n": v["k_gt_n"] if v else None,
                      "k_gt_half_n": v["k_gt_half_n"] if v else None,
                      "verifier_mismatches": v["verifier_mismatches"] if v else None,
                      "max_vmax_over_q": v["max_vmax_over_q"] if v else None,
                      "odd_form_failures": v.get("odd_denominator_form_failure_count") if v else None})
boxes.sort(key=lambda b: (b["n"], b["N"]))
total_core_s = sum(b["core_s_upper"] for b in boxes)
summ = {"boxes": boxes, "total_core_seconds_upper_bound_of_listed_boxes": total_core_s, "total_core_hours_upper_bound": round(total_core_s / 3600, 2)}
json.dump(summ, open(os.path.join(root, "data", "summary.json"), "w"), indent=1)
print(json.dumps(summ, indent=1))

files = {}
for dp, dn, fn in os.walk(root):
    if "__pycache__" in dp:
        continue
    for f in fn:
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, root)
        if rel in ("result.json",):
            continue
        files[rel] = sha(p)
res_path = os.path.join(root, "result.json")
base = json.load(open(res_path)) if os.path.exists(res_path) else {}
base["files_sha256"] = dict(sorted(files.items()))
json.dump(base, open(res_path, "w"), indent=1)
