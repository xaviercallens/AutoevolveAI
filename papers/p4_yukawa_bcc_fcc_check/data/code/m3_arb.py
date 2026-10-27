"""M3 positive control and Tier C (ball) re-run of Luo-Wei (arXiv 2610.31456) Lemmas A.5 and A.6.

Two independent evaluations of G(kappa) = 2 (E_kappa(L_B) - E_kappa(L_F)), unit covolume:
  (E) Ewald split (paper eq. 2.3/2.4):  G = sum_B [I(q,c) - J(q,c)] - sum_F [I(q,c) - J(q,c)],  c = kappa^2/(4 pi),
      I(q,c) = [e^{-k sqrt q} erfc(sqrt(pi q) - sqrt c) + e^{k sqrt q} erfc(sqrt(pi q) + sqrt c)] / (2 sqrt q),
      J(q,c) = e^{-pi q - c} / (pi q + c).
  (D) Direct real-space sum: G = sum_B e^{-k r}/r - sum_F e^{-k r}/r, r = |v|.
Shell multiplicities come from m3_shells.py (numpy enumeration, not the paper's table).
Tails: r3(k) <= 2 (2 sqrt k + 1)^2 (fix two coordinates; at most two choices for the third), so with
  |I - J| <= I + J <= 2 e^{-pi q}/(pi q) (both bounds hold for c >= 0) and e^{-k r}/r decreasing, the omitted shells are
  bounded by explicit sums/integrals evaluated in Arb (outward).  Every number is an Arb ball: Tier C (ball), NOT Lean.

usage: python -I m3_arb.py SHELLS.json OUT.json
"""

from __future__ import annotations

import json
import sys
import time
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / ".scratchpad" / "b2_pylib"))
import flint  # noqa: E402
from flint import arb, ctx  # noqa: E402

ctx.prec = 320

PI = arb.pi()
S3 = arb(2) ** (arb(1) / 3)          # 2^{1/3} = a^2
QF = S3                               # FCC squared length per n
QB = 1 / (2 * S3)                     # BCC squared length per l  (2^{-4/3})


def ar(x: Fraction | int | str) -> arb:
    f = Fraction(x)
    return arb(f.numerator) / arb(f.denominator)


def I_ker(q: arb, c: arb, kap: arb) -> arb:
    sq = q.sqrt()
    spq = (PI * q).sqrt()
    sc = c.sqrt()
    return ((-kap * sq).exp() * (spq - sc).erfc() + (kap * sq).exp() * (spq + sc).erfc()) / (2 * sq)


def J_ker(q: arb, c: arb) -> arb:
    return (-PI * q - c).exp() / (PI * q + c)


def r3_bound(k: int) -> arb:
    return 2 * (2 * arb(k).sqrt() + 1) ** 2


def ewald_G(kap: arb, fcc: dict[int, int], bcc: dict[int, int], nmax: int, lmax: int) -> arb:
    c = kap * kap / (4 * PI)
    g = arb(0)
    for ell, m in bcc.items():
        if ell <= lmax:
            q = QB * ell
            g += m * (I_ker(q, c, kap) - J_ker(q, c))
    for n, nn in fcc.items():
        if n <= nmax:
            q = QF * n
            g -= nn * (I_ker(q, c, kap) - J_ker(q, c))
    # tail: sum over omitted shells of count * 2 e^{-pi q}/(pi q), count(FCC n) <= r3_bound(2n), count(BCC l) <= r3_bound(l)
    # geometric majorant: for k > K, r3_bound(k) e^{-pi s k}/(pi s k) <= r3_bound(K+1)/(pi s (K+1)) * x^k * ((k)/(K+1))^0...
    # use the crude but valid  r3_bound(k)/(pi s k) <= 18/(pi s)  (k >= 1) and sum x^k geometric.
    tail = arb(0)
    for s, kmin in ((QF, nmax + 1), (QB, lmax + 1)):
        x = (-PI * s).exp()
        # r3_bound for FCC uses 2n: 2(2 sqrt(2n)+1)^2 <= 16n + 8 sqrt(2n) + 2 <= 26 n;  BCC: 8l+8 sqrt l+2 <= 18 l
        per = (26 if s is QF else 18) / (PI * s)
        tail += 2 * per * x ** kmin / (1 - x)
    return g + arb(0, tail.upper())


def direct_G(kap: arb, fcc: dict[int, int], bcc: dict[int, int], kf: int, kb: int) -> arb:
    g = arb(0)
    for ell, m in bcc.items():
        if ell <= kb:
            r = (QB * ell).sqrt()
            g += m * (-kap * r).exp() / r
    for n, nn in fcc.items():
        if n <= kf:
            r = (QF * n).sqrt()
            g -= nn * (-kap * r).exp() / r
    # tail: shells with integer norm k > K (k = 2n for FCC, k = l for BCC), physical r = sqrt(s' k) with s' = 2^{-2/3}
    # (FCC, |v|^2 = 2^{-2/3}|m|^2) or 2^{-4/3} (BCC). count <= r3_bound(k); f(k) = r3_bound(k) e^{-kap r}/r is
    # decreasing for k >= K (checked below), so sum_{k > K} f(k) <= int_K^inf f(x) dx; with u = sqrt x, beta = kap sqrt s',
    # int = (4/sqrt s') int_U^inf (2u+1)^2 e^{-beta u} du = (4/sqrt s') e^{-beta U}[(4U^2+4U+1)/beta + (8U+4)/beta^2 + 8/beta^3]
    tail = arb(0)
    for sp, kk in ((S3 ** -2, 2 * kf + 1), (QB, kb)):
        rs = sp.sqrt()
        beta = kap * rs
        uu = arb(kk).sqrt()
        tail += 4 / rs * (-beta * uu).exp() * ((4 * uu * uu + 4 * uu + 1) / beta + (8 * uu + 4) / beta ** 2 + 8 / beta ** 3)
    return g + arb(0, tail.upper())


def bisect_root(fn: Callable[[arb], arb], lo: Fraction, hi: Fraction, iters: int) -> tuple[Fraction, Fraction]:
    """Certified bracket: fn(lo) < 0 < fn(hi) as balls; shrink while signs are decided."""
    assert fn(ar(lo)) < 0 and fn(ar(hi)) > 0
    for _ in range(iters):
        mid = (lo + hi) / 2
        v = fn(ar(mid))
        if v < 0:
            lo = mid
        elif v > 0:
            hi = mid
        else:
            break
    return lo, hi


def lemma_a5(fcc: dict[int, int], bcc: dict[int, int]) -> dict[str, object]:
    a2 = S3
    b = QB
    N = {n: fcc[n] for n in range(1, 13)}
    M = {ell: m for ell, m in bcc.items() if ell <= 48}
    eps = ar(Fraction(1, 10 ** 18))
    worst6 = None
    fail6 = []
    for j in range(1000):
        v = 1 + ar(Fraction(j + 1, 10000))
        u = 1 + ar(Fraction(j, 10000))
        lhs = PI * a2 * sum((n * N[n] * (-PI * a2 * n * v).exp() for n in N), arb(0)) \
            - PI * b * sum((ell * M[ell] * (-PI * b * ell * u).exp() for ell in M), arb(0)) - eps
        slack = lhs - ar(Fraction(3, 1000))
        if not slack > 0:
            fail6.append(j)
        if worst6 is None or slack.lower() < worst6[1]:
            worst6 = (j, float(slack.lower()))
    worst7 = None
    fail7 = []
    for j in range(2000):
        v = ar(Fraction(11, 10)) + ar(Fraction(j + 1, 2000))
        u = ar(Fraction(11, 10)) + ar(Fraction(j, 2000))
        lhs = sum((M[ell] * (-PI * b * ell * v).exp() for ell in M), arb(0)) \
            - sum((N[n] * (-PI * a2 * n * u).exp() for n in N), arb(0)) - eps
        slack = lhs - ar(Fraction(1, 10000))
        if not slack > 0:
            fail7.append(j)
        if worst7 is None or slack.lower() < worst7[1]:
            worst7 = (j, float(slack.lower()))
    a8 = 8 * ((PI * a2 - 3 * PI * b) * ar(Fraction(21, 10))).exp() - ar(Fraction(25, 2))
    # tail / constant claims in the proof of Lemma 6.1
    t1 = 30 * sum((arb(n) / arb(49) ** n for n in range(13, 400)), arb(0))
    t2 = ar(Fraction(75, 2)) * sum((arb(ell) ** 2 * ar(Fraction(3, 10)) ** ell for ell in range(49, 1200)), arb(0))
    consts = {
        "exp(-pi a^2) < 1/49": bool((-PI * a2).exp() < ar(Fraction(1, 49))),
        "exp(-pi 2^-4/3) < 3/10": bool((-PI * b).exp() < ar(Fraction(3, 10))),
        "pi 2^-4/3 < 5/4": bool(PI * b < ar(Fraction(5, 4))),
        "a^2 > 3 2^-4/3": bool(a2 > 3 * b),
        "exp(-pi a^2 21/10) < 1/128": bool((-PI * a2 * ar(Fraction(21, 10))).exp() < ar(Fraction(1, 128))),
        "30 sum_{n>=13} n 49^-n (n<400) < 1e-18": [str(t1), bool(t1 < ar(Fraction(1, 10 ** 18)))],
        "75/2 sum_{l>=49} l^2 (3/10)^l (l<1200) < 1e-18": [str(t2), bool(t2 < ar(Fraction(1, 10 ** 18)))],
    }
    return {"A6_cells": 1000, "A6_fail": fail6, "A6_min_slack_lower": worst6,
            "A7_cells": 2000, "A7_fail": fail7, "A7_min_slack_lower": worst7,
            "A8_slack": str(a8), "A8_ok": bool(a8 > 0), "lemma61_constants": consts}


def lemma_a1(fcc: dict[int, int], bcc: dict[int, int]) -> dict[str, object]:
    c0 = arb(0)
    kap0 = arb(0)
    pf = arb(0)
    for n, nn in fcc.items():
        if n <= 300:
            pf += nn * I_ker(QF * n, c0, kap0) / 2
    for ell, m in bcc.items():
        if ell <= 900:
            pf += m * J_ker(QB * ell, c0) / 2
    # omitted: same crude geometric majorant as ewald_G (one copy each, halved)
    tail = arb(0)
    for s, kmin, k in ((QF, 301, 26), (QB, 901, 18)):
        x = (-PI * s).exp()
        tail += k / (PI * s) * x ** kmin / (1 - x)
    pf = pf + arb(0, tail.upper())
    i1625 = I_ker(ar(Fraction(16, 25)), c0, kap0)
    return {"P(L_F,0)": str(pf), "P_lt_55995e-6": bool(pf < ar(Fraction(55995, 10 ** 6))),
            "I(16/25,0)": str(i1625), "I_gt_7/125": bool(i1625 > ar(Fraction(7, 125))),
            "55995e-6_lt_7/125": Fraction(55995, 10 ** 6) < Fraction(7, 125)}


def main() -> int:
    t0 = time.time()
    sh = json.loads(Path(sys.argv[1]).read_text())
    fcc = {int(k): v for k, v in sh["fcc_N"].items()}
    bcc = {int(k): v for k, v in sh["bcc_M"].items()}
    out: dict[str, object] = {"prec_bits": ctx.prec, "flint": flint.__version__}

    def GE(k: arb) -> arb:
        return ewald_G(k, fcc, bcc, 60, 240)

    def GD(k: arb) -> arb:
        return direct_G(k, fcc, bcc, 1900, 4100)

    # decreasing-ness of the direct-sum tail integrand at the cut (f'(x) < 0 for x >= K holds when beta sqrt K > 2 + ...);
    # record beta*sqrt(K) for the audit: f(x) = (2 sqrt x + 1)^2 e^{-beta sqrt x}/sqrt x decreases once beta sqrt x > 2.
    out["direct_tail_beta_sqrtK_min"] = float(min(arb("1.7") * (S3 ** -2 * (2 * 1900 + 1)).sqrt(),
                                                arb("1.7") * (QB * 4100).sqrt()).lower())
    kap_lo = Fraction(1717921868469903, 10 ** 15)
    kap_hi = Fraction(1717921868469904, 10 ** 15)
    rows = {}
    for name, kq in (("A6_lower_903", kap_lo), ("A6_upper_904", kap_hi),
                     ("ctl_902", Fraction(1717921868469902, 10 ** 15)), ("ctl_905", Fraction(1717921868469905, 10 ** 15)),
                     ("coulomb_side_1", Fraction(1)), ("fcc_side_sqrtpi_3", Fraction(3))):
        ge = GE(ar(kq))
        gd = GD(ar(kq))
        rows[name] = {"kappa": str(kq), "G_ewald": ge.str(30, radius=True), "G_direct": gd.str(30, radius=True),
                      "overlap": bool(ge.overlaps(gd)), "G_ewald_mid": float(ge.mid()), "G_ewald_rad": float(ge.rad())}
    out["G_values"] = rows
    out["A6_claim_lower"] = bool(GE(ar(kap_lo)) < -ar(Fraction(1, 10 ** 19)))
    out["A6_claim_upper"] = bool(GE(ar(kap_hi)) > ar(Fraction(1, 10 ** 20)))
    out["A6_sign_lower_negative"] = bool(GE(ar(kap_lo)) < 0)
    out["A6_sign_upper_positive"] = bool(GE(ar(kap_hi)) > 0)
    lo, hi = bisect_root(GE, Fraction(17, 10), Fraction(174, 100), 90)
    out["kappa_star_bracket_ewald"] = [f"{float(lo):.17g}", f"{float(hi):.17g}",
                                       str(ar(lo).str(25)), str(ar(hi).str(25))]
    lo2, hi2 = bisect_root(GD, Fraction(17, 10), Fraction(174, 100), 75)
    out["kappa_star_bracket_direct"] = [str(ar(lo2).str(25)), str(ar(hi2).str(25))]
    # derivative dG/dkappa at kappa* (finite difference of balls, informative only)
    h = Fraction(1, 10 ** 12)
    out["dG_dkappa_fd"] = ((GE(ar(lo) + ar(h)) - GE(ar(lo) - ar(h))) / (2 * ar(h))).str(12)
    out["lemmaA5"] = lemma_a5(fcc, bcc)
    out["lemmaA1"] = lemma_a1(fcc, bcc)
    out["seconds"] = round(time.time() - t0, 1)
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
