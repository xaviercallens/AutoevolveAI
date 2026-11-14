"""Assemble result.json from the verification output, controls, logs and file hashes (no hand-entered numbers)."""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sha(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def cpu_from_logs() -> dict:
    tot = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "logs", "*.log"))):
        s = 0.0
        txt = open(p).read()
        for m in re.finditer(r"^n=\d+ restart=\d+ uncovered=.* cpu=([0-9.]+)$", txt, re.M):
            s += float(m.group(1))
        for m in re.finditer(r"^n=\d+ attempt=\d+ .*END .* cpu=([0-9.]+)$", txt, re.M):
            s += float(m.group(1))
        for m in re.finditer(r"^n=\d+ final .* cpu=([0-9.]+)$", txt, re.M):
            s += float(m.group(1))
        for m in re.finditer(r"^n=\d+ float_best=.* cpu=([0-9.]+)$", txt, re.M):
            s += float(m.group(1))
        tot[os.path.basename(p)] = round(s, 1)
    return tot


def main() -> None:
    ver = json.load(open(sys.argv[1]))
    ctl = json.load(open(os.path.join(ROOT, "logs", "controls_run1.json")))
    fuzz = json.load(open(os.path.join(ROOT, "logs", "fuzz_agree.json")))
    certs = {c["n"]: c for c in ver["certificates"]}
    table = []
    for n in range(5, 95):
        c = certs.get(n)
        if c is None:
            table.append({"n": n, "status": "OPEN"})
            continue
        cj = json.load(open(os.path.join(ROOT, "certificates", c["file"])))
        both = c["checker1"] and c["checker2"]
        table.append({"n": n, "status": "CERTIFIED" if both else "KILLED_CHECKER_DISAGREE",
                      "v_is_[n]": cj["v"] == list(range(1, n + 1)), "max_v": max(cj["v"]), "D": cj["D"],
                      "file": c["file"]})
    closed = [r["n"] for r in table if r["status"] == "CERTIFIED" and r["n"] >= 18]
    target = list(range(18, 95))
    N = 17
    while N + 1 in closed:
        N += 1
    controls_pass = (all(x["pass_gamma"] and x["pass_cover"] for x in ctl["positive"])
                     and all(x.get("pass", True) for x in ctl["negative"])
                     and fuzz["stats"]["mismatch"] == 0)
    status = "KEEP" if set(target) <= set(closed) and controls_pass else ("PARTIAL" if closed else "DISCARD")
    files = {}
    for sub in ("code", "certificates", "logs", "controls"):
        for p in sorted(glob.glob(os.path.join(ROOT, sub, "*"))):
            if os.path.isfile(p):
                files[os.path.relpath(p, ROOT)] = sha(p)
    out = {
        "item": "SLR-18", "lane": "W1-a", "status": status,
        "claim": "For every n in the certified list, explicit distinct positive integers v_1..v_n and rational shifts s with max_t min_i ||s_i + v_i t|| < 1/(n+1) (open bad arcs of radius 1/(n+1) cover R/Z), checked in exact integer arithmetic by two independent checkers.",
        "certified_n_ge_18": closed, "open_n_in_18_94": [n for n in target if n not in closed],
        "contiguous_closed_range": [18, N] if N >= 18 else None,
        "certified_5_17_own_shifts": [r["n"] for r in table if r["status"] == "CERTIFIED" and 5 <= r["n"] <= 17],
        "controls_all_pass": controls_pass,
        "controls": {"positive": ctl["positive"],
                     "negative": [{k: v for k, v in x.items() if k != "rows"} for x in ctl["negative"]],
                     "agreement_fuzz": fuzz["stats"],
                     "perturbation_on_new_certificates": ver["perturbation_control"]},
        "table": table, "tier": "C (exact integer checks, two independent checkers; no Lean replay)",
        "cpu_seconds_by_log": cpu_from_logs(), "sha256": files,
    }
    man = json.load(open(os.path.join(ROOT, "logs", "manual_runs_ledger.json")))
    out["cpu_seconds_manual_runs"] = man.get("total_cpu_s", 0.0)
    out["cpu_seconds_total"] = round(sum(out["cpu_seconds_by_log"].values()) + out["cpu_seconds_manual_runs"], 1)
    out["cpu_hours_total"] = round(out["cpu_seconds_total"] / 3600.0, 2)
    json.dump(out, open(os.path.join(ROOT, "result.json"), "w"), indent=1)
    print(json.dumps({"status": status, "closed": closed, "contiguous": out["contiguous_closed_range"],
                      "open": out["open_n_in_18_94"], "controls_all_pass": controls_pass,
                      "cpu_hours_total": out["cpu_hours_total"]}, indent=1))


if __name__ == "__main__":
    main()
