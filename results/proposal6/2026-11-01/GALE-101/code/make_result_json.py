"""Write result.json with sha256 of every file. usage: python make_result_json.py <item_dir>"""
from __future__ import annotations

import hashlib
import json
import os
import sys

root = sys.argv[1]
files = {}
for d, _, fs in os.walk(root):
    if "__pycache__" in d:
        continue
    for f in fs:
        if f == "result.json":
            continue
        p = os.path.join(d, f)
        files[os.path.relpath(p, root)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
h = json.load(open(os.path.join(root, "data/headline.json")))
h.pop("five_colouring", None)
res = {
    "item": "GALE-101",
    "label": "independent recheck of a claim by others (arXiv 2610.28828); no novelty claim",
    "outcome": "CONFIRMED",
    "tiers": {"geometry_and_UNSAT": "C", "sigma3_inequality": "C", "upper_bound_ball": "L", "tetra_sphere_sanity": "X", "lean": "not done"},
    "n_points": 101, "edges": 2030, "threshold": "88928/100000", "D2_1e14": 100000021020030,
    "weakest_included_ratio": 0.8892809651305066, "strongest_excluded_ratio": 0.889259794998014,
    "unsat": {"glucose4_drat_trim_verified_sym": True, "glucose4_drat_trim_verified_nosym": True,
              "cadical195_encB": "UNSAT", "dsatur_nodes": 745},
    "five_colourable": True, "mus_edges": 425, "headline": h, "controls_passed": True,
    "compute": "taskset -c 1",
    "files_sha256": files,
}
json.dump(res, open(os.path.join(root, "result.json"), "w"), indent=1)
print(len(files))
