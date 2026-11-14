"""S2 check 1: calibration identity W(E_tri) = 6K + lambda + 2*pi*mu (Lemma cal:energy-identity).

Inputs: the outward-rounded printed pairs of the certificate (units 1e-7) from
verification/data/certificate-record.txt (equal to our S1 positive run).
Interval for 6K+lambda+2*pi*mu is formed with exact Fractions and a rational
enclosure of pi. It is compared with two independent values of W for the
covolume-one triangular lattice in the a.e. B-S normalization:
  (a) Betermin-Sandier 2018 Section 7.3 closed form pi*log(2*sqrt(2)*pi/(sqrt3*Gamma(1/3)^3))  [docstring corrected at REVISE; the code was already right],
  (b) an Ewald (heat-kernel split) evaluation of pi*R, R = regular part of the
      mean-zero torus Green function with -Lap G = 2pi(delta - 1), area 1.
Positive control: (a) and (b) agree; (b) for the square lattice reproduces
Sandier-Serfaty Remark 1.5 (-0.1958 in SS normalization) after the 2pi scaling.
Negative controls: the square-lattice value and two mis-normalized triangular
values must fall outside the certificate interval.
Tier: interval from printed pairs is exact rational arithmetic; values (a),(b)
are 50-digit mpmath floats (tier X).
"""
from fractions import Fraction as Fr
import json
import sys

import mpmath as mp

mp.mp.dps = 50

UNIT = Fr(1, 10**7)
lam = (Fr(-67300312) * UNIT, Fr(-67300275) * UNIT)
mu = (Fr(4138830) * UNIT, Fr(4138838) * UNIT)
K = (Fr(-34823) * UNIT, Fr(-34809) * UNIT)
PI_LO = Fr(3141592653589793, 10**15)
PI_HI = Fr(3141592653589794, 10**15)


def interval_sum() -> tuple[Fr, Fr]:
    lo = 6 * K[0] + lam[0] + 2 * PI_LO * mu[0]
    hi = 6 * K[1] + lam[1] + 2 * PI_HI * mu[1]
    return lo, hi


def bs_closed_form() -> mp.mpf:
    # BS2018 p.26, expanded form: pi log pi - (pi/2) log 3 - 3 pi log Gamma(1/3) + (3/2) pi log 2
    # (= pi log(2 sqrt(2) pi / (sqrt(3) Gamma(1/3)^3)); a first transcription with sqrt(2 pi) was wrong)
    g = mp.gamma(mp.mpf(1) / 3)
    return mp.pi * mp.log(mp.pi) - mp.pi / 2 * mp.log(3) - 3 * mp.pi * mp.log(g) + mp.mpf(3) / 2 * mp.pi * mp.log(2)


def ewald_W(basis: list[list[mp.mpf]], s0: mp.mpf, nmax: int = 12) -> mp.mpf:
    """pi * R for a covolume-one lattice with basis vectors (rows)."""
    (u1, u2), (v1, v2) = basis
    det = u1 * v2 - u2 * v1
    assert abs(abs(det) - 1) < mp.mpf(10) ** -40
    # dual basis
    du = (v2 / det, -v1 / det)
    dv = (-u2 / det, u1 / det)
    real = mp.mpf(0)
    recip = mp.mpf(0)
    for i in range(-nmax, nmax + 1):
        for j in range(-nmax, nmax + 1):
            if i == 0 and j == 0:
                continue
            gx, gy = i * u1 + j * v1, i * u2 + j * v2
            r2 = gx * gx + gy * gy
            real += mp.e1(r2 / (4 * s0)) / 2
            kx, ky = i * du[0] + j * dv[0], i * du[1] + j * dv[1]
            k2 = kx * kx + ky * ky
            recip += mp.exp(-4 * mp.pi ** 2 * k2 * s0) / (2 * mp.pi * k2)
    R = -mp.euler / 2 + mp.log(4 * s0) / 2 + real - 2 * mp.pi * s0 + recip
    return mp.pi * R


def main() -> int:
    lo, hi = interval_sum()
    a = mp.sqrt(2 / mp.sqrt(3))
    tri = [[a, mp.mpf(0)], [a / 2, a * mp.sqrt(3) / 2]]
    sq = [[mp.mpf(1), mp.mpf(0)], [mp.mpf(0), mp.mpf(1)]]
    w_bs = bs_closed_form()
    w_tri_1 = ewald_W(tri, 1 / (4 * mp.pi))
    w_tri_2 = ewald_W(tri, 1 / (2 * mp.pi))
    w_sq = ewald_W(sq, 1 / (4 * mp.pi))
    # SS normalization: W_SS = W/(2pi) + (1/4) log(2pi)  (inverse of W = 2pi(W_SS - 1/4 log 2pi))
    ss_tri = w_tri_1 / (2 * mp.pi) + mp.log(2 * mp.pi) / 4
    ss_sq = w_sq / (2 * mp.pi) + mp.log(2 * mp.pi) / 4
    c_from_w = w_bs / mp.pi + mp.log(mp.pi) / 2 + mp.log(2)
    c_bhs = 2 * mp.log(2) + mp.log(mp.mpf(2) / 3) / 2 + 3 * mp.log(mp.sqrt(mp.pi) / mp.gamma(mp.mpf(1) / 3))

    def inside(x: mp.mpf) -> bool:
        return mp.mpf(lo.numerator) / lo.denominator <= x <= mp.mpf(hi.numerator) / hi.denominator

    neg_controls = {
        "square_lattice_W": w_sq,
        "triangular_SS_normalized_no_2pi_scaling": ss_tri,
        "triangular_missing_quarter_log_2pi_shift": 2 * mp.pi * ss_tri,
    }
    out = {
        "interval_6K_plus_lambda_plus_2pi_mu": [mp.nstr(mp.mpf(lo.numerator) / lo.denominator, 12),
                                               mp.nstr(mp.mpf(hi.numerator) / hi.denominator, 12)],
        "interval_width": mp.nstr(mp.mpf((hi - lo).numerator) / (hi - lo).denominator, 6),
        "W_tri_BS2018_closed_form": mp.nstr(w_bs, 20),
        "W_tri_ewald_s0_1over4pi": mp.nstr(w_tri_1, 20),
        "W_tri_ewald_s0_1over2pi": mp.nstr(w_tri_2, 20),
        "pos_ctl_ewald_vs_closed_form_absdiff": mp.nstr(abs(w_tri_1 - w_bs), 5),
        "pos_ctl_ewald_s0_independence_absdiff": mp.nstr(abs(w_tri_1 - w_tri_2), 5),
        "pos_ctl_SS_normalized_tri (SS Remark 1.5 says ~ -0.2011)": mp.nstr(ss_tri, 8),
        "pos_ctl_SS_normalized_square (SS Remark 1.5 says ~ -0.1958)": mp.nstr(ss_sq, 8),
        "closed_form_inside_certificate_interval": inside(w_bs),
        "ewald_inside_certificate_interval": inside(w_tri_1),
        "C_from_BS_Thm1.5_with_W_tri": mp.nstr(c_from_w, 15),
        "C_BHS_formula": mp.nstr(c_bhs, 15),
        "C_absdiff": mp.nstr(abs(c_from_w - c_bhs), 5),
        "negative_controls": {k: {"value": mp.nstr(v, 12), "inside": inside(v)} for k, v in neg_controls.items()},
    }
    ok = (out["closed_form_inside_certificate_interval"] and out["ewald_inside_certificate_interval"]
          and abs(w_tri_1 - w_bs) < mp.mpf(10) ** -20
          and not any(v["inside"] for v in out["negative_controls"].values()))
    out["all_checks_pass"] = ok
    print(json.dumps(out, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
