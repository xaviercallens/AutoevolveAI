#!/usr/bin/env python3
"""Pre-registered analysis of "perturb the best at collapse" (design fixed before any run).

Hypothesis H_PB: on collapse (<= 2 distinct fitness values), refilling the worst half with 1-3 mutants of the
current best raises the UNCONDITIONAL L3 solve rate at budget 4000 under Baldwin by >= +0.04, and does so by
restoring selectable variance. Arms (same seeds, same sample points, same budget):
  A0 none | A1 random (legacy) | A2 pb13-forced (treatment) | A3 pb13-matched (same operator, ordinary admission)
  A4 clone (same slots/cost, no new genotype) | A5 pb10-forced | A6 pb1-forced | A7 pb3-forced
  A8 none @ budget 8000 (harness sensitivity) | A9 none on a scrambled spec (must solve nothing)

KILL RULE, fixed in advance:
  * harness invalid (reported as INVALID, not negative) if: A0/A1 do not reproduce the stored solved sets, A8 shows
    no L3 gain over A0 (exact McNemar p >= .05), or A9 solves anything;
  * H_PB unsupported if the primary (A2 vs A0, L3, two-sided exact McNemar) has p >= .05 OR paired diff < +0.04;
  * if supported: "variance restoration" only if A2 > A0 AND A2 > A3 AND A2 > A4 (one-sided exact McNemar each,
    alpha .05, intersection-union); A2 > A0 but A2 <= A3 => "intensification / triggered hypermutation";
    A2 > A0 but A2 <= A4 => "extra search".
  * secondary: L4, L5 A2 vs A0, Holm over m = 2. L6 is a floor, not claimable.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

L3, L4, L5, L6 = "L3_minus_wq", "L4_minus_hwq", "L5_minus_half_hwq", "L6_full"


def binom_two_sided(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def binom_one_sided(win: int, lose: int) -> float:
    """P(X >= win) for X ~ Bin(win+lose, 1/2): evidence that the first arm beats the second."""
    n = win + lose
    if n == 0:
        return 1.0
    return sum(math.comb(n, i) for i in range(win, n + 1)) / 2 ** n


def solved(path: Path) -> dict[str, dict[int, bool]]:
    d = json.loads(path.read_text())
    return {r["rung"]: {a["seed"]: a["solved"] for a in r["arms"]} for r in d["rungs"]}


def arms(path: Path) -> dict[str, list[dict]]:
    d = json.loads(path.read_text())
    return {r["rung"]: r["arms"] for r in d["rungs"]}


def paired(a: dict[int, bool], b: dict[int, bool]) -> dict:
    seeds = sorted(set(a) & set(b))
    n = len(seeds)
    a_only = sum(1 for s in seeds if a[s] and not b[s])
    b_only = sum(1 for s in seeds if b[s] and not a[s])
    diff = (a_only - b_only) / n
    se = math.sqrt(max(a_only + b_only - (a_only - b_only) ** 2 / n, 0)) / n          # Wald SE of a paired difference
    return {"n": n, "a_solved": sum(a[s] for s in seeds), "b_solved": sum(b[s] for s in seeds),
            "a_only": a_only, "b_only": b_only, "diff": diff, "ci95": [diff - 1.96 * se, diff + 1.96 * se],
            "p_two_sided": binom_two_sided(a_only, b_only), "p_a_beats_b": binom_one_sided(a_only, b_only)}


def holm(ps: dict[str, float], alpha: float = 0.05) -> dict[str, bool]:
    order = sorted(ps, key=ps.get)
    out, still = {}, True
    for i, k in enumerate(order):
        still = still and ps[k] <= alpha / (len(order) - i)
        out[k] = still
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", type=Path, required=True, help="directory holding A0.json ... A9.json (+ stored/ for the off-switch)")
    ap.add_argument("--stored-none", type=Path, required=True)
    ap.add_argument("--stored-random", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    S = {k: solved(a.dir / f"{k}.json") for k in ("A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9") if (a.dir / f"{k}.json").exists()}
    report: dict = {"arms_present": sorted(S)}

    # ---- harness validity
    inv: list[str] = []
    for k, stored in (("A0", a.stored_none), ("A1", a.stored_random)):
        st = solved(stored)
        for rung, m in st.items():
            if rung not in S[k]:
                continue                                    # the arm did not run this rung (A1 ran L3-L5 only)
            same = all(S[k][rung].get(s) == v for s, v in m.items())
            if not same:
                inv.append(f"{k} does not reproduce the stored solved set on {rung}")
    if "A8" in S:
        sens = paired(S["A8"][L3], S["A0"][L3])
        report["sensitivity_A8_vs_A0_L3"] = sens
        if not (sens["diff"] > 0 and sens["p_two_sided"] < 0.05):
            inv.append("A8 (budget 8000) shows no L3 gain: the harness cannot register an improvement")
    if "A9" in S and any(any(v.values()) for v in S["A9"].values()):
        inv.append("A9 (scrambled spec) solved something")
    report["harness_invalid_reasons"] = inv

    # ---- primary, mechanism (intersection-union), secondary
    prim = paired(S["A2"][L3], S["A0"][L3])
    report["primary_A2_vs_A0_L3"] = prim
    supported = prim["p_two_sided"] < 0.05 and prim["diff"] >= 0.04
    mech = {n: paired(S["A2"][L3], S[n][L3]) for n in ("A0", "A3", "A4") if n in S}
    report["mechanism_one_sided"] = {n: {"p_A2_beats": v["p_a_beats_b"], "diff": v["diff"]} for n, v in mech.items()}
    iut = all(v["p_a_beats_b"] < 0.05 for v in mech.values()) and len(mech) == 3
    sec = {r: paired(S["A2"][r], S["A0"][r]) for r in (L4, L5)}
    report["secondary_A2_vs_A0"] = {r: v for r, v in sec.items()}
    report["secondary_holm_significant"] = holm({r: v["p_two_sided"] for r, v in sec.items()})
    # ---- easy-rung equivalence guard (pre-registered margin +-0.05; L2 is near ceiling, so this is a bug guard only)
    eq = {}
    for r in ("L1_base", "L2_minus_q"):
        if r in S["A2"] and r in S["A0"]:
            v = paired(S["A2"][r], S["A0"][r])
            eq[r] = {"diff": v["diff"], "ci95": v["ci95"], "inside_margin_0.05": bool(v["ci95"][0] > -0.05 and v["ci95"][1] < 0.05)}
    report["easy_rung_equivalence_A2_vs_A0"] = eq
    report["L6_floor_solves_by_arm"] = {k: sum(S[k][L6].values()) for k in S if L6 in S[k]}

    # ---- dose-response (descriptive + pre-registered monotone sign)
    dose = {n: sum(S[n][L3].values()) for n in ("A6", "A7", "A2", "A5", "A1", "A0") if n in S}
    report["dose_response_L3_solved"] = dose
    gains = [dose[n] - dose["A0"] for n in ("A6", "A7", "A5", "A1") if n in dose]
    report["dose_gain_non_increasing_pb1_pb3_pb10_random"] = all(x >= y for x, y in zip(gains, gains[1:]))

    # ---- mechanism check by survival and variance (positive control 4)
    surv, var = {}, {}
    for k in ("A0", "A1", "A2", "A3", "A4"):
        if k not in S:
            continue
        rows = arms(a.dir / f"{k}.json")[L3]
        flat = [g for r in rows for g in r.get("survival_gens", [])]
        surv[k] = {"charged": sum(r.get("inserted_total", 0) for r in rows), "admitted": len(flat), "median_survival_gens": statistics.median(flat) if flat else None,
                   "inserted_equal_best_frac": (sum(r.get("inserted_equal_to_best_fitness", 0) for r in rows) / max(1, sum(r.get("inserted_total", 0) for r in rows))),
                   "dedup_fail": sum(r.get("dedup_fail", 0) for r in rows)}
        vs = [r["var_fitness_post10"] for r in rows if r.get("var_fitness_post10") is not None]
        var[k] = {"n": len(vs), "mean_var_post10": statistics.fmean(vs) if vs else None}
    report["survival_L3"], report["var_fitness_post10_L3"] = surv, var
    mech_ok = ("A2" in surv and "A1" in surv and (surv["A2"]["median_survival_gens"] or 0) > (surv["A1"]["median_survival_gens"] or 0)
               and var["A2"]["mean_var_post10"] is not None and var["A2"]["mean_var_post10"] > var["A0"]["mean_var_post10"]
               and var["A2"]["mean_var_post10"] > var["A4"]["mean_var_post10"])
    report["mechanism_check_ran"] = bool(mech_ok)

    # ---- verdict, computed from the pre-registered rule
    if inv:
        verdict = "INVALID: " + "; ".join(inv)
    elif not supported:
        verdict = "H_PB NOT SUPPORTED at this budget: collapse looks like a symptom of the plateau, not its cause."
    elif not mech_ok:
        verdict = "A2 > A0 but the mechanism check failed (inserted individuals did not survive / variance not restored): not interpretable as variance restoration."
    elif iut:
        verdict = "SUPPORTED as variance restoration (A2 > A0, A3 and A4)."
    elif mech["A3"]["p_a_beats_b"] >= 0.05:
        verdict = "SUPPORTED only as intensification / triggered hypermutation (A2 does not beat the matched operator A3)."
    else:
        verdict = "SUPPORTED only as extra search (A2 does not beat the clone control A4)."
    if any(not v["inside_margin_0.05"] for v in eq.values()):
        verdict += "  [CAUTION: A2 differs from A0 on an easy rung beyond the +-0.05 margin; check for a bug or a cost on easy targets.]"
    report["verdict"] = verdict
    a.out.write_text(json.dumps(report, indent=2, default=str) + "\n")
    print(json.dumps({k: report[k] for k in ("primary_A2_vs_A0_L3", "mechanism_one_sided", "dose_response_L3_solved", "harness_invalid_reasons", "easy_rung_equivalence_A2_vs_A0", "mechanism_check_ran", "verdict")}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
