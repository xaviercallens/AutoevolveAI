"""Second-stage analyses (added after the first dataset pass revealed long-decimal entries; logged as deviation).

Usage: python analysis2.py <jdft_json> <per_entry_jsonl> <out_json>
"""
from __future__ import annotations

import collections
import json
import math
import sys
from fractions import Fraction
from multiprocessing import Pool
from typing import Any

import numpy as np

import born_exact as be

CAP = Fraction(1, 20)  # half-width floor 0.05 = half of one unit in the first decimal place (resolution of 97% of entries)


def capped(item: tuple[str, list[list[float]]]) -> tuple[str, str, str, str]:
    jid, rows = item
    s = be.symmetrize(be.to_matrix(rows))
    hs = be.symmetrize(be.half_widths(rows))
    hs = [[max(v, CAP) for v in r] for r in hs]
    nominal = be.ldl_verdict(s)
    extra = None
    if not nominal[0]:
        arr = np.array(rows, dtype=float)
        w, v = np.linalg.eigh((arr + arr.T) / 2)
        extra = [[Fraction(round(float(t) * 10**6), 10**6) for t in v[:, 0]]]
    iv = be.interval_verdict(s, hs, nominal, extra)
    # upper-triangle and lower-triangle mirrored verdicts (asymmetry sensitivity)
    m = be.to_matrix(rows)
    up = [[m[min(i, j)][max(i, j)] for j in range(6)] for i in range(6)]
    lo = [[m[max(i, j)][min(i, j)] for j in range(6)] for i in range(6)]
    return jid, iv, "PD" if nominal[0] else "NOT_PD", f"{be.is_pd(up)}/{be.is_pd(lo)}"


def main(src: str, per_entry: str, out: str) -> int:
    data = json.load(open(src))
    byjid = {d["jid"]: d for d in data}
    res = [json.loads(l) for l in open(per_entry)]
    items = []
    for r in res:
        items.append((r["jid"], byjid[r["jid"]]["elastic_tensor"]))
    O: dict[str, Any] = {}

    # (1) sensitivity: half-width floor 0.05
    with Pool(2) as p:
        cap = p.map(capped, items, chunksize=200)
    O["interval_floor_0.05"] = dict(collections.Counter(c[1] for c in cap))
    O["interval_floor_0.05_by_nominal"] = {f"{c[2]}/{c[1]}": v for c, v in
                                          collections.Counter((c[2], c[1]) for c in cap).items()} if False else {
        f"{a}/{b}": v for (a, b), v in collections.Counter((c[2], c[1]) for c in cap).items()}
    # asymmetric tensors: does the verdict depend on which triangle is mirrored?
    asym = [(r, c) for r, c in zip(res, cap) if not r["symmetric"]]
    O["asymmetric_n"] = len(asym)
    O["asymmetric_triangle_verdicts_differ_from_symmetrised"] = sum(
        1 for r, c in asym if c[3] != f"{r['pd_exact']}/{r['pd_exact']}")

    # (2) read-sanity: Voigt bulk/shear from the tensor vs the stored kv / gv fields
    errK, errG, nK = [], [], 0
    for r, (jid, rows) in zip(res, items):
        d = byjid[jid]
        a = np.array(rows, dtype=float)
        K = (a[0, 0] + a[1, 1] + a[2, 2] + 2 * (a[0, 1] + a[0, 2] + a[1, 2])) / 9
        G = ((a[0, 0] + a[1, 1] + a[2, 2]) - (a[0, 1] + a[0, 2] + a[1, 2]) + 3 * (a[3, 3] + a[4, 4] + a[5, 5])) / 15
        kv, gv = d.get("bulk_modulus_kv"), d.get("shear_modulus_gv")
        if isinstance(kv, (int, float)) and math.isfinite(kv) and abs(K) > 1e-9:
            nK += 1
            errK.append(abs(K - kv) / max(abs(kv), 1e-9))
        if isinstance(gv, (int, float)) and math.isfinite(gv):
            errG.append(abs(G - gv) / max(abs(gv), 1.0))
    if errK:
        O["sanity_Kv"] = {"n": nK, "median_rel_err": float(np.median(errK)), "frac_within_1pct": float(np.mean(np.array(errK) < 0.01))}
    if errG:
        O["sanity_Gv"] = {"n": len(errG), "median_rel_err": float(np.median(errG)), "frac_within_1pct": float(np.mean(np.array(errG) < 0.01))}

    # (3) Tier X: relation with the lowest IR (Gamma) mode frequency where JARVIS stores one
    tab: collections.Counter[tuple[str, str]] = collections.Counter()
    for r, (jid, _) in zip(res, items):
        v = byjid[jid].get("min_ir_mode")
        if isinstance(v, (int, float)) and math.isfinite(v):
            tab[("NOT_PD" if not r["pd_exact"] else "PD", "min_ir_negative" if v < -1e-3 else "min_ir_nonneg")] += 1
    O["TierX_gamma_mode_crosstab"] = {f"{a}/{b}": v for (a, b), v in tab.items()}

    # (4) characterise float-tolerance disagreements and outliers
    f1 = [r for r in res if r["F1"] != r["pd_exact"]]
    O["F1_disagree_n"] = len(f1)
    O["F1_disagree_lmin_range"] = [min(r["lmin"] for r in f1), max(r["lmin"] for r in f1)] if f1 else None
    O["F1_disagree_pivot_zero_exact"] = sum(1 for r in f1 if r["pivot_nonpos"])
    O["F1_disagree_by_pivot_idx"] = dict(collections.Counter(r["pivot_idx"] for r in f1))
    f2 = [r for r in res if r["F2"] != r["pd_exact"]]
    O["F2_disagree_n"] = len(f2)
    O["F2_disagree_lmin_lmax"] = [[r["lmin"], r["lmax"]] for r in f2]
    O["F0_float_pd_exact_pd_agree"] = sum(r["F0"] == r["pd_exact"] for r in res)
    lm = np.array([r["lmin"] for r in res])
    O["lmin_float_quantiles"] = {str(q): float(np.quantile(lm, q)) for q in (0.0, 0.01, 0.1, 0.33, 0.5, 0.9, 1.0)}
    O["huge_magnitude_tensors_abs_gt_1e4_GPa"] = sum(1 for _, rows in items if max(abs(v) for r in rows for v in r) > 1e4)
    O["tensors_with_entry_printed_places_gt_6"] = sum(1 for r in res if r["max_places"] > 6)
    O["tensors_with_exactly_zero_row"] = sum(1 for _, rows in items if any(all(v == 0 for v in row) for row in rows))
    O["nonfinite_tensors_total"] = sum(1 for d in data if isinstance(d.get("elastic_tensor"), list) and
                                       not all(isinstance(v, (int, float)) and math.isfinite(v) for r in d["elastic_tensor"] for v in r))
    O["na_string_values"] = dict(collections.Counter(d["elastic_tensor"] for d in data if isinstance(d.get("elastic_tensor"), str)).most_common(3))
    json.dump(O, open(out, "w"), indent=1, default=str)
    print(json.dumps(O, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
