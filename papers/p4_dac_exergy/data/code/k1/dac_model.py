"""Faithful Python re-implementation of the NIST IntrinsicDACCycle v0.0.2 energy balance.

Source re-implemented (NIST software, public service licence; Zenodo record 14452152, file
IntrinsicDACCycle-0.0.2.tar.gz): src/Analyze_GCMC_Results.jl (T_to_beta, Kh_extrapolate, q_ads_inf,
keep_monotonic_decreasing, truncate_to_saturation), src/Generate_Equilibrium_Sorption.jl
(Analytical_Henry_Generate_sorption_path), src/Intrinsic_Refresh_Energy_Balance.jl (step 1, step 2, E3 = 0).
Modified work: translated to Python by an AI agent on 2026-10-27; no change of physics. Acknowledgement: NIST is
the source of the original software. Every function mirrors the Julia line by line, including the leading NaN
of the per-step arrays and the nansum over step 2.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

KB: float = 1.380649e-23  # J/K
NA: float = 6.02214076e23  # 1/mol
AMU: float = 1.66053906660e-27  # kg
R: float = NA * KB  # J/(K mol)
TVALUE: float = 1.959


def t_to_beta(t: np.ndarray | float) -> np.ndarray | float:
    """Temperature [K] -> beta [mol/kJ], as T_to_β in Analyze_GCMC_Results.jl."""
    return (1.0 / t) * (1.0 / KB) * (1.0 / NA) * 1000.0


def beta_to_t(b: np.ndarray | float) -> np.ndarray | float:
    return (1.0 / b) * (1.0 / KB) * (1.0 / NA) * 1000.0


def _powers_matrix(db: np.ndarray, power: int) -> tuple[np.ndarray, np.ndarray]:
    powers = np.arange(power, dtype=float)
    dbm = db[:, None] * np.ones(power)[None, :]
    return dbm ** powers[None, :], powers


def kh_extrapolate(beta: np.ndarray, kh_results: dict, material: dict) -> tuple[np.ndarray, np.ndarray]:
    """Kh [mmol/(kg Pa)] and its std, as Kh_extrapolate."""
    rho = float(material["cell_density"]) * AMU * 1e30  # kg/m^3
    b0 = float(kh_results["beta"])
    coeff = np.asarray(kh_results["Kcoeff"], dtype=float)
    db = np.asarray(beta, dtype=float) - b0
    dbp, _ = _powers_matrix(db, coeff.size)
    x = (dbp * coeff[None, :]).sum(axis=1)
    kh = (np.asarray(beta) / rho) * x
    cov = np.array(kh_results["Kcoeff_covar"], dtype=float).T  # hcat of rows -> columns
    jac = (np.asarray(beta)[:, None] / rho) * dbp
    var = np.einsum("ij,jk,ik->i", jac, cov, jac)
    std = np.sqrt(var / float(kh_results["trials"])) * TVALUE
    return kh, std


def q_ads_inf(beta: np.ndarray, kh_results: dict) -> np.ndarray:
    """Heat of adsorption at infinite dilution [kJ/mol], as qₐ∞ (mean only)."""
    b0 = float(kh_results["beta"])
    coeff = np.asarray(kh_results["Kcoeff"], dtype=float)
    p = coeff.size
    db = np.asarray(beta, dtype=float) - b0
    dbp, powers = _powers_matrix(db, p)
    den = (dbp * coeff[None, :]).sum(axis=1)
    dbm1 = db[:, None] * np.ones(p - 1)[None, :]
    num = ((dbm1 ** (powers[1:][None, :] - 1.0)) * coeff[1:][None, :] * powers[1:][None, :]).sum(axis=1)
    return 1.0 / np.asarray(beta) + num / den


def keep_monotonic_decreasing(x: np.ndarray) -> np.ndarray:
    """Return the (1-based in Julia, here 0-based) indices kept by keep_monotonic_decreasing.

    Julia: truth = [true; x[2:end] .<= x[1:end-1]]; indices = cumsum(truth[truth .== true]), i.e. 1..k with
    k = count(truth). Note: this keeps the FIRST k entries, not the entries where truth is true.
    """
    truth = np.concatenate([[True], x[1:] <= x[:-1]])
    k = int(truth.sum())
    return np.arange(k)


def analytical_henry_sorption_path(ps: np.ndarray, alpha: float, h_co2: np.ndarray, h_n2: np.ndarray
                                   ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Analytical_Henry_Generate_sorption_path [mmol/kg]."""
    n = len(ps)
    n_c = np.empty(n)
    n_n = np.empty(n)
    d_c = np.full(n, np.nan)
    d_n = np.full(n, np.nan)
    al = np.empty(n)
    n_c[0] = h_co2[0] * ps[0] * alpha
    n_n[0] = h_n2[0] * ps[0] * (1 - alpha)
    al[0] = alpha
    for i in range(1, n):
        p = ps[i]
        hc = h_co2[i]
        hn = h_n2[i]
        a = hn * p - hc * p
        b = n_c[i - 1] + n_n[i - 1] + hc * p - hn * p
        c = -1.0 * n_c[i - 1]
        disc = b * b - 4 * a * c
        if disc < 0:
            raise ValueError("DomainError: sqrt of negative number")
        s = math.sqrt(disc)
        x1 = (-b + s) / (2 * a)
        x2 = (-b - s) / (2 * a)
        x = x1 if abs(x1 - al[i - 1]) <= abs(x2 - al[i - 1]) else x2  # argmin picks first on ties
        n_c[i] = hc * p * x
        n_n[i] = hn * p * (1 - x)
        d_c[i] = n_c[i - 1] - n_c[i]
        d_n[i] = n_n[i - 1] - n_n[i]
        al[i] = x
    return n_c, n_n, d_c, d_n, al


@dataclass
class Terms:
    """Per-path energy terms in J/kg_sorb, exactly as the Julia evaluators store them."""

    ts: np.ndarray
    ps: np.ndarray
    n_co2: np.ndarray  # mol/kg
    n_n2: np.ndarray
    d_co2: np.ndarray
    d_n2: np.ndarray
    q_co2: np.ndarray  # J/mol
    q_n2: np.ndarray
    cv: np.ndarray  # J/(kg K)
    Q_ads_co2: float
    Q_ads_n2: float
    W_ads_co2: float
    W_ads_n2: float
    Q_des_co2: np.ndarray
    Q_des_n2: np.ndarray
    W_des_co2: np.ndarray
    W_des_n2: np.ndarray
    E_heat_co2: np.ndarray
    E_heat_n2: np.ndarray
    E_heat_sorb: np.ndarray
    E_P: np.ndarray
    E1: float
    E2: float
    E3: float
    E: float
    dn_co2: float
    dn_n2: float
    xi: float  # mol/J
    purity: float


def step_terms(ts: np.ndarray, ps: np.ndarray, n_co2: np.ndarray, n_n2: np.ndarray, d_co2: np.ndarray,
               d_n2: np.ndarray, q_co2: np.ndarray, q_n2: np.ndarray, cv: np.ndarray) -> Terms:
    """intrinsic_refresh_step_1 + intrinsic_refresh_step_2 + E3 = 0 (inputs in mol/kg, J/mol, J/(kg K))."""
    dn_c = n_co2[0] - n_co2[-1]
    dn_n = n_n2[0] - n_n2[-1]
    Qa_c = dn_c * q_co2[0]
    Qa_n = dn_n * q_n2[0]
    Wa_c = -(-dn_c) * R * ts[0]
    Wa_n = -(-dn_n) * R * ts[0]
    Qd_c = d_co2 * q_co2
    Qd_n = d_n2 * q_n2
    tmid = np.concatenate([[np.nan], 0.5 * (ts[1:] + ts[:-1])])
    Wd_c = d_co2 * R * tmid
    Wd_n = d_n2 * R * tmid
    dT = np.concatenate([[np.nan], ts[1:] - ts[:-1]])
    nc_mid = np.concatenate([[np.nan], 0.5 * (n_co2[1:] + n_co2[:-1])])
    nn_mid = np.concatenate([[np.nan], 0.5 * (n_n2[1:] + n_n2[:-1])])
    Eh_c = 4.5 * R * dT * nc_mid
    Eh_n = 3.5 * R * dT * nn_mid
    Eh_s = cv * dT
    logp = np.concatenate([[np.nan], np.log(ps[1:] / ps[:-1])])
    E_P = np.abs((nc_mid + nn_mid) * R * tmid * logp)
    E1 = Qa_c + Qa_n + Wa_c + Wa_n
    E2 = float(np.nansum(Qd_c + Qd_n + Wd_c + Wd_n + Eh_c + Eh_n + Eh_s + E_P))
    E3 = 0.0
    E = E1 + E2 + E3
    return Terms(ts, ps, n_co2, n_n2, d_co2, d_n2, q_co2, q_n2, cv, Qa_c, Qa_n, Wa_c, Wa_n, Qd_c, Qd_n, Wd_c,
                 Wd_n, Eh_c, Eh_n, Eh_s, E_P, E1, E2, E3, E, dn_c, dn_n, dn_c / E, dn_c / (dn_c + dn_n))


def nominal_path(ts: np.ndarray, ps: np.ndarray, alpha: float, kh_co2: dict, kh_n2: dict, material: dict,
                 sat_loading_mmol_per_kg: float, cv_fn) -> Terms | None:
    """Intrinisic_refresh_path (nominal, close_enough assumed true): truncations, IAST recursion, terms.

    cv_fn(ts) must return Cv [J/(kg K)] at the (truncated) temperatures.
    """
    bs = t_to_beta(ts)
    hc, _ = kh_extrapolate(bs, kh_co2, material)
    hn, _ = kh_extrapolate(bs, kh_n2, material)
    ic = keep_monotonic_decreasing(hc)
    inn = keep_monotonic_decreasing(hn)
    idx = ic if len(ic) <= len(inn) else inn  # argmin of lengths picks first on ties
    hc, hn, ts, ps, bs = hc[idx], hn[idx], ts[idx], ps[idx], bs[idx]
    mask = (hc * alpha * ps) < sat_loading_mmol_per_kg
    hc, hn, ts, ps, bs = hc[mask], hn[mask], ts[mask], ps[mask], bs[mask]
    if ts.size == 0:
        return None
    n_c, n_n, d_c, d_n, _ = analytical_henry_sorption_path(ps, alpha, hc, hn)
    n_c, n_n, d_c, d_n = n_c * 1e-3, n_n * 1e-3, d_c * 1e-3, d_n * 1e-3
    q_c = q_ads_inf(bs, kh_co2) * 1e3
    q_n = q_ads_inf(bs, kh_n2) * 1e3
    return step_terms(ts, ps, n_c, n_n, d_c, d_n, q_c, q_n, np.asarray(cv_fn(ts), dtype=float))


def linear_path(t1: float, dT: float, p1: float, dP: float, dT_max: float = 0.25, dP_max: float = -125.0
                ) -> tuple[np.ndarray, np.ndarray]:
    """ScorePath discretisation: steps = max(length(T1:dTmax:T1+dT), length(P1:dPmax:P1+dP)); LinRange."""
    t_steps = int(math.floor((dT) / dT_max + 1e-12)) + 1 if dT >= 0 else 0
    p_steps = int(math.floor((dP) / dP_max + 1e-12)) + 1 if dP <= 0 else 0
    steps = max(t_steps, p_steps)
    return np.linspace(t1, t1 + dT, steps), np.linspace(p1, p1 + dP, steps)
