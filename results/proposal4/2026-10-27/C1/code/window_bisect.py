"""Bracket r_max (upper end of the amplification window) by bisection with the certified comparison of fixation_cert.
Usage: window_bisect.py <graph6 file> <out.json> <lo p/q (G above K)> <hi p/q (G below K)> <steps>
Each midpoint verdict is certified (exact-rational residual bound); the bracket is therefore rigorous (Tier C)."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dbcore as d  # noqa: E402
import fixation_cert as fc  # noqa: E402


def frac(tok: str) -> Fraction:
    p, q = tok.split("/")
    return Fraction(int(p), int(q))


def main() -> None:
    adj = d.parse_graph6(open(sys.argv[1]).readline().strip())
    lo, hi, steps = frac(sys.argv[3]), frac(sys.argv[4]), int(sys.argv[5])
    log = []
    for _ in range(steps):
        mid = (lo + hi) / 2
        rec = fc.certify(adj, mid)
        log.append(rec)
        print(json.dumps({"r": rec["r"], "verdict": rec["verdict"], "diff": rec["diff_interval"]}), flush=True)
        if rec["verdict"] == "G_above_K":
            lo = mid
        elif rec["verdict"] == "G_below_K":
            hi = mid
        else:
            break
    out = {"r_max_bracket": [f"{lo.numerator}/{lo.denominator}", f"{hi.numerator}/{hi.denominator}"],
           "r_max_bracket_float": [float(lo), float(hi)], "steps": log}
    json.dump(out, open(sys.argv[2], "w"), indent=1)
    print(out["r_max_bracket_float"])


if __name__ == "__main__":
    main()
