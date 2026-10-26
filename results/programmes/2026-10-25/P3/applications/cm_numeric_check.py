"""Tier X: floating-point screen of candidate potentials for complete monotonicity (CM) in t = r^2.

For each candidate F, evaluate (-1)^n F^{(n)}(t) for n = 0..N on a log grid of t with mpmath (60 digits, numerical
differentiation) and report the minimum signed value found and where. A negative value REFUTES CM (modulo the
numerical differentiation error, controlled by the checker's own controls); a clean grid never PROVES CM.
Controls: positive (known CM: Yukawa g_kappa, Riesz) and negative (known non-CM: cos, h_d dipolar sign-flip,
Yukawa signed mixture).
Usage: python -I cm_numeric_check.py OUT.json
"""
from __future__ import annotations

import json
import sys

from mpmath import cos, diff, exp, mp, mpf, sqrt

mp.dps = 60
N = 7
TS = [mpf(10) ** (mpf(k) / 2) for k in range(-6, 9)]  # 1e-3 .. 1e4


def g(kappa, t):
    return exp(-kappa * sqrt(t)) / sqrt(t)


def riesz(s, t):
    return t ** (-s / 2)


CANDIDATES = {
    # controls
    "ctl_pos_riesz1": lambda t: riesz(1, t),
    "ctl_pos_yukawa_k1": lambda t: g(1, t),
    "ctl_neg_cos": lambda t: cos(t),
    "ctl_neg_h_dipolar_d1": lambda t: t ** mpf(-0.5) - 2 * (t + 1) ** mpf(-0.5),
    "ctl_neg_yukawa_signed_mix": lambda t: g(1, t) - 2 * g(2, t),
    # candidates
    "quadrupole_0_c_4c_c1": lambda t: t ** mpf(-0.5) - 2 * (t + 1) ** mpf(-0.5) + (t + 4) ** mpf(-0.5),
    # exciton-exciton interaction of two aligned +1,-2,+1 quadrupoles: 6 f(t) - 8 f(t+c) + 2 f(t+4c), c = d^2
    "quadrupolar_pair_interaction_c1": lambda t: 2 * (3 * t ** mpf(-0.5) - 4 * (t + 1) ** mpf(-0.5) + (t + 4) ** mpf(-0.5)),
    "quadrupolar_pair_interaction_screened_k1_c1": lambda t: 2 * (3 * g(1, t) - 4 * g(1, t + 1) + g(1, t + 4)),
    # negative control for the factorisation: wrong weights 2,-3,1 (zero total charge but a negative far field)
    "ctl_neg_weights_2_m3_1_c1": lambda t: 2 * t ** mpf(-0.5) - 3 * (t + 1) ** mpf(-0.5) + (t + 4) ** mpf(-0.5),
    "seconddiff_0_c_2c_c1": lambda t: t ** mpf(-0.5) - 2 * (t + 1) ** mpf(-0.5) + (t + 2) ** mpf(-0.5),
    "screened_dipolar_k1_d1": lambda t: 2 * (g(1, t) - g(1, t + 1)),
    "screened_dipolar_k3_d2": lambda t: 2 * (g(3, t) - g(3, t + 4)),
    "yukawa_exp_spectrum": lambda t: 1 / (sqrt(t) * (1 + sqrt(t))),
    "yukawa_box_spectrum_0_to_2": lambda t: (1 - exp(-2 * sqrt(t))) / t,
}


def main(out: str) -> None:
    res = {}
    for name, F in CANDIDATES.items():
        worst = None
        for t in TS:
            for n in range(N + 1):
                v = diff(F, t, n) if n else F(t)
                s = (-1) ** n * v
                if worst is None or s < worst[0]:
                    worst = (s, n, t)
        res[name] = {"min_signed": mp.nstr(worst[0], 8), "at_n": worst[1], "at_t": mp.nstr(worst[2], 6),
                     "negative_found": bool(worst[0] < 0)}
        print(name, res[name], flush=True)
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
