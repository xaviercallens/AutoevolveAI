#!/usr/bin/env python3
"""Run the chunk list of one worker sequentially (skips chunks whose JSON exists). Usage: run_worker.py WORKER NWORKERS"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "data" / "chunks"
MODES = ["PSI", "R", "PLANT4", "HF_R", "HF_PSI"]
STEP = 1024
N_F0 = 2**15


def chunk_list() -> list[tuple[str, int, int]]:
    return [(m, lo, lo + STEP) for m in MODES for lo in range(0, N_F0, STEP)]


def main() -> int:
    worker, nworkers = int(sys.argv[1]), int(sys.argv[2])
    for i, (mode, lo, hi) in enumerate(chunk_list()):
        if i % nworkers != worker:
            continue
        path = OUT / f"{mode}_{lo:05d}_{hi:05d}.json"
        if path.exists():
            continue
        tmp = path.with_suffix(".tmp")
        subprocess.run([sys.executable, str(HERE / "psi_exhaust.py"), "chunk", mode, str(lo), str(hi), str(tmp)], check=True)
        tmp.rename(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
