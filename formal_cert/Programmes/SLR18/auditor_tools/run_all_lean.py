#!/usr/bin/env python3
"""Generate and compile the Lean covering proof for every certificate n=5..38 (sequential, one process)."""
from __future__ import annotations

import json
import subprocess
import sys

REPO = "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery"
CERTS = REPO + "/results/proposal5/2026-10-27/SLR18/certificates"
OUT = "/tmp/slraudit/final"


def main() -> None:
    summary = []
    for n in range(5, 39):
        name = f"N{n:02d}"
        lean = f"{OUT}/SLR{name}.lean"
        with open(lean, "w") as fh:
            subprocess.run(["python3", "-I", "/tmp/slraudit/gen_lean.py", f"{CERTS}/cert_n{n:03d}.json", name],
                           stdout=fh, stderr=subprocess.DEVNULL, check=True)
        src = open(lean).read()
        banned = any(w in src for w in ("sorry", "admit", "native_decide", "\naxiom "))
        res = subprocess.run(["python3", REPO + "/scripts/certified_numerics/lean_pinned.py", "compile", lean,
                              "--timeout", "3600", "--json-out", f"{OUT}/lean_{name}.json"],
                             cwd=REPO, capture_output=True, text=True)
        out = res.stdout
        axl = [l for l in out.splitlines() if "depends on axioms" in l or "does not depend" in l]
        head = json.loads(out.splitlines()[0])
        row = {"n": n, "rc": head["rc"], "seconds": head["seconds"], "banned_tokens": banned, "axioms": axl}
        summary.append(row)
        print(json.dumps(row), flush=True)
    json.dump(summary, open(f"{OUT}/lean_all_summary.json", "w"), indent=1)


if __name__ == "__main__":
    sys.exit(main())
