"""Largest distance |tau - rho| of any dynamically stable n=96 shape over the 12 completely monotone potentials.

Reads the G1 scan CSVs committed in the rusty branch (crates/qf-yukawa-crystal/results/phonon_gate/data/*__*.csv) and writes
data/max_stable_dist.json, which gen_inputs.py reads to fill \\ZPMaxStableDist (it was hard-coded as 0.23 before the audit).
Usage: python -I max_stable_dist.py RUSTY_DATA_DIR
"""
from __future__ import annotations

import csv
import glob
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CM = ["dipolar_0.1", "dipolar_0.5", "gauss_0.25", "gauss_0.5", "gauss_1", "gauss_2", "gauss_4", "riesz_3", "riesz_4", "riesz_6", "yukawa_1", "yukawa_2"]


def main() -> int:
    d = Path(sys.argv[1])
    rho = complex(0.5, math.sqrt(3) / 2)
    best: dict[str, float] = {}
    files: list[str] = []
    for f in sorted(glob.glob(str(d / "*__*.csv"))):
        pot = Path(f).name.split("__")[0]
        if pot not in CM:
            continue
        files.append(Path(f).name)
        with open(f) as fh:
            for r in csv.DictReader(fh):
                if int(r["n"]) != 96 or r["e_zp"] == "NaN":
                    continue
                dist = abs(complex(float(r["x"]), float(r["y"])) - rho)
                best[pot] = max(best.get(pot, 0.0), dist)
    worst = max(best, key=best.__getitem__)
    out = {"max_dist": best[worst], "argmax_potential": worst, "per_potential": best, "n_files": len(files),
           "rule": "rows with n=96 and finite e_zp (dynamically stable); distance |x+iy-rho|"}
    (HERE / "data/max_stable_dist.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"max_dist": out["max_dist"], "argmax_potential": worst, "n_files": len(files)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
