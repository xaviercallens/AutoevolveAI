"""Ledger + controls on the new certificate(s). Writes logs/final_checks.json."""
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from slr_exact import covers_open  # noqa: E402

out = {}
tot = 0
for f in glob.glob(os.path.join(ROOT, "logs", "cpsat_*.log")):
    for ln in open(f):
        m = re.match(r"wall=(\d+)s", ln)
        if m:
            tot += int(m.group(1))
out["cpsat_wall_s_logged"] = tot
out["cpsat_core_h_upper_x7"] = round(tot * 7 / 3600, 2)
certs = {}
for p in sorted(glob.glob(os.path.join(ROOT, "certificates", "cert_n*.json"))):
    c = json.load(open(p))
    v, a, D, n = c["v"], c["a"], c["D"], c["n"]
    assert len(v) == n == len(set(v)) and min(v) >= 1
    r = {"checker1": covers_open(v, a, D, 1, n + 1)[0]}
    r["checker2"] = subprocess.run([os.path.join(HERE, "check_cover"), p], capture_output=True, text=True).stdout.strip()
    S = sum(v)
    D2 = D * 10 * S
    base = [x * 10 * S for x in a]
    br = 0
    for i in range(n):
        for sg in (1, -1):
            aa = list(base)
            aa[i] = (aa[i] + sg * D) % D2
            br += not covers_open(v, aa, D2, 1, n + 1)[0]
    r["N2_perturb_broken"] = f"{br}/{2 * n}"
    r["N0_cover_at_looser_radius_1/(n+2)"] = covers_open(v, a, D, 1, n + 2)[0]
    r["N1_s0_[n]_at_1/(n+1)"] = covers_open(list(range(1, n + 1)), [0] * n, 1, 1, n + 1)[0]
    try:
        covers_open([v[0]] + v[:-1], a, D, 1, n + 1)
        r["dup_velocity_rejected"] = False
    except ValueError:
        r["dup_velocity_rejected"] = True
    certs[os.path.basename(p)] = r
out["certs"] = certs
json.dump(out, open(os.path.join(ROOT, "logs", "final_checks.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
