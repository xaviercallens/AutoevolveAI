"""S2 check 2: independent evaluation of B(l) (eq. comp:constant-B) and |c_1| < 1.

B(l) = -log R0 + pi R0^2/2 + sum_{m=1}^{38} V_m(R0), with V_m(R0) = (-1)^m c_m R0^{6m}
(Section 4: the m-th mode on a vertex ray equals (-1)^m c_m r^{k_m}; at r=R0 the edge
polynomial and the vertex value coincide).  c_m = (1/k) sum_{z != 0} z^{-k}, k = 6m, over
the covolume-one triangular lattice a(Z + Z e^{i pi/3}), a = sqrt(2/sqrt3).
c_m is summed in mpmath over max(|n|,|q|) <= D (D=256 for m=1, 48 otherwise, as in the paper)
plus the paper's tail bound; this is an independent float (tier X) evaluation, not the C++.
Compared with the certificate's printed pair bcon = (10464643, 10464644) * 1e-7.
Positive control: the m=1 coefficient also equals G_6/6 computed with a larger square (D=400).
Negative controls: (i) drop the m=1 mode, (ii) use lattice scale a=1 instead of sqrt(2/sqrt3);
both must fall outside the printed pair.
"""
import json
import sys

import mpmath as mp

mp.mp.dps = 30


def coeff(m: int, D: int, a: mp.mpf) -> mp.mpf:
    k = 6 * m
    s = mp.mpf(0)
    w0 = mp.mpc(mp.mpf(1) / 2, mp.sqrt(3) / 2)
    for n in range(0, D + 1):
        for q in range(-D, D + 1):
            if n == 0 and q <= 0:
                continue
            w = n + q * w0
            s += 2 * mp.re(w ** (-k))
    return s / (k * a ** k)


def main() -> int:
    a = mp.sqrt(2 / mp.sqrt(3))
    p = a / 2
    R0 = 2 * p / mp.sqrt(3)
    cs = {m: coeff(m, 256 if m == 1 else 48, a) for m in range(1, 39)}
    c1_big = coeff(1, 400, a)

    def B_of(cdict: dict[int, mp.mpf], skip_m1: bool = False) -> mp.mpf:
        val = -mp.log(R0) + mp.pi * R0 ** 2 / 2
        for m, c in cdict.items():
            if skip_m1 and m == 1:
                continue
            val += (-1) ** m * c * R0 ** (6 * m)
        return val

    B = B_of(cs)
    lo, hi = mp.mpf(10464643) / 10**7, mp.mpf(10464644) / 10**7
    B_skip1 = B_of(cs, skip_m1=True)
    a_wrong = mp.mpf(1)
    cs_wrong = {m: coeff(m, 48, a_wrong) for m in range(1, 39)}
    B_wrong_a = B_of(cs_wrong)
    out = {
        "c1": mp.nstr(cs[1], 20),
        "c1_D400_pos_ctl": mp.nstr(c1_big, 20),
        "abs_c1_lt_1": bool(abs(cs[1]) < 1),
        "c2": mp.nstr(cs[2], 12),
        "c38": mp.nstr(cs[38], 12),
        "B_l": mp.nstr(B, 15),
        "printed_bcon": ["1.0464643", "1.0464644"],
        "B_l_inside_printed_pair": bool(lo <= B <= hi),
        "neg_ctl_drop_m1": {"value": mp.nstr(B_skip1, 12), "inside": bool(lo <= B_skip1 <= hi)},
        "neg_ctl_wrong_a": {"value": mp.nstr(B_wrong_a, 12), "inside": bool(lo <= B_wrong_a <= hi)},
    }
    ok = (out["B_l_inside_printed_pair"] and out["abs_c1_lt_1"] and abs(c1_big - cs[1]) < mp.mpf(10) ** -10
          and not out["neg_ctl_drop_m1"]["inside"] and not out["neg_ctl_wrong_a"]["inside"])
    out["all_checks_pass"] = bool(ok)
    print(json.dumps(out, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
