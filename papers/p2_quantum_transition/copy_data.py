"""Copy the B1 result records this paper uses into data/ and write data/MANIFEST.json (sha256 of every copied file)."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1] / "results/proposal2/2026-10-26/B1"
DST = HERE / "data"
FILES = [
    "result_numbers.json", "result.json", "TRANSITION.md",
    "data/b1a_curvature.json", "data/summary.json", "data/controls.json", "data/pimc_feasibility.json",
    "data/scha.json", "data/scha_extend.json", "data/scha_slope_control.json",
    "data/scan_a1.json", "data/scan_a0.5.json", "data/scan_a0.7.json", "data/scan_a0.8.json", "data/scan_a1.2.json",
    "data/scan_a0.3.json", "data/scan_a2.json",
]


def main() -> int:
    DST.mkdir(exist_ok=True)
    man = {}
    for f in FILES:
        s = SRC / f
        d = DST / Path(f).name
        shutil.copyfile(s, d)
        man[d.name] = {"from": str(s.relative_to(HERE.parents[1])), "sha256": hashlib.sha256(d.read_bytes()).hexdigest(), "bytes": d.stat().st_size}
    (DST / "MANIFEST.json").write_text(json.dumps(man, indent=1))
    print(len(man), "files copied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
