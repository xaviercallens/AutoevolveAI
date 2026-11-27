#!/usr/bin/env python3
"""Compare emptiness of I(k,p,k+1) from the naive direct_I.py scan with lr_sieve's positive-control runs."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CASES = [(4, p) for p in (7, 11, 13, 17, 19, 23, 29)] + [(5, p) for p in (7, 11, 13)] + [(3, p) for p in (5, 7, 11, 13)]


def main() -> int:
    rows, bad = [], 0
    for k, p in CASES:
        out = subprocess.run([sys.executable, str(HERE / "direct_I.py"), str(k), str(p), str(k + 1)],
                             capture_output=True, text=True, check=True).stdout
        d = json.loads(out)
        s = json.loads((ROOT / "data" / "controls_pos" / f"k{k}_p{p}.json").read_text())
        ok = (d["improper_multisets"] == 0) == (s["final_classes"] == 0)
        bad += not ok
        rows.append({"k": k, "p": p, "direct_improper_multisets": d["improper_multisets"],
                     "sieve_final_classes": s["final_classes"], "agree": ok})
        print(rows[-1], flush=True)
    (ROOT / "logs" / "direct_vs_sieve.json").write_text(json.dumps(rows, indent=1) + "\n")
    print("disagreements", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
