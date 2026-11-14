"""Exergy re-accounting of the 14 Table 2 paths (stored nominal terms) + the consistency-gate controls."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dac_model import step_terms  # noqa: E402
from exergy import build_ledger, consistency_gate, exergy_cost, face_value_cost, heat_costs, w_min_per_mol  # noqa: E402
from load_data import Dataset  # noqa: E402
from stored import terms_from_stored  # noqa: E402

T0S = (273.15, 298.15, 313.15)


def evaluate(L, T0s=T0S) -> dict:
    out = {"xi_fv_umol_per_J": L.dn_co2 / face_value_cost(L) * 1e6}
    for T0 in T0s:
        nc, credit, refr = heat_costs(L, T0)
        works = sum(L.works.values())
        d = {}
        for r in (0.0, 0.5, 1.0):
            B = exergy_cost(L, T0, r)
            d[f"r={r}"] = {"B_J_per_kg": B, "xi_umol_per_J": L.dn_co2 / B * 1e6 if B > 0 else None,
                           "B_per_mol_kJ": B / L.dn_co2 / 1e3}
        y = L.dn_co2 / (L.dn_co2 + L.dn_n2)
        d["works_J_per_kg"] = works
        d["refrigeration_J_per_kg"] = refr
        d["nc_heat_J_per_kg"] = nc
        d["credits_J_per_kg"] = credit
        d["refrigeration_share_of_B_NC"] = refr / (nc + works)
        d["W_min_P0_kJ_per_mol"] = w_min_per_mol(T0, 400e-6, y) / 1e3
        d["W_min_lowP_kJ_per_mol"] = w_min_per_mol(T0, 400e-6, y, min(L.Pend, L.P1) / 101325.0) / 1e3
        out[f"T0={T0}"] = d
    return out


def main() -> int:
    ds = Dataset(Path(sys.argv[1]))
    pc = json.loads(Path(sys.argv[2]).read_text())
    outp = Path(sys.argv[3])
    rows = []
    for r in pc["rows"]:
        name = r["row"][0].replace(" ", "_")
        opt = ds.optimized(name)
        t = terms_from_stored(opt, r["solution_index"])
        L = build_ledger(t)
        ev = evaluate(L)
        g = consistency_gate(L, 298.15, xi_reported_umol_per_J=t.xi * 1e6)
        rows.append({"row": r["row"][:2] + r["row"][5:], "T1": L.T1, "Tend": L.Tend, "purity_nominal": t.purity,
                     "xi_nominal_umol_per_J": t.xi * 1e6, "eval": ev,
                     "gate_T0_298": {"ok": g.ok, "reasons": g.reasons, "numbers": g.numbers}})
    # ---------- controls ----------
    base = terms_from_stored(ds.optimized("BEVQID_clean"), [r for r in pc["rows"] if r["row"][0] == "BEVQID clean"][0]
                             ["solution_index"])
    controls = {}
    # positive control 1: the real ledger passes the gate
    gL = consistency_gate(build_ledger(base), 298.15, xi_reported_umol_per_J=base.xi * 1e6)
    controls["PC_real_BEVQID_passes_gate"] = {"ok": gL.ok, "reasons": gL.reasons}
    # positive control 2: a path entirely at T >= T0: same material arrays, temperatures shifted to start at 300 K
    sh = copy.deepcopy(base)
    shift = 300.0 - sh.ts[0]
    ts2 = sh.ts + shift
    t2 = step_terms(ts2, sh.ps, sh.n_co2, sh.n_n2, sh.d_co2, sh.d_n2, sh.q_co2, sh.q_n2, sh.cv)
    L2 = build_ledger(t2)
    T0 = 298.15
    ws = [(1 - T0 / h.T) if h.direction == "in" else (T0 / h.T - 1) for h in L2.heats]
    win = [(1 - T0 / h.T) for h in L2.heats if h.direction == "in"]
    _, _, refr2 = heat_costs(L2, T0)
    controls["PC_all_above_T0"] = {"min_T": float(min(h.T for h in L2.heats)), "heat_in_weights_in_0_1":
                                   bool(all(0 < w < 1 for w in win)), "refrigeration_term": refr2,
                                   "all_out_weights_negative_free": bool(all(w <= 0 for w, h in zip(ws, L2.heats)
                                                                             if h.direction == "out"))}
    # negative control 1: double-counted sorbent heating in step 2
    dbl = copy.deepcopy(base)
    dbl.E_heat_sorb = 2 * dbl.E_heat_sorb
    Ld = build_ledger(dbl)
    Ld.sorb_heat_step2 = float(np.nansum(dbl.E_heat_sorb))
    gd = consistency_gate(Ld, 298.15)
    controls["NC_double_counted_sorbent_heat"] = {"rejected": not gd.ok, "reasons": gd.reasons}
    # negative control 2: planted unit error (xi reported in mol/J but read as umol/J, i.e. factor 1e6)
    gu = consistency_gate(build_ledger(base), 298.15, xi_reported_umol_per_J=base.xi * 1e12)
    controls["NC_unit_error_x1e6"] = {"rejected": not gu.ok, "reasons": gu.reasons}
    # negative control 2b: the paper's sentence value 1.0e5 mol/J taken at face value (= 1.0e11 umol/J)
    gs = consistency_gate(build_ledger(base), 298.15, xi_reported_umol_per_J=1.0e11)
    controls["NC_sentence_value_1e5_mol_per_J"] = {"rejected": not gs.ok, "reasons": gs.reasons}
    # negative control 3: planted W_min violation: heats of adsorption set to zero (only RT works remain)
    wv = copy.deepcopy(base)
    t3 = step_terms(wv.ts, wv.ps, wv.n_co2, wv.n_n2, wv.d_co2, wv.d_n2, 0 * wv.q_co2, 0 * wv.q_n2, wv.cv)
    g3 = consistency_gate(build_ledger(t3), 298.15)
    controls["NC_heat_removed_violates_Wmin"] = {"rejected": not g3.ok, "reasons": g3.reasons}
    res = {"rows": rows, "controls": controls}
    outp.write_text(json.dumps(res, indent=1, default=float))
    for x in rows:
        e = x["eval"]
        print(x["row"][0], "T1", round(x["T1"], 1), "Tend", round(x["Tend"], 1), "xi_fv", round(e["xi_fv_umol_per_J"], 3),
              "| T0=298 NC", round(e["T0=298.15"]["r=0.0"]["xi_umol_per_J"], 2), "r.5",
              round(e["T0=298.15"]["r=0.5"]["xi_umol_per_J"], 2), "rev", e["T0=298.15"]["r=1.0"]["xi_umol_per_J"],
              "Brev kJ/mol", round(e["T0=298.15"]["r=1.0"]["B_per_mol_kJ"], 2), "Wmin P0/lowP",
              round(e["T0=298.15"]["W_min_P0_kJ_per_mol"], 2), round(e["T0=298.15"]["W_min_lowP_kJ_per_mol"], 2),
              "refr share", round(e["T0=298.15"]["refrigeration_share_of_B_NC"], 3), "gate", x["gate_T0_298"]["ok"],
              x["gate_T0_298"]["reasons"])
    print(json.dumps(controls, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
