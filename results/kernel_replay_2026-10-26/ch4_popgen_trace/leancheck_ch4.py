"""Kernel replay (leanchecker) of the population-genetics modules quoted in chapter 4.

Run from anywhere: python3 -I leancheck_ch4.py. Pins itself to cores 0,1.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
PINNED = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/openai_math_pinned/lean")
BIN = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/elan/toolchains/leanprover--lean4---v4.34.1/bin")
OUT = REPO / "formal_cert" / ".olean_out"
MODULES = [
    "Autoresearch.PopGenFisher",
    "Autoresearch.PopGenWrightFisher",
    "Programmes.PopGen.Absorption",
    "Programmes.PopGen.WrightFisherFixation",
    "Programmes.PopGen.MoranModel",
    "Programmes.PopGen.MoranFixation",
    "Programmes.PopGen.Price",
    "Programmes.EvoGraph.Transport",
    "Programmes.EvoGraph.BirthDeath",
    "Programmes.EvoGraph.Examples",
]


def main() -> int:
    os.sched_setaffinity(0, {0, 1})
    env = dict(os.environ, PATH=f"{BIN}:{os.environ.get('PATH', '')}")
    lp = subprocess.run(["lake", "env", "printenv", "LEAN_PATH"], cwd=PINNED, env=env,
                        capture_output=True, text=True, check=True).stdout.strip()
    env["LEAN_PATH"] = f"{lp}:{OUT}"
    results = []
    for m in MODULES:
        t0 = time.time()
        res = subprocess.run([str(BIN / "leanchecker"), m], env=env, capture_output=True, text=True)
        results.append({"module": m, "rc": res.returncode, "seconds": round(time.time() - t0, 1),
                        "stdout": res.stdout[-400:], "stderr": res.stderr[-400:]})
        print(m, res.returncode, round(time.time() - t0, 1), flush=True)
    Path(sys.argv[1]).write_text(json.dumps(results, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
