"""N1: collect the real tool outputs (certified runs, Lean compile JSONs, LeanFlow results, cross-check, controls)
into results/proposal3/2026-10-26/N1/result.json. Nothing is typed in by hand: every number is read from a file.

usage: python -I n1_make_result.py N1_DIR
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import sys


def sha(p: str) -> str:
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def lean_summary(p: str) -> dict:
    d = json.load(open(p))
    axioms = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", d["output"].replace("\n ", " "))
    errors = [ln for ln in d["output"].splitlines() if ": error" in ln]
    return {"file": d["file"], "rc": d["rc"], "seconds": d["seconds"], "n_errors": len(errors), "errors": errors[:5],
            "axioms": {k: [x.strip() for x in v.split(",")] for k, v in axioms}}


def main() -> None:
    d = sys.argv[1]
    repo = os.path.abspath(os.path.join(d, "..", "..", "..", ".."))
    out: dict = {"item": "N1", "date": "2026-10-26",
                 "preregistration": "results/proposal3/2026-10-26/preregistration.json"}
    out["certificate_summary"] = json.load(open(os.path.join(d, "cert_summary.json")))
    runs = []
    for p in [os.path.join(d, x) if not os.path.isabs(x) else x for x in out["certificate_summary"]["inputs"]]:
        for r in json.load(open(p)):
            runs.append({k: r[k] for k in ("a_lo", "a_hi", "a_c", "delta", "N", "depth", "tol", "qmax",
                                           "n_lattice_half", "ok", "sign", "Q", "D", "R", "Epp_window", "stats",
                                           "tail_T", "seconds", "script_sha256")} | {"file": os.path.relpath(p, d)})
    out["runs"] = runs
    out["n_runs"] = len(runs)
    out["cpu_seconds_sweep"] = round(sum(r["seconds"] for r in runs), 1)
    out["lean"] = {os.path.basename(p): lean_summary(p) for p in sorted(glob.glob(os.path.join(d, "lean_*.json")))}
    lf = {}
    for p in sorted(glob.glob(os.path.join(d, "leanflow", "leanflow_result_*.json"))):
        x = json.load(open(p))
        lf[os.path.basename(p)] = {k: x.get(k) for k in ("status", "code", "tier", "verified", "failed", "lean_version",
                                                          "claim_sha256", "statement_sha256", "seconds")}
        lf[os.path.basename(p)]["n_assertions"] = len(x.get("assertions", []))
    out["leanflow"] = lf
    cc = os.path.join(d, "crosscheck_tierX.json")
    if os.path.exists(cc):
        c = json.load(open(cc))
        out["crosscheck_tierX"] = {"n_checks": c["n_checks"], "n_not_contained": c["n_not_contained"]}
    out["sha256"] = {os.path.relpath(p, repo): sha(p) for p in
                     sorted(glob.glob(os.path.join(d, "code", "*.py")))
                     + sorted(glob.glob(os.path.join(repo, "formal_cert", "Programmes", "ZeroPointClass", "*.lean")))}
    json.dump(out, open(os.path.join(d, "result.json"), "w"), indent=1)
    print("wrote result.json:", out["n_runs"], "runs;", {k: v["rc"] for k, v in out["lean"].items()}, lf and
          {k: v["status"] for k, v in lf.items()})


if __name__ == "__main__":
    main()
