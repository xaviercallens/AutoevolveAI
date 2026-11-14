"""S2 check 3: exact rational re-verification of the hand constants in Section 5 (tails),
Section 7 (b < d_*) and the Appendix (Section 8).

Every comparison below is evaluated with Python Fractions or sympy exact arithmetic
(tier X-exact: exact arithmetic run by us; not kernel-checked).  Polynomial suprema on
intervals are computed exactly from critical points (sympy real roots).
Negative controls: each family has a deliberately tightened variant that must FAIL.
"""
from fractions import Fraction as Fr
import json
import sys

import sympy as sp

results: dict[str, dict[str, object]] = {}


def record(name: str, claim: str, value: object, passed: bool) -> None:
    results[name] = {"claim": claim, "value": str(value), "pass": bool(passed)}


def poly_sup_abs(expr: sp.Expr, var: sp.Symbol, lo: sp.Expr, hi: sp.Expr) -> sp.Expr:
    pts = [lo, hi]
    for r in sp.real_roots(sp.Poly(sp.diff(expr, var), var)):
        if lo <= r <= hi:
            pts.append(r)
    return max(sp.Abs(expr.subs(var, x)) for x in pts)


def main() -> int:
    y, z = sp.symbols("y z", real=True)
    S = 10 * y**3 - 15 * y**4 + 6 * y**5
    sup_S = [poly_sup_abs(sp.diff(S, y, j), y, 0, 1) for j in range(4)]
    record("S_derivs", "|S|<=1,|S'|<=2,|S''|<=6,|S'''|<=60 on [0,1]", [sp.nsimplify(s) for s in sup_S],
           sup_S[0] <= 1 and sup_S[1] <= 2 and sup_S[2] <= 6 and sup_S[3] <= 60)
    record("NEG_S3_tight", "NEGATIVE CONTROL: |S'''|<=59 must fail", sup_S[3], not (sup_S[3] <= 59))

    hs = sp.Rational(3, 40)
    P = z - 6 * z**3 / hs**2 + 8 * z**4 / hs**3 - 3 * z**5 / hs**4
    Q = z**2 / 2 - 3 * z**3 / (2 * hs) + 3 * z**4 / (2 * hs**2) - z**5 / (2 * hs**3)
    PQ_end = [sp.diff(P, z, j).subs(z, 0) for j in range(3)] + [sp.diff(Q, z, j).subs(z, 0) for j in range(3)]
    PQ_hs = [sp.diff(P, z, j).subs(z, hs) for j in range(3)] + [sp.diff(Q, z, j).subs(z, hs) for j in range(3)]
    record("PQ_matching", "(P,P',P'')(0)=(0,1,0),(Q,Q',Q'')(0)=(0,0,1), all six vanish at h_s",
           [PQ_end, PQ_hs], PQ_end == [0, 1, 0, 0, 0, 1] and all(v == 0 for v in PQ_hs))
    supP = [poly_sup_abs(sp.diff(P, z, j), z, 0, hs) for j in range(4)]
    supQ = [poly_sup_abs(sp.diff(Q, z, j), z, 0, hs) for j in range(4)]
    record("PQ_derivs", "|P^(j)|<=2e5, |Q^(j)|<=4000 (j<=3) on [0,h_s]", [supP, supQ],
           max(supP) <= 200000 and max(supQ) <= 4000)

    tau_scale = sp.Rational(3, 40)
    tau_b = [sup_S[j] / tau_scale**j for j in range(4)]
    record("tau_derivs", "|tau^(j)| <= 1,27,1067,142223", tau_b,
           tau_b[0] <= 1 and tau_b[1] <= 27 and tau_b[2] <= 1067 and tau_b[3] <= 142223)
    record("leibniz_factor", "1+3*27+3*1067+142223 = 145506 < 1e6", 1 + 3 * 27 + 3 * 1067 + 142223,
           1 + 3 * 27 + 3 * 1067 + 142223 == 145506 and 145506 < 10**6)

    # rational bounds on p, R0, l, a
    p4, R04 = Fr(1, 12), Fr(4, 27)
    ok = (Fr(537, 1000)**4 < p4 < Fr(538, 1000)**4) and (Fr(620, 1000)**4 < R04 < Fr(621, 1000)**4)
    record("p_R0_bounds", ".537<p<.538, .620<R0<.621 from p^4=1/12, R0^4=4/27", "", ok)
    # l = R0 + .076; l/a < 13/20 with a = 2p: (R0+.076) < (13/20)*2p sufficient with R0<.621, p>.537
    record("l_over_a", "l/a < 13/20 (using R0<.621, p>.537)", Fr(621 + 76, 1000) / (2 * Fr(537, 1000)),
           Fr(621 + 76, 1000) < Fr(13, 20) * 2 * Fr(537, 1000))
    record("R0_over_a", "R0/a = 1/sqrt3 < 289/500", Fr(289, 500)**2, Fr(1, 3) < Fr(289, 500)**2)

    # coefficient bracket at d=12
    br = 6 + 2 * Fr(1, 3**6) + 24 * Fr(4, 3)**6 * Fr(2)**(1 - 12)
    record("c_bracket_d12", "6+2*3^-6+24(4/3)^6 2^-11 = 6+50/729 < 7", br, br == 6 + Fr(50, 729) and br < 7)
    record("NEG_c_bracket", "NEGATIVE CONTROL: bracket < 6.05 must fail", br, not (br < Fr(605, 100)))

    k = 234
    lmin = Fr(69, 100)
    c3 = 7 * (1 / lmin**3 + Fr(60) / (k * lmin**2) + Fr(1800) / (k**2 * lmin) + Fr(60000) / k**3)
    record("U_third_coef", "7(l^-3+60/(kl^2)+1800/(k^2 l)+60000/k^3) < 25.445 at l=.69,k=234", float(c3),
           c3 < Fr(25445, 1000))
    record("NEG_U_third_coef", "NEGATIVE CONTROL: < 25.43 must fail", float(c3), not (c3 < Fr(2543, 100)))
    c0 = Fr(7, k**3)
    c1 = 7 * (1 / lmin + Fr(20, k)) / k**2
    c2 = 7 * (Fr(k) / lmin**2 + 40 / lmin + Fr(600, k)) / k**2
    record("U_low_orders", "orders 0,1,2 coefficients below .000001,.000197,.070572", [float(c0), float(c1), float(c2)],
           c0 < Fr(1, 10**6) and c1 < Fr(197, 10**6) and c2 < Fr(70572, 10**6))

    cc = Fr(6, 100)
    # |q| <= (7/k + .84k + .0168k^3)2^-k etc.; b''' <= 60/c^3|q| + 18/c^2|q'| + 6/c|q''|
    for kk in (234, 240, 600, 3000):
        q0 = Fr(7, kk) + Fr(84, 100) * kk + Fr(168, 10000) * kk**3
        q1 = 14 * kk + Fr(56, 100) * kk**3
        q2 = Fr(28, 3) * kk**3
        bb = (60 / cc**3) * q0 + (18 / cc**2) * q1 + (6 / cc) * q2
        if not bb < 8500 * kk**3:
            record("b_inner_third", "b''' < 8500 k^3 2^-k", (kk, float(bb / kk**3)), False)
            break
    else:
        record("b_inner_third", "b''' < 8500 k^3 2^-k (checked k=234,240,600,3000; ratio decreasing in k)",
               float(((60 / cc**3) * (Fr(7, 234) + Fr(84, 100) * 234 + Fr(168, 10000) * 234**3)
                      + (18 / cc**2) * (14 * 234 + Fr(56, 100) * 234**3) + (6 / cc) * Fr(28, 3) * 234**3) / 234**3), True)
    pm = Fr(537, 1000)
    record("X_le_1.2p", ".02p+.0001 < .04p^2 at p=.537 (increasing slack in p)", "",
           Fr(2, 100) * pm + Fr(1, 10000) < Fr(4, 100) * pm**2)
    v597 = 7 * (8 * Fr(55, 100)**3 * 2**6 + Fr(12) * Fr(55, 100) * 2**4 / 234**2)
    record("V_near_p", "7(8(.55)^3 2^6 + 12(.55)2^4/234^2) < 597", float(v597), v597 < 597)
    zp = Fr(63, 100) / Fr(103, 1000)
    zpp = Fr(54, 100)**2 / Fr(103, 1000)**3
    zppp = 3 * Fr(54, 100)**2 * Fr(63, 100) / Fr(103, 1000)**5
    record("z_derivs", "|z'|<=7,|z''|<=300,|z'''|<=60000 from sqrt(r^2-p^2)>.103,p<.54,r<.63",
           [float(zp), float(zpp), float(zppp)], zp <= 7 and zpp <= 300 and zppp <= 60000)
    sq = Fr(538, 1000) + Fr(1, 100)
    record("sqrt_gt_.103", "sqrt((p+.01)^2-p^2) > .103 (r^2-p^2 >= .02p+.0001 > .103^2 at p>.537)", "",
           Fr(2, 100) * pm + Fr(1, 10000) > Fr(103, 1000)**2)
    v20000 = 7 * (8 * 343 + Fr(12 * 7 * 300, 234) + Fr(2 * 60000, 234**2))
    record("V_outer", "7(8*343+12*7*300/234+2*60000/234^2) < 20000", float(v20000), v20000 < 20000)
    record("extension", "(1+200000+4000)*3e6 < 7e11", (1 + 200000 + 4000) * 3 * 10**6,
           (1 + 200000 + 4000) * 3 * 10**6 < 7 * 10**11)

    # weighted sum frak a
    pairs = [(2, Fr(13, 20)), (3, Fr(1, 2)), (5, Fr(3, 5)), (2, Fr(289, 500))]
    pref = [Fr(30), Fr(3 * 10**6), Fr(5600), Fr(7 * 10**11)]
    ratios = [Fr(241, 235)**4 * Fr(240, 234)**s * r**6 for s, r in pairs]
    record("ratios_lt_0.1", "rho_i(234) < 1/10 for the four pairs", [float(x) for x in ratios],
           all(x < Fr(1, 10) for x in ratios))
    T0 = sum(10**6 * c * 235**4 * Fr(234)**s * r**234 for c, (s, r) in zip(pref, pairs))
    record("T0", "T0 = first weighted summand < 1.56e-21", float(T0), T0 < Fr(156, 10**23))
    record("NEG_T0", "NEGATIVE CONTROL: T0 < 1.0e-21 must fail", float(T0), not (T0 < Fr(1, 10**21)))
    # exact partial sum + geometric remainder (independent of the 10/9 shortcut)
    part = Fr(0)
    for j in range(62):
        kk = 234 + 6 * j
        part += sum(10**6 * c * (kk + 1)**4 * Fr(kk)**s * r**kk for c, (s, r) in zip(pref, pairs))
    rem = Fr(0)
    for c, (s, r) in zip(pref, pairs):
        t606 = 10**6 * c * 607**4 * Fr(606)**s * r**606
        rho606 = Fr(613, 607)**4 * Fr(612, 606)**s * r**6
        rem += t606 / (1 - rho606)
    A_up = part + rem
    record("frak_a", "frak a <= P600 + R606 < 2e-21 (and 10/9*T0 < 2e-21)", float(A_up),
           A_up < Fr(2, 10**21) and Fr(10, 9) * T0 < Fr(2, 10**21))
    Asym = sp.Symbol("A")
    W = 4 * Asym
    F = 2 * sp.Rational(22, 7) * (3 * W + 16 * Asym) + sp.Rational(1, 2) * (
        60000 * W + 8 * Asym + 12 * 2 * 10**6 * W + 48 * (6000 + W) * Asym + 8 * 2 * 10**6 * Asym + 16 * Asym**2)
    Fexp = sp.expand(F)
    target = sp.expand(Asym * (56264180 + 104 * Asym))
    record("F_identity", "F(A,4A) = A(56264180 + 104A)", Fexp, sp.simplify(Fexp - target) == 0)
    A0 = sp.Rational(2, 10**21)
    record("f_second_deriv", "2F(A0,4A0) < 2.4e-13", float(2 * Fexp.subs(Asym, A0)), 2 * Fexp.subs(Asym, A0) < sp.Rational(24, 10**14))
    e2 = 2 * (16 * 2 * 10**6 * A0 + 32 * A0**2)
    record("e_second_deriv", "2(16*2e6*A0+32A0^2) < 1.3e-13", float(e2), e2 < sp.Rational(13, 10**14))
    dB = Fr(7, 234) * Fr(289, 500)**234 / (1 - Fr(289, 500)**6)
    record("DeltaB_l", "(7/234)(289/500)^234/(1-(289/500)^6) < 6.075e-58", float(dB), dB < Fr(6075, 10**61))
    # [0,b]: sum_{k=12,18,...} 7k^2 (2/7)^(k-3) < .014
    s = Fr(0)
    for kk in range(12, 12 + 6 * 60, 6):
        s += 7 * kk**2 * Fr(2, 7)**(kk - 3)
    last_ratio = Fr(12 + 6 * 60, 12 + 6 * 59)**2 * Fr(2, 7)**6
    tail = 7 * (12 + 6 * 60)**2 * Fr(2, 7)**(12 + 6 * 60 - 3) / (1 - last_ratio)
    record("inner_B1_sum", "sum_{k=12,18,..} 7k^2(2/7)^(k-3) < .014", float(s + tail), s + tail < Fr(14, 1000))
    # b < d_* = 1/(2 sqrt(pi)) from pi < 3.1416 : 4 b^2 * 3.1416 < 1
    b = Fr(28209, 100000)
    record("b_lt_dstar", "4 b^2 * 3.1416 < 1 (so b < 1/(2 sqrt pi))", float(4 * b**2 * Fr(31416, 10000)),
           4 * b**2 * Fr(31416, 10000) < 1)
    record("NEG_b_lt_dstar", "NEGATIVE CONTROL: b'=0.282095 must fail 4 b'^2 pi_lo < 1 (pi_lo=3.14159)",
           float(4 * Fr(282095, 10**6)**2 * Fr(314159, 10**5)), not (4 * Fr(282095, 10**6)**2 * Fr(314159, 10**5) < 1))
    # domain facts used in Section 6
    record("sqrt_b2_065_gt_l", "b^2+.65^2 > .697^2 (so t>l when s>=.65)", float(b**2 + Fr(65, 100)**2),
           b**2 + Fr(65, 100)**2 > Fr(697, 1000)**2)
    record("D0_contains_stationary", ".52528<p<.54930 and .29420<x0=R0/2<.32621", "",
           Fr(52528, 10**5)**4 < p4 < Fr(54930, 10**5)**4 and (2 * Fr(29420, 10**5))**4 < R04 < (2 * Fr(32621, 10**5))**4)

    # Section 6 elementary-function remainders vs q^-1 = 2^-144
    qinv = Fr(1, 2**144)
    logrem = 2 * Fr(3, 5)**401 / (401 * (1 - Fr(3, 5)**2))
    record("log_remainder", "2(3/5)^401/(401(1-(3/5)^2)) < 2^-144 (comp:logarithm)", float(logrem), logrem < qinv)
    pirem = [Fr(1, v**301 * 301) for v in (5, 239)]
    record("pi_remainder", "v^-301/301 < 2^-144 for v=5,239 (comp:pi)", [float(x) for x in pirem], all(x < qinv for x in pirem))

    allpass = all(v["pass"] for v in results.values())
    print(json.dumps({"results": results, "all_pass": allpass}, indent=1))
    return 0 if allpass else 1


if __name__ == "__main__":
    sys.exit(main())
