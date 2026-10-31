#!/usr/bin/env python3
"""Aggregate DH-Psi2 chunk results (Python kernel) and the C enumeration; cross-check; write data/summary.json."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
LANE = HERE.parent
CHUNKS = LANE / "data" / "chunks"
CENUM = LANE / "data" / "c_enum"
MODES = {"PSI": (3, True), "R": (1, True), "PLANT4": (4, True), "HF_R": (1, False), "HF_PSI": (3, False)}
N_F0 = 2**15
EXPECTED_MAX = {"PSI": 192, "R": 128, "HF_R": 192}  # preregistered expectations in units of 1/64

spec = importlib.util.spec_from_file_location("psi_exhaust_agg", HERE / "psi_exhaust.py")
assert spec is not None and spec.loader is not None
pe = importlib.util.module_from_spec(spec)
sys.modules["psi_exhaust_agg"] = pe
spec.loader.exec_module(pe)


def py_mode(mode: str) -> dict[str, Any]:
    files = sorted(CHUNKS.glob(f"{mode}_*.json"))
    rows = [json.loads(f.read_text()) for f in files]
    covered = sorted((r["f0_lo"], r["f0_hi"]) for r in rows)
    contiguous = bool(covered) and covered[0][0] == 0 and covered[-1][1] == N_F0 and all(a[1] == b[0] for a, b in zip(covered, covered[1:]))
    hist: Counter[int] = Counter()
    for r in rows:
        hist.update({int(k): v for k, v in r["hist_maxS_per_pair"].items()})
    best = max(rows, key=lambda r: r["max_S"]) if rows else None
    return {
        "chunks": len(rows),
        "complete": contiguous,
        "pairs": sum(r["pairs"] for r in rows),
        "max_S": best["max_S"] if best else None,
        "max_value": str(Fraction(best["max_S"], 64)) if best else None,
        "violating_pairs_gt3": sum(r["violating_pairs"] for r in rows),
        "violating_f0": sum(r["violating_f0"] for r in rows),
        "argmax_rechecks": sum(r["argmax_rechecks"] for r in rows),
        "argmax_rechecks_agree": sum(r["argmax_rechecks_agree"] for r in rows),
        "pairs_attaining_max": hist.get(best["max_S"], 0) if best else None,
        "hist": {str(k): hist[k] for k in sorted(hist)},
        "argmax": best["argmax"] if best else None,
        "elapsed_s_total": round(sum(r["elapsed_s"] for r in rows), 1),
    }


def c_mode(mode: str) -> dict[str, Any] | None:
    parts = [CENUM / f"{mode}_h{h}.json" for h in (0, 1)]
    if not all(p.exists() and p.stat().st_size > 0 for p in parts):
        return None
    rows = [json.loads(p.read_text()) for p in parts]
    hist: Counter[int] = Counter()
    for r in rows:
        hist.update({int(k): v for k, v in r["hist"].items()})
    best = max(rows, key=lambda r: r["max_S"])
    w_t, haar = MODES[mode]
    cfg = [np.array(m, dtype=np.int64) for m in best["argmax"]]
    recheck = {"direct_value": pe.direct_value(cfg, w_t, haar)}
    if haar:
        recheck["h5_exact"] = pe.h5_exact_value(cfg, w_t)
    return {
        "max_S": best["max_S"],
        "max_value": str(Fraction(best["max_S"], 64)),
        "violating_pairs_gt3": sum(r["violating_pairs_gt192"] for r in rows),
        "recheck_fail_internal": sum(r["recheck_fail"] for r in rows),
        "pairs": sum(hist.values()),
        "hist": {str(k): hist[k] for k in sorted(hist)},
        "argmax": best["argmax"],
        "argmax_recheck_python": recheck,
        "argmax_recheck_agrees": all(v == best["max_S"] for v in recheck.values()),
    }


def main() -> int:
    out: dict[str, Any] = {"modes": {}}
    for mode in MODES:
        p = py_mode(mode)
        c = c_mode(mode)
        entry: dict[str, Any] = {"python_kernel": p, "c_int_enumeration": c}
        if c is not None and p["complete"]:
            entry["hist_identical"] = p["hist"] == c["hist"]
            entry["max_identical"] = p["max_S"] == c["max_S"]
            entry["violations_identical"] = p["violating_pairs_gt3"] == c["violating_pairs_gt3"]
        if mode in EXPECTED_MAX and p["complete"]:
            entry["expected_max_S"] = EXPECTED_MAX[mode]
            entry["expected_max_met"] = p["max_S"] == EXPECTED_MAX[mode]
        out["modes"][mode] = entry
    (LANE / "data" / "summary.json").write_text(json.dumps(out, indent=1))
    short = {m: {k: v for k, v in e.items() if k not in ("python_kernel", "c_int_enumeration")} | {"py_max": e["python_kernel"]["max_value"], "py_complete": e["python_kernel"]["complete"], "c_max": (e["c_int_enumeration"] or {}).get("max_value"), "py_viol": e["python_kernel"]["violating_pairs_gt3"], "c_viol": (e["c_int_enumeration"] or {}).get("violating_pairs_gt3")} for m, e in out["modes"].items()}
    print(json.dumps(short, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
