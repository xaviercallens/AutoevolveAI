"""Which single path did the stored SinglePath files run? (T1, T_end, P range, number of steps)."""
from __future__ import annotations

import json
import sys

import numpy as np


def main() -> int:
    for f in sys.argv[1:]:
        d = json.load(open(f))
        rp = d["Refresh_Path"]
        T = np.array(rp["Temperatures"], dtype=float)
        P = np.array(rp["Pressures"], dtype=float)
        i = int(np.argmax(T >= T.max() - 1e-9))
        print(f.split("/")[-1], "n", T.size, "T1", T[0], "Tmax", T.max(), "T at P-start-drop", T[i],
              "P1", P[0], "Pend", P[-1], "xi mol/J", d.get("Intrinsic_capture_efficiency"),
              "units", d.get("Intrinsic_capture_efficiency_units"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
