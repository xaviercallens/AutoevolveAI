"""N1: jellium (OCP) Madelung energies per particle at unit density, with controls.

Positive controls: alpha independence; literature Madelung constants in Wigner-Seitz units
(e * r_s): bcc -0.895929255682, fcc -0.895873615195, hcp -0.895838120459, sc -0.880059440
(Coldwell-Horsfall & Maradudin 1960 / standard OCP tables; tier L, checked here numerically).
Negative control: dropping the background term makes the result alpha dependent.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ewald3d as ew  # noqa: E402

OUT = Path(__file__).resolve().parent / "n1_energies.json"
LIT_WS = {"bcc": -0.895929255682, "fcc": -0.895873615195, "hcp": -0.895838120459, "sc": -0.880059440}


def main() -> None:
    rs = ew.R_S_UNIT_DENSITY
    res: dict[str, object] = {"r_s_unit_density": rs, "structures": {}}
    structs = [ew.bcc(), ew.fcc(), ew.hcp(), ew.sc(), ew.a15(), ew.c15()]
    for st in structs:
        vals = [ew.ewald_energy_per_particle(st, alpha=a) for a in (1.6, 2.2, 3.0)]
        e = vals[1]
        entry = {
            "n_basis": st.n,
            "e_per_particle": e,
            "alpha_spread": max(vals) - min(vals),
            "e_times_rs": e * rs,
        }
        if st.name in LIT_WS:
            entry["literature_e_times_rs"] = LIT_WS[st.name]
            entry["abs_dev_from_literature"] = abs(e * rs - LIT_WS[st.name])
        res["structures"][st.name] = entry
        print(st.name, entry, flush=True)
    b = res["structures"]["bcc"]["e_per_particle"]
    for k, v in res["structures"].items():
        v["gap_above_bcc"] = v["e_per_particle"] - b
        v["rel_gap_above_bcc"] = (v["e_per_particle"] - b) / abs(b)
    # negative control
    st = ew.bcc()
    nb = [ew.ewald_energy_per_particle(st, alpha=a, background=False) for a in (1.6, 2.2, 3.0)]
    res["negative_control_no_background"] = {"values_at_alpha_1.6_2.2_3.0": nb, "spread": max(nb) - min(nb)}
    # 2D comparison (from P1 audit, tier X there): W(tri) = -4.1504128077, W(square) = -4.1171606 (manuscript normalization)
    res["two_d_reference"] = {
        "W_tri": -4.1504128077,
        "W_square": -4.1171606,
        "rel_gap_square_vs_tri": (-4.1171606 + 4.1504128077) / 4.1504128077,
        "source": "results/programmes/2026-10-25/P1/REDUCTION_AUDIT.md (BS2018 sec 7.3 closed form, Ewald reproduced)",
    }
    OUT.write_text(json.dumps(res, indent=1))
    print(json.dumps(res["negative_control_no_background"]))


if __name__ == "__main__":
    main()
