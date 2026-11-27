#!/usr/bin/env python3
"""Compile the P2 case modules (fit point, C6 tampered data, EdS, preregistered slabs, A2 refined slabs) in parallel.

Requires the table modules (compile_p2_tables.py). Records go to results/certified_numerics/P2_likelihood/compile_<Module>.json.
"""

from __future__ import annotations

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RES = REPO / "results" / "certified_numerics" / "P2_likelihood"
LEAN = REPO / "formal_cert" / "BAOCert" / "P2"


def job(mod: str) -> tuple[str, int, float]:
    rec = RES / f"compile_{mod}.json"
    r = subprocess.run([sys.executable, str(REPO / "scripts/certified_numerics/lean_pinned.py"), "compile", str(LEAN / f"{mod}.lean"),
                        "--olean", f"BAOCert.P2.{mod}", "--json-out", str(rec), "--timeout", "7200"], capture_output=True, text=True)
    sec = json.loads(rec.read_text())["seconds"] if rec.exists() else -1
    return mod, r.returncode, sec


def main() -> int:
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    first = ["Data_Tamper"]
    mods = ["Fit", "Fit_Tamper"]
    mods += [s["name"] for s in json.loads((RES / "slabs_plan.json").read_text()) if s["A_lo_positive"]]
    mods += [s["name"] for s in json.loads((RES / "refine_plan.json").read_text())["leaves"] if s["excluded"]]
    mods = [m for m in dict.fromkeys(mods) if (LEAN / f"{m}.lean").exists()]
    for m in first:
        print(*job(m), flush=True)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for res in ex.map(job, mods):
            print(*res, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
