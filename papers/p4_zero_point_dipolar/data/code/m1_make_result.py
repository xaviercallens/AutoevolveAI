"""M1: assemble result.json (status per potential, key numbers, controls, Lean gate records, sha256 of every file).

usage: python -I m1_make_result.py M1_DIR LEAN_DIR
"""
from __future__ import annotations

import hashlib
import json
import os
import sys


def sha(p: str) -> str:
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load(p: str) -> dict | None:
    if not os.path.exists(p):
        return None
    with open(p) as fh:
        return json.load(fh)


def summary(rec: dict | None) -> dict | None:
    if rec is None:
        return None
    if "refused" in rec:
        return {"certified": False, "refused": rec["refused"], "infinite_keys": rec.get("infinite_keys")}
    M = rec["M_window_curvature_bound"]
    return {"certified_not_local_min": rec["certified_not_local_min"], "positivity_ok": rec["positivity_ok"],
            "M": [M["lo_float"], M["hi_float"]], "M_hi_rational": rec["cert_rationals"]["M_hi"],
            "M_lo_rational": rec["cert_rationals"]["M_lo"], "E0": [rec["E0"]["lo_float"], rec["E0"]["hi_float"]],
            "U_lin_pp0": [rec["U_lin_pp0_B2_majorant"]["lo_float"], rec["U_lin_pp0_B2_majorant"]["hi_float"]],
            "lmin_lo": rec["cert_rationals"]["lmin_lo"], "lminu_lo": rec["cert_rationals"]["lminu_lo"],
            "qpd_lo": rec["cert_rationals"]["qpd_lo"], "cells": rec["stats"]["cells"], "failed": rec["stats"]["failed"],
            "seconds": rec["seconds"], "qmax": rec["qmax"], "alpha": rec.get("alpha"), "N": rec["N"],
            "max_depth": rec["max_depth"], "refine_tol": rec["refine_tol"], "controls": rec["controls"],
            "script_sha256": rec.get("script_sha256")}


def main() -> None:
    m1, lean_dir = sys.argv[1], sys.argv[2]
    data = os.path.join(m1, "data")
    runs = {n[:-5]: summary(load(os.path.join(data, n))) for n in sorted(os.listdir(data))
            if n.endswith(".json") and not n.startswith(("selfcheck", "explore"))}
    files = {}
    for sub in ("code", "data", "logs"):
        for root, _, names in os.walk(os.path.join(m1, sub)):
            for n in sorted(names):
                if "__pycache__" in root:
                    continue
                p = os.path.join(root, n)
                files[os.path.relpath(p, m1)] = sha(p)
    for n in sorted(os.listdir(lean_dir)):
        p = os.path.join(lean_dir, n)
        if os.path.isfile(p):
            files["LEAN/" + n] = sha(p)
    for extra in ("RESULT.md",):
        p = os.path.join(m1, extra)
        if os.path.exists(p):
            files[extra] = sha(p)
    lean = {n[:-5]: load(os.path.join(m1, n)) for n in sorted(os.listdir(m1)) if n.startswith("lean_") and n.endswith(".json")}
    lean = {k: ({"rc": v["rc"], "seconds": v["seconds"], "output": v["output"]} if v else None) for k, v in lean.items()}
    status_in = load(os.path.join(m1, "status_input.json")) or {}
    out = {"item": "M1", "proposal": "docs/proposals/NEXT_STEPS_PROPOSAL_4_2026-10-27.md", "status": status_in.get("status"),
           "per_potential": status_in.get("per_potential"), "runs": runs, "lean": lean,
           "replay": load(os.path.join(m1, "replay.json")), "grep": load(os.path.join(m1, "grep.json")),
           "sha256": files}
    with open(os.path.join(m1, "result.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: out[k] for k in ("status", "per_potential")}, indent=1))
    for k, v in runs.items():
        print(k, v if v is None else {kk: v.get(kk) for kk in ("certified_not_local_min", "M", "seconds")})


if __name__ == "__main__":
    main()
