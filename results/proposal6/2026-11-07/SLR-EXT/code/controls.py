"""Positive and negative controls for both checkers (run before any n >= 18 counts)."""
from __future__ import annotations

import json
import os
import random
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from slr_exact import covers_open, gamma_exact  # noqa: E402

C_CHECKER = os.path.join(HERE, "check_cover")
OUT = os.path.join(os.path.dirname(HERE), "controls")


def write(name: str, v: list[int], a: list[int], D: int, dp: int, dq: int) -> str:
    path = os.path.join(OUT, name)
    with open(path, "w") as fh:
        json.dump({"n": len(v), "v": v, "a": a, "D": D, "delta_num": dp, "delta_den": dq}, fh)
    return path


def both(name: str, v: list[int], a: list[int], D: int, dp: int, dq: int) -> tuple[bool, bool, str]:
    p = write(name, v, a, D, dp, dq)
    ok1 = covers_open(v, a, D, dp, dq)[0]
    r = subprocess.run([C_CHECKER, p], capture_output=True, text=True)
    return ok1, r.returncode == 0, r.stdout.strip()


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    res: dict = {"positive": [], "negative": []}

    # P1: gamma(1..5; s) = 15/94 at s = (0,46,38,47,72)/94
    v5 = [1, 2, 3, 4, 5]
    a5 = [0, 46, 38, 47, 72]
    g, t = gamma_exact(v5, [Fraction(x, 94) for x in a5])
    c16 = both("P1_n5_delta_1_6.json", v5, a5, 94, 1, 6)
    c1594 = both("N_P1_n5_delta_15_94.json", v5, a5, 94, 15, 94)
    res["positive"].append({"id": "P1", "gamma_exact": str(g), "argmax_t": str(t), "expected": "15/94",
                            "pass_gamma": g == Fraction(15, 94),
                            "cover_at_1/6": c16[:2], "pass_cover": c16[0] and c16[1]})
    res["negative"].append({"id": "N0", "what": "P1 shifts at delta = gamma = 15/94 exactly (open arcs must miss argmax)",
                            "checker1": c1594[0], "checker2": c1594[1], "pass": (not c1594[0]) and (not c1594[1])})

    # P2: gamma_sh(2,3,4,5,6,8) <= 2/15 with s = (0,29,17,0,16,22)/30
    v6 = [2, 3, 4, 5, 6, 8]
    a6 = [0, 29, 17, 0, 16, 22]
    g6, t6 = gamma_exact(v6, [Fraction(x, 30) for x in a6])
    c17 = both("P2_v234568_delta_1_7.json", v6, a6, 30, 1, 7)
    res["positive"].append({"id": "P2", "gamma_exact": str(g6), "argmax_t": str(t6), "expected": "2/15",
                            "pass_gamma": g6 == Fraction(2, 15), "cover_at_1/7": c17[:2], "pass_cover": c17[0] and c17[1]})

    # N1: s = 0 for [n] at delta = 1/(n+1) must NOT certify, n = 2..94
    n1 = []
    for n in range(2, 95):
        v = list(range(1, n + 1))
        r = both(f"N1_s0_n{n:03d}.json", v, [0] * n, 1, 1, n + 1)
        n1.append((n, r[0], r[1]))
        if n <= 12:
            ge = gamma_exact(v, [Fraction(0)] * n)[0]
            assert ge == Fraction(1, n + 1), (n, ge)
    res["negative"].append({"id": "N1", "what": "[n], s=0, delta=1/(n+1), n=2..94",
                            "n_certified_checker1": sum(1 for x in n1 if x[1]),
                            "n_certified_checker2": sum(1 for x in n1 if x[2]),
                            "gamma_exact_equals_1/(n+1)_for_n<=12": True,
                            "pass": all((not x[1]) and (not x[2]) for x in n1)})
    for f in os.listdir(OUT):
        if f.startswith("N1_s0_n"):
            os.remove(os.path.join(OUT, f))

    # N3: random s=0 instances with <= 14 distinct speeds must never certify at 1/(k+1) (LRC(k), k<=14, Tier L)
    rng = random.Random(20261027)
    cnt = 0
    bad1 = bad2 = 0
    for trial in range(3000):
        k = rng.randint(2, 14)
        vmax = rng.choice([k + 5, 3 * k, 10 * k, 60])
        vmax = max(vmax, k)
        v = sorted(rng.sample(range(1, vmax + 1), k))
        r = both("N3_tmp.json", v, [0] * k, 1, 1, k + 1)
        cnt += 1
        bad1 += int(r[0])
        bad2 += int(r[1])
    # include the tight instances explicitly
    for v in ([1, 3, 4, 7], [1, 3, 4, 5, 9], [1, 2, 3, 4, 5, 7, 12], [1, 4, 5, 6, 7, 11, 13], list(range(1, 15))):
        r = both("N3_tmp.json", v, [0] * len(v), 1, 1, len(v) + 1)
        cnt += 1
        bad1 += int(r[0])
        bad2 += int(r[1])
    os.remove(os.path.join(OUT, "N3_tmp.json"))
    res["negative"].append({"id": "N3", "what": "s=0, <=14 distinct speeds (3000 random + 5 tight), delta=1/(k+1)",
                            "instances": cnt, "certified_checker1": bad1, "certified_checker2": bad2,
                            "pass": bad1 == 0 and bad2 == 0})

    # N2 (perturbation) on P1 and P2 at their published shift scale
    # perturbation rule fixed in advance: for each runner i separately, shift a_i by +-1/(10*sum v) (both signs);
    # report how many single-runner perturbations break the covering at the certified delta.
    tight1 = Fraction(15, 94) + Fraction(1, 20 * 15)
    tight2 = Fraction(2, 15) + Fraction(1, 20 * 28)
    for tag, v, a, D, dp, dq in (("P1", v5, a5, 94, 1, 6), ("P2", v6, a6, 30, 1, 7),
                                 ("P1tight", v5, a5, 94, tight1.numerator, tight1.denominator),
                                 ("P2tight", v6, a6, 30, tight2.numerator, tight2.denominator)):
        S = sum(v)
        D2 = D * 10 * S
        base = [x * 10 * S for x in a]
        rows = []
        for i in range(len(v)):
            for sg in (1, -1):
                aa = list(base)
                aa[i] = (aa[i] + sg * D) % D2  # +- 1/(10 S) in units of 1/D2 is D2/(10S) = D
                r = both("N2_tmp.json", v, aa, D2, dp, dq)
                rows.append({"runner": i, "sign": sg, "checker1": r[0], "checker2": r[1]})
        os.remove(os.path.join(OUT, "N2_tmp.json"))
        res["negative"].append({"id": f"N2_{tag}", "what": f"single-runner perturbation by 1/(10*sum v) of {tag} at delta={dp}/{dq}",
                                "rows": rows,
                                "n_broken_both": sum(1 for r in rows if not r["checker1"] and not r["checker2"]),
                                "n_disagree": sum(1 for r in rows if r["checker1"] != r["checker2"]),
                                "n_total": len(rows)})
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
