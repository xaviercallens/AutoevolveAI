"""Kernel replay of the compiled C1 Lean modules with the pinned toolchain's leanchecker.
Usage: leanchecker_replay.py <Module.Name> [<Module.Name> ...]"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "scripts" / "certified_numerics"))
import lean_pinned as lp  # noqa: E402


def main() -> int:
    env = dict(os.environ, LEAN_PATH=lp.lean_path(), PATH=f"{lp.TOOLCHAIN_BIN}:{os.environ.get('PATH', '')}")
    rc_all = 0
    out = []
    for mod in sys.argv[1:]:
        res = subprocess.run([str(lp.TOOLCHAIN_BIN / "leanchecker"), mod], env=env, capture_output=True, text=True, timeout=3000)
        out.append({"module": mod, "rc": res.returncode, "stdout": res.stdout[-3000:], "stderr": res.stderr[-3000:]})
        rc_all |= res.returncode
    print(json.dumps(out, indent=1))
    return rc_all


if __name__ == "__main__":
    sys.exit(main())
