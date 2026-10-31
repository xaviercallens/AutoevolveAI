"""Write result.json with sha256 of every file under E2/ (except result.json itself)."""
import hashlib
import json
import os

BASE = "results/proposal4/2026-10-27/E2"
sha = {}
for root, _, fs in os.walk(BASE):
    if "__pycache__" in root:
        continue
    for f in fs:
        p = os.path.join(root, f)
        if p.endswith("/result.json"):
            continue
        sha[os.path.relpath(p, BASE)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
out = dict(
    item="E2",
    outcome="PARTIAL",
    producer="Sonnet 5.5 (audited by separate AI agent: ACCEPT_WITH_CORRECTIONS, applied)",
    date="2026-10-31",
    headline="Certified t*(C) enclosures (relative width <= 1e-13) for C=1..4, x0 in {0.05,0.25,0.5}, x* in {1.0,0.9014}; "
             "PyBaMM SPM agrees to 4.2e-4 (r_n=20) and 1.7e-5 (r_n=100); SPMe identical to SPM; DFN local max-over-x "
             "saturates earlier; DFN fails for C>=3; no Lean.",
    tiers=dict(A="none", C="Arb enclosures", X="mpmath, finite volume, PyBaMM", L="closed form, parameters"),
    prereg_sha256="514d7fddec830319fa0cdaab327819d657961a4413de6e74fa1517eb898d9269",
    parent_preregistration_sha256="7f7d5ac1b2ba2987860542bcb6acec4bf5b68bbdabce183433d9d2135e65b438",
    files_sha256=dict(sorted(sha.items())),
)
json.dump(out, open(os.path.join(BASE, "result.json"), "w"), indent=1)
print(len(sha))
