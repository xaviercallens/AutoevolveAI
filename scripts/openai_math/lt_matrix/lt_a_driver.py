#!/usr/bin/env python3
"""Lane LT_A driver (2026-10-08): runs frozen campaign.py chunks, at most two concurrent subprocesses, never reuses seeds.

Subcommands
  chunk  --jobs name:gamma:family:K:P:restarts [name:...]   (<=2 jobs; one chunk = one call, budget-s <= 420)
  aggregate                                                 per-cell summary + verdict -> cell_summary.json
  recheck                                                   third grid (L=32, M=256) on stored params of flagged restarts
Does not modify instrument.py / campaign.py / controls.py.  Refuses to run chunks unless <lane>/controls.json has all_pass.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LANE = HERE.parents[2] / "results/openai_math/hypotheses/night_2026-10-08/LT_A"
SEED_START, SEED_BLOCK = 1000, 40


def controls_ok() -> bool:
    p = LANE / "controls.json"
    return p.exists() and json.loads(p.read_text()).get("all_pass") is True


def alloc_seed(name: str) -> int:
    """Append-only ledger; each chunk gets a fresh block of SEED_BLOCK seeds starting at 1000."""
    led = LANE / "seed_ledger.json"
    data = json.loads(led.read_text()) if led.exists() else {"next": SEED_START, "blocks": []}
    s = data["next"]
    data["blocks"].append({"start": s, "end": s + SEED_BLOCK - 1, "name": name})
    data["next"] = s + SEED_BLOCK
    led.write_text(json.dumps(data, indent=1) + "\n")
    return s


def chunk(jobs: list[str], budget: float) -> int:
    if not controls_ok():
        print("VOID: lane controls.json missing or not all_pass; refusing to run cells")
        return 3
    if len(jobs) > 2:
        print("at most 2 concurrent campaign processes")
        return 2
    procs = []
    for j in jobs:
        name, g, fam, K, P, n = j.split(":")
        k = 0
        while (LANE / "cells" / f"{name}_c{k:02d}.json").exists():
            k += 1
        out = LANE / "cells" / f"{name}_c{k:02d}.json"
        seed0 = alloc_seed(out.stem)
        M = 320 if abs(float(g) - 0.75) < 1e-9 else 160
        b = min(budget, 360.0) if M == 320 else min(budget, 420.0)
        cmd = [sys.executable, str(HERE / "campaign.py"), "--gamma", g, "--m", "2", "--family", fam, "--K", K, "--P", P,
               "--seed0", str(seed0), "--restarts", n, "--budget-s", str(b), "--M", str(M), "--threads", "2", "--out", str(out)]
        procs.append((out, subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)))
    t0 = time.time()
    for out, p in procs:
        try:
            txt, _ = p.communicate(timeout=max(10.0, 520.0 - (time.time() - t0)))
        except subprocess.TimeoutExpired:
            p.kill()
            txt, _ = p.communicate()
            txt += "\nKILLED_AT_TIMEOUT (no result json)"
        print(out.name, p.returncode, txt.strip()[-600:])
    return 0


def parse_name(stem: str) -> str:
    return stem.rsplit("_c", 1)[0]


def aggregate() -> int:
    cells: dict[str, dict] = {}
    for f in sorted((LANE / "cells").glob("*_c[0-9][0-9].json")):
        d = json.loads(f.read_text())
        c = cells.setdefault(parse_name(f.stem), {
            "gamma": d["gamma"], "family": d["family"], "K": d["K"], "P": d["P"], "M": d["grid"]["M"], "L1": d["L1"],
            "restarts": 0, "flagged": 0, "best_excess": -math.inf, "best_seed": None, "chunks": [], "cert": 0,
            "undecided": 0, "seconds": 0.0})
        c["restarts"] += d["restarts_done"]
        c["flagged"] += d["n_flagged_above_1e-7"]
        c["seconds"] += d["elapsed_s"]
        c["chunks"].append(f.stem)
        for r in d["rows"]:
            if r["excess"] > c["best_excess"]:
                c["best_excess"], c["best_seed"], c["best_chunk"] = r["excess"], r["seed"], f.stem
            if "refinement" in r:
                rf = r["refinement"]
                e_ref, e_fd = rf["R_refined_grid"] / d["L1"] - 1, rf["R_fd_richardson"] / d["L1"] - 1
                if e_ref > 1e-5 and e_fd > 5e-6:
                    c["cert"] += 1
                else:
                    c["undecided"] += 1
    for c in cells.values():
        c["verdict"] = "VIOLATION_CERTIFIED" if c["cert"] else "UNDECIDED" if c["flagged"] else "NO_VIOLATION_FOUND"
        c["closeness_below_L1"] = -c["best_excess"]
    (LANE / "cell_summary.json").write_text(json.dumps(cells, indent=1) + "\n")
    for n, c in sorted(cells.items(), key=lambda kv: -kv[1]["best_excess"]):
        print(f"{n:34s} best_excess={c['best_excess']:+.3e} restarts={c['restarts']:3d} flagged={c['flagged']} {c['verdict']}")
    return 0


def recheck() -> int:
    import torch
    sys.path.insert(0, str(HERE))
    from instrument import Blobs, Grid, ratio, sharp_constant
    torch.set_num_threads(2)
    out = []
    for f in sorted((LANE / "cells").glob("*_c[0-9][0-9].json")):
        d = json.loads(f.read_text())
        for r in d["rows"]:
            if "refinement" not in r:
                continue
            pt = f.with_suffix(f".best_seed{r['seed']}.pt")
            if not pt.exists():
                out.append({"cell": f.stem, "seed": r["seed"], "status": "NO_STORED_PARAMS"})
                continue
            mdl = Blobs(d["m"], d["K"], d["P"], r["seed"])
            mdl.load_state_dict(torch.load(pt))
            g3 = Grid(32.0, 256, 3200)
            L1 = sharp_constant(d["gamma"])
            with torch.no_grad():
                r3 = ratio(mdl.W(g3.x), d["gamma"], g3)
            rf = r["refinement"]
            out.append({"cell": f.stem, "seed": r["seed"], "excess_base": r["excess"],
                        "excess_refined": rf["R_refined_grid"] / L1 - 1, "excess_fd": rf["R_fd_richardson"] / L1 - 1,
                        "excess_grid3_L32_M256": r3 / L1 - 1})
    (LANE / "recheck_grid3.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["chunk", "aggregate", "recheck"])
    ap.add_argument("--jobs", nargs="*", default=[])
    ap.add_argument("--budget-s", type=float, default=420.0)
    a = ap.parse_args()
    raise SystemExit(chunk(a.jobs, a.budget_s) if a.cmd == "chunk" else aggregate() if a.cmd == "aggregate" else recheck())
