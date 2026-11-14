"""Revision 2026-10-27 (audit item B1): K1-H2 over EVERY stored Pareto path of every optimized-cycle file, with BOTH
step-3 quadratures, against BOTH W_min floors, at all three T0.

  "trapezoid": the v1 rule (reproduces the retracted 14/18/21 low-P and 16+22+25 = 63 P0 flags);
  "right":     the right-point rule of the published step 2 (closure-consistent; the revised convention).

Fixes the v1 own-counter bug (h2_all.py skipped W_min(low P) < 0 cases): every path is compared with both floors,
whatever the floor's sign. Also records, under the right rule, the G2 sensible-closure maximum over all paths (an
implementation self-check: it is exact by construction) and the stored-Pareto re-selection counts.

Usage: python -I rev_h2_rules.py <DAC_data dir> <out.json>
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exergy import build_ledger, exergy_cost, w_min_per_mol  # noqa: E402
from load_data import Dataset  # noqa: E402
from stored import n_paths, terms_from_stored  # noqa: E402

T0S = (273.15, 298.15, 313.15)
RULES = ("trapezoid", "right")
X_AIR = 400e-6  # alpha = 400/1000000 in run_optimize_intrinsic_dac.jl:15 (NIST v0.0.2)


def main() -> int:
    ds = Dataset(Path(sys.argv[1]))
    outp = Path(sys.argv[2])
    t0 = time.time()
    names = ds.optimized_names()
    counts = {rule: {"lowP": {str(T0): 0 for T0 in T0S}, "P0": {str(T0): 0 for T0 in T0S}} for rule in RULES}
    mats = {rule: {"lowP": {str(T0): set() for T0 in T0S}, "P0": {str(T0): set() for T0 in T0S}} for rule in RULES}
    violators: list[dict] = []
    g2_max_right = 0.0
    g2_max_trap = 0.0
    n_mat = 0
    n_paths_total = 0
    xi_post_max = (0.0, None)
    gt10: set[str] = set()
    resel = {str(T0): {"fv_below": 0, "nc_below": 0, "n": 0} for T0 in T0S}
    for k, name in enumerate(names):
        try:
            opt = ds.optimized(name)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        recs = []
        for i in range(n_paths(opt)):
            try:
                t = terms_from_stored(opt, i)
            except (KeyError, TypeError, IndexError, ValueError):
                t = None
            if t is None or not np.isfinite(t.xi) or t.dn_co2 <= 0 or not np.isfinite(t.E):
                continue
            post = opt["Intrinsic_capture_efficiency"][i]
            xp = float(post) * 1e6 if post is not None else float("nan")
            if xp > 10.0:
                gt10.add(name)
            if xp > xi_post_max[0]:
                xi_post_max = (xp, name)
            y = float(t.purity)
            rec = {"T1": float(t.ts[0]), "xi_fv": float(t.xi * 1e6)}
            for rule in RULES:
                L = build_ledger(t, step3=rule)
                g2 = abs(L.sorb_heat_step2 - L.sorb_heat_step3) / max(abs(L.sorb_heat_step3), 1e-300)
                if rule == "right":
                    g2_max_right = max(g2_max_right, g2)
                else:
                    g2_max_trap = max(g2_max_trap, g2)
                for T0 in T0S:
                    brev = exergy_cost(L, T0, 1.0) / t.dn_co2
                    wl = w_min_per_mol(T0, X_AIR, y, min(L.Pend, L.P1) / 101325.0)
                    wp = w_min_per_mol(T0, X_AIR, y, 1.0)
                    vl, vp = bool(brev < wl), bool(brev < wp)
                    if vl:
                        counts[rule]["lowP"][str(T0)] += 1
                        mats[rule]["lowP"][str(T0)].add(name)
                    if vp:
                        counts[rule]["P0"][str(T0)] += 1
                        mats[rule]["P0"][str(T0)].add(name)
                    if vl or vp:
                        violators.append({"rule": rule, "name": name, "i": i, "T0": T0, "purity": y,
                                          "dn_CO2_mol_per_kg": float(t.dn_co2), "xi_fv_umol_per_J": float(t.xi * 1e6),
                                          "B_rev_kJ_per_mol": brev / 1e3, "W_min_lowP_kJ": wl / 1e3,
                                          "W_min_P0_kJ": wp / 1e3, "lowP": vl, "P0": vp})
                    if rule == "right":
                        bnc = exergy_cost(L, T0, 0.0)
                        rec[f"xi_nc_{T0}"] = float(t.dn_co2 / bnc * 1e6) if bnc > 0 else None
            recs.append(rec)
        if not recs:
            continue
        n_mat += 1
        n_paths_total += len(recs)
        bf = max(recs, key=lambda r: r["xi_fv"])
        for T0 in T0S:
            c = [r for r in recs if r[f"xi_nc_{T0}"] is not None]
            if c:
                be = max(c, key=lambda r: r[f"xi_nc_{T0}"])
                resel[str(T0)]["n"] += 1
                resel[str(T0)]["fv_below"] += int(bf["T1"] < T0)
                resel[str(T0)]["nc_below"] += int(be["T1"] < T0)
        if k % 1000 == 0:
            print(k, len(names), round(time.time() - t0), flush=True)
    summ = {"n_optimized_files": len(names), "n_materials_with_valid_paths": n_mat, "n_paths": n_paths_total,
            "violations": counts,
            "violating_materials": {r: {f: {T0: sorted(v) for T0, v in d.items()} for f, d in mats[r].items()}
                                    for r in RULES},
            "G2_closure_max_rel_right": g2_max_right, "G2_closure_max_rel_trapezoid": g2_max_trap,
            "max_posterior_xi_umol_per_J": list(xi_post_max), "n_materials_xi_post_gt_10": len(gt10),
            "reselect_right_rule": resel, "x_air": X_AIR, "seconds": round(time.time() - t0, 1)}
    outp.write_text(json.dumps({"summary": summ, "violators": violators}, indent=1, default=float))
    print(json.dumps(summ, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
