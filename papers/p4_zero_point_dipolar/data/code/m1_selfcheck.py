"""M1 Tier X self-check of the Ewald split: B(s, t') = D(s e)/s^2 and its t-derivatives from the certifier's ball sums
(m1_certify.M1Model.sums2) against an independent floating-point real-space sum (numpy, cutoff RC, continuum tail
-pi RC V'(RC) I as in n2_explore.py, t-derivatives by central differences), at a few points of both Duffy triangles,
for two split parameters alpha (the result must not depend on alpha).

usage: python -I m1_selfcheck.py POT PARAM QMAX RC OUT.json
"""

from __future__ import annotations

import json
import math
import sys

import numpy as np

sys.path.insert(0, "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal4/2026-10-27/M1/code")
import m1_certify as M  # noqa: E402

C = math.sqrt(2 / math.sqrt(3))


def radial(pot: str, d: float):
    if pot.startswith("riesz3"):
        return lambda r: r ** -3.0, lambda r: -3 * r ** -4.0, lambda r: 12 * r ** -5.0
    # V = 2(1/r - 1/s)/d^2, s = sqrt(r^2 + d^2)
    def V(r):
        return 2 * (1 / r - 1 / np.sqrt(r * r + d * d)) / d ** 2

    def V1(r):
        return 2 * (-1 / r ** 2 + r / (r * r + d * d) ** 1.5) / d ** 2

    def V2(r):
        s2 = r * r + d * d
        return 2 * (2 / r ** 3 + 1 / s2 ** 1.5 - 3 * r * r / s2 ** 2.5) / d ** 2
    return V, V1, V2


def direct_B(pot: str, d: float, rc: float, tri: int, s: float, tp: float, t: float) -> np.ndarray:
    V, V1, V2 = radial(pot, d)
    L = int(rc / C * 1.2) + 2
    m, l = np.meshgrid(np.arange(-L, L + 1), np.arange(-L, L + 1), indexing="ij")
    m, l = m.ravel().astype(float), l.ravel().astype(float)
    X0, Y0 = C * (m + l / 2), C * l * math.sqrt(3) / 2
    keep = (X0 * X0 + Y0 * Y0 <= rc * rc) & ((m != 0) | (l != 0))
    m, l, X0, Y0 = m[keep], l[keep], X0[keep], Y0[keep]
    X, Y = X0 + t * Y0, t * X0 + (1 + t * t) * Y0
    r = np.sqrt(X * X + Y * Y)
    a = V1(r) / r
    b = (V2(r) - a) / (r * r)
    th = (math.pi * (m - l) + 2 * math.pi * l * tp) if tri == 0 else (math.pi * (l - m) + 2 * math.pi * m * tp)
    ph = 1 - np.cos(s * th)
    tail = -math.pi * rc * V1(rc)
    D = np.array([ph @ (a + b * X * X) + tail, ph @ (b * X * Y), ph @ (a + b * Y * Y) + tail])
    return D / (s * s)


def main() -> None:
    pot, par, qmax, rc, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
    d = float(M.N2.q_arb(par).mid()) if pot == "dipolar" else 0.0
    t0 = M.N2.q_arb("1/100000")
    pts = [(0, 0.1, 0.3), (0, 0.23, 0.9), (0, 0.6, 0.4), (1, 0.95, 0.05), (1, 0.4, 0.7), (0, 0.999, 0.5)]
    rows = []
    for alpha in ("1/10", "1/6"):
        model, _ = M.build(pot, par, t0, qmax, M.N2.q_arb(alpha))
        for (tri, s, tp) in pts:
            S = model.sums2(tri, M.arb(s), M.arb(tp))
            h = 1e-3
            Dp, D0, Dm = (direct_B(pot, d, rc, tri, s, tp, tt) for tt in (h, 0.0, -h))
            ref = {"B": D0.tolist(), "B1": ((Dp - Dm) / (2 * h)).tolist(), "B2": ((Dp - 2 * D0 + Dm) / h ** 2).tolist()}
            got = {"B": [float(S[i].v.mid()) for i in range(3)], "B1": [float(S[3 + i].v.mid()) for i in range(3)],
                   "B2": [float(S[6 + i].v.mid()) for i in range(3)],
                   "rad_B": [float(S[i].v.rad()) for i in range(3)]}
            err = max(abs(got[k][i] - ref[k][i]) for k in ("B", "B1", "B2") for i in range(3))
            rows.append({"alpha": alpha, "tri": tri, "s": s, "tp": tp, "ref": ref, "ball_mid": got, "max_abs_diff": err})
            print(alpha, tri, s, tp, "B", [round(x, 6) for x in got["B"]], "ref", [round(x, 6) for x in ref["B"]],
                  "maxdiff", f"{err:.2e}", flush=True)
    with open(out, "w") as fh:
        json.dump({"pot": pot, "param": par, "qmax": qmax, "rc_direct": rc, "rows": rows}, fh, indent=1)


if __name__ == "__main__":
    main()
