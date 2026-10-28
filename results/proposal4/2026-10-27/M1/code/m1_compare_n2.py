"""M1 positive control: compare a run of m1_certify.py with the N2 run of the same configuration.

usage: python -I m1_compare_n2.py M1_RUN.json N2_RUN.json
"""
from __future__ import annotations

import json
import sys


def main() -> None:
    a = json.load(open(sys.argv[1]))
    b = json.load(open(sys.argv[2]))
    out = {}
    for k in ("M_window_curvature_bound", "U_lin_pp0_B2_majorant", "E0"):
        if k in b:
            out[k] = {"m1": [a[k]["lo"], a[k]["hi"]], "n2": [b[k]["lo"], b[k]["hi"]],
                      "identical_rationals": [a[k]["lo"], a[k]["hi"]] == [b[k]["lo"], b[k]["hi"]],
                      "m1_float": [a[k]["lo_float"], a[k]["hi_float"]], "n2_float": [b[k]["lo_float"], b[k]["hi_float"]]}
    out["cells"] = [a["stats"]["cells"], b["stats"]["cells"]]
    out["certified"] = [a["certified_not_local_min"], b["certified_not_local_min"]]
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
