"""Tier X falsification gate for the H8 shape theorems (run before Lean).

S_B(x) = x / sqrt(1 + x^2), x = k/ks. Checks on a dense grid (mpmath, 50 digits):
  mono   : S_B strictly increasing
  phonon : x/(1+x) <= S_B <= x
  lt1    : S_B < 1
  free   : 1 - S_B <= 1/x^2
  dual   : S_B <= sqrt(x/2)
  epsB   : eps_B == eps0 / S_B  (eps0 = x^2, eps_B = sqrt(x^2 + x^4), units hc = ks = 1)
Negative controls (must FAIL somewhere): S = 1 against S <= x for x < 1;
a wrong "free" bound 1 - S_B <= 1/(4 x^2) (too tight by factor 2 at large x);
a wrong lower bound x <= S_B.
"""
import json
import sys

import mpmath as mp

mp.mp.dps = 50


def s_b(x: mp.mpf) -> mp.mpf:
    return x / mp.sqrt(1 + x * x)


def main(out_path: str) -> None:
    xs = [mp.mpf(10) ** (mp.mpf(e) / 100) for e in range(-1200, 401)]  # 1e-12 .. 1e4
    xs += [mp.mpf(i) / 1000 for i in range(1, 100001)]  # (0, 100]
    xs = sorted(set(xs))
    viol = {"mono": 0, "phonon_upper": 0, "phonon_lower": 0, "lt1": 0, "free": 0, "dual": 0, "epsB": 0}
    neg = {"S1_vs_phonon_x_lt_1": 0, "wrong_free_quarter": 0, "wrong_lower_x": 0}
    prev = None
    for x in xs:
        s = s_b(x)
        if prev is not None and not (s > prev):
            viol["mono"] += 1
        prev = s
        if not (s <= x):
            viol["phonon_upper"] += 1
        if not (x / (1 + x) <= s):
            viol["phonon_lower"] += 1
        if not (s < 1):
            viol["lt1"] += 1
        if not (1 - s <= 1 / (x * x)):
            viol["free"] += 1
        if not (s <= mp.sqrt(x / 2) * (1 + mp.mpf(10) ** -40)):
            viol["dual"] += 1
        e0 = x * x
        eb = mp.sqrt(x * x + x ** 4)
        if abs(eb - e0 / s) > mp.mpf(10) ** -35 * eb:
            viol["epsB"] += 1
        if x < 1 and not (1 <= x):
            neg["S1_vs_phonon_x_lt_1"] += 1
        if not (1 - s <= 1 / (4 * x * x)):
            neg["wrong_free_quarter"] += 1
        if not (x <= s):
            neg["wrong_lower_x"] += 1
    res = {
        "n_points": len(xs),
        "x_range": [mp.nstr(xs[0], 5), mp.nstr(xs[-1], 5)],
        "violations_claimed": viol,
        "negative_controls_failures_found": neg,
        "gate_pass": all(v == 0 for v in viol.values()) and all(v > 0 for v in neg.values()),
        "tier": "X (floating-point exploration; supports no claim)",
    }
    with open(out_path, "w") as fh:
        json.dump(res, fh, indent=2)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
