"""Positive control for part (b): single exponential h = exp(-t/30), m = exp(-t/50): u = (e^{-t/50}-e^{-t/30})/(1/30-1/50),
peak at t* = ln((1/30)/(1/50))/(1/30-1/50) = 75 ln(5/3). The interval-certified bisection must enclose it."""
import json
import sys
from fractions import Fraction as F
from pathlib import Path

import mpmath

sys.path.insert(0, str(Path(__file__).parent))
from k3lib import IRF  # noqa: E402
from run_b import SeshPath, peak  # noqa: E402

mpmath.mp.dps = 40
exact = 75 * mpmath.log(mpmath.mpf(5) / 3)
r = peak(SeshPath(F(0), F(60), F(50)), IRF(F(0), [F(1)], [F(30)]), 2000.0)
lo, hi = [mpmath.mpf(x.numerator) / x.denominator for x in map(F, r["t2_enclosure"])]
ok = bool(lo - mpmath.mpf("1e-12") <= exact <= hi + mpmath.mpf("1e-12"))
out = {"closed_form_75ln(5/3)": mpmath.nstr(exact, 25), "enclosure": [mpmath.nstr(lo, 25), mpmath.nstr(hi, 25)],
       "contains_closed_form": ok, "pass": ok}
json.dump(out, open(Path(__file__).resolve().parents[1] / "data" / "control_closed_form.json", "w"), indent=1)
print(out)
