import hashlib
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
r = {}
for d, _, fs in os.walk(ROOT):
    if "__pycache__" in d:
        continue
    for f in sorted(fs):
        if f == "result.json":
            continue
        p = os.path.join(d, f)
        r[os.path.relpath(p, ROOT)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
json.dump({"outcome": "NEGATIVE", "tier": "C", "core_hours_est": 2.9,
           "baseline_gamma": "1/(n+2) for n=95..117; 1/(n+3) for n=118..140",
           "best_ours": "tie only (n=118 control, gamma 1/121)", "sha256": r},
          open(os.path.join(ROOT, "result.json"), "w"), indent=1)
print(len(r))
