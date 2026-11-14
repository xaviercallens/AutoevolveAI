"""Stage-5 revision: numerical check (Tier X) of the all-positive route (e) for Theorem 2.

Route (e): V(r) = r0^-1 int_0^inf e^{-r u/r0} (1+u^2)^{-1/2} du        (DLMF 11.5.2, nu=0)
subordination: e^{-rho sqrt t} = int_0^inf e^{-t a} rho/(2 sqrt pi) a^{-3/2} e^{-rho^2/(4a)} da
inner integral: int_0^inf u (1+u^2)^{-1/2} e^{-lam u^2} du = (1/2) sqrt(pi/lam) erfcx(sqrt lam)
result: V = int_0^inf e^{-t a} erfcx(1/(2 r0 sqrt a)) / (2 r0 a) da, and a = 1/(4b) gives w(b)/(2b) db.

Positive controls: each identity at several parameter points.
Negative controls: a perturbed inner integrand (e^{-lam u} in place of e^{-lam u^2}, compared with the same
closed form) and a wrong subordination exponent (a^{-1/2} instead of a^{-3/2}) must be visibly off. Each control's
minimum separation is reported separately.
"""
from __future__ import annotations

import json
import sys

import mpmath as mp

mp.mp.dps = 30


def erfcx(x: mp.mpf) -> mp.mpf:
    return mp.exp(x * x) * mp.erfc(x)


def v_struve(r0: mp.mpf, r: mp.mpf) -> mp.mpf:
    z = r / r0
    return mp.pi / (2 * r0) * (mp.struveh(0, z) - mp.bessely(0, z))


def v_laplace(r0: mp.mpf, r: mp.mpf) -> mp.mpf:
    return mp.quad(lambda u: mp.exp(-r * u / r0) / mp.sqrt(1 + u * u), [0, 1, 10, mp.inf]) / r0


def v_mixture(r0: mp.mpf, r: mp.mpf) -> mp.mpf:
    t = r * r
    return mp.quad(lambda b: erfcx(mp.sqrt(b) / r0) / r0 / (2 * b) * mp.exp(-t / (4 * b)),
                   [0, t / 40, t / 4, t, 10 * t, mp.inf])


def v_rho(r0: mp.mpf, r: mp.mpf) -> mp.mpf:
    t = r * r
    return mp.quad(lambda a: mp.exp(-t * a) * erfcx(1 / (2 * r0 * mp.sqrt(a))) / (2 * r0 * a),
                   [0, 1 / (40 * t), 1 / t, 10 / t, mp.inf])


def inner_lhs(lam: mp.mpf) -> mp.mpf:
    return mp.quad(lambda u: u / mp.sqrt(1 + u * u) * mp.exp(-lam * u * u), [0, 1, 10, mp.inf])


def inner_lhs_perturbed(lam: mp.mpf) -> mp.mpf:
    return mp.quad(lambda u: u / mp.sqrt(1 + u * u) * mp.exp(-lam * u), [0, 1, 10, mp.inf])


def inner_rhs(lam: mp.mpf) -> mp.mpf:
    return mp.sqrt(mp.pi / lam) / 2 * erfcx(mp.sqrt(lam))


def subord(rho: mp.mpf, t: mp.mpf, power: mp.mpf) -> mp.mpf:
    return mp.quad(lambda a: mp.exp(-t * a) * rho / (2 * mp.sqrt(mp.pi)) * a ** (-power)
                   * mp.exp(-rho * rho / (4 * a)), [0, rho * rho / 40, rho * rho, 10, mp.inf])


def rel(a: mp.mpf, b: mp.mpf) -> float:
    return float(abs(a - b) / abs(b))


def main(out: str) -> int:
    pts = [(mp.mpf("0.7"), mp.mpf("1.3")), (mp.mpf("0.1"), mp.mpf("1")), (mp.mpf("5"), mp.mpf("0.2")),
           (mp.mpf("1"), mp.mpf("5"))]
    rows = []
    for r0, r in pts:
        s = v_struve(r0, r)
        rows.append({"r0": str(r0), "r": str(r), "struve": mp.nstr(s, 20),
                     "laplace_rel": rel(v_laplace(r0, r), s), "rho_form_rel": rel(v_rho(r0, r), s),
                     "mixture_rel": rel(v_mixture(r0, r), s)})
    inner = []
    for lam in [mp.mpf("0.01"), mp.mpf("0.5"), mp.mpf("3"), mp.mpf("40")]:
        lhs = inner_lhs(lam)
        inner.append({"lam": str(lam), "rel": rel(lhs, inner_rhs(lam)),
                      "neg_ctl_perturbed_integrand_rel": rel(inner_lhs_perturbed(lam), inner_rhs(lam))})
    sub = []
    for rho, t in [(mp.mpf("0.5"), mp.mpf("2")), (mp.mpf("2"), mp.mpf("0.3"))]:
        exact = mp.exp(-rho * mp.sqrt(t))
        sub.append({"rho": str(rho), "t": str(t), "rel": rel(subord(rho, t, mp.mpf("1.5")), exact),
                    "neg_ctl_power_half_rel": rel(subord(rho, t, mp.mpf("0.5")), exact)})
    pos_max = max([max(x["laplace_rel"], x["rho_form_rel"], x["mixture_rel"]) for x in rows]
                  + [x["rel"] for x in inner] + [x["rel"] for x in sub])
    neg_inner = min(x["neg_ctl_perturbed_integrand_rel"] for x in inner)
    neg_sub = min(x["neg_ctl_power_half_rel"] for x in sub)
    neg_min = min(neg_inner, neg_sub)
    res = {"tier": "X", "claim_licence": False, "dps": 30, "potential": rows, "inner_integral": inner,
           "subordination": sub, "positive_max_rel_err": pos_max, "negative_min_rel_err": neg_min,
           "negative_min_rel_err_inner_perturbed": neg_inner, "negative_min_rel_err_subordination_power": neg_sub,
           "positive_pass": pos_max < 1e-12, "negative_caught": neg_min > 1e-2}
    with open(out, "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: res[k] for k in ["positive_max_rel_err", "negative_min_rel_err_inner_perturbed",
                                          "negative_min_rel_err_subordination_power", "positive_pass",
                                          "negative_caught"]}))
    return 0 if res["positive_pass"] and res["negative_caught"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
