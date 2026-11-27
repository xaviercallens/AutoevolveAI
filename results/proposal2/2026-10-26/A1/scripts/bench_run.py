"""Time + max-RSS of compiling each benchmark file with the pinned Lean (cores 4,5). Writes bench_results.json.
Usage: bench_run.py OUTJSON FILE...
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]


def main(argv: list[str]) -> int:
    out = Path(argv[0])
    rows = []
    for f in argv[1:]:
        cmd = ["/usr/bin/time", "-v", "taskset", "-c", "4,5", "python3", str(REPO / "scripts/certified_numerics/lean_pinned.py"),
               "compile", f, "--timeout", "2700"]
        t0 = time.time()
        res = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
        wall = time.time() - t0
        m = re.search(r"Maximum resident set size \(kbytes\): (\d+)", res.stderr)
        first = res.stdout.splitlines()[0] if res.stdout else ""
        rows.append({"file": f, "wall_s": round(wall, 1), "lean_report": first, "max_rss_kb": int(m.group(1)) if m else None,
                     "rc": res.returncode, "tail": res.stdout[-800:]})
        print(json.dumps(rows[-1]), flush=True)
        out.write_text(json.dumps(rows, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
