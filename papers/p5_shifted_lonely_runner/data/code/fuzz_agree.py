"""Agreement fuzz: on random small instances, checker 1 (sweep), checker 2 (C endpoints)
and the exact gamma evaluator must agree: covered(delta) <=> gamma(v;s) < delta.
delta is drawn at gamma exactly (must reject), just above, just below, and at random."""
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

C = os.path.join(HERE, "check_cover")
TMP = os.path.join(os.path.dirname(HERE), "controls", "fuzz_tmp.json")


def main() -> None:
    rng = random.Random(7)
    stats = {"instances": 0, "tests": 0, "mismatch": 0, "covered_true": 0}
    mism = []
    for _ in range(600):
        n = rng.randint(2, 7)
        v = sorted(rng.sample(range(1, rng.choice([8, 12, 20]) + 1), n))
        D = rng.choice([7, 30, 94, 101, 360])
        a = [rng.randrange(D) for _ in range(n)]
        g = gamma_exact(v, [Fraction(x, D) for x in a])[0]
        stats["instances"] += 1
        deltas = [g, g + Fraction(1, 10**6), g - Fraction(1, 10**6), Fraction(rng.randint(1, 499), 1000)]
        for d in deltas:
            if not (0 < d < Fraction(1, 2)):
                continue
            expect = g < d
            ok1 = covers_open(v, a, D, d.numerator, d.denominator)[0]
            with open(TMP, "w") as fh:
                json.dump({"n": n, "v": v, "a": a, "D": D, "delta_num": d.numerator, "delta_den": d.denominator}, fh)
            ok2 = subprocess.run([C, TMP], capture_output=True).returncode == 0
            stats["tests"] += 1
            stats["covered_true"] += int(expect)
            if not (ok1 == ok2 == expect):
                stats["mismatch"] += 1
                mism.append({"v": v, "a": a, "D": D, "delta": str(d), "gamma": str(g), "c1": ok1, "c2": ok2})
    os.remove(TMP)
    print(json.dumps({"stats": stats, "mismatches": mism[:20]}, indent=1))


if __name__ == "__main__":
    main()
