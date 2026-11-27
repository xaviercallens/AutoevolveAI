"""Run the exact Born audit on the JARVIS-DFT dft_3d elastic tensors.

Usage: python run_dataset.py <jdft_json> <per_entry_out_jsonl (outside repo)> <summary_json>
Per-entry results go to the third-party directory (not redistributed); only the summary is for the repo.
"""
from __future__ import annotations

import collections
import json
import math
import random
import sys
from fractions import Fraction
from multiprocessing import Pool
from typing import Any

import numpy as np
import sympy

import born_exact as be

THETAS = [Fraction(1, 100), Fraction(2, 100), Fraction(5, 100), Fraction(10, 100), Fraction(20, 100)]


def analyse(item: tuple[str, int, list[list[float]]]) -> dict[str, Any]:
    jid, spg, rows = item
    m = be.to_matrix(rows)
    s = be.symmetrize(m)
    hs = be.symmetrize(be.half_widths(rows))
    nominal = be.ldl_verdict(s)
    pd_exact = nominal[0]
    pd_bareiss = be.minors_pd(s)
    arr = np.array(rows, dtype=float)
    sym_f = (arr + arr.T) / 2
    lam, vec = np.linalg.eigvalsh(sym_f), None
    lmin, lmax = float(lam.min()), float(lam.max())
    extra = None
    if not pd_exact:
        w, v = np.linalg.eigh(sym_f)
        x = [Fraction(round(float(t) * 10**6), 10**6) for t in v[:, 0]]
        extra = [x]
    interval = be.interval_verdict(s, hs, nominal, extra)
    cls = be.laue_class(spg)
    sv = be.to_voigt(s)
    born = be.born_class_verdict(sv, cls)
    out: dict[str, Any] = {
        "jid": jid, "spg": spg, "cls": cls,
        "symmetric": be.is_symmetric(m),
        "pd_exact": pd_exact, "pd_bareiss": pd_bareiss,
        "pivot_idx": nominal[1], "pivot_nonpos": (not pd_exact) and nominal[2] == 0,
        "interval": interval,
        "linear_pass": be.linear_orthorhombic_pass(s),
        "F0": lmin > 0, "F1": lmin > -1e-8, "F2": lmin > -1e-6 * lmax,
        "lmin": lmin, "lmax": lmax,
        "born_class": born,
        "all_zero": all(v == 0 for r in m for v in r),
        "max_places": max(be.printed_places(v) for r in rows for v in r),
    }
    if not pd_exact:
        x = nominal[3]
        assert x is not None and be.quad_form(s, x) == nominal[2] and nominal[2] <= 0
        out["witness"] = [str(t) for t in x]
        out["witness_xSx"] = str(nominal[2])
    margins = {}
    if pd_exact:
        F = be.frob_upper(s)
        for th in THETAS:
            margins[str(float(th))] = be.is_pd(be.shifted(s, th * F))
    out["margin_ok"] = margins
    return out


def main(src: str, per_entry: str, summary: str) -> int:
    data = json.load(open(src))
    flags: dict[str, Any] = {"n_records": len(data)}
    items: list[tuple[str, int, list[list[float]]]] = []
    seen: collections.Counter[str] = collections.Counter(d["jid"] for d in data)
    flags["duplicate_jids"] = sum(1 for k, v in seen.items() if v > 1)
    n_na = n_bad = n_nonfinite = 0
    for d in data:
        t = d.get("elastic_tensor")
        if not isinstance(t, list):
            n_na += 1
            continue
        ok = len(t) == 6 and all(isinstance(r, list) and len(r) == 6 and all(isinstance(v, (int, float)) for v in r) for r in t)
        if not ok:
            n_bad += 1
            continue
        if not all(math.isfinite(v) for r in t for v in r):
            n_nonfinite += 1
            continue
        spg = d.get("spg_number")
        items.append((d["jid"], int(spg) if isinstance(spg, (int, float)) or (isinstance(spg, str) and spg.isdigit()) else 0, t))
    flags.update({"records_without_list_tensor": n_na, "malformed_tensor": n_bad, "nonfinite_tensor": n_nonfinite,
                  "n_full_tensors": len(items)})
    print(flags, flush=True)

    with Pool(2) as p:
        res = p.map(analyse, items, chunksize=200)
    with open(per_entry, "w") as f:
        for r in res:
            f.write(json.dumps(r) + "\n")

    N = len(res)
    S: dict[str, Any] = {"flags": flags, "N": N}
    S["agree_ldl_bareiss"] = sum(r["pd_exact"] == r["pd_bareiss"] for r in res)
    S["not_symmetric_as_stored"] = sum(not r["symmetric"] for r in res)
    S["all_zero_tensors"] = sum(r["all_zero"] for r in res)
    S["printed_places_hist"] = dict(collections.Counter(r["max_places"] for r in res))
    S["exact_PD"] = sum(r["pd_exact"] for r in res)
    S["exact_NOT_PD"] = sum(not r["pd_exact"] for r in res)
    S["exact_NOT_PD_boundary_pivot_zero"] = sum(r["pivot_nonpos"] for r in res)
    S["exact_NOT_PD_fraction"] = S["exact_NOT_PD"] / N
    S["interval"] = dict(collections.Counter(r["interval"] for r in res))
    S["interval_by_nominal"] = {f"{'PD' if r['pd_exact'] else 'NOT_PD'}/{k}": v for (k, v), r in []}
    cross = collections.Counter(("PD" if r["pd_exact"] else "NOT_PD", r["interval"]) for r in res)
    S["interval_by_nominal"] = {f"{a}/{b}": v for (a, b), v in cross.items()}
    S["linear_pass"] = sum(r["linear_pass"] for r in res)
    S["linear_pass_but_exact_NOT_PD"] = sum(r["linear_pass"] and not r["pd_exact"] for r in res)
    S["linear_pass_but_robust_NOT_PD"] = sum(r["linear_pass"] and r["interval"] == "ROBUST_NOT_PD" for r in res)
    S["linear_fail_but_exact_PD"] = sum((not r["linear_pass"]) and r["pd_exact"] for r in res)
    for k in ("F0", "F1", "F2"):
        S[f"float_{k}_disagree"] = sum(r[k] != r["pd_exact"] for r in res)
        S[f"float_{k}_says_stable_exact_not"] = sum(r[k] and not r["pd_exact"] for r in res)
        S[f"float_{k}_says_unstable_exact_pd"] = sum((not r[k]) and r["pd_exact"] for r in res)
    S["margin_pd_counts"] = {str(float(th)): sum(r["margin_ok"].get(str(float(th)), False) for r in res) for th in THETAS}
    # per-class table
    by: dict[str, dict[str, int]] = collections.defaultdict(lambda: collections.Counter())
    for r in res:
        c = by[r["cls"]]
        c["n"] += 1
        c["not_pd"] += int(not r["pd_exact"])
        c["linear_pass_not_pd"] += int(r["linear_pass"] and not r["pd_exact"])
        c["robust_not_pd"] += int(r["interval"] == "ROBUST_NOT_PD")
        c["undecided"] += int(r["interval"] == "UNDECIDED_BY_BOUND")
        c["F0_disagree"] += int(r["F0"] != r["pd_exact"])
        c["F1_disagree"] += int(r["F1"] != r["pd_exact"])
        c["F2_disagree"] += int(r["F2"] != r["pd_exact"])
        if r["born_class"] is not None:
            c["born_applicable"] += 1
            c["born_stable_full_not_pd"] += int(r["born_class"] and not r["pd_exact"])
            c["born_unstable_full_pd"] += int((not r["born_class"]) and r["pd_exact"])
    S["by_class"] = {k: dict(v) for k, v in sorted(by.items())}
    S["born_class_total_disagree"] = sum(
        v.get("born_stable_full_not_pd", 0) + v.get("born_unstable_full_pd", 0) for v in by.values())
    S["born_class_applicable"] = sum(v.get("born_applicable", 0) for v in by.values())
    S["spg_missing_or_zero"] = sum(r["spg"] == 0 for r in res)

    # Voigt-order assumption check on hexagonal-class entries (Tier X diagnostic)
    errs_vasp, errs_alt = [], []
    for it, r in zip(items, res):
        if r["cls"] == "hexagonal":
            a = it[2]
            c66_expect = (a[0][0] - a[0][1]) / 2
            if c66_expect > 1:
                errs_vasp.append(abs(a[3][3] - c66_expect) / c66_expect)
                errs_alt.append(abs(a[5][5] - c66_expect) / c66_expect)
    if errs_vasp:
        S["voigt_check_hexagonal"] = {"n": len(errs_vasp), "median_rel_err_idx3_vs_(C11-C12)/2": float(np.median(errs_vasp)),
                                      "median_rel_err_idx5_vs_(C11-C12)/2": float(np.median(errs_alt))}

    # Third implementation (sympy leading minors) on: every NOT_PD entry, every undecided, random 3000 PD
    rng = random.Random(7)
    sel = [i for i, r in enumerate(res) if (not r["pd_exact"]) or r["interval"] == "UNDECIDED_BY_BOUND"]
    pdl = [i for i, r in enumerate(res) if r["pd_exact"] and i not in set(sel)]
    sel += rng.sample(pdl, min(3000, len(pdl)))
    mism = 0
    for i in sel:
        m = be.symmetrize(be.to_matrix(items[i][2]))
        M = sympy.Matrix(6, 6, lambda a, b: sympy.Rational(m[a][b].numerator, m[a][b].denominator))
        v = all(M[:k, :k].det() > 0 for k in range(1, 7))
        mism += int(v != res[i]["pd_exact"])
    S["sympy_subset_size"] = len(sel)
    S["sympy_subset_mismatches"] = mism

    # example witnesses for the first 5 NOT_PD entries (rationals) for the Lean stage; jids only for flagged classes
    bad = [r for r in res if not r["pd_exact"]]
    S["n_witness_verified_exactly"] = len(bad)
    json.dump(S, open(summary, "w"), indent=1, default=str)
    print(json.dumps(S, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
