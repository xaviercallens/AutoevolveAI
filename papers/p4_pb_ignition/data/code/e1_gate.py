"""E1 consistency gate (written before the certified run; see RESULT.md 'Deviations' for its timing).

The gate is a pure function of a results dict produced by e1_certify.run_pipeline(). It PASSES only if
  G1  the certified D-T ideal-ignition temperature enclosure lies in [4.25, 4.35)            (W-H: 4.3 keV)
  G2  the certified Q_fuel = inf triple-product minimiser enclosure lies in [13.5, 14.5) keV and the
      minimum enclosure lies in [2.85e21, 2.95e21) m^-3 keV s                               (W-H Table III)
  G2b the certified Q_fuel = inf Lawson-parameter minimiser lies in [25.5, 26.5) keV and the
      minimum in [1.55e20, 1.65e20) m^-3 s                                                   (W-H Table II)
  G3  p-11B under the Nevins-Swain fit at T_e = T_i and the W-H optimal mix (n_B/n_i = 1/6, Zeff = 3) has a
      certified P_c < P_B for every T_i in [50, 500] keV                                     (W-H Table II/III '-', Fig. 28)
  G4  the independent float implementation lands inside the certified enclosures (constant-hull variant)
Any missing (None) enclosure is a FAIL. Negative controls run the same pipeline and must FAIL.
"""
from __future__ import annotations

from typing import Any


def _inside(enc: list[float] | None, lo: float, hi: float) -> bool:
    return enc is not None and lo <= enc[0] and enc[1] < hi


def gate(res: dict[str, Any], float_ref: dict[str, Any] | None = None) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    checks["G1_T_ign_4.3"] = _inside(res.get("T_ign"), 4.25, 4.35)
    checks["G2_TP_Tmin_14"] = _inside(res.get("TP_Tmin"), 13.5, 14.5)
    checks["G2_TP_min_2.9e21"] = _inside(res.get("TP_min"), 2.85e21, 2.95e21)
    checks["G2b_LP_Tmin_26"] = _inside(res.get("LP_Tmin"), 25.5, 26.5)
    checks["G2b_LP_min_1.6e20"] = _inside(res.get("LP_min"), 1.55e20, 1.65e20)
    checks["G3_pB_NS_no_window_WHmix"] = bool(res.get("pB_NS_WHmix_theta1_certified_below_1"))
    if float_ref is not None:
        hullres = res.get("hull", {})
        ok = True
        for key, fkey in (("T_ign", "T_ign"), ("TP_min", "TP_min"), ("LP_min", "LP_min")):
            enc = hullres.get(key)
            val = float_ref.get(fkey)
            ok = ok and enc is not None and val is not None and enc[0] <= val <= enc[1]
        checks["G4_float_inside_hull"] = ok
    verdict = "PASS" if all(checks.values()) else "FAIL"
    return {"verdict": verdict, "checks": checks}
