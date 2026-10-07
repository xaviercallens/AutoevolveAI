#!/usr/bin/env python3
"""H2: extreme small values of L(1, chi_D) against 1/log log|D|, imaginary quadratic fields.

Anchor: openai/math family 003 (Lean-formalized, statement read 2026-10-07, not compiled
here): every Dirichlet L-function is zero-free in Re s > 7/8. Classical consequence (the
GRH argument of Littlewood only needs a fixed zero-free strip): L(1, chi) >> 1/log log q,
hence h(D) >> sqrt|D| / log log|D|. That part is a COROLLARY (type a).

The type (b) part is an explicit constant: for every fundamental D < -4,
    S(D) := L(1, chi_D) * log log|D|  >=  c_train,
where c_train is the minimum of S over the training range 7 <= |D| <= 10^6, tested on the
holdout 10^6 < |D| <= 10^7 (preregistered). L(1, chi_D) = pi h(D) / sqrt|D| for D < -4.

Controls (preregistered):
* positive: exactly 9 fundamental D < 0 with h(D) = 1 in |D| <= 10^6 (Heegner-Stark);
  h(-23) = 3, h(-47) = 5, h(-71) = 7.
* negative: the wrong-order statistic U(D) = L(1, chi_D) (no log log factor) must keep
  falling: min U over the last decade window [10^6.5, 10^7] < min U over [10^5, 10^5.5].
  If the instrument cannot see that drift, it cannot see anything.
Note: the correctness range of PARI's qfbclassno for large |D| was not checked here, and
PARI's quadclassunit is GRH-conditional unless certified. The two minimisers are recomputed
with quadclassunit as an independent algorithm; agreement is recorded, not assumed.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT_DIR = REPO / "results" / "openai_math" / "hypotheses" / "H2"


def chunk(lo: int, hi: int) -> list[tuple[int, int]]:
    """All fundamental D with lo <= |D| < hi as (|D|, h(D)), D < 0."""
    import cypari2

    pari = cypari2.Pari()
    pari.allocatemem(512 * 10**6, silent=True)
    vec = pari(
        f"my(v=List()); for(a={lo},{hi - 1}, my(D=-a); if(isfundamental(D), listput(v,[a, qfbclassno(D)]))); Vec(v)"
    )
    return [(int(x[0]), int(x[1])) for x in vec]


def compute(max_abs: int, workers: int, step: int) -> list[tuple[int, int]]:
    ranges = [(lo, min(lo + step, max_abs + 1)) for lo in range(3, max_abs + 1, step)]
    out: list[tuple[int, int]] = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for part in ex.map(chunk, [r[0] for r in ranges], [r[1] for r in ranges]):
            out.extend(part)
    return sorted(out)


def window_min(rows: list[tuple[int, float]], lo: float, hi: float) -> tuple[float, int]:
    vals = [(v, d) for d, v in rows if lo <= d <= hi]
    return min(vals) if vals else (math.nan, 0)


def main() -> int:
    p = argparse.ArgumentParser(description="H2 class-number extreme values")
    p.add_argument("--train-max", type=int, default=10**6)
    p.add_argument("--holdout-max", type=int, default=10**7)
    p.add_argument("--workers", type=int, default=7)
    p.add_argument("--step", type=int, default=100_000)
    args = p.parse_args()
    t0 = time.time()
    rows = compute(args.holdout_max, args.workers, args.step)
    h = {d: hh for d, hh in rows}
    heegner = sorted(d for d, hh in rows if hh == 1 and d <= args.train_max)
    pos_ok = len(heegner) == 9 and h.get(23) == 3 and h.get(47) == 5 and h.get(71) == 7
    lvals = [(d, math.pi * hh / math.sqrt(d)) for d, hh in rows if d > 4]
    s_vals = [(d, l1 * math.log(math.log(d))) for d, l1 in lvals if d >= 7]
    train = [(v, d) for d, v in s_vals if d <= args.train_max]
    hold = [(v, d) for d, v in s_vals if args.train_max < d <= args.holdout_max]
    c_train, d_train = min(train)
    c_hold, d_hold = min(hold)
    u_early, d_ue = window_min(lvals, 10**5, 10**5.5)
    u_late, d_ul = window_min(lvals, 10**6.5, 10**7)
    neg_ok = u_late < u_early
    # dyadic-window minima of S, to see whether the 1/loglog order is stable
    windows = []
    lo = 8
    while lo < args.holdout_max:
        hi = lo * 2
        vmin, dmin = window_min(s_vals, lo, hi)
        windows.append({"lo": lo, "hi": hi, "min_S": vmin, "argmin_absD": dmin})
        lo = hi
    import cypari2

    pari = cypari2.Pari()
    recheck = {str(d): int(pari(f"quadclassunit({-d})[1]")) for d in (d_train, d_hold)}
    result = {
        "train_max": args.train_max,
        "holdout_max": args.holdout_max,
        "n_fundamental": len(rows),
        "positive_control": {"heegner_found": [-d for d in heegner], "pass": pos_ok},
        "negative_control": {"min_L1_window_1e5_1e5.5": [u_early, -d_ue], "min_L1_window_1e6.5_1e7": [u_late, -d_ul], "pass": neg_ok},
        "c_train": c_train, "argmin_train_D": -d_train,
        "c_holdout": c_hold, "argmin_holdout_D": -d_hold,
        "h_recheck_quadclassunit": recheck,
        "h_recheck_agrees": recheck[str(d_train)] == h[d_train] and recheck[str(d_hold)] == h[d_hold],
        "holdout_pass": c_hold >= c_train,
        "dyadic_window_min_S": windows,
        "controls_pass": pos_ok and neg_ok,
        "elapsed_s": round(time.time() - t0, 1),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("n_fundamental", "c_train", "argmin_train_D", "c_holdout", "argmin_holdout_D", "holdout_pass", "controls_pass", "elapsed_s")}))
    return 0 if result["controls_pass"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
