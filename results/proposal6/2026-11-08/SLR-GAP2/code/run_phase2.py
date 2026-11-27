"""SLR-GAP2 phase 2 driver: control, then families b3, b2w, b6, one (N, family) at a time, 6 workers, 600 s.
Resumable from logs/runs2.jsonl.  Run:  setsid nohup taskset -c 1-6 python run_phase2.py &
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOG2 = os.path.join(ROOT, "logs", "runs2.jsonl")
START = os.path.join(ROOT, "logs", "runs2_start.log")
LOG1 = os.path.join(ROOT, "logs", "runs.jsonl")
PY = "/home/callensxavier_gmail_com/.cache/slrvenv/bin/python"
sys.path.insert(0, HERE)
from cpsat_gen import smooth  # noqa: E402

WORKERS, TLIM, BUDGET_H = 6, 600, 14.0
FAMS = {
    "b3": dict(b=3, evmin=6, evp="2,3", odp="2,5", qs="12", dmult=24, jstep=6, J=4, cap_h=7.0),
    "b2w": dict(b=2, evmin=2, evp="2,3,5", odp="3,5,7", qs="8", dmult=8, jstep=1, J=2, cap_h=4.5),
    "b6": dict(b=6, evmin=6, evp="2,3", odp="2,5", qs="12", dmult=24, jstep=6, J=4, cap_h=2.5),
}


def ratio(N: int, f: dict) -> tuple[float, int, int]:
    b = f["b"]
    evp = tuple(int(x) for x in f["evp"].split(","))
    pe = {v for v in smooth(b * N, evp) if v % f["evmin"] == 0 and v % b == 0}
    F = [b * k for k in range(1, N + 1) if b * k not in pe]
    slots = N - 1 - len(F)
    iv = []
    r = Fraction(1, N)
    for v in F:  # open arcs ||v t|| < 1/N, t in [0,1)
        for k in range(v + 1):
            c = Fraction(k, v)
            iv.append((max(Fraction(0), c - r / v), min(Fraction(1), c + r / v)))
    iv.sort()
    cov, R = Fraction(0), Fraction(0)
    for lo, hi in iv:
        if hi <= R:
            continue
        cov += hi - max(lo, R)
        R = hi
    unc = 1 - cov
    cap = Fraction(slots * 2, N)
    return (float(unc / cap) if slots > 0 else 9e9), slots, len(F)


def rows(path: str) -> list[dict]:
    return [json.loads(x) for x in open(path)] if os.path.exists(path) else []


def spent_h() -> float:
    """CPU-hours actually spent: completed rows (wall x workers) + killed runs (start w/o row) up to next start/now."""
    done = rows(LOG2)
    tot = sum(d["wall_s"] * d["workers"] for d in done)
    starts = [json.loads(x) for x in open(START)] if os.path.exists(START) else []
    finished = {d["tag"] for d in done}
    for s in starts:
        if s["tag"] not in finished and s.get("killed_s"):
            tot += s["killed_s"] * s["workers"]
    return tot / 3600


def run_one(tag: str, N: int, f: dict, fam: str, extra: list[str]) -> dict:
    size1 = os.path.getsize(LOG1)
    t0 = time.time()
    with open(START, "a") as sf:
        sf.write(json.dumps({"tag": tag, "N": N, "t0": t0, "workers": WORKERS}) + "\n")
    cmd = [PY, os.path.join(HERE, "cpsat_gen.py"), str(N), str(f["J"]), str(TLIM), tag, "--workers", str(WORKERS),
           "--family", fam, "--outdir", os.path.join(ROOT, "certificates", "p2")] + extra
    r = subprocess.run(cmd, capture_output=True, text=True)
    with open(LOG1, "r+b") as fh:  # keep the frozen phase-1 log byte-identical
        fh.truncate(size1)
    try:
        out = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        out = {"N": N, "n": N - 1, "status": "DRIVER_ERROR", "stderr": r.stderr[-400:], "tag": tag, "family": fam,
               "workers": WORKERS}
    out["wall_s"] = round(time.time() - t0, 1)
    out["workers"] = WORKERS
    with open(LOG2, "a") as lf:
        lf.write(json.dumps(out) + "\n")
    return out


def reap_killed() -> None:
    """Mark start entries with no row (killed by reboot/kill) with their lost wall time (to last log mtime guess)."""
    if not os.path.exists(START):
        return
    starts = [json.loads(x) for x in open(START)]
    done = {d["tag"] for d in rows(LOG2)}
    seen: set[str] = set()
    out = []
    for i, s in enumerate(starts):
        if s["tag"] not in done and "killed_s" not in s:
            nxt = starts[i + 1]["t0"] if i + 1 < len(starts) else time.time()
            s["killed_s"] = round(min(nxt - s["t0"], TLIM + 60), 1)
        out.append(s)
    with open(START, "w") as sf:
        for s in out:
            sf.write(json.dumps(s) + "\n")


def main() -> None:
    reap_killed()
    done = {d["tag"]: d for d in rows(LOG2)}
    # positive control
    if "ctl2_n63" not in done:
        d = run_one("ctl2_n63", 64, dict(J=8), "ctl2_pos",
                    ["--evmin", "4"])
        done["ctl2_n63"] = d
    c = done["ctl2_n63"]
    ok = c.get("status") in ("OPTIMAL", "FEASIBLE") and c.get("certify", {}).get("checker1") and \
        c.get("certify", {}).get("checker2")
    if not ok:
        print("CONTROL FAILED: solver-power failure; stop", flush=True)
        return
    p1_inf = {(d["family"], d["N"]) for d in rows(LOG1) if d["status"] == "INFEASIBLE"}
    plan = {}
    for fam, f in FAMS.items():
        lst = []
        for N in range(40, 96):
            if (fam, N) in p1_inf:
                continue
            rt, slots, nf = ratio(N, f)
            lst.append((rt, N, slots, nf))
        keep = sorted(x for x in lst if x[0] <= 1.0)
        plan[fam] = keep
        with open(os.path.join(ROOT, "logs", f"prune_{fam}.json"), "w") as pf:
            json.dump({"all": lst, "kept_order": keep}, pf)
        print(fam, "kept", len(keep), "of", len(lst), flush=True)
    for fam, f in FAMS.items():
        fam_spent = lambda: sum(d["wall_s"] * d["workers"] for d in rows(LOG2) if d.get("family") == fam) / 3600
        extra = ["--b", str(f["b"]), "--evmin", str(f["evmin"]), "--evp", f["evp"], "--odp", f["odp"], "--qs", f["qs"],
                 "--dmult", str(f["dmult"]), "--jstep", str(f["jstep"])]
        for rt, N, slots, nf in plan[fam]:
            tag = f"p2_{fam}_N{N}"
            if tag in {d["tag"] for d in rows(LOG2)}:
                continue
            if spent_h() >= BUDGET_H - 0.05 or fam_spent() >= f["cap_h"]:
                break
            d = run_one(tag, N, f, fam, extra)
            d["ratio"] = rt
            print(tag, d.get("status"), d.get("wall_s"), flush=True)
            if d.get("status") in ("OPTIMAL", "FEASIBLE"):
                print("COVER FOUND", tag, flush=True)
                return
    print("DONE", spent_h(), flush=True)


if __name__ == "__main__":
    main()
