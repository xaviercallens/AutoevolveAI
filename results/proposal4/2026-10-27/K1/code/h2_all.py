"""K1-H2 over every stored Pareto path of every optimized-cycle file (no re-optimisation).

For each path: signed reversible exergy cost B_rev per mol CO2 (the second-law floor of the model's own heat
flows, works at face value) vs ideal-mixture W_min at the delivered purity, (i) at P0 = 101325 Pa and (ii) at the
lowest pressure of the path (the most permissive bound, used by the gate). Also xi_fv, xi_NC (r = 0), the
sensible closure of the gate, and (per material) which stored Pareto path maximises xi under each accounting and
its start temperature (a re-selection inside the stored Pareto set, Tier X).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exergy import build_ledger, consistency_gate, exergy_cost, face_value_cost, w_min_per_mol  # noqa: E402
from load_data import Dataset  # noqa: E402
from stored import n_paths, terms_from_stored  # noqa: E402

T0S = (273.15, 298.15, 313.15)


def main() -> int:
    ds = Dataset(Path(sys.argv[1]))
    outp = Path(sys.argv[2])
    t0 = time.time()
    names = ds.optimized_names()
    n_files = len(names)
    n_mat_with_paths = 0
    n_paths_total = 0
    viol_low = {T0: 0 for T0 in T0S}
    viol_p0 = {T0: 0 for T0 in T0S}
    gate_fail = {T0: 0 for T0 in T0S}
    gate_reasons: dict[str, int] = {}
    worst = {T0: None for T0 in T0S}
    per_mat = []
    xi_fv_max = 0.0
    xi_fv_max_name = None
    gt10: set[str] = set()
    for k, name in enumerate(names):
        try:
            opt = ds.optimized(name)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        npth = n_paths(opt)
        recs = []
        for i in range(npth):
            try:
                t = terms_from_stored(opt, i)
            except (KeyError, TypeError, IndexError, ValueError):
                t = None
            if t is None or not np.isfinite(t.xi) or t.dn_co2 <= 0 or not np.isfinite(t.E):
                continue
            L = build_ledger(t)
            y = t.purity
            rec = {"i": i, "T1": float(t.ts[0]), "Tend": float(t.ts[-1]), "purity": float(y),
                   "xi_fv": float(t.xi * 1e6), "xi_post": float((opt["Intrinsic_capture_efficiency"][i] or float("nan")) * 1e6)}
            if rec["xi_post"] > 10.0:
                gt10.add(name)
            if rec["xi_post"] > xi_fv_max:
                xi_fv_max, xi_fv_max_name = rec["xi_post"], name
            for T0 in T0S:
                brev = exergy_cost(L, T0, 1.0) / t.dn_co2
                bnc = exergy_cost(L, T0, 0.0)
                wl = w_min_per_mol(T0, 400e-6, y, min(L.Pend, L.P1) / 101325.0)
                wp = w_min_per_mol(T0, 400e-6, y, 1.0)
                rec[f"xi_nc_{T0}"] = float(t.dn_co2 / bnc * 1e6) if bnc > 0 else None
                rec[f"brev_over_wmin_lowP_{T0}"] = float(brev / wl) if wl > 0 else None
                if wl > 0 and brev < wl:
                    viol_low[T0] += 1
                if wp > 0 and brev < wp:
                    viol_p0[T0] += 1
                g = consistency_gate(L, T0, xi_reported_umol_per_J=t.xi * 1e6)
                if not g.ok:
                    gate_fail[T0] += 1
                    for rr in g.reasons:
                        gate_reasons[rr[:2] + f"@{T0}"] = gate_reasons.get(rr[:2] + f"@{T0}", 0) + 1
                ratio = rec[f"brev_over_wmin_lowP_{T0}"]
                if ratio is not None and (worst[T0] is None or ratio < worst[T0][0]):
                    worst[T0] = (ratio, name, i, rec["T1"], rec["purity"])
            recs.append(rec)
        if not recs:
            continue
        n_mat_with_paths += 1
        n_paths_total += len(recs)
        bf = max(recs, key=lambda r: r["xi_fv"])
        m = {"name": name, "n": len(recs), "T1_best_fv": bf["T1"], "xi_best_fv": bf["xi_fv"]}
        for T0 in T0S:
            c = [r for r in recs if r[f"xi_nc_{T0}"] is not None]
            if c:
                be = max(c, key=lambda r: r[f"xi_nc_{T0}"])
                m[f"T1_best_nc_{T0}"] = be["T1"]
                m[f"xi_best_nc_{T0}"] = be[f"xi_nc_{T0}"]
        per_mat.append(m)
        if k % 1000 == 0:
            print(k, n_files, round(time.time() - t0), flush=True)
    summ = {"n_optimized_files": n_files, "n_materials_with_valid_paths": n_mat_with_paths,
            "n_paths": n_paths_total, "H2_violations_lowP": viol_low, "H2_violations_P0": viol_p0,
            "gate_failures": gate_fail, "gate_failure_reasons": gate_reasons,
            "closest_to_Wmin_lowP": {str(k): v for k, v in worst.items()},
            "max_posterior_xi_umol_per_J": [xi_fv_max, xi_fv_max_name],
            "n_materials_xi_post_gt_10": sorted(gt10), "seconds": round(time.time() - t0, 1)}
    for T0 in T0S:
        a = [m for m in per_mat if f"T1_best_nc_{T0}" in m]
        summ[f"reselect_best_fv_T1_below_T0_{T0}"] = sum(1 for m in a if m["T1_best_fv"] < T0)
        summ[f"reselect_best_nc_T1_below_T0_{T0}"] = sum(1 for m in a if m[f"T1_best_nc_{T0}"] < T0)
        summ[f"reselect_n_{T0}"] = len(a)
    outp.write_text(json.dumps({"summary": summ, "per_material": per_mat}, default=float))
    print(json.dumps(summ, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
