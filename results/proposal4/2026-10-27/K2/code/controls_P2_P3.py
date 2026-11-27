"""P3 (printed Dickson Guide check values), N4 (corrupted constant), P2 (closed form vs numerical derivative)."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import mpmath
from mpmath import iv, mp

sys.path.insert(0, str(Path(__file__).parent))
import k2lib as K  # noqa: E402

mp.dps = 50
out: dict = {}

# P3: printed values at S=35, 25 C
c = K.constants(iv.mpf(25), iv.mpf(35))
vals = {
    "lnK0": float(iv.log(c["K0"]).mid),
    "log10K1": float((iv.log(c["K1"]) / K.LN10).mid),
    "log10K2": float((iv.log(c["K2"]) / K.LN10).mid),
    "lnKB": float(iv.log(c["KB"]).mid),
    "lnKW": float(iv.log(c["KW"]).mid),
}
printed = {"lnK0": -3.5617, "log10K1": -5.8472, "log10K2": -8.9660, "lnKB": -19.7964, "lnKW": -30.434}
digits = {"lnK0": 4, "log10K1": 4, "log10K2": 4, "lnKB": 4, "lnKW": 3}
p3 = {}
for k in printed:
    ok = round(vals[k], digits[k]) == printed[k]
    p3[k] = {"computed": vals[k], "printed": printed[k], "equal_at_printed_digits": ok}
out["P3"] = p3
out["P3_pass"] = all(v["equal_at_printed_digits"] for v in p3.values())

# N4: corrupted K1 coefficient breaks P3
cc = K.constants(iv.mpf(25), iv.mpf(35), 0.0, {"k1_coef_shift": 100.0})
v = float((iv.log(cc["K1"]) / K.LN10).mid)
out["N4"] = {"log10K1_corrupt": v, "printed": -5.8472, "rejected": round(v, 4) != -5.8472}


# P2: closed form vs 50-digit numerical derivative of DIC(TA) at fixed fCO2
def point_consts(t: float, s: float) -> dict:
    ci = K.constants(iv.mpf(t), iv.mpf(s))
    return {k: mpmath.mpf(v.mid.a) if False else (mpmath.mpf(v.a) + mpmath.mpf(v.b)) / 2 for k, v in ci.items()}


def solve_h(cm: dict, f: float, ta: mpmath.mpf) -> mpmath.mpf:
    C = cm["K0"] * f * mpmath.mpf("1e-6")
    F = lambda lh: (lambda h: C * (cm["K1"] / h + 2 * cm["K1"] * cm["K2"] / h**2) + cm["BT"] * cm["KB"] / (cm["KB"] + h) + cm["KW"] / h - h - ta)(mpmath.e**lh)
    return mpmath.e ** mpmath.findroot(F, (mpmath.log(mpmath.mpf("1e-10")), mpmath.log(mpmath.mpf("1e-6"))), solver="anderson", tol=mpmath.mpf(10) ** -45)


def dic(cm: dict, f: float, ta: mpmath.mpf) -> mpmath.mpf:
    h = solve_h(cm, f, ta)
    C = cm["K0"] * f * mpmath.mpf("1e-6")
    return C * (1 + cm["K1"] / h + cm["K1"] * cm["K2"] / h**2)


random.seed(20261031)
worst = mpmath.mpf(0)
rows = []
for _ in range(50):
    t, s, f, ta35 = random.uniform(0, 30), random.uniform(30, 38), random.uniform(280, 560), random.uniform(2200, 2400)
    ta = mpmath.mpf(ta35) * 1e-6 * s / 35
    cm = point_consts(t, s)
    eps = mpmath.mpf("1e-12")
    num = (dic(cm, f, ta + eps) - dic(cm, f, ta - eps)) / (2 * eps)
    h = solve_h(cm, f, ta)
    ci = K.constants(iv.mpf(t), iv.mpf(s))
    eta_cf = float(K.eta_at(iv.mpf(float(h)), ci, iv.mpf(f)).mid)
    rel = abs(mpmath.mpf(eta_cf) - num) / num
    worst = max(worst, rel)
    rows.append({"T": t, "S": s, "f": f, "TA35": ta35, "eta_cf": eta_cf, "eta_num": float(num), "rel": float(rel)})
out["P2"] = {"n": 50, "worst_rel": float(worst), "pass_1e-12": bool(worst < 1e-12), "rows": rows[:5]}
Path(sys.argv[1]).write_text(json.dumps(out, indent=1))
print(json.dumps({k: out[k] for k in ("P3", "P3_pass", "N4")}, indent=1))
print("P2 worst rel", float(worst))
