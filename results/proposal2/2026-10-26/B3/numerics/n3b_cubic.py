"""N3b: degree-4 cubic-harmonic coefficient of the bcc Green function, and the same fit for fcc and sc
(positive control: the regular constant C must equal 2 * Madelung energy per particle, e.g. bcc -2.888461503,
as in Muratov-Novaga arXiv:2610.29732 eq. (11))."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ewald3d as ew  # noqa: E402
from n3_green_obstruction import cubic_coefficient  # noqa: E402

OUT = Path(__file__).resolve().parent / "n3b_cubic.json"


def main() -> None:
    res = {}
    for st in (ew.bcc(), ew.fcc(), ew.sc()):
        pot = ew.Potential(st, alpha=2.4)
        fit = cubic_coefficient(pot)
        fit["two_times_madelung"] = 2 * ew.ewald_energy_per_particle(st, alpha=2.2)
        res[st.name] = fit
        print(st.name, fit, flush=True)
    OUT.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
