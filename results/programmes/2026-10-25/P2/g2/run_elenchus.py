"""Run the Elenchus seed detector on the P2 Lean files under the pinned openai/math toolchain (Lean 4.34.1 + Mathlib).

usage: python3 run_elenchus.py OUT.json
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/scripts/certified_numerics")
import lean_pinned  # noqa: E402

FILES = [
    "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/formal_cert/Programmes/ZeroPoint/Basic.lean",
    "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/formal_cert/Programmes/ZeroPoint/Controls.lean",
]
TOOL = "/mnt/disks/disk-socrateai-local-1/SocrateAI-Scientific-Elenchus/tools/elenchus_check.py"

env = dict(os.environ, LEAN_PATH=lean_pinned.lean_path(), PATH=f"{lean_pinned.TOOLCHAIN_BIN}:{os.environ.get('PATH', '')}")
res = subprocess.run([sys.executable, "-I", TOOL, "--json", *FILES], env=env, capture_output=True, text=True, timeout=3000)
out = {"rc": res.returncode, "stdout": res.stdout, "stderr": res.stderr[-4000:]}
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(res.returncode)
print(res.stdout[-6000:])
print(res.stderr[-2000:])
