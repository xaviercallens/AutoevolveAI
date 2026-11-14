"""Tier X: max over T of P_c/P_B at T_e = T_i/3, W-H mix x = 1/6, NS and Wang fits (checks the Fig. 28 caption remark)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e1_float_indep as f  # noqa: E402


def main() -> None:
    Ts = np.geomspace(50, 500, 2001)
    for name, sv in (("NS", f.ns_pb), ("Wang", f.wang_pb)):
        best = max((f.pb_R(float(T), 1 / 3, 1 / 6, sv), float(T)) for T in Ts[::4])
        print(name, "max R at Te=Ti/3, x=1/6:", best)


if __name__ == "__main__":
    main()
