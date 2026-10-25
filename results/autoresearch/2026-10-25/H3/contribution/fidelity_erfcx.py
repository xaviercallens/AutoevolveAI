"""Tier X fidelity check for the Lean definition `erfcx x := (2/sqrt(pi)) * int_0^inf exp(-(y^2 + 2 x y)) dy`.

Compares against mpmath's erfc (e^{x^2} erfc x) at several x >= 0 (positive check) and shows that a perturbed
integrand exp(-(y^2 + x y)) disagrees (negative control). Also re-checks the two bounds proved in Lean,
erfcx <= 1 and erfcx <= 1/(sqrt(pi) x), on a grid (they are kernel-checked; this is only a sanity echo).
Writes fidelity_erfcx.json next to this script.
"""
import json
import os

import mpmath as mp

mp.mp.dps = 30
xs = [0, 0.01, 0.3, 1, 2.5, 7, 50]


def lean_def(x: float, coef: float = 2.0) -> mp.mpf:
    return 2 / mp.sqrt(mp.pi) * mp.quad(lambda y: mp.exp(-(y**2 + coef * x * y)), [0, 1, mp.inf])


def ref(x: float) -> mp.mpf:
    return mp.exp(mp.mpf(x) ** 2) * mp.erfc(x)


rows = []
for x in xs:
    a, r, bad = lean_def(x), ref(x), lean_def(x, 1.0)
    rows.append({
        "x": x,
        "lean_def": float(a),
        "reference": float(r),
        "rel_err": float(abs(a - r) / r),
        "perturbed_rel_err": float(abs(bad - r) / r),
        "le_one": bool(a <= 1 + mp.mpf(10) ** -25),
        "le_inv": bool(x == 0 or a <= 1 / (mp.sqrt(mp.pi) * x)),
    })
out = {
    "max_rel_err": max(r["rel_err"] for r in rows),
    "min_perturbed_rel_err_x_pos": min(r["perturbed_rel_err"] for r in rows if r["x"] > 0),
    "rows": rows,
}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fidelity_erfcx.json"), "w") as fh:
    json.dump(out, fh, indent=2)
print(json.dumps({k: v for k, v in out.items() if k != "rows"}))
