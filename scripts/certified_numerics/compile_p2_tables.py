#!/usr/bin/env python3
"""Compile the P2 table modules (slab edges + FitFine) in parallel under the pinned toolchain.

Each module's compile record goes to results/certified_numerics/P2_likelihood/compile_T_<name>.json.
Already compiled modules (record with rc 0 and olean present) are skipped.
"""

from __future__ import annotations

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RES = REPO / "results" / "certified_numerics" / "P2_likelihood"
OUT = REPO / "formal_cert" / ".olean_out" / "BAOCert" / "P2"


def job(name: str) -> tuple[str, int]:
    rec = RES / f"compile_T_{name}.json"
    if rec.exists() and json.loads(rec.read_text())["rc"] == 0 and (OUT / f"T_{name}.olean").exists():
        return name, 0
    r = subprocess.run([sys.executable, str(REPO / "scripts/certified_numerics/lean_pinned.py"), "compile",
                        str(REPO / f"formal_cert/BAOCert/P2/T_{name}.lean"), "--olean", f"BAOCert.P2.T_{name}",
                        "--json-out", str(rec), "--timeout", "7200"], capture_output=True, text=True)
    return name, r.returncode


def main() -> int:
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    names = [e[0] for e in json.loads((REPO / "scripts/certified_numerics/p2_edges.json").read_text())["edges"]] + ["FitFine"]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for name, rc in ex.map(job, names):
            print(name, "rc", rc, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
