"""Replay the E3 modules with leanchecker (pinned toolchain), same LEAN_PATH as lean_pinned.py. Run from repo root."""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, "scripts/certified_numerics")
import lean_pinned as L  # noqa: E402

env = dict(os.environ, LEAN_PATH=L.lean_path(), PATH=f"{L.TOOLCHAIN_BIN}:{os.environ.get('PATH', '')}")
res = []
for mod in sys.argv[1:]:
    t0 = time.time()
    r = subprocess.run([str(L.TOOLCHAIN_BIN / "leanchecker"), mod], env=env, capture_output=True, text=True, timeout=3000)
    res.append({"cmd": "leanchecker " + mod, "rc": r.returncode, "seconds": round(time.time() - t0, 1),
                "stdout": r.stdout[-2000:], "stderr": r.stderr[-2000:]})
json.dump(res, open("results/proposal4/2026-10-27/E3/logs/leanchecker_replay.json", "w"), indent=1)
print(json.dumps(res)[:1500])
