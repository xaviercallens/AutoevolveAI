"""Print the SCHA profiles of data/scha.json: per Lam, gamma at rho and the lowest stable sampled competitor."""

import json
import sys

d = json.load(open(sys.argv[1]))
for ak, r in sorted(d.items(), key=lambda kv: float(kv[0])):
    print("a =", ak, "breakdown", r.get("breakdown_lam"), "lam*_scha", r.get("lam_star_scha"), "harmonic Lam_1", r.get("harmonic_Lam_1"))
    for p in r["profiles"]:
        good = [q for q in p["points"] if q["status"] == "converged" and (q["stab_eff"] or -1) > 0]
        b = min(good, key=lambda q: q["dE"])
        print("  lam %.4f gamma_rho %.3f  best %-8s (%.4f,%.4f) dE %+.2e stab %.2e  n_unstable_or_unconverged %d"
              % (p["lam"], p["gamma_rho"], b["kind"], b["x"], b["y"], b["dE"], b["stab_eff"], len(p["points"]) - len(good)))
