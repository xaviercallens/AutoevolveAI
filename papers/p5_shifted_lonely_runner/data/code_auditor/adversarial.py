#!/usr/bin/env python3
"""Adversarial tests of the auditor checker (audit_check.py)."""
from __future__ import annotations

import json
import os
import random
import sys
from fractions import Fraction as F

sys.path.insert(0, "/tmp/slraudit")
from audit_check import check, cover_A, evalt, gamma_B  # noqa: E402

CERTS = sys.argv[1]
res: dict = {}

# 1. [n], s=0 at delta=1/(n+1): must NOT cover; gamma must equal 1/(n+1) (Dirichlet + t=1/(n+1)).
bad = []
for n in range(2, 41):
    v = list(range(1, n + 1)); a = [0] * n
    c = check({"n": n, "v": v, "a": a, "D": 1})
    if c["coverA"] or c["coverB"] or F(c["gamma"]) != F(1, n + 1):
        bad.append(n)
res["T1_unshifted_[n]_n2..40_failures"] = bad

# 2. Published gammas (Blanco-Criado-Santos Prop 5.11, 5.12).
pub = [((1, 2, 3, 4, 5), (0, 46, 38, 47, 72), 94, F(15, 94)),
       ((2, 3, 4, 5, 6, 8), (0, 29, 17, 0, 16, 22), 30, F(2, 15)),
       ((1, 2, 3, 4, 5, 6), (0, 39, 37, 51, 62, 54), 67, F(9, 67))]
res["T2_published_gamma"] = [(str(gamma_B(list(v), list(a), D)[0]), str(g)) for v, a, D, g in pub]

# 3. Tangency: every certificate at delta = its own exact gamma must fail; at gamma + 1/10^12 must cover.
tang = []
files = sorted(f for f in os.listdir(CERTS) if f.endswith(".json"))
certs = {f: json.load(open(os.path.join(CERTS, f))) for f in files}
for f in ["cert_n005.json", "cert_n018.json", "cert_n029.json", "cert_n038.json"]:
    c = certs[f]
    g, _ = gamma_B(c["v"], c["a"], c["D"])
    s = [F(x, c["D"]) for x in c["a"]]
    at, _ = cover_A(c["v"], s, g)
    above, _ = cover_A(c["v"], s, g + F(1, 10**12))
    below, _ = cover_A(c["v"], s, g - F(1, 10**12))
    tang.append((f, str(g), at, above, below))
res["T3_tangency(file,gamma,cover@gamma,cover@gamma+eps,cover@gamma-eps)"] = tang

# 4. Duplicated velocity / wrong n / wrong delta must be flagged by validate.
c = dict(certs["cert_n018.json"]); v = list(c["v"]); v[-1] = v[0]; c["v"] = v
r4a = check(c, do_gamma=False)
c2 = dict(certs["cert_n018.json"]); c2["delta_den"] = 18
r4b = check(c2, do_gamma=False)
c3 = dict(certs["cert_n018.json"]); c3["v"] = [0] + c3["v"][1:]
r4c = check(c3, do_gamma=False)
res["T4_dup_velocity_errs"] = r4a["errs"]; res["T4_wrong_delta_errs"] = r4b["errs"]; res["T4_zero_velocity_errs"] = r4c["errs"]
# trivial repeated-velocity counterexample v_i=1, s_i=i/n covers but is invalid
n = 6
r4d = check({"n": n, "v": [1] * n, "a": list(range(n)), "D": n})
res["T4_trivial_repeated(valid,coverA)"] = (r4d["valid"], r4d["coverA"])

# 5. Perturbations: shift one runner of n18/n38 by +-1/2 of an arc (delta/(2 v_i)) in t-space, i.e. a_i += +-D*delta/2.
pert = {}
for f in ["cert_n018.json", "cert_n038.json"]:
    c = certs[f]; n = c["n"]; D = c["D"]
    broke = 0; tot = 0; disagree = 0
    for i in range(n):
        for sgn in (1, -1):
            a2 = list(c["a"]); D2 = D * 2 * (n + 1)
            a2 = [x * 2 * (n + 1) for x in a2]; a2[i] += sgn * D  # shift s_i by delta/2
            cc = {"n": n, "v": c["v"], "a": a2, "D": D2}
            r = check(cc)
            tot += 1; broke += (not r["coverA"]); disagree += (r["coverA"] != r["coverB"])
    pert[f] = {"perturbations": tot, "broken": broke, "A_vs_B_disagree": disagree}
res["T5_shift_by_delta/2"] = pert

# 6. Random fuzz: method A vs method B vs dense float grid on small instances.
rng = random.Random(20261031)
mism = 0; tests = 0; grid_viol = 0
for _ in range(400):
    n = rng.randint(2, 7)
    v = rng.sample(range(1, 13), n); D = rng.randint(2, 60); a = [rng.randrange(D) for _ in range(n)]
    g, _ = gamma_B(v, a, D)
    # grid check: no grid point exceeds gamma
    N = 4000
    gm = max(min(abs(((am / D + vm * k / N) + 0.5) % 1 - 0.5) for vm, am in zip(v, a)) for k in range(N))
    if gm > float(g) + 1e-12: grid_viol += 1
    for delta in (g, g + F(1, 10**9), g - F(1, 10**9), F(1, n + 1)):
        if delta <= 0: continue
        ca, _ = cover_A(v, [F(x, D) for x in a], delta)
        tests += 1; mism += (ca != (g < delta))
res["T6_fuzz"] = {"instances": 400, "tests": tests, "A_vs_B_mismatch": mism, "grid_exceeds_gamma": grid_viol}
print(json.dumps(res, indent=1))
