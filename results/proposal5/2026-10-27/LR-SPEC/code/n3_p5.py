#!/usr/bin/env python3
"""P5 (Fan-Sun examples) and N3 (tuples with ML exactly 1/n are not near-tight; only the strictness-corrupted scan lists them)."""
import os, sys, json
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify import ml_exact, read_scan

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cdir = os.path.join(root, "data", "controls")
out = {}
p5 = {
    "FS_(8,3,11,19)=7/30": ((8, 3, 11, 19), Fraction(7, 30)),
    "FS_(5,6,11,17,23,28)=8/51": ((5, 6, 11, 17, 23, 28), Fraction(8, 51)),
    "FS_(1,3,4,5,7,13,18)=3/23": ((1, 3, 4, 5, 7, 13, 18), Fraction(3, 23)),
    "FS_(1,2,3,4,5,7,18)=3/23": ((1, 2, 3, 4, 5, 7, 18), Fraction(3, 23)),
    "FS_(1,3,4,5,7,11,30)=5/37": ((1, 3, 4, 5, 7, 11, 30), Fraction(5, 37)),
}
for s in range(0, 21):
    p5[f"FS_family_s={s}"] = ((8, 4 * s + 3, 4 * s + 11, 4 * s + 19), Fraction(2 * s + 7, 8 * s + 30))
res = {}
ok_all = True
for name, (v, expect) in p5.items():
    ml = ml_exact(v)
    ok = ml == expect
    ok_all &= ok
    res[name] = {"computed": f"{ml.numerator}/{ml.denominator}", "expected": f"{expect.numerator}/{expect.denominator}", "ok": ok}
out["P5_all_ok"] = ok_all
out["P5"] = res

# N3
n3 = {}
for n, N in [(4, 200), (6, 60), (7, 50), (8, 40)]:
    true_set = {r[0] for r in read_scan(os.path.join(cdir, f"T_n{n}_N{N}.txt"))}
    strict_set = {r[0] for r in read_scan(os.path.join(cdir, f"N1_strict_n{n}_N{N}.txt"))}
    extra = sorted(strict_set - true_set)
    missing = sorted(true_set - strict_set)
    sample = extra[:: max(1, len(extra) // 25)][:25]
    exact_one_over_n = 0
    not_one_over_n = []
    for v in sample:
        ml = ml_exact(v)
        if ml == Fraction(1, n):
            exact_one_over_n += 1
        else:
            not_one_over_n.append((v, str(ml)))
    n3[f"n{n}_N{N}"] = {"extra_in_corrupted": len(extra), "true_missing_from_corrupted": len(missing),
                        "sampled": len(sample), "sampled_with_ML_exactly_1_over_n": exact_one_over_n,
                        "sampled_other": not_one_over_n[:5],
                        "true_subset_of_corrupted": not missing}
out["N3"] = n3
print(json.dumps(out, indent=1))
