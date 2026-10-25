"""Write the pinned LEAN_PATH to lean_path.txt, then warm the import closure of Autoresearch.KeldyshCM (paper stage)."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINNED = "/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/openai_math_pinned/lean"
BIN = "/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/elan/toolchains/leanprover--lean4---v4.34.1/bin"
OUT = "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/formal_cert/.olean_out"


def main() -> None:
    env = dict(os.environ, PATH=BIN + ":" + os.environ.get("PATH", ""))
    lp = subprocess.run(["lake", "env", "printenv", "LEAN_PATH"], cwd=PINNED, env=env, capture_output=True,
                        text=True, check=True).stdout.strip() + ":" + OUT
    (HERE / "lean_path.txt").write_text(lp)
    r = subprocess.run(["python3", "-I", str(HERE / "warm_closure.py"), str(HERE / "lean_path.txt"),
                        "OAI.Analysis.Triangular.Energy.Universal", "Mathlib.MeasureTheory.Integral.DominatedConvergence", "Mathlib.Analysis.SpecialFunctions.Gaussian.GaussianIntegral"], capture_output=True, text=True)
    print(r.stdout, r.stderr[-2000:])


if __name__ == "__main__":
    main()
