"""Re-run, for a sample of the auditor's SLR Lean files, the pinned compile with olean, `#print axioms` via the
repo file-mode gate anse/formal/lean_runner.py (lean_cmd pointed at the pinned Lean 4.34.1 + Mathlib d13f23b7, as E1 did),
and leanchecker on the olean. Usage: python3 -I lean_gate_sample.py N18 N38. Logs go to ../logs/lean_gate/."""
from __future__ import annotations

import dataclasses
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts" / "certified_numerics"))
from anse.formal.lean_runner import LeanKernelVerifier  # noqa: E402
import lean_pinned  # noqa: E402

OUTDIR = Path(__file__).resolve().parent.parent / "logs" / "lean_gate"


def run_one(name: str) -> dict[str, object]:
    src = REPO / "formal_cert" / "Programmes" / "SLR18" / f"SLR{name}.lean"
    module = f"Programmes.SLR18.SLR{name}"
    comp = lean_pinned.compile_file(src, module, 3600)
    cmd = ["/usr/bin/env", f"LEAN_PATH={lean_pinned.lean_path()}", str(lean_pinned.TOOLCHAIN_BIN / "lean"), "-DautoImplicit=false"]
    runner = LeanKernelVerifier(formal_dir=lean_pinned.PINNED, lean_cmd=cmd)
    rows = [dataclasses.asdict(r) for r in runner.verify_file(src, timeout_s=3600.0)]
    env = dict(os.environ, LEAN_PATH=lean_pinned.lean_path(), PATH=f"{lean_pinned.TOOLCHAIN_BIN}:{os.environ.get('PATH', '')}")
    chk = subprocess.run([str(lean_pinned.TOOLCHAIN_BIN / "leanchecker"), module], env=env, capture_output=True, text=True, timeout=3600)
    return {"name": name, "compile": {k: comp[k] for k in ("module", "rc", "seconds", "output")},
            "lean_runner_verify_file": rows, "leanchecker": {"module": module, "rc": chk.returncode, "output": (chk.stdout + chk.stderr)[-2000:]}}


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:]:
        res = run_one(name)
        (OUTDIR / f"gate_{name}.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
        print(name, res["compile"]["rc"], [(r["theorem_name"], r["axioms"], r["compiled_successfully"]) for r in res["lean_runner_verify_file"]], res["leanchecker"]["rc"], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
