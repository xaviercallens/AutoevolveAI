import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = {}
for dp, _, fs in os.walk(ROOT):
    for f in fs:
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, ROOT)
        if rel == "result.json" or rel.startswith("logs/tmp") or rel in ("code/check_cover", "code/cover_ls_fast") or "__pycache__" in rel:
            continue
        d[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
json.dump({"outcome": "PARTIAL", "found_n": [63], "cpu_core_h_upper": 16, "sha256": d}, open(os.path.join(ROOT, "result.json"), "w"), indent=1, sort_keys=True)
print(len(d))
