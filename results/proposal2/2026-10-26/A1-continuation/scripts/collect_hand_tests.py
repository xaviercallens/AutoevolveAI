"""Collect the hand-test compile measurements (rc, wall, peak RSS, axioms lines) from the test roots into
hand_tests.json. The machine load during these tests was high (load average 15-17 on 8 cores), so the times are
upper-end measurements."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from l1common import CONT  # noqa: E402

T = Path("/home/callensxavier_gmail_com/a1l1_oleans/test")


def main() -> int:
    out = {}
    files = list(T.glob("*.json")) + list(T.glob("*/Programmes.*.json"))
    for f in sorted(files):
        try:
            r = json.loads(f.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if "module" not in r:
            continue
        o = str(r.get("output", ""))
        out[r["module"] + " @" + f.parent.name] = {
            "rc": r.get("rc"), "wall_s": r.get("wall_s"), "peak_rss_gb": round((r.get("peak_rss_kb") or 0) / 1048576, 2),
            "axioms": re.findall(r"'[^']+' (?:does not depend on any axioms|depends on axioms: \[[^\]]*\])", o)[:6],
            "errors": len(re.findall(r"error:", o)),
        }
    (CONT / "hand_tests.json").write_text(json.dumps(out, indent=1) + "\n")
    print(len(out), "entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
