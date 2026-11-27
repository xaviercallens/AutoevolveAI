#!/usr/bin/env python
"""Independent brute-force checks for the v2.1 pre-deposit review.

Everything here is recomputed from scratch (no import of run_pipeline.py) and compared
with results/dyadic_ns_regulator_elenchus/exact_dyadic_harness.json and with the numbers
written in the manuscript.
"""
import itertools
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np

ROOT = Path("/home/xavkal/xdev/AutoevolveAI")
H = json.load(open(ROOT / "results/dyadic_ns_regulator_elenchus/exact_dyadic_harness.json"))
out = {}
fails = []


def check(name, ok, detail=""):
    out[name] = {"ok": bool(ok), "detail": detail}
    print(("PASS " if ok else "FAIL ") + name + ("  -- " + detail if detail else ""))
    if not ok:
        fails.append(name)


# ---------------------------------------------------------------- Lambda_6 and triads
M = 6
Lam = [(x, y, z) for x in range(-M, M + 1) for y in range(-M, M + 1) for z in range(-M, M + 1)
       if 0 < x * x + y * y + z * z <= M * M]
LamSet = set(Lam)
check("lambda6_mode_count_924", len(Lam) == 924, f"brute force {len(Lam)}; harness {H['z3_depletion_screen_M6']['full_mode_count']}")


def ordered_triads(S):
    """Ordered (k1,k2,k3) in S^3 with k1+k2=k3."""
    Sset = set(S)
    c = 0
    for k1 in S:
        for k2 in S:
            if (k1[0] + k2[0], k1[1] + k2[1], k1[2] + k2[2]) in Sset:
                c += 1
    return c


def cross_scale_fraction(S):
    """Fraction of ordered triads with not all three |k|^2 equal (harness 'cross-scale')."""
    Sset = set(S)
    tot = 0
    cross = 0
    for k1 in S:
        n1 = sum(t * t for t in k1)
        for k2 in S:
            k3 = (k1[0] + k2[0], k1[1] + k2[1], k1[2] + k2[2])
            if k3 in Sset:
                tot += 1
                n2 = sum(t * t for t in k2)
                n3 = sum(t * t for t in k3)
                if not (n1 == n2 == n3):
                    cross += 1
    return tot, cross


T_full = ordered_triads(Lam)
check("lambda6_triad_count_398190", T_full == 398190, f"brute force {T_full}; harness {H['z3_depletion_screen_M6']['full_triad_count']}")

# Also the open ball (|k|^2 < 36) count, which the first-edition review flagged as 894.
Lam_open = [k for k in Lam if sum(t * t for t in k) < 36]
check("open_ball_count_894_is_the_stale_number", len(Lam_open) == 894, f"open ball {len(Lam_open)}")

# baseline M=2,3,4
for rec in H["z3_lattice_hypergraph_baseline"]:
    m = rec["M"]
    S = [k for k in Lam if sum(t * t for t in k) <= m * m] if m <= 6 else None
    if S is None:
        S = [(x, y, z) for x in range(-m, m + 1) for y in range(-m, m + 1) for z in range(-m, m + 1)
             if 0 < x * x + y * y + z * z <= m * m]
    t = ordered_triads(S)
    check(f"baseline_M{m}", len(S) == rec["mode_count"] and t == rec["ordered_triads"],
          f"modes {len(S)} vs {rec['mode_count']}, triads {t} vs {rec['ordered_triads']}")

PRIMES = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31}
SQUARES = {1, 4, 9, 16, 25, 36}


def nsq(k):
    return sum(t * t for t in k)


cands = {
    "Even Sublattice $(2\\mathbb{Z})^3$": [k for k in Lam if all(t % 2 == 0 for t in k)],
    "Coordinate Planes $k_x k_y k_z = 0$": [k for k in Lam if k[0] * k[1] * k[2] == 0],
    "Perfect-Square Shell $|k|^2 = m^2$": [k for k in Lam if nsq(k) in SQUARES],
    "Modular Shell $|k|^2 \\equiv 0 \\pmod 3$": [k for k in Lam if nsq(k) % 3 == 0],
    "Prime Norm-Square Shell $|k|^2 \\in \\mathbb{P}$": [k for k in Lam if nsq(k) in PRIMES],
    "Odd Norm-Square Shell $|k|^2 \\equiv 1 \\pmod 2$": [k for k in Lam if nsq(k) % 2 == 1],
}
harness_c = {c["candidate"]: c for c in H["z3_depletion_screen_M6"]["candidates"]}
paper_rows = {  # from Table 3 of the tex (|S|, f, |T|, null, D)
    "Even Sublattice $(2\\mathbb{Z})^3$": (122, 0.1320, 6642, 916.5, 7.2468),
    "Coordinate Planes $k_x k_y k_z = 0$": (300, 0.3247, 25518, 13628.2, 1.8724),
    "Perfect-Square Shell $|k|^2 = m^2$": (108, 0.1169, 846, 635.8, 1.3305),
    "Modular Shell $|k|^2 \\equiv 0 \\pmod 3$": (336, 0.3636, 20034, 19146.6, 1.0463),
    "Prime Norm-Square Shell $|k|^2 \\in \\mathbb{P}$": (236, 0.2554, 3792, 6634.5, 0.5716),
    "Odd Norm-Square Shell $|k|^2 \\equiv 1 \\pmod 2$": (466, 0.5043, 0, 51077.8, 0.0000),
}
for name, S in cands.items():
    tot, cross = cross_scale_fraction(S)
    f = Fr(len(S), len(Lam))
    null = float(f) ** 3 * T_full
    D = tot / null
    hc = harness_c[name]
    pr = paper_rows[name]
    ok = (len(S) == hc["mode_count"] == pr[0] and tot == hc["triad_count"] == pr[2]
          and abs(round(D, 4) - hc["depletion_D_float"]) < 1e-9 and abs(round(D, 4) - pr[4]) < 1e-9
          and abs(round(null, 1) - pr[3]) < 0.051 and abs(round(float(f), 4) - pr[1]) < 1e-9)
    cs = cross / tot if tot else None
    check("candidate::" + name, ok,
          f"|S|={len(S)} f={f} ({float(f):.4f}) |T|={tot} null={null:.1f} D={D:.4f} cross={cs}; harness cross={hc.get('cross_scale_triad_fraction_float')}")
    out["candidate::" + name]["values"] = dict(S=len(S), T=tot, D=D, null=null, cross=cs)

# random thinning control is seed-dependent; only check consistency of the harness record with itself
rc = harness_c["Random Thinning Control ($f \\approx 0.48$)"]
f = Fr(rc["mode_count"], 924)
check("random_control_internal_consistency",
      str(f) == rc["density_f_str"] and abs(rc["triad_count"] / (float(f) ** 3 * T_full) - rc["depletion_D_float"]) < 1e-4,
      f"f={f}, D recomputed {rc['triad_count'] / (float(f) ** 3 * T_full):.4f} vs {rc['depletion_D_float']}")

# Section 5 item 3 claims: 12 modes with |k|^2=2, every prime-shell triad involves a |k|^2=2 mode, no axis modes.
Sp = cands["Prime Norm-Square Shell $|k|^2 \\in \\mathbb{P}$"]
SpSet = set(Sp)
n_two = sum(1 for k in Sp if nsq(k) == 2)
through_two = all_tri = 0
for k1 in Sp:
    for k2 in Sp:
        k3 = (k1[0] + k2[0], k1[1] + k2[1], k1[2] + k2[2])
        if k3 in SpSet:
            all_tri += 1
            if 2 in (nsq(k1), nsq(k2), nsq(k3)):
                through_two += 1
check("prime_shell_12_modes_norm2_and_all_triads_through_norm2",
      n_two == 12 and through_two == all_tri and not any(k.count(0) == 2 for k in Sp),
      f"norm-2 modes {n_two}; triads through norm 2: {through_two}/{all_tri}")
# Square shell: "contains every coordinate-axis mode (±m,0,0)"
Ssq = cands["Perfect-Square Shell $|k|^2 = m^2$"]
axis = [k for k in Lam if k.count(0) == 2]
check("square_shell_contains_all_axis_modes", all(k in set(Ssq) for k in axis), f"{len(axis)} axis modes")
# densities as fractions in the text: 233/462, 9/77, 59/231
check("density_fractions_in_text", Fr(466, 924) == Fr(233, 462) and Fr(108, 924) == Fr(9, 77) and Fr(236, 924) == Fr(59, 231))
# prime list: all primes <= 36
check("prime_list_complete", PRIMES == {p for p in range(2, 37) if all(p % d for d in range(2, p))})

# ---------------------------------------------------------------- arithmetic witness 13 != 27
k = lambda n: n + 1
a = lambda n: 1 if n <= 2 else 0
prodOut = lambda n: k(n) ** 3 * a(n) ** 2 * a(n + 1)
prodIn = lambda n: 0 if n == 0 else k(n) ** 2 * k(n - 1) * a(n - 1) ** 2 * a(n)
terms = [prodIn(n) - prodOut(n) for n in range(3)]
check("arith_witness_terms_-1_-4_18_sum_13", terms == [-1, -4, 18] and sum(terms) == 13 and 3 * sum(prodOut(n) for n in range(2)) == 27, f"terms {terms}")
# NL-side check: sum k_n^2 a_n NL_n with a_3=0
NL = lambda n: -k(0) * a(0) * a(1) if n == 0 else k(n - 1) * a(n - 1) ** 2 - k(n) * a(n) * a(n + 1)
lhs = sum(k(n) ** 2 * a(n) * NL(n) for n in range(3))
check("arith_witness_NL_form_equals_13", lhs == 13, f"LHS of (3) = {lhs}")

# H2b witness: k=2^n, a=(1,2,3,0), N=2
kd = lambda n: 2 ** n
aw = [1, 2, 3, 0, 0]
flux = sum(Fr(kd(n) ** 2 * aw[n + 1] ** 2) for n in range(2))
Om2 = Fr(1, 2) * sum(kd(n) ** 2 * aw[n] ** 2 for n in range(3))
check("H2b_witness_40_vs_161_8", flux == 40 and Om2 == Fr(161, 2) and flux == Om2 / 2 - Fr(1, 4) and flux > Om2 / 4,
      f"flux {flux}, Omega_2 {Om2}, Omega_2/4 {Om2 / 4}={float(Om2 / 4)}")
S2 = sum(Fr(kd(n) ** 3 * aw[n] ** 2 * aw[n + 1]) for n in range(2))
check("H3_witness_S2_98_and_cubic_bound", S2 == 98 and S2 ** 2 == 9604 and 2 * Om2 ** 3 == Fr(4173281, 4) and S2 ** 2 <= 2 * Om2 ** 3,
      f"S_2={S2}, 2 Omega^3={2 * Om2 ** 3}")
# H1 witness: r=2, N=2, a=(1,2,3,0): LHS=294=(r^2-1)*98
NLd = lambda n: -kd(0) * aw[0] * aw[1] if n == 0 else kd(n - 1) * aw[n - 1] ** 2 - kd(n) * aw[n] * aw[n + 1]
lhs1 = sum(kd(n) ** 2 * aw[n] * NLd(n) for n in range(3))
check("H1_witness_294", lhs1 == 294 == 3 * 98, f"LHS {lhs1}")

# ---------------------------------------------------------------- unit sphere 15/17, 8/17
a0, a1 = Fr(15, 17), Fr(8, 17)
check("unit_sphere_normalization", a0 ** 2 + a1 ** 2 == 1)
S1 = 1 * a0 ** 2 * a1
D_half = 1 ** 3 * a0 ** 2 + 2 ** 3 * a1 ** 2
check("unit_sphere_3S1_5400_4913", 3 * S1 == Fr(5400, 4913), f"3S1={3 * S1}")
check("unit_sphere_D_12529_4913_eq_737_289", D_half == Fr(12529, 4913) == Fr(737, 289), f"D={D_half}")
check("unit_sphere_nu1_-7129_4913", 3 * S1 - D_half == Fr(-7129, 4913), f"{3 * S1 - D_half}")
check("unit_sphere_nu1_3_+3671_14739", 3 * S1 - Fr(1, 3) * D_half == Fr(3671, 14739), f"{3 * S1 - Fr(1, 3) * D_half}")
# The "more generally" formula 3S/D_alpha = 5400/(225+64*2^(2+2 alpha)) * 2^((1-2 alpha) m)
def ratio_exact(alpha_num, alpha_den, m):
    # use alpha = 1/2 (integer exponents) to avoid irrationals; general alpha check via floats below
    km = Fr(2) ** m
    km1 = Fr(2) ** (m + 1)
    S = km ** 3 * a0 ** 2 * a1
    e = Fr(2 + 2 * Fr(alpha_num, alpha_den))
    D = km ** e * a0 ** 2 + km1 ** e * a1 ** 2 if e.denominator == 1 else None
    return 3 * S / D


r_true = ratio_exact(1, 2, 0)
r_formula = Fr(5400, 225 + 64 * 2 ** 3)
check("unit_sphere_general_m_formula_matches_at_alpha_1_2_m_0", r_true == r_formula,
      f"true 3S/D = {r_true} = {float(r_true):.6f}; paper formula gives {r_formula} = {float(r_formula):.6f}; ratio formula/true = {r_formula / r_true}")
# float check for alpha=1/4, m=3
import math
alpha, m = 0.25, 3
km, km1 = 2.0 ** m, 2.0 ** (m + 1)
S = km ** 3 * float(a0) ** 2 * float(a1)
D = km ** (2 + 2 * alpha) * float(a0) ** 2 + km1 ** (2 + 2 * alpha) * float(a1) ** 2
f_paper = 5400 / (225 + 64 * 2 ** (2 + 2 * alpha)) * 2 ** ((1 - 2 * alpha) * m)
check("unit_sphere_general_m_formula_alpha_1_4_m_3", abs(3 * S / D - f_paper) < 1e-9,
      f"true {3 * S / D:.6f}, paper formula {f_paper:.6f}, factor {f_paper / (3 * S / D):.6f}")

# ---------------------------------------------------------------- Riccati table
def riccati(al):
    p = 1 / al - 1
    q = 4 - 1 / al
    r = 2 * q / (2 - p)
    s = r / 2
    rho = 3 - 1 / al
    th = 2 / rho
    return p, q, r, s, rho, th, th - 2


table = {  # alpha: (p,q,r,s,rho,theta*,delta)
    Fr(1, 4): (3, 0, 0, 0, -1, -2, -4),
    Fr(7, 20): (Fr(13, 7), Fr(8, 7), 16, 8, Fr(1, 7), 14, 12),
    Fr(3, 8): (Fr(5, 3), Fr(4, 3), 8, 4, Fr(1, 3), 6, 4),
    Fr(2, 5): (Fr(3, 2), Fr(3, 2), 6, 3, Fr(1, 2), 4, 2),
    Fr(9, 20): (Fr(11, 9), Fr(16, 9), Fr(32, 7), Fr(16, 7), Fr(7, 9), Fr(18, 7), Fr(4, 7)),
    Fr(1, 2): (1, 2, 4, 2, 1, 2, 0),
    Fr(3, 4): (Fr(1, 3), Fr(8, 3), Fr(16, 5), Fr(8, 5), Fr(5, 3), Fr(6, 5), Fr(-4, 5)),
    Fr(1): (0, 3, 3, Fr(3, 2), 2, 1, -1),
    Fr(5, 4): (Fr(-1, 5), Fr(16, 5), Fr(32, 11), Fr(16, 11), Fr(11, 5), Fr(10, 11), Fr(-12, 11)),
}
allok = True
for al, row in table.items():
    got = riccati(al)
    ok = all(Fr(g) == Fr(e) for g, e in zip(got, row))
    ok = ok and (Fr(got[2]) == (8 * al - 2) / (3 * al - 1)) and (got[3] - 1 == 1 / got[4]) and ((got[0] < 2) == (al > Fr(1, 3))) and ((got[4] >= 1) == (al >= Fr(1, 2)))
    if not ok:
        allok = False
        print("   riccati row mismatch", al, got, row)
check("riccati_table_9_rows_and_identities", allok)
# harness table consistency
hk = {Fr(r["alpha_str"]): r for r in H["fractional_riccati_exponent_table"]}
check("riccati_harness_rows_match_paper", set(hk) == set(table) and all(
    Fr(hk[al]["rho_exp_str"]) == Fr(table[al][4]) and Fr(hk[al]["theta_star_str"]) == Fr(table[al][5]) for al in table))

# ---------------------------------------------------------------- torus 2-section matrix and spectrum
def torus_check(m):
    G = [(x, y, z) for x in range(m) for y in range(m) for z in range(m)]
    Lam = [g for g in G if g != (0, 0, 0)]
    idx = {g: i for i, g in enumerate(Lam)}
    n = len(Lam)
    add = lambda u, v: ((u[0] + v[0]) % m, (u[1] + v[1]) % m, (u[2] + v[2]) % m)
    A = np.zeros((n, n), dtype=int)
    LamSet = set(Lam)
    for k1 in Lam:
        for k2 in Lam:
            k3 = add(k1, k2)
            if k3 in LamSet:
                for (i, j) in ((k1, k2), (k1, k3), (k2, k3)):
                    if i != j:
                        A[idx[i], idx[j]] += 1
                        A[idx[j], idx[i]] += 1
    J = np.ones((n, n), dtype=int)
    I = np.eye(n, dtype=int)
    P = np.zeros((n, n), dtype=int)
    for u in Lam:
        P[idx[u], idx[((-u[0]) % m, (-u[1]) % m, (-u[2]) % m)]] = 1
    closed_form = 6 * (J - I) - 2 * P
    ok_form = np.array_equal(A, closed_form)
    deg = A.sum(axis=1)
    ok_deg = np.all(deg == 6 * n - 8)
    ev = np.linalg.eigvalsh(A.astype(float))
    evs = sorted(set(np.round(ev, 6)))
    ok_spec = evs == [-8.0, -4.0, float(6 * n - 8)]
    mult = {v: int(np.sum(np.abs(ev - v) < 1e-6)) for v in evs}
    Lnorm = np.eye(n) - A / (6 * n - 8)
    lev = sorted(set(np.round(np.linalg.eigvalsh(Lnorm), 9)))
    expect = sorted({0.0, round(6 * n / (6 * n - 8), 9), round((6 * n - 4) / (6 * n - 8), 9)})
    ok_lap = lev == expect
    return n, ok_form, ok_deg, ok_spec, mult, ok_lap, lev


for m in (3, 5):
    n, ok_form, ok_deg, ok_spec, mult, ok_lap, lev = torus_check(m)
    check(f"torus_m{m}_A_eq_6(J-I)-2P_deg_spec_laplacian", ok_form and ok_deg and ok_spec and ok_lap,
          f"n={n} A==6(J-I)-2P:{ok_form} deg==6n-8:{ok_deg} spec {mult} laplacian {lev}")
# m=4 (even order, 2-torsion present): the closed form should FAIL -- the paper restricts to odd m
n, ok_form, ok_deg, ok_spec, mult, ok_lap, lev = torus_check(4)
check("torus_m4_even_order_closed_form_fails_as_expected", not ok_form, f"n={n} A==6(J-I)-2P:{ok_form} deg:{ok_deg} spec {mult}")
# n=2 edge case: G=Z_3 (allowed by '2 <= n' in the Lean spec and 'n >= 2' in the paper)
G = [1, 2]
A = np.zeros((2, 2), dtype=int)
for k1 in G:
    for k2 in G:
        k3 = (k1 + k2) % 3
        if k3 != 0:
            for (i, j) in ((k1, k2), (k1, k3), (k2, k3)):
                if i != j:
                    A[G.index(i), G.index(j)] += 1
                    A[G.index(j), G.index(i)] += 1
ev2 = sorted(np.linalg.eigvalsh(A.astype(float)))
check("torus_n2_edge_case_eigen_minus8_absent", ev2 == [-4.0, 4.0], f"G=Z_3, n=2: A={A.tolist()} eigenvalues {ev2} (no -8 eigenvalue: even zero-sum subspace is trivial)")

# harness torus rows
for rec in H["torus_two_section_spectrum"]:
    mm = rec["m"]
    n = mm ** 3 - 1
    ok = rec["nonzero_modes_n"] == n and rec["incidence_degree_6n_minus_8"] == 6 * n - 8 and Fr(rec["normalized_laplacian_even_eig_str"]) == Fr(6 * n, 6 * n - 8) and Fr(rec["normalized_laplacian_odd_eig_str"]) == Fr(6 * n - 4, 6 * n - 8)
    check(f"harness_torus_row_m{mm}", ok)

# ---------------------------------------------------------------- sigma rule table
for rec in H["dispersive_sigma_rule_table"]:
    s = rec["sigma"]
    ok = all(Fr(v) == Fr(2) ** ((3 - s) * int(kk[2:])) for kk, v in rec["ratios_by_cutoff"].items())
    check(f"sigma_{s}_ratio_2^((3-sigma)N)", ok, f"uniform={rec['cutoff_uniform_enstrophy_control']}")

# ---------------------------------------------------------------- dyadic shell progression (Fig 1)
prog = H["dyadic_shell_progression_N1_to_16"]
ok = True
for rec in prog:
    N = rec["N"]
    if rec["profile"] == "(n+1)/2^n":
        av = [Fr(n + 1, 2 ** n) for n in range(N + 1)] + [Fr(0)]
    else:
        av = [Fr(1), Fr(2), Fr(3), Fr(0)]
    kk = [Fr(2) ** n for n in range(N + 2)]
    Om = Fr(1, 2) * sum(kk[n] ** 2 * av[n] ** 2 for n in range(N + 1))
    SN = sum(kk[n] ** 3 * av[n] ** 2 * av[n + 1] for n in range(N))
    flux = sum(kk[n] ** 2 * av[n + 1] ** 2 for n in range(N))
    r1 = float(flux / (Om / 2))
    ok_row = (Fr(rec["Omega_N_str"]) == Om and Fr(rec["S_N_str"]) == SN and abs(r1 - rec["step1_ratio_to_half_Omega"]) < 1e-12
              and rec["step1_violates_quarter_Omega"] == (flux > Om / 4) and abs(float(SN ** 2 / (2 * Om ** 3)) - rec["cubic_ratio_S2_to_2Omega3"]) < 1e-12
              and SN ** 2 <= 2 * Om ** 3)
    if not ok_row:
        ok = False
        print("   progression mismatch at N", N, rec)
check("dyadic_progression_N1_16_recomputed", ok, f"{len(prog)} rows")

# ---------------------------------------------------------------- ratio-r table
for rec in H["ratio_enstrophy_production_verifications"]:
    r = Fr(rec["r_str"])
    N = rec["N"]
    # profile unknown from record: only check the stated lhs == rhs and prefactor
    check(f"ratio_r_{rec['r_str']}_residual_zero", rec["residual_zero"] and Fr(rec["lhs_str"]) == Fr(rec["rhs_str"]) and Fr(rec["prefactor_r2_minus_1_str"]) == r * r - 1)

json.dump(out, open(ROOT / "papers/dyadic_ns_regulator_elenchus/review_v21/brute_force_checks.json", "w"), indent=1, default=str)
print("\nFAILURES:", fails)
