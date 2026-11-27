"""Tier X sanity gate for the H2 contribution (never supports a claim).

Checks (-1)^n d^n/dt^n f(t) >= 0 for n = 0..8 on a grid of t, with mpmath high-precision differentiation, for
  * positive control: the mixture e^{-r}/r + 0.5 e^{-3r}/r (t = r^2), and the rescaled one at density rho = 3;
  * negative control: the signed mixture g_1 - 2 g_2 (must be flagged; Lean proves it negative at t = 1/4).
"""

from __future__ import annotations

import json
import sys

import mpmath as mp

mp.mp.dps = 40


def g(kappa: float, t: mp.mpf) -> mp.mpf:
    return mp.e ** (-kappa * mp.sqrt(t)) / mp.sqrt(t)


def mix(t: mp.mpf) -> mp.mpf:
    return g(1, t) + mp.mpf("0.5") * g(3, t)


def mix_rho3(t: mp.mpf) -> mp.mpf:
    return mix(t / 3)


def signed(t: mp.mpf) -> mp.mpf:
    return g(1, t) - 2 * g(2, t)


def violations(f, ts: list[mp.mpf], nmax: int = 8) -> list[tuple[float, int, float]]:
    out = []
    for t in ts:
        for n in range(nmax + 1):
            v = (-1) ** n * mp.diff(f, t, n)
            if v < 0:
                out.append((float(t), n, float(v)))
    return out


def main() -> int:
    ts = [mp.mpf(x) / 20 for x in range(1, 81)]
    res = {
        "grid": "t = k/20, k = 1..80; orders n = 0..8; mpmath dps 40",
        "positive_mix_violations": len(violations(mix, ts)),
        "positive_mix_rho3_violations": len(violations(mix_rho3, ts)),
    }
    neg = violations(signed, ts)
    res["negative_signed_violations"] = len(neg)
    res["negative_signed_first"] = neg[:3]
    res["signed_at_quarter"] = float(signed(mp.mpf(1) / 4))
    res["gate_pass"] = (res["positive_mix_violations"] == 0 and res["positive_mix_rho3_violations"] == 0
                        and res["negative_signed_violations"] > 0)
    out = sys.argv[1]
    with open(out, "w") as fh:
        json.dump(res, fh, indent=2)
    print(json.dumps(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
