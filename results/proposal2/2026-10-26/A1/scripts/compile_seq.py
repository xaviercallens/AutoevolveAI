"""Compile a sequence of Lean files with the pinned toolchain (cores 4,5), one JSON log each; stop at first failure
unless --keep-going. Usage: compile_seq.py [--keep-going] FILE[:Module.Name] ...
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
LOGS = REPO / "results/proposal2/2026-10-26/A1/logs"


def main(argv: list[str]) -> int:
    keep = "--keep-going" in argv
    items = [a for a in argv if a != "--keep-going"]
    LOGS.mkdir(parents=True, exist_ok=True)
    status = 0
    for item in items:
        path, _, module = item.partition(":")
        stem = Path(path).stem
        out = LOGS / f"compile_{stem}.json"
        cmd = ["taskset", "-c", "4,5", "python3", str(REPO / "scripts/certified_numerics/lean_pinned.py"), "compile",
               str(REPO / path), "--json-out", str(out), "--timeout", "2700"]
        if module:
            cmd += ["--olean", module]
        rc = subprocess.run(cmd, cwd=REPO).returncode
        res = json.loads(out.read_text())
        print(json.dumps({"file": path, "rc": res["rc"], "seconds": res["seconds"]}), flush=True)
        if rc != 0:
            status = 1
            if not keep:
                break
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
