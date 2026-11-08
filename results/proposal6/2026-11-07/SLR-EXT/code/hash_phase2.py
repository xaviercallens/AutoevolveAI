import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = {}
for dp, _, fs in os.walk(ROOT):
    for f in fs:
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, ROOT)
        if rel in ("result_phase2.json", "code/check_cover", "code/cover_ls_fast") or rel.startswith("logs/tmp") or "__pycache__" in rel:
            continue
        d[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
json.dump({"outcome": "NO_NEW_N", "found_n": [], "phase2_core_h": 8, "sha256": d}, open(os.path.join(ROOT, "result_phase2.json"), "w"), indent=1, sort_keys=True)
print(len(d))
