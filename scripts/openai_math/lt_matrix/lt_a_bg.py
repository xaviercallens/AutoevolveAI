#!/usr/bin/env python3
"""Lane LT_A background queue: runs frozen campaign.py jobs, <=2 concurrent, --threads 2 each, fresh seed blocks from the ledger.

usage: lt_a_bg.py name:gamma:family:K:P:restarts[:budget_s] ...   (jobs start in order as slots free up)
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lt_a_driver import LANE, alloc_seed, controls_ok  # noqa: E402


def launch(job: str) -> tuple[str, subprocess.Popen]:
    f = job.split(":")
    name, g, fam, K, P, n = f[:6]
    budget = f[6] if len(f) > 6 else "2400"
    k = 0
    while (LANE / "cells" / f"{name}_c{k:02d}.json").exists():
        k += 1
    out = LANE / "cells" / f"{name}_c{k:02d}.json"
    seed0 = alloc_seed(out.stem)
    M = "320" if abs(float(g) - 0.75) < 1e-9 else "160"
    cmd = [sys.executable, str(HERE / "campaign.py"), "--gamma", g, "--m", "2", "--family", fam, "--K", K, "--P", P,
           "--seed0", str(seed0), "--restarts", n, "--budget-s", budget, "--M", M, "--threads", "2", "--out", str(out)]
    log = open(LANE / "cells" / f"{out.stem}.log", "w")
    print(time.strftime("%H:%M:%S"), "start", out.stem, flush=True)
    return out.stem, subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)


def main(jobs: list[str]) -> int:
    if not controls_ok():
        print("VOID: controls not all_pass")
        return 3
    running: list[tuple[str, subprocess.Popen]] = []
    queue = list(jobs)
    while queue or running:
        running = [(n, p) for n, p in running if p.poll() is None or print(time.strftime("%H:%M:%S"), "done", n, p.returncode, flush=True)]
        while queue and len(running) < 2:
            running.append(launch(queue.pop(0)))
        time.sleep(5)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
