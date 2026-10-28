#!/usr/bin/env python3
"""LR-IND: summarise data/ into logs/summary.json (controls first, then the k = 10 headline)."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def primes(lo: int, hi: int) -> list[int]:
    return [p for p in range(max(lo, 2), hi + 1) if all(p % q for q in range(2, int(p ** 0.5) + 1))]


def load(rel: str) -> dict | None:
    f = DATA / rel
    return json.loads(f.read_text()) if f.exists() else None


def B(k: int) -> tuple[int, int]:
    """B_k = (C(k+1,2)^(k-1) / k)^k as an exact fraction (num, den)."""
    c = (k + 1) * k // 2
    return c ** ((k - 1) * k), k ** k


def prod_ge_B(k: int, ps: list[int]) -> bool:
    num, den = B(k)
    return math.prod(ps) * den >= num


def main() -> int:
    S: dict[str, object] = {}
    ok_all = True
    # ---------- positive controls ----------
    expected = {
        3: ("Rosenfeld 2509.14111 Table 1 uses {7,11,13}; Sec. 7: true for all primes from 7 on (k=3)", lambda p: p >= 7),
        4: ("Rosenfeld Table 1 uses {17..37}; Sec. 7: all primes from 17 on", lambda p: p >= 17),
        5: ("Rosenfeld Table 1 uses {23..71}; Sec. 7: all primes from 23 on", lambda p: p >= 23),
        6: ("Rosenfeld Sec. 7: all primes > 31 and 13, 19; not 17, 23, 29", lambda p: p in (13, 19) or p >= 31),
        7: ("Rosenfeld Sec. 7: any prime >= 31 other than 41; Thm 1 uses S = {31..163} without 41", lambda p: p >= 31 and p != 41),
        8: ("Trakulthongchai 2511.22427 Sec. 6: I(8,9,p) nonempty for 11<=p<=43, empty for S_8 = {47..241}", lambda p: p >= 47),
    }
    ranges = {3: (5, 103), 4: (7, 103), 5: (7, 103), 6: (11, 197), 7: (11, 257), 8: (11, 241)}
    pos = {}
    for k, (src, fn) in expected.items():
        lo, hi = ranges[k]
        rows, mism, works = [], [], []
        for p in primes(lo, hi):
            if p <= k:
                continue
            d = load(f"controls_pos/k{k}_p{p}.json")
            if d is None:
                mism.append((p, "missing"))
                continue
            w = d["final_classes"] == 0
            if w:
                works.append(p)
            if w != fn(p):
                mism.append((p, "works" if w else "fails"))
        prod_ok = prod_ge_B(k, [p for p in works if p > k + 1]) if k >= 3 else None
        pos[k] = {"source": src, "range": [lo, hi], "primes_with_J_empty": works, "mismatches": mism,
                  "prod_of_those_primes_ge_B_k": prod_ok}
        ok_all &= not mism
    S["positive_controls"] = pos
    # ---------- negative control 1: planted witness-rule mutations ----------
    neg = []
    for k, p in [(7, 31), (8, 47), (8, 53), (10, 127), (10, 131)]:
        r = {}
        for mut in (0, 1, 2):
            d = load(f"controls_neg/k{k}_p{p}_mut{mut}.json")
            if d is None:
                continue
            r[mut] = {"S1_classes": d["S1"]["classes"], "S1_hash": d["S1"]["class_hash"],
                      "steps": [(s["op"], s["classes_mod_p"]) for s in d["steps"]], "final_classes": d["final_classes"]}
        neg.append({"k": k, "p": p, "runs": r,
                    "mut1_changes_anything": (r.get(1) != r.get(0)) if 0 in r and 1 in r else None,
                    "mut2_changes_anything": (r.get(2) != r.get(0)) if 0 in r and 2 in r else None})
    S["negative_control_mutations"] = neg
    # ---------- negative control 2: fiber program at L with 11 not dividing L p ----------
    fneg = []
    for p in (127, 467):
        for L in (5, 7):
            d = load(f"controls_neg/fiber_k10_p{p}_L{L}.json")
            if d:
                fneg.append({"p": p, "L": L, "improper": d["improper"], "first_improper_w": d["first_improper_w"]})
                ok_all &= d["improper"] >= 1
    S["negative_control_fiber"] = fneg
    # ---------- headline k = 10 ----------
    P10 = primes(127, 467)
    main_rows, missing = [], []
    for p in P10:
        d = load(f"k10_main/p{p}.json")
        f11 = load(f"k10_fiber11/p{p}.json")
        nc = load(f"k10_nocanon/p{p}.json")
        if d is None:
            missing.append(p)
            continue
        row = {"p": p, "S1_classes": d["S1"]["classes"], "S1_hash": d["S1"]["class_hash"],
               "sizes": [s["size"] for s in d["steps"]], "classes": [s["classes_mod_p"] for s in d["steps"]],
               "identity_survives": d["identity_survives"], "only_identity": d["only_identity"],
               "phase1_nodes": d["phase1"]["nodes"], "seconds": d["total_seconds"]}
        if f11:
            row["fiber11_improper"] = f11["improper"]
            row["fiber11_leaves"] = f11["leaves"]
            row["fiber11_seconds"] = f11["seconds"]
        if nc:
            same = (nc["S1"]["class_hash"] == d["S1"]["class_hash"] and
                    [s["class_hash"] for s in nc["steps"]] == [s["class_hash"] for s in d["steps"]])
            row["nocanon_agrees"] = same
            row["ST_convention_improper_tuples_l1"] = nc["phase1"]["improper_normalised"]
            row["ST_convention_S2_S3_S4_sizes"] = [s["size"] for s in nc["steps"][:3]]
            row["nocanon_seconds"] = nc["total_seconds"]
        main_rows.append(row)
    S["k10"] = main_rows
    S["k10_missing"] = missing
    S["k10_all_only_identity"] = all(r["only_identity"] for r in main_rows) and not missing
    S["k10_all_fiber11_zero"] = all(r.get("fiber11_improper") == 0 for r in main_rows) and not missing
    S["k10_nocanon_done"] = sum(1 for r in main_rows if "nocanon_agrees" in r)
    S["k10_nocanon_all_agree"] = all(r.get("nocanon_agrees", True) for r in main_rows)
    S["k10_core_seconds_main"] = round(sum(r["seconds"] for r in main_rows), 1)
    S["k10_core_seconds_fiber11"] = round(sum(r.get("fiber11_seconds", 0) for r in main_rows), 1)
    S["k10_core_seconds_nocanon"] = round(sum(r.get("nocanon_seconds", 0) for r in main_rows), 1)
    num, den = B(10)
    S["B10"] = {"num": str(num), "den": den, "ln_B10": math.log(num) - math.log(den),
                "ln_prod_P10": sum(math.log(p) for p in P10), "prod_ge_B10": math.prod(P10) * den >= num,
                "P10_is_all_primes_127_467": P10 == primes(127, 467) and len(P10) == 61}
    # ---------- optional k = 9 over S_9 ----------
    k9 = []
    for p in primes(137, 401):
        d = load(f"k9_S9/p{p}.json")
        if d:
            k9.append({"p": p, "final_classes": d["final_classes"], "seconds": d["total_seconds"]})
    S["k9_S9"] = {"done": len(k9), "of": len(primes(137, 401)), "all_empty": all(r["final_classes"] == 0 for r in k9),
                  "rows": k9}
    S["controls_ok"] = ok_all
    (ROOT / "logs" / "summary.json").write_text(json.dumps(S, indent=1) + "\n")
    print(json.dumps({k: v for k, v in S.items() if k not in ("k10", "k9_S9")}, indent=1)[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
