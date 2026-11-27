#!/usr/bin/env python3
"""H2(b) extension: S(D) = L(1, chi_D) * log log|D| >= 2/5 for fundamental D with 1e7 < |D| <= 1e8.

Streaming, resumable successor of ``h2_class_numbers.py`` (which keeps every row in memory).
The range is cut into chunks (lo, hi] of |D|; each chunk is computed in a worker process with
PARI (cypari2, ``nbthreads`` = 1), summarised, and written atomically to its own JSON file.
Reruns skip chunks whose JSON already exists. ``aggregate`` checks that the chunk files tile
the preregistered range exactly and only then applies the preregistered decision rule.

Primary class number: ``qfbclassno(D)`` (Shanks BSGS). PARI 2.13.3's own documentation
states it is unconditionally correct for |D| < 2*10^10; that is PARI's claim, not checked here.
Independent recheck: ``quadclassunit(D)[1]`` (GRH-conditional) on every chunk minimiser of
S and of L, on every D with S < RECHECK_S_BELOW, and on a deterministic sample per chunk.

Subcommands:
  positive   positive control (known h values, Heegner list, regression slice (2^21, 2^22])
  run        compute missing chunks until --budget-s is spent (stops submitting new chunks)
  aggregate  tiling check, controls, decision rule -> result.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import time
from collections.abc import Callable, Iterable
from concurrent.futures import FIRST_COMPLETED, Future, ProcessPoolExecutor, wait
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[4]
OUT_DIR = REPO / "results" / "openai_math" / "hypotheses" / "night_2026-10-07" / "H2"
CHUNK_DIR = OUT_DIR / "chunks"

RANGE_LO_EXCL = 10**7
RANGE_HI_INCL = 10**8
CHUNK_WIDTH = 500_000
THRESHOLD = 0.4
RECHECK_S_BELOW = 0.5
SAMPLE_PER_CHUNK = 64
NEAR_TIE = 1e-9

KNOWN_H = {23: 3, 47: 5, 71: 7, 163: 1}
HEEGNER_ABS = [3, 4, 7, 8, 11, 19, 43, 67, 163]
REGRESSION_SLICE = (2**21, 2**22)
REGRESSION_MIN_S = 0.5357676931072192
REGRESSION_ARGMIN = 2383747

_PARI: Any = None


def _pari() -> Any:
    global _PARI
    if _PARI is None:
        import cypari2

        _PARI = cypari2.Pari()
        _PARI.allocatemem(256 * 10**6, silent=True)
        _PARI("default(nbthreads, 1)")
    return _PARI


def fundamental_rows(lo_excl: int, hi_incl: int) -> list[tuple[int, int]]:
    """(|D|, qfbclassno(D)) for every fundamental D < 0 with lo_excl < |D| <= hi_incl."""
    vec = _pari()(
        f"my(v=List()); for(a={lo_excl + 1},{hi_incl}, if(isfundamental(-a), "
        f"listput(v,[a, qfbclassno(-a)]))); Vec(v)"
    )
    return [(int(x[0]), int(x[1])) for x in vec]


def quadclassunit_h(abs_d: int) -> int:
    """Class number of D = -abs_d by quadclassunit (GRH-conditional, independent algorithm)."""
    return int(_pari()(f"quadclassunit({-abs_d})[1]"))


def l_value(abs_d: int, h: int) -> float:
    """L(1, chi_D) = pi h / sqrt|D| for fundamental D < -4."""
    return math.pi * h / math.sqrt(abs_d)


def s_value(abs_d: int, h: int) -> float:
    """S(D) = L(1, chi_D) * log log |D|."""
    return l_value(abs_d, h) * math.log(math.log(abs_d))


def dyadic_k(abs_d: int) -> int:
    """k with 2^k < abs_d <= 2^(k+1) (half-open dyadic windows (2^k, 2^(k+1)])."""
    if abs_d < 2:
        raise ValueError("abs_d must be >= 2")
    return (abs_d - 1).bit_length() - 1


def chunk_bounds(lo_excl: int, hi_incl: int, width: int) -> list[tuple[int, int]]:
    """Half-open chunks (lo, hi] tiling (lo_excl, hi_incl]."""
    out = []
    lo = lo_excl
    while lo < hi_incl:
        hi = min(lo + width, hi_incl)
        out.append((lo, hi))
        lo = hi
    return out


def summarize_chunk(
    rows: list[tuple[int, int]], lo_excl: int, hi_incl: int, recheck: Callable[[int], int]
) -> dict[str, Any]:
    """Reduce one chunk's rows to its minima, Heegner count, per-window minima and rechecks."""
    rows = [(a, h) for a, h in rows if a > 4]
    if not rows:
        raise ValueError(f"no fundamental discriminants in ({lo_excl}, {hi_incl}]")
    best_s = (math.inf, 0, 0)
    best_l = (math.inf, 0, 0)
    windows: dict[int, dict[str, Any]] = {}
    h1: list[int] = []
    low_s: list[int] = []
    for a, h in rows:
        if h == 1:
            h1.append(a)
        lv = l_value(a, h)
        sv = lv * math.log(math.log(a))
        if sv < best_s[0]:
            best_s = (sv, a, h)
        if lv < best_l[0]:
            best_l = (lv, a, h)
        if sv < RECHECK_S_BELOW:
            low_s.append(a)
        k = dyadic_k(a)
        w = windows.setdefault(
            k, {"k": k, "n": 0, "min_S": math.inf, "argmin_S_absD": 0, "h_at_min_S": 0,
                "min_L": math.inf, "argmin_L_absD": 0, "h_at_min_L": 0}
        )
        w["n"] += 1
        if sv < w["min_S"]:
            w["min_S"], w["argmin_S_absD"], w["h_at_min_S"] = sv, a, h
        if lv < w["min_L"]:
            w["min_L"], w["argmin_L_absD"], w["h_at_min_L"] = lv, a, h
    h_of = dict(rows)
    step = max(1, len(rows) // SAMPLE_PER_CHUNK)
    sample = [rows[i][0] for i in range(0, len(rows), step)][:SAMPLE_PER_CHUNK]
    targets = sorted(set([best_s[1], best_l[1]] + low_s + sample))
    mismatches = []
    for a in targets:
        hq = recheck(a)
        if hq != h_of[a]:
            mismatches.append({"absD": a, "qfbclassno": h_of[a], "quadclassunit": hq})
    return {
        "lo_excl": lo_excl,
        "hi_incl": hi_incl,
        "n_fundamental": len(rows),
        "min_S": best_s[0], "argmin_S_D": -best_s[1], "h_at_min_S": best_s[2],
        "min_L": best_l[0], "argmin_L_D": -best_l[1], "h_at_min_L": best_l[2],
        "h1_count": len(h1), "h1_absD": h1[:20],
        "n_S_below_recheck_threshold": len(low_s),
        "n_rechecked": len(targets),
        "recheck_mismatches": mismatches,
        "recheck_agrees": not mismatches,
        "windows": [windows[k] for k in sorted(windows)],
    }


def chunk_path(lo: int, hi: int) -> Path:
    return CHUNK_DIR / f"chunk_{lo:010d}_{hi:010d}.json"


def _write_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp{os.getpid()}")
    tmp.write_text(json.dumps(payload, indent=1) + "\n")
    os.replace(tmp, path)


def compute_chunk(lo: int, hi: int) -> dict[str, Any]:
    t0 = time.time()
    summary = summarize_chunk(fundamental_rows(lo, hi), lo, hi, quadclassunit_h)
    summary["elapsed_s"] = round(time.time() - t0, 2)
    summary["pari_version"] = str(_pari()("version()"))
    return summary


def _worker(lo: int, hi: int, out_path: str) -> tuple[int, int, float]:
    summary = compute_chunk(lo, hi)
    _write_atomic(Path(out_path), summary)
    return lo, hi, summary["elapsed_s"]


def cmd_run(budget_s: float, workers: int, lo_excl: int, hi_incl: int, width: int) -> int:
    t0 = time.time()
    todo = [(lo, hi) for lo, hi in chunk_bounds(lo_excl, hi_incl, width) if not chunk_path(lo, hi).exists()]
    print(json.dumps({"chunks_todo": len(todo)}), flush=True)
    done = 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        pending: set[Future[tuple[int, int, float]]] = set()
        queue = list(todo)
        while queue or pending:
            while queue and len(pending) < workers and time.time() - t0 < budget_s:
                lo, hi = queue.pop(0)
                pending.add(ex.submit(_worker, lo, hi, str(chunk_path(lo, hi))))
            if not pending:
                break
            finished, pending = wait(pending, return_when=FIRST_COMPLETED)
            for f in finished:
                lo, hi, el = f.result()
                done += 1
                print(json.dumps({"chunk": [lo, hi], "elapsed_s": el}), flush=True)
    left = len([1 for lo, hi in chunk_bounds(lo_excl, hi_incl, width) if not chunk_path(lo, hi).exists()])
    print(json.dumps({"done_this_call": done, "chunks_left": left, "wall_s": round(time.time() - t0, 1)}))
    return 0


def check_tiling(chunks: Iterable[dict[str, Any]], lo_excl: int, hi_incl: int) -> list[str]:
    """Problems (gaps, overlaps, out-of-range) in a set of chunk summaries; empty if exact tiling."""
    spans = sorted((c["lo_excl"], c["hi_incl"]) for c in chunks)
    problems = []
    cur = lo_excl
    for lo, hi in spans:
        if lo > cur:
            problems.append(f"gap ({cur}, {lo}]")
        elif lo < cur:
            problems.append(f"overlap at ({lo}, {min(cur, hi)}]")
        cur = max(cur, hi)
    if cur < hi_incl:
        problems.append(f"gap ({cur}, {hi_incl}]")
    if cur > hi_incl:
        problems.append(f"beyond range to {cur}")
    return problems


def merge_windows(chunks: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Combine per-chunk dyadic-window minima into one record per window."""
    merged: dict[int, dict[str, Any]] = {}
    for c in chunks:
        for w in c["windows"]:
            m = merged.get(w["k"])
            if m is None:
                merged[w["k"]] = dict(w)
                continue
            m["n"] += w["n"]
            if w["min_S"] < m["min_S"]:
                m["min_S"], m["argmin_S_absD"], m["h_at_min_S"] = w["min_S"], w["argmin_S_absD"], w["h_at_min_S"]
            if w["min_L"] < m["min_L"]:
                m["min_L"], m["argmin_L_absD"], m["h_at_min_L"] = w["min_L"], w["argmin_L_absD"], w["h_at_min_L"]
    return [merged[k] for k in sorted(merged)]


def exact_s_below(abs_d: int, h: int, threshold: float) -> bool:
    """S(D) < threshold at 50 digits (used only when the float minimum is a near-tie)."""
    import mpmath

    mpmath.mp.dps = 50
    s = mpmath.pi * h / mpmath.sqrt(abs_d) * mpmath.log(mpmath.log(abs_d))
    return bool(s < mpmath.mpf(threshold))


def cmd_positive(workers: int) -> int:
    t0 = time.time()
    lo, hi = REGRESSION_SLICE
    parts = chunk_bounds(lo, hi, (hi - lo) // 4 + 1)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        sums = list(ex.map(compute_chunk, [p[0] for p in parts], [p[1] for p in parts]))
    small = dict(fundamental_rows(2, 200))
    known_qfb = {str(a): small.get(a) for a in KNOWN_H}
    known_qcu = {str(a): quadclassunit_h(a) for a in KNOWN_H}
    heegner = sorted(a for a, h in small.items() if h == 1)
    known_ok = all(known_qfb[str(a)] == h and known_qcu[str(a)] == h for a, h in KNOWN_H.items())
    best = min(sums, key=lambda c: c["min_S"])
    reg_ok = best["argmin_S_D"] == -REGRESSION_ARGMIN and abs(best["min_S"] - REGRESSION_MIN_S) < 1e-12
    rech_ok = all(c["recheck_agrees"] for c in sums)
    result = {
        "known_h_qfbclassno": known_qfb,
        "known_h_quadclassunit": known_qcu,
        "known_h_expected": {str(a): h for a, h in KNOWN_H.items()},
        "heegner_absD_found_le_200": heegner,
        "heegner_ok": heegner == HEEGNER_ABS,
        "known_ok": known_ok,
        "regression_slice": [lo, hi],
        "regression_min_S": best["min_S"],
        "regression_argmin_D": best["argmin_S_D"],
        "regression_expected": [REGRESSION_MIN_S, -REGRESSION_ARGMIN],
        "regression_n_fundamental": sum(c["n_fundamental"] for c in sums),
        "regression_ok": reg_ok,
        "regression_recheck_agrees": rech_ok,
        "pass": known_ok and heegner == HEEGNER_ABS and reg_ok and rech_ok,
        "elapsed_s": round(time.time() - t0, 1),
    }
    _write_atomic(OUT_DIR / "positive_control.json", result)
    print(json.dumps(result))
    return 0 if result["pass"] else 3


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decide(controls_pass: bool, sha_matches: bool, min_s_below_threshold: bool) -> str:
    """Preregistered decision rule (tiling is checked before this is reached)."""
    if not sha_matches:
        return "CRASH (runner changed after preregistration or no preregistration)"
    if not controls_pass:
        return "CRASH (control failed; numbers are not evidence)"
    return "FAIL" if min_s_below_threshold else "PASS"


def cmd_aggregate(lo_excl: int, hi_incl: int) -> int:
    chunks = [json.loads(p.read_text()) for p in sorted(CHUNK_DIR.glob("chunk_*.json"))]
    tiling = check_tiling(chunks, lo_excl, hi_incl)
    prereg_path = OUT_DIR / "preregistration.json"
    prereg = json.loads(prereg_path.read_text()) if prereg_path.exists() else {}
    me = Path(__file__).resolve()
    sha_now = sha256(me)
    sha_prereg = prereg.get("code", {}).get("runner", {}).get("sha256")
    pos_path = OUT_DIR / "positive_control.json"
    pos = json.loads(pos_path.read_text()) if pos_path.exists() else {"pass": False}
    result: dict[str, Any] = {
        "hypothesis": "H2(b)",
        "range_absD": [lo_excl, hi_incl],
        "n_chunks": len(chunks),
        "tiling_problems": tiling,
        "runner_sha256": sha_now,
        "runner_sha256_matches_preregistration": sha_now == sha_prereg,
    }
    if tiling:
        result["verdict"] = "INCOMPLETE"
        _write_atomic(OUT_DIR / "result.json", result)
        print(json.dumps(result))
        return 4
    windows = merge_windows(chunks)
    best = min(chunks, key=lambda c: c["min_S"])
    best_l = min(chunks, key=lambda c: c["min_L"])
    h1_total = sum(c["h1_count"] for c in chunks)
    rech_ok = all(c["recheck_agrees"] for c in chunks)
    first, last = windows[0], windows[-1]
    neg_ok = last["min_L"] < first["min_L"]
    abs_d = -best["argmin_S_D"]
    near_tie = abs(best["min_S"] - THRESHOLD) < NEAR_TIE
    below = exact_s_below(abs_d, best["h_at_min_S"], THRESHOLD) if near_tie else best["min_S"] < THRESHOLD
    controls = bool(pos.get("pass")) and h1_total == 0 and neg_ok and rech_ok
    verdict = decide(controls, sha_now == sha_prereg, below)
    result.update({
        "n_fundamental": sum(c["n_fundamental"] for c in chunks),
        "min_S": best["min_S"], "argmin_S_D": best["argmin_S_D"], "h_at_min_S": best["h_at_min_S"],
        "min_L": best_l["min_L"], "argmin_L_D": best_l["argmin_L_D"], "h_at_min_L": best_l["h_at_min_L"],
        "near_tie_mpmath_used": near_tie,
        "positive_control_pass": bool(pos.get("pass")),
        "h1_count_in_range": h1_total,
        "negative_control": {
            "first_window_k": first["k"], "first_window_min_L": first["min_L"],
            "last_window_k": last["k"], "last_window_min_L": last["min_L"], "pass": neg_ok,
        },
        "all_rechecks_agree": rech_ok,
        "n_rechecked": sum(c["n_rechecked"] for c in chunks),
        "controls_pass": controls,
        "dyadic_windows": windows,
        "verdict": verdict,
        "counterexample_D": best["argmin_S_D"] if verdict == "FAIL" else None,
        "chunk_cpu_s_total": round(sum(c["elapsed_s"] for c in chunks), 1),
    })
    _write_atomic(OUT_DIR / "result.json", result)
    print(json.dumps({k: v for k, v in result.items() if k != "dyadic_windows"}))
    return 0 if verdict in ("PASS", "FAIL") else 3


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    pp = sub.add_parser("positive")
    pp.add_argument("--workers", type=int, default=3)
    pr = sub.add_parser("run")
    pr.add_argument("--budget-s", type=float, default=240.0)
    pr.add_argument("--workers", type=int, default=3)
    sub.add_parser("aggregate")
    args = p.parse_args()
    if args.cmd == "positive":
        return cmd_positive(args.workers)
    if args.cmd == "run":
        return cmd_run(args.budget_s, args.workers, RANGE_LO_EXCL, RANGE_HI_INCL, CHUNK_WIDTH)
    return cmd_aggregate(RANGE_LO_EXCL, RANGE_HI_INCL)


if __name__ == "__main__":
    raise SystemExit(main())
