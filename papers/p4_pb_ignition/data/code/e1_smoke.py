"""Smoke test of the Arb model: point values only (no claims)."""
from __future__ import annotations

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))  # noqa: E401
from e1_model import (A, K_const, iv, sv_bosch_hale_dt, sv_nevins_swain, wang_reactivity, pb_ratio, pb_E_keV, arb)


def main() -> None:
    K = K_const()
    print("K", K, K.lower(), K.upper())
    print("BH DT sv(10 keV)", sv_bosch_hale_dt(arb(10)))
    print("BH DT sv([13.9,14.1])", sv_bosch_hale_dt(iv(arb("13.9"), arb("14.1"))))
    for T in [50, 100, 300, 500]:
        ns = sv_nevins_swain(arb(T))
        wg = wang_reactivity(arb(T))
        print("T", T, "NS", ns, "Wang", wg, "ratio", wg / ns)
    r = pb_ratio(arb(300), arb(1), arb(1) / 6, sv_nevins_swain, K, pb_E_keV(), arb(1))
    print("R(300,1,1/6)", r)


if __name__ == "__main__":
    main()
