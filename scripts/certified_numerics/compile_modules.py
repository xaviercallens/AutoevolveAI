#!/usr/bin/env python3
"""Compile Lean modules of formal_cert/ in parallel under the pinned toolchain.

Usage: python3 scripts/certified_numerics/compile_modules.py <records_dir> <workers> <Module.Name> [<Module.Name> ...]
       python3 scripts/certified_numerics/compile_modules.py <records_dir> <workers> --glob BAOCert/P3/Box_*.lean
Each record goes to <records_dir>/compile_<last component>.json; modules with an existing rc-0 record and olean are skipped.
"""

from __future__ import annotations

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FC = REPO / "formal_cert"
OUT = FC / ".olean_out"


def job(args: tuple[Path, str]) -> tuple[str, int, float]:
    recdir, mod = args
    rec = recdir / f"compile_{mod.split('.')[-1]}.json"
    olean = OUT / (mod.replace(".", "/") + ".olean")
    if rec.exists() and json.loads(rec.read_text())["rc"] == 0 and olean.exists():
        return mod, 0, json.loads(rec.read_text())["seconds"]
    subprocess.run([sys.executable, str(REPO / "scripts/certified_numerics/lean_pinned.py"), "compile",
                    str(FC / (mod.replace(".", "/") + ".lean")), "--olean", mod, "--json-out", str(rec), "--timeout", "7200"],
                   capture_output=True, text=True)
    r = json.loads(rec.read_text()) if rec.exists() else {"rc": -1, "seconds": -1}
    return mod, r["rc"], r["seconds"]


def main() -> int:
    recdir = Path(sys.argv[1]).resolve()
    recdir.mkdir(parents=True, exist_ok=True)
    workers = int(sys.argv[2])
    if sys.argv[3] == "--glob":
        mods = sorted(str(p.relative_to(FC).with_suffix("")).replace("/", ".") for p in FC.glob(sys.argv[4]))
    else:
        mods = sys.argv[3:]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for mod, rc, sec in ex.map(job, [(recdir, m) for m in mods]):
            print(mod, rc, sec, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
