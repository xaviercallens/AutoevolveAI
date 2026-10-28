"""M1 kernel replay (producer-run) and forbidden-pattern grep.

leanchecker MODULE from the pinned Lean 4.34.1 toolchain with the LEAN_PATH of scripts/certified_numerics/lean_pinned.py
(as results/kernel_replay_2026-10-26/scripts/kr_run.py), run from /tmp; default mode (imports trusted).
usage: python -I m1_replay.py REPO M1_DIR
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time


def main() -> None:
    repo, m1 = sys.argv[1], sys.argv[2]
    sys.path.insert(0, os.path.join(repo, "scripts", "certified_numerics"))
    import lean_pinned as LP  # noqa: E402

    env = dict(os.environ, LEAN_PATH=LP.lean_path(), PATH=f"{LP.TOOLCHAIN_BIN}:{os.environ.get('PATH', '')}")
    rows = []
    for mod in ("Programmes.ZeroPointDipolar.Basic",):
        olean = os.path.join(str(LP.OUT), mod.replace(".", "/") + ".olean")
        src = os.path.join(repo, "formal_cert", mod.replace(".", "/") + ".lean")
        t0 = time.time()
        p = subprocess.run([str(LP.TOOLCHAIN_BIN / "leanchecker"), mod], env=env, capture_output=True, text=True,
                           timeout=3600, cwd="/tmp")
        rows.append({"module": mod, "rc": p.returncode, "seconds": round(time.time() - t0, 1),
                     "output": (p.stdout + p.stderr)[-4000:],
                     "olean_fresh": os.path.getmtime(olean) >= os.path.getmtime(src)})
    with open(os.path.join(m1, "replay.json"), "w") as fh:
        json.dump(rows, fh, indent=1)
    pat = re.compile(r"skipKernelTC|addDecl|native_decide|implemented_by|implementedBy")
    hits = []
    d = os.path.join(repo, "formal_cert", "Programmes", "ZeroPointDipolar")
    for n in sorted(os.listdir(d)):
        if n.endswith(".lean"):
            for i, line in enumerate(open(os.path.join(d, n)), 1):
                if pat.search(line):
                    hits.append({"file": n, "line": i, "text": line.rstrip()})
    with open(os.path.join(m1, "grep.json"), "w") as fh:
        json.dump({"pattern": pat.pattern, "files": sorted(x for x in os.listdir(d) if x.endswith(".lean")),
                   "hits": hits}, fh, indent=1)
    print(json.dumps(rows, indent=1))
    print("grep hits", hits)


if __name__ == "__main__":
    main()
