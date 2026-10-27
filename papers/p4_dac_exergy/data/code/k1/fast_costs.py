"""Vectorised second implementation of the face-value and exergy costs of exergy.py (written independently from
the ledger code, directly from the Terms arrays). Used for the joint scan and cross-checked against exergy.py."""

from __future__ import annotations

import numpy as np

from dac_model import R, Terms


def costs(t: Terms, T0: float) -> dict:
    """Return face-value E, works, NC heat cost, credits, refrigeration part (J/kg_sorb) at ambient T0."""
    ts = t.ts
    tm = 0.5 * (ts[1:] + ts[:-1])
    q1 = t.Q_ads_co2 + t.Q_ads_n2  # heat out at T1 (if > 0)
    qin2 = (t.Q_des_co2 + t.Q_des_n2 + t.E_heat_co2 + t.E_heat_n2 + t.E_heat_sorb)[1:]  # signed heat in, step 2
    gas_c = 4.5 * R * t.n_co2[-1] + 3.5 * R * t.n_n2[-1]
    ctot = t.cv + gas_c
    q3 = 0.5 * (ctot[1:] + ctot[:-1]) * (ts[1:] - ts[:-1])  # heat out, step 3 (trapezoid)
    works = float(t.W_ads_co2 + t.W_ads_n2 + np.nansum(t.W_des_co2 + t.W_des_n2) + np.nansum(t.E_P))
    # signed exergy contributions: heat in at T costs (1 - T0/T); heat out at T costs (T0/T - 1)
    c1 = q1 * (T0 / ts[0] - 1.0)
    c2 = qin2 * (1.0 - T0 / tm)  # negative qin2 (= heat out) gives q_out (T0/T - 1): same formula
    c3 = q3 * (T0 / tm - 1.0)
    allc = np.concatenate([[c1], c2, c3])
    allc = allc[np.isfinite(allc)]
    nc = float(allc[allc > 0].sum())
    credit = float(-allc[allc < 0].sum())
    refr = float(max(c1, 0.0) + c3[c3 > 0].sum() + (c2[(c2 > 0) & (qin2 < 0)]).sum())
    E_fv = float(q1 + np.nansum(qin2) + works)
    return {"E_fv": E_fv, "works": works, "nc": nc, "credit": credit, "refr": refr, "q3": float(q3.sum())}


def xi_set(t: Terms, T0s: tuple, rs: tuple) -> dict:
    out = {}
    base = None
    for T0 in T0s:
        c = costs(t, T0)
        base = c
        for r in rs:
            B = c["works"] + c["nc"] - r * c["credit"]
            out[f"ex_{T0}_{r}"] = float(t.dn_co2 / B * 1e6) if B > 0 else None
    out["fv"] = float(t.dn_co2 / base["E_fv"] * 1e6) if base["E_fv"] > 0 else None
    return out
