#!/usr/bin/env python3
"""LR-IND driver: runs the job queue for one core (2 or 3), one JSON file per job under data/, resumable.

Usage: python3 driver.py <lane>   (lane 'A' runs on core 2, lane 'B' on core 3)
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
SIEVE = str(HERE / "lr_sieve")
FIBER = str(HERE / "fiber_check")


def primes(lo: int, hi: int) -> list[int]:
    return [p for p in range(max(lo, 2), hi + 1) if all(p % q for q in range(2, int(p ** 0.5) + 1))]


P10 = primes(127, 467)


def jobs(lane: str) -> list[tuple[str, list[str], str]]:
    out: list[tuple[str, list[str], str]] = []
    if lane == "A":
        # positive controls: printed per-prime verdict patterns (Rosenfeld 2509.14111, Trakulthongchai 2511.22427)
        for k, plan, lo, hi in [(3, "4", 5, 103), (4, "5", 7, 103), (5, "2,3", 7, 103), (6, "7", 11, 103),
                                (7, "2,2,2", 11, 163), (8, "3,3", 11, 241)]:
            for p in primes(lo, hi):
                if p <= k:
                    continue
                out.append((f"controls_pos/k{k}_p{p}.json", [SIEVE, str(k), str(p), plan, "0", "1", "1"], "sieve"))
        # negative control 1: planted wrong witness rules
        for k, p, plan in [(7, 31, "2,2,2"), (8, 47, "3,3"), (8, 53, "3,3"), (10, 127, "2,2,2,/"), (10, 131, "2,2,2,/")]:
            for mut in (0, 1, 2):
                out.append((f"controls_neg/k{k}_p{p}_mut{mut}.json", [SIEVE, str(k), str(p), plan, str(mut), "1", "1"], "sieve"))
        # negative control 2 (fiber program): L with 11 not dividing L*p must leave (1..10) improper
        for p in (127, 467):
            for L in (5, 7):
                out.append((f"controls_neg/fiber_k10_p{p}_L{L}.json", [FIBER, "10", str(p), str(L)], "fiber"))
        # direct check of the Prop 4.4 conclusion at every p in P_10 (removes the dependence on Prop 1.4)
        for p in P10:
            out.append((f"k10_fiber11/p{p}.json", [FIBER, "10", str(p), "11"], "fiber"))
        # LRC(9) premise re-run over Trakulthongchai's S_9 (optional, last)
        for p in primes(137, 401):
            out.append((f"k9_S9/p{p}.json", [SIEVE, "9", str(p), "2,5", "0", "1", "1"], "sieve"))
    else:
        for p in P10:
            out.append((f"k10_main/p{p}.json", [SIEVE, "10", str(p), "2,2,2,/", "0", "1", "1"], "sieve"))
        # second pass, phase 1 without the canonical-support pruning: per-prime hash agreement and counts in
        # the paper's own representative convention (1 = v1 <= ... <= vk <= (p-1)/2)
        for p in P10:
            out.append((f"k10_nocanon/p{p}.json", [SIEVE, "10", str(p), "2,2,2,/", "0", "1", "0"], "sieve"))
    return out


def main() -> int:
    lane = sys.argv[1]
    core = "2" if lane == "A" else "3"
    log = open(ROOT / "logs" / f"driver_{lane}.log", "a")
    for rel, cmd, kind in jobs(lane):
        dst = DATA / rel
        if dst.exists() and dst.stat().st_size > 0:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        t0 = time.time()
        res = subprocess.run(["taskset", "-c", core] + cmd, capture_output=True, text=True)
        dt = time.time() - t0
        if res.returncode != 0:
            log.write(f"{time.strftime('%H:%M:%S')} FAIL rc={res.returncode} {rel} {res.stderr.strip()}\n")
            log.flush()
            continue
        json.loads(res.stdout)
        tmp = dst.with_suffix(".tmp")
        tmp.write_text(res.stdout)
        tmp.rename(dst)
        log.write(f"{time.strftime('%H:%M:%S')} ok {rel} {dt:.1f}s\n")
        log.flush()
    log.write(f"{time.strftime('%H:%M:%S')} lane {lane} done\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
