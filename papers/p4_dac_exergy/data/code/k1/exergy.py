"""Exergy (second-law) re-accounting of the published IntrinsicDACCycle energy terms, plus a consistency gate.

Convention change tested (and only this one): every HEAT is weighted by its Carnot factor relative to an explicit
ambient temperature T0; every WORK term (W_ads, W_des, E_P, including the abs() in E_P) is kept exactly as
published. Step 3 (return from T_end to T1), which the paper sets to E3 = 0, is given an explicit sensible-heat
ledger entry computed by an independent quadrature of Cv(T) (trapezoid on the path grid), not copied from step 2.

Weights for a heat Q > 0 crossing the boundary at temperature T:
  heat IN  at T: signed cost (1 - T0/T)      no-credit cost max(0, 1 - T0/T)
  heat OUT at T: signed cost (T0/T - 1)      no-credit cost max(0, T0/T - 1)
"no-credit" (NC) = heat supplied below T0 is free (from ambient), heat rejected above T0 is free (to ambient),
nothing is recovered: the faithful second-law reading of "no energy recovery".
"signed" (REV) = reversible heat engines/pumps against T0 credit every negative contribution: the second-law floor
for the model's heat flows (equivalent to perfect recovery).
A recovery fraction r in [0, 1] credits the fraction r of the forgone credits: B(r) = B_NC - r * credits.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from dac_model import R, Terms


@dataclass
class HeatFlow:
    label: str
    step: int
    direction: str  # "in" or "out"
    T: float  # K
    Q: float  # J/kg_sorb, > 0


@dataclass
class Ledger:
    heats: list[HeatFlow] = field(default_factory=list)
    works: dict[str, float] = field(default_factory=dict)
    dn_co2: float = 0.0
    dn_n2: float = 0.0
    T1: float = 0.0
    Tend: float = 0.0
    Pend: float = 0.0
    P1: float = 0.0
    sorb_heat_step2: float = 0.0  # as published (right-point rule)
    sorb_heat_step3: float = 0.0  # independent trapezoid


def _add(heats: list[HeatFlow], label: str, step: int, T: float, signed_in: float) -> None:
    """Record a heat that is 'signed_in' J/kg INTO the system at T (negative -> it is heat out)."""
    if signed_in == 0.0 or not np.isfinite(signed_in):
        return
    heats.append(HeatFlow(label, step, "in" if signed_in > 0 else "out", float(T), float(abs(signed_in))))


def build_ledger(t: Terms) -> Ledger:
    L = Ledger(dn_co2=t.dn_co2, dn_n2=t.dn_n2, T1=float(t.ts[0]), Tend=float(t.ts[-1]), P1=float(t.ps[0]),
               Pend=float(t.ps[-1]))
    # Step 1: heat of adsorption released at T1 and removed by cooling ("energy will be spent cooling").
    _add(L.heats, "step1_Qads", 1, t.ts[0], -(t.Q_ads_co2 + t.Q_ads_n2))
    # Step 2: per sub-step heat into the system at the sub-step mid temperature.
    tmid = 0.5 * (t.ts[1:] + t.ts[:-1])
    for i in range(1, len(t.ts)):
        qin = (t.Q_des_co2[i] + t.Q_des_n2[i] + t.E_heat_co2[i] + t.E_heat_n2[i] + t.E_heat_sorb[i])
        _add(L.heats, f"step2_{i}", 2, tmid[i - 1], qin)
    L.sorb_heat_step2 = float(np.nansum(t.E_heat_sorb))
    # Step 3: cooling from T_end back to T1 of the sorbent + the gas still adsorbed at the end of step 2
    # (9/2 R per CO2, 7/2 R per N2: the paper's own heat capacities for adsorbed gas), trapezoid on the grid.
    gas_c = 4.5 * R * t.n_co2[-1] + 3.5 * R * t.n_n2[-1]
    ts = t.ts
    c_tot = t.cv + gas_c
    q3 = 0.5 * (c_tot[1:] + c_tot[:-1]) * (ts[1:] - ts[:-1])  # per interval, heat OUT
    L.sorb_heat_step3 = float(np.sum(0.5 * (t.cv[1:] + t.cv[:-1]) * (ts[1:] - ts[:-1])))
    for i in range(len(q3)):
        _add(L.heats, f"step3_{i}", 3, tmid[i], -q3[i])
    L.works = {
        "W_ads": float(t.W_ads_co2 + t.W_ads_n2),
        "W_des": float(np.nansum(t.W_des_co2 + t.W_des_n2)),
        "E_P": float(np.nansum(t.E_P)),
    }
    return L


def heat_costs(L: Ledger, T0: float) -> tuple[float, float, float]:
    """Return (B_NC_heat, credits, refrigeration_part) for ambient T0 [K]."""
    nc = 0.0
    credit = 0.0
    refr = 0.0
    for h in L.heats:
        w = (1.0 - T0 / h.T) if h.direction == "in" else (T0 / h.T - 1.0)
        c = h.Q * w
        if c >= 0:
            nc += c
            if h.direction == "out":
                refr += c
        else:
            credit += -c
    return nc, credit, refr


def exergy_cost(L: Ledger, T0: float, r: float = 0.0) -> float:
    """B(r) in J/kg_sorb: works at face value + NC heat costs - r * credits."""
    nc, credit, _ = heat_costs(L, T0)
    return sum(L.works.values()) + nc - r * credit


def face_value_cost(L: Ledger, r: float = 0.0) -> float:
    """The published E_Total (steps 1+2, E3 = 0) minus r * (step-3 sensible heat), i.e. Eq. 5 adjusted."""
    e = sum(L.works.values())
    q3 = 0.0
    for h in L.heats:
        if h.step == 1:
            e += h.Q if h.direction == "out" else -h.Q  # as published: E1 counts the removed heat as a cost
        elif h.step == 2:
            e += h.Q if h.direction == "in" else -h.Q  # as published: the signed sum over step 2
        elif h.step == 3:
            q3 += h.Q
    return e - r * q3


def w_min_per_mol(T0: float, x_air: float, y: float, p_out_over_p_air: float = 1.0) -> float:
    """Ideal-mixture minimum work [J per mol CO2] to take CO2 out of an infinite air reservoir (capture fraction
    f -> 0) at mole fraction x_air and deliver a product of CO2 mole fraction y at total pressure p_out (the N2
    co-product dn_N2 = dn_CO2 (1 - y)/y is delivered in the same stream). Ideal gases, isothermal at T0."""
    w = R * T0 * (np.log(y * p_out_over_p_air / x_air))
    if y < 1.0:
        w += R * T0 * ((1.0 - y) / y) * np.log((1.0 - y) * p_out_over_p_air / (1.0 - x_air))
    return float(w)


@dataclass
class GateResult:
    ok: bool
    reasons: list[str]
    numbers: dict[str, float]


def consistency_gate(L: Ledger, T0: float, xi_reported_umol_per_J: float | None = None,
                     x_air: float = 400e-6) -> GateResult:
    """Accept a ledger only if it is internally consistent.

    G1 uniqueness: every (step, label) heat flow appears once.
    G2 cyclic sensible closure: sorbent heat absorbed in step 2 (published right-point rule) equals sorbent heat
       released in step 3 (independent trapezoid) within 2 %.
    G3 second law: the signed reversible cost B(r=1) per mol CO2 is >= W_min at the delivered purity and at the
       lowest delivery pressure of the path (the most permissive W_min); a violation means the inputs are
       thermodynamically inconsistent.
    G4 units: a reported xi (umol/J) must equal dn_CO2 / E_Total * 1e6 within 1e-9 relative, and lie below
       1 / W_min(P0, y) in umol/J.
    """
    reasons: list[str] = []
    keys = [(h.step, h.label) for h in L.heats]
    if len(keys) != len(set(keys)):
        reasons.append("G1 duplicate heat flow")
    s2, s3 = L.sorb_heat_step2, L.sorb_heat_step3
    rel = abs(s2 - s3) / max(abs(s3), 1e-300)
    if rel > 0.02:
        reasons.append(f"G2 sensible closure broken: step2 {s2:.6g} vs step3 {s3:.6g} J/kg (rel {rel:.3g})")
    y = L.dn_co2 / (L.dn_co2 + L.dn_n2)
    wmin_low_p = w_min_per_mol(T0, x_air, y, min(L.Pend, L.P1) / 101325.0)
    wmin_p0 = w_min_per_mol(T0, x_air, y, 1.0)
    b_rev = exergy_cost(L, T0, r=1.0) / L.dn_co2
    if b_rev < wmin_low_p:
        reasons.append(f"G3 second-law violation: B_rev {b_rev:.6g} J/mol < W_min {wmin_low_p:.6g} J/mol")
    xi_fv = L.dn_co2 / face_value_cost(L) * 1e6
    if xi_reported_umol_per_J is not None:
        if abs(xi_reported_umol_per_J - xi_fv) > 1e-9 * abs(xi_fv):
            reasons.append(f"G4 unit/value mismatch: reported {xi_reported_umol_per_J:.6g} vs ledger {xi_fv:.6g} umol/J")
        if xi_reported_umol_per_J > 1e6 / wmin_p0:
            reasons.append(f"G4 reported xi {xi_reported_umol_per_J:.6g} umol/J above 1/W_min {1e6 / wmin_p0:.6g}")
    return GateResult(not reasons, reasons, {"sorb_closure_rel": rel, "B_rev_J_per_mol": b_rev,
                                             "W_min_lowP_J_per_mol": wmin_low_p, "W_min_P0_J_per_mol": wmin_p0,
                                             "xi_fv_umol_per_J": xi_fv})
