"""Paper-stage recompile of the H7 Lean files (same rc2 environment as run_lean.py), by the paper-writing agent.

Usage: python -I paper_stage_recompile.py
Writes recompile_paper_stage_flow.json and recompile_paper_stage_controls.json next to this script.
Each compile is capped at 1800 s. This is a rerun by another AI agent instance, not an independent human check.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
QF = "/mnt/disks/disk-socrateai-local-1/leanmaster/qf-lake"
TC = "/home/callensxavier_gmail_com/.elan/toolchains/leanprover--lean4---v4.34.0-rc2"
PKGS = ["mathlib", "batteries", "Qq", "aesop", "proofwidgets", "importGraph",
        "LeanSearchClient", "plausible", "Cli"]


def compile_one(src: Path, out: Path) -> int:
    roots = [QF + "/build/lib/lean"] + [QF + "/packages/" + p + "/.lake/build/lib/lean" for p in PKGS]
    roots.append(TC + "/lib/lean")
    env = dict(os.environ)
    env["LEAN_PATH"] = ":".join(roots)
    env.pop("LEAN_SRC_PATH", None)
    sha = hashlib.sha256(src.read_bytes()).hexdigest()
    t0 = time.time()
    try:
        p = subprocess.run([TC + "/bin/lean", str(src)], env=env, capture_output=True, text=True, timeout=1800)
        rc, so, se = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        rc, so, se = -999, "", "TIMEOUT after 1800 s"
    rec = {"file": str(src), "sha256": sha, "rc": rc, "seconds": round(time.time() - t0, 1),
           "stdout": so, "stderr": se, "lean": TC + "/bin/lean", "LEAN_PATH": roots,
           "who": "paper-stage agent (Claude), not the stage-1 producer process; not an independent human check"}
    out.write_text(json.dumps(rec, indent=1))
    print(src.name, "rc", rc, "seconds", rec["seconds"])
    return rc


def main() -> int:
    a = compile_one(HERE / "Autoresearch_EnstrophyFlow.lean", HERE / "recompile_paper_stage_flow.json")
    b = compile_one(HERE / "Autoresearch_EnstrophyFlowControls.lean", HERE / "recompile_paper_stage_controls.json")
    return 0 if a == 0 and b == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
