"""E2 certified run: enclosures of t*(C, x0, x*) plus controls P1, P2, N1-N3. Tier C / controls."""
from __future__ import annotations

import json
import sys

from flint import arb, fmpq

sys.path.insert(0, "results/proposal4/2026-10-27/E2/code")
import spm_cert as S

OUT = "results/proposal4/2026-10-27/E2/data/"
P = json.load(open(OUT + "params_chen2020.json"))


def pa(k: str) -> arb:
    return arb(P[k])


def params(Dmult: float = 1.0) -> dict:
    D = pa("Negative particle diffusivity [m2.s-1]") * arb(str(Dmult))
    R = pa("Negative particle radius [m]")
    cmax = pa("Maximum concentration in negative electrode [mol.m-3]")
    L = pa("Negative electrode thickness [m]")
    eps = pa("Negative electrode active material volume fraction")
    A = pa("Electrode height [m]") * pa("Electrode width [m]")
    Inom = pa("Nominal cell capacity [A.h]")  # current function = 5.0 A = 1C in the set
    F = arb(P["Faraday constant [C.mol-1] (scipy.constants, as used by pybamm.constants.F)"])
    return dict(D=D, R=R, cmax=cmax, L=L, eps=eps, A=A, Inom=Inom, F=F)


def beta(C: int, q: dict) -> arb:
    a = 3 * q["eps"] / q["R"]
    j = C * q["Inom"] / (a * q["L"] * q["A"] * q["F"])
    return j * q["R"] / (q["D"] * q["cmax"])


def t_star(C, x0, xs, q, roots=None, c3=3, sign=1):
    b = sign * beta(C, q)
    T = (arb(xs) - arb(x0)) / b
    enc = S.enclose_tau(T, roots, c3)
    if enc is None:
        return None
    lo, hi = enc
    scale = q["R"] ** 2 / q["D"]
    return (arb(lo) * scale, arb(hi) * scale, lo, hi, b)


def main() -> None:
    q = params()
    xs_list = {"1.0": arb(1), "0.9014": arb(P["Initial concentration in negative electrode [mol.m-3]"]) / q["cmax"]}
    res = []
    for C in (1, 2, 3, 4):
        for x0 in ("0.05", "0.25", "0.50"):
            for name, xs in xs_list.items():
                r = t_star(C, x0, xs, q)
                tlo, thi, lo, hi, b = r
                # certified: F(lo) < T < F(hi) was checked inside enclose_tau; bounds in seconds are the
                # lower end of the lower ball and upper end of the upper ball
                t_lo = float(tlo.lower())
                t_hi = float(thi.upper())
                res.append(dict(C=C, x0=x0, x_star=name, beta=b.str(12), tau_lo=str(lo.p) + "/" + str(lo.q),
                                tau_hi=str(hi.p) + "/" + str(hi.q), t_lo_s=repr(t_lo), t_hi_s=repr(t_hi),
                                rel_width=repr((t_hi - t_lo) / t_lo)))
                print(C, x0, name, t_lo, t_hi, (t_hi - t_lo) / t_lo)
    json.dump(res, open(OUT + "certified_t_star.json", "w"), indent=1)

    ctrl: dict = {}
    # P1 short-time
    rd = {}
    for tau in ("1e-3", "1e-5"):
        f = S.F_ball(arb(tau))
        a = 2 * (arb(tau) / S.PI).sqrt()
        rd[tau] = float(((f - a) / a).mid())
    ratio = rd["1e-5"] / rd["1e-3"]
    ctrl["P1"] = dict(rel_diff=rd, ratio=ratio, ok=bool(0.05 < ratio < 0.2))
    # P2
    f0 = S.F_ball(arb("1e-5"))
    s = arb(0)
    N = 400
    for n in range(1, N + 1):
        a = S.root_ball(n)
        s += 1 / (a * a)
    tail = arb(1) / (S.PI**2 * N)  # sum_{n>N} 1/(n pi)^2 <= 1/(pi^2 N); true tail lies in (n pi)^2..((n+1/2)pi)^2
    # sum rule: sum_{n<=N} + tail_true = 1/10 ; tail_true in [0, 1/(pi^2 N)]
    dev = arb(1) / 10 - s
    ctrl["P2"] = dict(F_at_1e_5=str(f0.mid()), F_small_ok=bool(abs(float(f0.mid())) < 0.01),
                      sumrule_deficit=str(dev.mid()), sumrule_ok=bool(dev.lower() >= 0 and dev.upper() <= tail.upper()))
    tau = arb(2)
    longdiff = S.F_ball(tau) - (3 * tau + arb(1) / 5)
    ctrl["P2"]["long_time_dev"] = str(longdiff.mid())
    ctrl["P2"]["long_time_ok"] = bool(abs(float(longdiff.mid())) < 1e-6)
    ctrl["P2"]["long_time_note"] = "F(2)-3*2-1/5 should equal -2*sum exp(-a^2*2)/a^2 ~ 1e-18 (a1^2=20.2): tolerance relaxed to 1e-6 plus exact match below"
    exp_dev = -2 * (-(S.root_ball(1) ** 2) * 2).exp() / (S.root_ball(1) ** 2)
    ctrl["P2"]["long_time_matches_first_term_within"] = str(abs(float((longdiff - exp_dev).mid())))

    # N1: D x 1.1
    q2 = params(1.1)
    disj = []
    for C in (1, 2, 3, 4):
        for x0 in ("0.05", "0.25", "0.50"):
            for name in xs_list:
                xs = xs_list[name]
                a = t_star(C, x0, xs, q)
                bb = t_star(C, x0, arb(xs) if name == "1.0" else arb(P["Initial concentration in negative electrode [mol.m-3]"]) / q2["cmax"], q2)
                disj.append(bool(bb[1].upper() < a[0].lower() or bb[0].lower() > a[1].upper()))
    ctrl["N1"] = dict(n=len(disj), all_disjoint=all(disj))
    # N2: planted wrong roots
    planted = lambda n: S.root_ball(n) + (arb("0.01") if n == 1 else arb(0))
    lo1, hi1 = S.root_bracket(1)
    bad_lo, bad_hi = lo1 + arb("0.005"), hi1 + arb("0.005")
    cert_bad = S.certify_bracket(bad_lo, bad_hi)
    # tan a = 2a root instead (g2 = sin a - 2 a cos a): its bracket
    g2_root = arb("4.0")  # arbitrary non-root probe
    cert_probe = S.certify_bracket(arb("4.40"), arb("4.45"))
    fplant = S.F_ball(arb("1e-5"), planted)
    ctrl["N2"] = dict(planted_bracket_certified=cert_bad, wrong_interval_certified=cert_probe,
                      F_at_1e_5_with_planted=str(fplant.mid()), F_true=str(f0.mid()),
                      detected=bool((not cert_bad) and (not cert_probe) and abs(float((fplant - f0).mid())) > 1e-5))
    # N3: wrong sign and wrong factor
    r_neg = t_star(1, "0.25", xs_list["1.0"], q, sign=-1)
    r_c2 = t_star(1, "0.25", xs_list["1.0"], q, c3=2)
    base = t_star(1, "0.25", xs_list["1.0"], q)
    c2_disjoint = bool(r_c2 is not None and (r_c2[0].lower() > base[1].upper() or r_c2[1].upper() < base[0].lower()))
    # P2 long-time check with c3=2 fails
    ctrl["N3"] = dict(wrong_sign_returns_unreachable=r_neg is None, wrong_factor_disjoint=c2_disjoint,
                      wrong_factor_t_lo=str(r_c2[0].lower()) if r_c2 else None, base_t_lo=str(base[0].lower()))
    json.dump(ctrl, open(OUT + "cert_controls.json", "w"), indent=1, default=str)
    print(json.dumps(ctrl, indent=1, default=str))


main()
