"""Print the key numbers of M1 run JSONs. usage: python -I m1_show.py RUN.json [RUN.json ...]"""
from __future__ import annotations

import json
import sys


def main() -> None:
    for p in sys.argv[1:]:
        a = json.load(open(p))
        if "refused" in a:
            print(p.split("/")[-1], "REFUSED", a["refused"])
            continue
        M, E = a["M_window_curvature_bound"], a["E0"]
        print(p.split("/")[-1], a["potential"], a["param"], "M=[%.5f, %.5f]" % (M["lo_float"], M["hi_float"]),
              "E0=[%.6f, %.6f]" % (E["lo_float"], E["hi_float"]), "cert", a["certified_not_local_min"],
              "pos", a["positivity_ok"], "cells", a["stats"]["cells"], "s", a["seconds"], "sha", a.get("script_sha256", "")[:12],
              "ctl", a["controls"].get("M_contains_TierX_Epp0"), a["controls"].get("E0_minus_TierX_E0"))


if __name__ == "__main__":
    main()
