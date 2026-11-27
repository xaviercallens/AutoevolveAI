"""Wang 2026 fit at the W-H mix x = 1/6: two-sided certified theta* (stage that replaces the 'not separated' entry).

Candidate theta values come from the Tier X float scan (logs/float_indep.json: theta_c,max = 0.3988); both sides
are then certified exactly as in e1_certify.theta_threshold. Writes logs/certify_wang_mix.json.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1_certify import max_R  # noqa: E402
from e1_model import GridSV, K_const, arb, pb_E_keV, wang_reactivity  # noqa: E402

HERE = Path(__file__).resolve().parent


def main() -> None:
    t0 = time.time()
    sv = GridSV(wang_reactivity, "49.999999", "500.000001", "1.0005")
    K, E = K_const(), pb_E_keV()
    xb = ("0.16666666666666666", "0.16666666666666667")
    out: dict[str, object] = {"grid_nodes": len(sv.nodes)}
    for th in ("0.380", "0.390", "0.394", "0.396", "0.398", "0.400", "0.402", "0.404", "0.410"):
        r = max_R(arb(th), sv, K, E, arb(1), ("50", "500"), xb, rtol=1e-3, decide=True, min_rel=2e-4, max_iter=200000)
        out[th] = r
        print(th, r, flush=True)
    (HERE.parent / "logs" / "certify_wang_mix.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
