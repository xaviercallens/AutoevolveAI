"""Part (a): certified eta enclosures over the seawater box + P1 / N1 / N2 / N3 controls against PyCO2SYS."""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import PyCO2SYS as pyco2

sys.path.insert(0, str(Path(__file__).parent))
import k2lib as K  # noqa: E402

BOX = {"T": (0.0, 30.0), "S": (30.0, 38.0), "f": (280.0, 560.0), "TA35": (2200.0, 2400.0)}
NG = {"T": 15, "S": 16, "f": 16, "TA35": 8}
NSUB = (20, 4)
CACHE: dict = {}


def edges(lo: float, hi: float, n: int) -> list[tuple[float, float]]:
    w = (hi - lo) / n
    return [(lo + i * w, (lo + (i + 1) * w) if i < n - 1 else hi) for i in range(n)]


def cell_of(t: float, s: float, f: float, ta35: float) -> tuple[int, int, int, int]:
    idx = []
    for key, v in zip(("T", "S", "f", "TA35"), (t, s, f, ta35)):
        lo, hi = BOX[key]
        idx.append(min(int((v - lo) / (hi - lo) * NG[key]), NG[key] - 1))
    return tuple(idx)  # type: ignore[return-value]


def cell_ranges(ix: tuple[int, int, int, int]) -> dict:
    out = {}
    for k, i in zip(("T", "S", "f", "TA35"), ix):
        out[k] = edges(*BOX[k], NG[k])[i]
    return out


def box_enclosure(r: dict, nsigma: float, corrupt: dict | None = None) -> tuple[float, float]:
    # TA = (S/35)*TA35 in mol/kg: interval product; enclose by corner extremes (monotone product)
    cands = [s / 35 * ta * 1e-6 for s in r["S"] for ta in r["TA35"]]
    lo_ta, hi_ta = min(cands) * (1 - 1e-12), max(cands) * (1 + 1e-12)
    return K.eta_box(r["T"], r["S"], r["f"], (lo_ta, hi_ta), nsigma, corrupt, NSUB, CACHE)[:2]


def pyco2_eta(t: float, s: float, f: float, ta_umol: float) -> float:
    kw = dict(par1_type=1, par2=f, par2_type=5, salinity=s, temperature=t, opt_k_carbonic=10, opt_pH_scale=1,
              total_sulfate=0, total_fluoride=0, opt_total_borate=1)
    up = pyco2.sys(par1=ta_umol + 0.5, **kw)["dic"]
    dn = pyco2.sys(par1=ta_umol - 0.5, **kw)["dic"]
    return float(up - dn)  # per 1 umol/kg


WEIGHT = {"T": 1.0, "S": 2.0, "f": 1.0, "TA35": 2.0}
KEYS = ("T", "S", "f", "TA35")


def eval_cell(rng: dict, ns: float) -> tuple[float, float]:
    cands = [s / 35 * ta * 1e-6 for s in rng["S"] for ta in rng["TA35"]]
    lo_ta, hi_ta = min(cands) * (1 - 1e-12), max(cands) * (1 + 1e-12)
    nt = min(24, max(1, int((rng["T"][1] - rng["T"][0]) / 0.1) + 1))
    nsb = min(6, max(1, int((rng["S"][1] - rng["S"][0]) / 0.5) + 1))
    e = K.eta_box(rng["T"], rng["S"], rng["f"], (lo_ta, hi_ta), ns, None, (nt, nsb), None)
    return e[0], e[1]


def point_cell(pt: dict) -> dict:
    return {k: (v * (1 - 1e-9), v * (1 + 1e-9)) for k, v in pt.items()}


def bb(mode: str, ns: float, maxevals: int = 3000) -> dict:
    """Rigorous branch-and-bound for the upper (mode='max') or lower (mode='min') enclosure bound of eta over the box."""
    import heapq
    sign = -1.0 if mode == "max" else 1.0  # heap min-first on sign*key
    NI = {"T": 6, "S": 4, "f": 4, "TA35": 8}
    heap = []
    evals = 0
    for it in range(NI["T"]):
        for js in range(NI["S"]):
            for kf in range(NI["f"]):
                for lt in range(NI["TA35"]):
                    sub = {"T": edges(*BOX["T"], NI["T"])[it], "S": edges(*BOX["S"], NI["S"])[js],
                           "f": edges(*BOX["f"], NI["f"])[kf], "TA35": edges(*BOX["TA35"], NI["TA35"])[lt]}
                    e = eval_cell(sub, ns)
                    e = (max(e[0], 0.0), min(e[1], 1.0))  # 0 < eta < 1 (Lean: eta_pos, eta_lt_one)
                    evals += 1
                    heap.append((sign * (e[1] if mode == "max" else e[0]), evals, sub, e))
    heapq.heapify(heap)
    best_point = None
    counter = evals
    while heap and evals < maxevals:
        key, _, cell, (clo, chi) = heapq.heappop(heap)
        if evals % 100 < 3:
            print(mode, ns, 'evals', evals, 'top', clo, chi, 'best', best_point, 'live', len(heap), flush=True)
        top = chi if mode == "max" else clo
        if best_point is not None and (abs(top - best_point) <= 5e-4):
            heapq.heappush(heap, (key, 0, cell, (clo, chi)))
            break
        # normalised weighted widths
        wd = {k: WEIGHT[k] * (cell[k][1] - cell[k][0]) / (BOX[k][1] - BOX[k][0]) for k in KEYS}
        k = max(wd, key=wd.get)
        if wd[k] < 1.0 / 2000:
            heapq.heappush(heap, (key, 0, cell, (clo, chi)))
            break  # top cell cannot be resolved further
        mid = 0.5 * (cell[k][0] + cell[k][1])
        for part in ((cell[k][0], mid), (mid, cell[k][1])):
            sub = dict(cell)
            sub[k] = part
            e = eval_cell(sub, ns)
            e = (max(e[0], 0.0), min(e[1], 1.0))
            evals += 1
            # prune: for max keep cells with hi >= best_point
            bound = e[1] if mode == "max" else e[0]
            if best_point is not None and ((mode == "max" and bound < best_point) or (mode == "min" and bound > best_point)):
                continue
            counter += 1
            heapq.heappush(heap, (sign * bound, counter, sub, e))
        # update the certified one-sided bound with the midpoint point-box of the popped cell
        # evaluation point: the cell corner in the (numerically observed) direction of larger eta for 'max',
        # the opposite corner for 'min'. Any point gives a valid one-sided bound; this choice only makes it sharp.
        up = {"T": 0, "S": 0, "f": 1, "TA35": 0}
        pt = {kk: cell[kk][up[kk] if mode == "max" else 1 - up[kk]] for kk in KEYS}
        pe = eval_cell(point_cell(pt), ns)
        evals += 1
        cand = pe[0] if mode == "max" else pe[1]
        if best_point is None or (mode == "max" and cand > best_point) or (mode == "min" and cand < best_point):
            best_point = cand
    top_key, _, top_cell, (tlo, thi) = heap[0]
    bound = thi if mode == "max" else tlo
    return {"mode": mode, "nsigma": ns, "certified_bound": bound, "one_sided_attained_bound": best_point, "evals": evals,
            "top_cell": top_cell, "live_cells": len(heap)}


def run_enclosure(outdir: Path, name: str, ns: float) -> None:
    t0 = time.time()
    mx = bb("max", ns)
    mn = bb("min", ns)
    res = {"scenario": name, "nsigma": ns, "box": BOX, "method": "branch-and-bound (rigorous outer bounds)",
           "eta_lo": mn["certified_bound"], "eta_hi": mx["certified_bound"], "max_run": mx, "min_run": mn,
           "seconds": time.time() - t0}
    (outdir / f"enclosure_{name}.json").write_text(json.dumps(res, indent=1))
    print(name, res["eta_lo"], res["eta_hi"], mx["one_sided_attained_bound"], mn["one_sided_attained_bound"], res["seconds"], flush=True)


def main(outdir: Path) -> None:
    t0 = time.time()
    res: dict = {"box": BOX, "grid": NG}
    # float true range (Tier X) with PyCO2SYS-independent float root on a dense grid
    rng = random.Random(20261031)
    pts = [(rng.uniform(*BOX["T"]), rng.uniform(*BOX["S"]), rng.uniform(*BOX["f"]), rng.uniform(*BOX["TA35"])) for _ in range(500)]

    # P1
    inside_cell = inside_pt = 0
    worst_rel = 0.0
    p1_rows = []
    pyvals = []
    for (t, s, f, ta35) in pts:
        ta_umol = ta35 * s / 35
        ref = pyco2_eta(t, s, f, ta_umol)
        pyvals.append(ref)
        nb = {"T": (max(0.0, t - 0.5), min(30.0, t + 0.5)), "S": (max(30.0, s - 0.25), min(38.0, s + 0.25)),
              "f": (max(280.0, f - 5), min(560.0, f + 5)), "TA35": (max(2200.0, ta35 - 5), min(2400.0, ta35 + 5))}
        lo, hi = eval_cell(nb, 0.0)
        inside_cell += int(lo <= ref <= hi)
        pe = K.eta_box((t, t), (s, s), (f, f), (ta_umol * 1e-6, ta_umol * 1e-6), 0.0)
        # tiny box: widen by 1e-12 relative to keep iv nondegenerate
        inside_pt += int(pe[0] <= ref <= pe[1])
        mine = 0.5 * (pe[0] + pe[1])
        rel = abs(mine - ref) / ref
        worst_rel = max(worst_rel, rel)
        if len(p1_rows) < 5:
            p1_rows.append({"T": t, "S": s, "f": f, "TA35": ta35, "pyco2sys": ref, "ours_lo": pe[0], "ours_hi": pe[1], "rel": rel})
    res["P1"] = {"n": 500, "inside_neighbourhood_enclosure_U0": inside_cell, "inside_point_enclosure_U0": inside_pt,
                 "worst_rel_float_agreement": worst_rel, "pass": inside_cell == 500 and worst_rel < 1e-4, "examples": p1_rows}
    print("P1", res["P1"]["inside_neighbourhood_enclosure_U0"], res["P1"]["inside_point_enclosure_U0"], worst_rel, flush=True)
    res["pyco2sys_eta_range_float"] = [min(pyvals), max(pyvals)]

    # P1b: strong form. Feed PyCO2SYS our K_water and total boron (the two inputs where the Guide transcription
    # differs from PyCO2SYS's defaults, see const_crosscheck.json); then the agreement must be at point level.
    from mpmath import iv as _iv
    inside_b = 0
    worst_b = 0.0
    for (t, s, f, ta35) in pts[:100]:
        ta_umol = ta35 * s / 35
        cc = K.constants(_iv.mpf(t), _iv.mpf(s))
        kwv = float(cc["KW"].mid)
        btv = float(cc["BT"].mid) * 1e6
        kw2 = dict(par1_type=1, par2=f, par2_type=5, salinity=s, temperature=t, opt_k_carbonic=10, opt_pH_scale=1,
                   total_sulfate=0, total_fluoride=0, opt_total_borate=1, k_water=kwv, total_borate=btv)
        refb = float(pyco2.sys(par1=ta_umol + 0.5, **kw2)["dic"] - pyco2.sys(par1=ta_umol - 0.5, **kw2)["dic"])
        pe = K.eta_box((t, t), (s, s), (f, f), (ta_umol * 1e-6, ta_umol * 1e-6), 0.0)
        inside_b += int(pe[0] - 1e-6 <= refb <= pe[1] + 1e-6)
        worst_b = max(worst_b, abs(0.5 * (pe[0] + pe[1]) - refb) / refb)
    res["P1b_matched_KW_BT"] = {"n": 100, "inside_point_enclosure_plus_1e-6": inside_b, "worst_rel": worst_b}
    print("P1b", res["P1b_matched_KW_BT"], flush=True)

    # X1 (Tier X): effect of including sulfate + fluoride (PyCO2SYS defaults) on eta
    dev = []
    for (t, s, f, ta35), ref in zip(pts[:100], pyvals[:100]):
        kw = dict(par1_type=1, par2=f, par2_type=5, salinity=s, temperature=t, opt_k_carbonic=10, opt_pH_scale=1, opt_total_borate=1)
        ta_umol = ta35 * s / 35
        full = pyco2.sys(par1=ta_umol + 0.5, **kw)["dic"] - pyco2.sys(par1=ta_umol - 0.5, **kw)["dic"]
        dev.append(abs(float(full) - ref))
    res["X1_sulfate_fluoride_effect_abs_eta"] = {"max": max(dev), "mean": sum(dev) / len(dev), "n": len(dev)}

    # N1 / N2: corrupted models must exclude PyCO2SYS values
    for tag, corrupt in (("N1_swap_K1K2", {"swap_k1k2": True}), ("N2_flip_borate_sign", {"flip_borate_sign": True})):
        detected = failed = 0
        for k, (t, s, f, ta35) in enumerate(pts[:100]):
            ta_umol = ta35 * s / 35
            try:
                e = K.eta_box((t, t), (s, s), (f, f), (ta_umol * 1e-6, ta_umol * 1e-6), 0.0, corrupt)
            except RuntimeError:
                detected += 1  # model cannot even reproduce a pH bracket: counts as rejected
                failed += 1
                continue
            detected += int(not (e[0] <= pyvals[k] <= e[1]))
        res[tag] = {"n": 100, "detected": detected, "bracketing_failed": failed, "pass": detected >= 95}
        print(tag, res[tag], flush=True)

    # N3: unit error: 420 read as atm -> 4.2e8 uatm; box guard rejects, forced evaluation disagrees
    def guard(f_uatm: float) -> bool:
        return BOX["f"][0] <= f_uatm <= BOX["f"][1]

    forced = None
    try:
        forced = K.float_root(15.0, 35.0, 420.0 * 1e6, 2300e-6)
    except Exception as exc:  # noqa: BLE001
        forced = f"error {exc}"
    res["N3"] = {"guard_accepts_420_atm_as_uatm_x1e6": guard(420.0 * 1e6), "guard_accepts_420_uatm": guard(420.0),
                 "forced_h_value": forced, "pass": (not guard(420.0 * 1e6)) and guard(420.0)}
    res["seconds"] = time.time() - t0
    (outdir / "seawater_result.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    if sys.argv[2] == "controls":
        main(Path(sys.argv[1]))
    else:
        run_enclosure(Path(sys.argv[1]), sys.argv[2], {"U0": 0.0, "U1": 1.0, "U2": 2.0}[sys.argv[2]])
