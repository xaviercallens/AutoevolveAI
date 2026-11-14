"""M3 extra Tier C checks: Lemma A.6 with the paper's OWN truncation (FCC n<=12, BCC l<=48) plus its printed tail
7e-21; the printed tail inequality in exact rationals; Lemma A.3 (A.4) endpoint exponentials; printed count
arithmetic; shell bounds N_n < 30n, M_l < 30l over the enumerated table.

usage: python -I m3_extra.py SHELLS.json OUT.json
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m3_arb  # noqa: E402
from m3_arb import ar, arb, ewald_G  # noqa: E402


def trunc_G(kap: arb, fcc: dict[int, int], bcc: dict[int, int]) -> arb:
    c = kap * kap / (4 * m3_arb.PI)
    g = arb(0)
    for ell, m in bcc.items():
        if ell <= 48:
            q = m3_arb.QB * ell
            g += m * (m3_arb.I_ker(q, c, kap) - m3_arb.J_ker(q, c))
    for n, nn in fcc.items():
        if n <= 12:
            q = m3_arb.QF * n
            g -= nn * (m3_arb.I_ker(q, c, kap) - m3_arb.J_ker(q, c))
    return g


def main() -> int:
    sh = json.loads(Path(sys.argv[1]).read_text())
    fcc = {int(k): v for k, v in sh["fcc_N"].items()}
    bcc = {int(k): v for k, v in sh["bcc_M"].items()}
    out: dict[str, object] = {}
    tail_q = 60 * Fraction(1, 49) ** 13 / (1 - Fraction(1, 49)) + 60 * Fraction(3, 10) ** 49 / (1 - Fraction(3, 10))
    out["A6_printed_tail_exact"] = f"{float(tail_q):.6e}"
    out["A6_printed_tail_lt_7e-21"] = tail_q < Fraction(7, 10 ** 21)
    k903 = ar(Fraction(1717921868469903, 10 ** 15))
    k904 = ar(Fraction(1717921868469904, 10 ** 15))
    g3 = trunc_G(k903, fcc, bcc)
    g4 = trunc_G(k904, fcc, bcc)
    t = ar(Fraction(7, 10 ** 21))
    out["A6_trunc_G903"] = g3.str(20, radius=True)
    out["A6_trunc_G904"] = g4.str(20, radius=True)
    out["A6_trunc_lower_ok (G+7e-21 < -1e-19)"] = bool(g3 + t < -ar(Fraction(1, 10 ** 19)))
    out["A6_trunc_upper_ok (G-7e-21 > 1e-20)"] = bool(g4 - t > ar(Fraction(1, 10 ** 20)))
    out["A6_trunc_upper_slack"] = (g4 - t - ar(Fraction(1, 10 ** 20))).str(6)
    out["A6_trunc_lower_slack"] = (-ar(Fraction(1, 10 ** 19)) - g3 - t).str(6)
    full3 = ewald_G(k903, fcc, bcc, 60, 240)
    full4 = ewald_G(k904, fcc, bcc, 60, 240)
    out["A6_actual_omitted_tail_903"] = (full3 - g3).str(6)
    out["A6_actual_omitted_tail_904"] = (full4 - g4).str(6)
    # Lemma A.3 (A.4)
    a1 = Fraction(-7394735416760227, 2 ** 53)
    a2 = Fraction(-2158713440539059, 2 ** 50)
    be = Fraction(5182419497180053, 2 ** 54)
    ea1, ea2, eb = ar(a1).exp(), ar(a2).exp(), ar(be).exp()
    out["A4_e^alpha1"] = ea1.str(25)
    out["A4_e^alpha1 <= 11/25"] = bool(ea1 <= ar(Fraction(11, 25)))
    out["A4_e^alpha1 - 11/25"] = (ea1 - ar(Fraction(11, 25))).str(6)
    out["A4_e^alpha2"] = ea2.str(25)
    out["A4_e^alpha2 <= 147/1000"] = bool(ea2 <= ar(Fraction(147, 1000)))
    out["A4_e^alpha2 - 147/1000"] = (ea2 - ar(Fraction(147, 1000))).str(6)
    out["A4_e^beta"] = eb.str(25)
    out["A4_e^beta >= 4/3"] = bool(eb >= ar(Fraction(4, 3)))
    out["A4_e^beta - 4/3"] = (eb - ar(Fraction(4, 3))).str(6)
    nj = [20037, 15481, 10757, 8852, 7032, 5523, 4295, 3409, 4154, 4503]
    out["A3_sum_nj"] = sum(nj)
    out["A3_sum_nj_eq_84043"] = sum(nj) == 84043
    out["A4_1118+193+86+5828"] = 1118 + 193 + 86 + 5828
    out["A4_counts_eq_7225"] = 1118 + 193 + 86 + 5828 == 7225
    out["N_lt_30n_all_enumerated"] = all(v < 30 * n for n, v in fcc.items())
    out["M_lt_30l_all_enumerated"] = all(v < 30 * ell for ell, v in bcc.items())
    out["M_le_18l_all_enumerated"] = all(v <= 18 * ell for ell, v in bcc.items())
    out["enumerated_ranges"] = [max(fcc), max(bcc)]
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
