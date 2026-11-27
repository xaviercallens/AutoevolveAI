"""Replay Programmes.CarbonateK2.Core with leanchecker (pinned toolchain), same LEAN_PATH as lean_pinned.py."""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, "scripts/certified_numerics")
import lean_pinned as L  # noqa: E402

env = dict(os.environ, LEAN_PATH=L.lean_path(), PATH=f"{L.TOOLCHAIN_BIN}:{os.environ.get('PATH', '')}")
t0 = time.time()
r = subprocess.run([str(L.TOOLCHAIN_BIN / "leanchecker"), "Programmes.CarbonateK2.Core"], env=env, capture_output=True, text=True, timeout=3000)
out = {"cmd": "leanchecker Programmes.CarbonateK2.Core", "rc": r.returncode, "seconds": round(time.time() - t0, 1),
       "stdout": r.stdout[-2000:], "stderr": r.stderr[-2000:]}
json.dump(out, open("results/proposal4/2026-10-27/K2/logs/leanchecker_replay.json", "w"), indent=1)
print(json.dumps(out)[:800])
