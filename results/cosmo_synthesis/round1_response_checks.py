"""Computations requested by the round-1 referees of cosmo_synthesis.tex.

Every number the revised paper states in response to the referees and that is not
already in a run's result JSON is computed here and written to
results/cosmo_synthesis/round1_response_checks.json. Nothing outside
results/cosmo_synthesis/ is written.

Sections
  h0_gate_propagation   gate tolerance (0.25 sigma on h r_d) propagated to H0 with the
                        measured d ln(hr_d)/d ln h slope (fixround_diagnostics.json)
  dr1_dr2_conventions   DR1->DR2 Omega_m shift under three uncertainty conventions
  overlap_sensitivity   SDSS-DESI N_sigma when a cross-covariance X = rho sqrt(C_S) sqrt(C_D)
                        is subtracted (illustration only; rho is not estimated)
  n4_margin             N4 margin in units of the T1 posterior-mean MC error
  camb_shifted_pull     DR2 Omega_m pull shifted by the CAMB / radiation model offsets
  aubourg_points        eq.16-vs-CAMB validation points and the stated 0.021% accuracy
  controls_count        distinct preregistered positive-control ids in DR2 controls.json
  rust_pr61             `gh pr view 61` in the rusty-SUNDIALS worktree (merge record)
  h0_audit_binding      audit-to-source hash binding of the H0 Tier A rows
Run: /mnt/disks/disk-socrateai-local-1/venv-cosmo/bin/python results/cosmo_synthesis/round1_response_checks.py
"""
from __future__ import annotations

import datetime
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
from scipy.linalg import sqrtm
from scipy.stats import chi2 as chi2dist
from scipy.stats import norm

WT = Path(__file__).resolve().parents[2]
RES = WT / "results"
OUT = RES / "cosmo_synthesis/round1_response_checks.json"
RUST = Path("/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-cosmo")


def load(rel: str) -> Any:
    return json.loads((WT / rel).read_text())


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def h0_gate_propagation() -> dict[str, Any]:
    dg = load("results/bao_bbn_h0/fixround_diagnostics.json")["slope_and_T2_propagation"]
    fit = load("results/bao_bbn_h0/fit.json")
    pre = load("results/bao_bbn_h0/preregistration.json")
    tg = {t["id"]: t for t in pre["targets"]}
    out: dict[str, Any] = {"gate_rule": pre["tolerance"]["gate_G1"], "gate_G2_rule": pre["tolerance"]["gate_G2"],
                           "formula": "dH0 = H0_target * (d_hrd / hrd_target) / slope, slope = d ln(hr_d)/d ln h"}
    for g, key, h0t, slope_key in (("G1", "T1", tg["T1"]["value"], "primary_T1_DR2_dlnhrd_dlnh"),
                                   ("G2", "T2", tg["T2"]["value"], "primary_T2_DR1_dlnhrd_dlnh")):
        hrd_t, hrd_s = fit[g]["target"]["hrd"]
        slope = dg[slope_key]
        tol_hrd = 0.25 * hrd_s
        max_dh0 = h0t * (tol_hrd / hrd_t) / slope
        off = fit[g]["chain"]["mean"]["hrd"] - hrd_t
        out[g] = {"hrd_target": hrd_t, "hrd_sigma": hrd_s, "slope": slope, "gate_tol_hrd_Mpc": tol_hrd,
                  "max_H0_shift_admitted_by_gate": max_dh0, "observed_hrd_offset_Mpc": off,
                  "observed_offset_pull": off / hrd_s, "implied_H0_shift_from_offset": h0t * (off / hrd_t) / slope,
                  "gate_passed_field": bool(fit[g]["passed"])}
    strict = pre["tolerance"]["strict_H0_km_s_Mpc"]
    soft = pre["tolerance"]["soft_H0_km_s_Mpc"]
    out["strict"] = strict
    out["soft"] = soft
    out["G1_max_exceeds_strict"] = out["G1"]["max_H0_shift_admitted_by_gate"] > strict
    out["G2_max_exceeds_strict"] = out["G2"]["max_H0_shift_admitted_by_gate"] > strict
    out["G2_max_exceeds_soft"] = out["G2"]["max_H0_shift_admitted_by_gate"] > soft
    out["T2_observed_offset"] = fit["T2_boundary_resolution"]["primary"]["abs_dH0"]
    return out


def dr1_dr2_conventions() -> dict[str, Any]:
    s = load("results/desi_dr2_bao/fit.json")["DR1_to_DR2_shift"]
    d, s1, s2 = s["Delta_Om"], s["sd_DR1"], s["sd_DR2"]
    return {"Delta_Om": d, "sd_DR1": s1, "sd_DR2": s2,
            "sigma_nested": math.sqrt(s1 ** 2 - s2 ** 2), "ratio_nested": d / math.sqrt(s1 ** 2 - s2 ** 2),
            "sigma_independent": math.hypot(s1, s2), "ratio_independent": d / math.hypot(s1, s2),
            "sigma_C1_perfect_correlation": abs(s1 - s2), "ratio_C1": d / abs(s1 - s2),
            "note": ("DESI DR2 (arXiv:2503.14738 Sec. III.C.1, footnote 12) describes its DR1-DR2 comparison as assuming "
                     "perfect correlation but computes sigma^2 = s2^2 + s1^2 - 2 C s1 s2 with C = sqrt(N_DR1/N_DR2) per "
                     "distance, which equals the nested form when s is proportional to N^-1/2. C = 1 is the bracket.")}


def overlap_sensitivity() -> dict[str, Any]:
    f = load("results/eboss_vs_desi/fit.json")
    S = f["fits"]["SDSS_eBOSS_DR16_baseline"]["emcee"]
    D = f["fits"]["DESI_DR2"]["emcee"]

    def cov(e: dict[str, Any]) -> np.ndarray:
        a, b, r = e["std_Om"], e["std_hrd"], e["corr"]
        return np.array([[a * a, r * a * b], [r * a * b, b * b]])

    cs, cd = cov(S), cov(D)
    dv = np.array([S["mean_Om"] - D["mean_Om"], S["mean_hrd"] - D["mean_hrd"]])
    rs, rd = np.real(sqrtm(cs)), np.real(sqrtm(cd))
    rows = []
    for rho in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.57, 0.6):
        x = rho * rs @ rd
        c = cs + cd - x - x.T
        ev = np.linalg.eigvalsh(c)
        ch = float(dv @ np.linalg.solve(c, dv))
        pte = float(chi2dist.sf(ch, 2))
        rows.append({"rho": rho, "chi2": ch, "PTE": pte, "N_sigma": float(norm.isf(pte / 2)),
                     "min_eigenvalue": float(ev.min()), "positive_definite": bool(ev.min() > 0)})
    return {"model": "Cov(diff) = C_S + C_D - X - X^T, X = rho sqrtm(C_S) sqrtm(C_D); emcee moments of the "
                     "baseline SDSS and DESI DR2 fits in results/eboss_vs_desi/fit.json",
            "rho_0.57_source": ("C ~ 0.57 is DR2's estimate for the LRG2 / eBOSS LRG pair only "
                                "(arXiv:2503.14738 Sec. III.C.2); used here as an illustration, not an estimate "
                                "of the parameter-level correlation"),
            "grid": rows,
            "reproduces_fit_json_at_rho0": abs(rows[0]["N_sigma"] - f["tension"]["primary_emcee_moments"]["N_sigma"]) < 1e-6}


def n4_margin() -> dict[str, Any]:
    n4 = load("results/bao_bbn_h0/controls/N4.json")
    ch = load("results/bao_bbn_h0/fit.json")["primary"]["T1_DR2"]["chain"]
    mc = ch["std"]["H0"] / math.sqrt(ch["ess"])
    marg = abs(n4["dH0_wrong_minus_correct"]) - n4["strict_tolerance"]
    return {"margin": marg, "T1_mc_error_H0": mc, "margin_over_mc": marg / mc,
            "delta_chi2_wrong_minus_correct": n4["delta_chi2_wrong_minus_correct"],
            "shift_is_MAP_not_posterior_mean": True}


def camb_shifted_pull() -> dict[str, Any]:
    f = load("results/desi_dr2_bao/fit.json")
    pull = next(r["pull_sigma"] for r in f["results"] if r["name"] == "DR2_LCDM_Om")
    camb = f["camb_crosscheck"]["primary_model_vs_camb_mnu0.06_shift_in_published_sigma"]["lcdm"]["Om"]
    rad = f["radiation_sensitivity"]["DR2_LCDM"]["shift_Om_in_published_sigma"]
    return {"pull_Om": pull, "primary_minus_camb_Om_sigma": camb,
            "pull_if_camb_model": pull - camb, "radiation_shift_Om_sigma": rad, "pull_if_radiation": pull + rad,
            "sign_convention": ("camb_crosscheck.py: shift = primary fit - CAMB truth, so a CAMB-model analysis sits "
                                "lower by that amount; radiation_sensitivity is (with radiation - without)")}


def dr2_mc_error() -> dict[str, Any]:
    f = load("results/desi_dr2_bao/fit.json")
    r = next(r for r in f["results"] if r["name"] == "DR2_LCDM_Om")
    ess = f["mcmc_diagnostics"]["DR2_LCDM"]["ess"]
    mc = r["sigma"] / math.sqrt(ess)
    return {"posterior_sd_Om": r["sigma"], "ess": ess, "mc_error_Om_mean": mc, "target_sigma": r["target_sigma"],
            "mc_error_in_published_sigma": mc / r["target_sigma"]}


def aubourg_points() -> dict[str, Any]:
    v = load("results/bao_bbn_h0/rd_camb_validation.json")["class_and_aubourg_vs_camb"]
    pts = [{"omega_b": x["omega_b"], "omega_cdm": x["omega_cdm"], "h": x["h"],
            "frac": x["frac_aub16_minus_camb"]} for x in v]
    worst = max(pts, key=lambda p: abs(p["frac"]))
    return {"points": pts, "worst": worst, "stated_accuracy_frac": 0.00021,
            "n_exceeding_stated": sum(1 for p in pts if abs(p["frac"]) > 0.00021),
            "proxy_window_note": ("literature review: proxy 3-sigma window omega_b in [0.02191, 0.02281]; Aubourg's "
                                  "statement is for N_eff = 3.046 while the CAMB table uses N_eff = 3.044")}


def controls_count() -> dict[str, Any]:
    c = load("results/desi_dr2_bao/controls.json")
    keys = list(c["positive_controls"].keys())
    ids = sorted({re.match(r"(PC\d+)", k).group(1) for k in keys if re.match(r"PC\d+", k)})
    return {"json_keys": keys, "distinct_ids": ids, "n_ids": len(ids), "n_keys": len(keys)}


def rust_pr61() -> dict[str, Any]:
    try:
        p = subprocess.run(["gh", "pr", "view", "61", "--json", "number,state,mergedAt,mergeCommit,title,headRefName"],
                           cwd=RUST, capture_output=True, text=True, timeout=60)
        rec = json.loads(p.stdout) if p.returncode == 0 else {"error": p.stderr.strip()}
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        rec = {"error": repr(e)}
    return {"command": "gh pr view 61 --json number,state,mergedAt,mergeCommit,title,headRefName", "cwd": str(RUST),
            "queried_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "result": rec}


def _theorem_statement(text: str, name: str) -> str | None:
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if re.match(rf"^theorem {re.escape(name)}\b", ln):
            block = []
            for cur in lines[i:]:
                if ":=" in cur:
                    block.append(cur[: cur.index(":=")].rstrip())
                    break
                block.append(cur)
            return "\n".join(block)
    return None


def h0_audit_binding() -> dict[str, Any]:
    cur = WT / "formal/ANSE/BAO_BBN_H0.lean"
    cur_sha = sha(cur)
    ledger = load("results/bao_bbn_h0/ledger/ledger.json")
    scratch = WT / "results/cosmo_synthesis/h0_prefix_scratch_copy.lean"  # copy of /tmp/BAO_BBN_H0_negctrl.lean
    scratch_text = scratch.read_text() if scratch.exists() else None
    rows = []
    for c in ledger["claims"]:
        if c["tier"] != "A":
            continue
        m = re.search(r"ANSE\.BAOBBNH0\.(\w+)", c.get("statement", ""))
        name = m.group(1) if m else None
        a = c.get("audit")
        audited = a.get("reviewed_source_sha256") if isinstance(a, dict) else None
        st_cur = _theorem_statement(cur.read_text(), name) if name else None
        st_old = _theorem_statement(scratch_text, name) if (name and scratch_text) else None
        rows.append({"id": c["id"], "theorem": name, "audited": isinstance(a, dict),
                     "audited_source_sha256": audited, "bound_to_current_source": audited == cur_sha,
                     "statement_in_prefix_scratch_copy_identical": (st_cur == st_old) if st_old is not None else None})
    commits = subprocess.run(["git", "log", "--format=%h %H", "--", "formal/ANSE/BAO_BBN_H0.lean"], cwd=WT,
                             capture_output=True, text=True).stdout.split("\n")
    committed_shas = []
    for ln in commits:
        if ln.strip():
            h = ln.split()[1]
            blob = subprocess.run(["git", "show", f"{h}:formal/ANSE/BAO_BBN_H0.lean"], cwd=WT, capture_output=True).stdout
            committed_shas.append({"commit": ln.split()[0], "file_sha256": hashlib.sha256(blob).hexdigest()})
    return {"current_source_sha256": cur_sha, "rows": rows, "committed_versions": committed_shas,
            "prefix_scratch_copy": str(scratch.relative_to(WT)) if scratch.exists() else None,
            "prefix_scratch_copy_sha256": sha(scratch) if scratch.exists() else None,
            "note": ("The scratch copy is the sorry negative-control file made from the pre-fix source; it is not "
                     "hash-linked to the audited bytes. The audited source (sha prefix c0663994) was never committed. "
                     "The ledger itself is outside this paper's write scope and was not modified.")}


def main() -> None:
    out = {"script": "results/cosmo_synthesis/round1_response_checks.py",
           "date": datetime.date.today().isoformat(),
           "h0_gate_propagation": h0_gate_propagation(),
           "dr1_dr2_conventions": dr1_dr2_conventions(),
           "overlap_sensitivity": overlap_sensitivity(),
           "n4_margin": n4_margin(),
           "camb_shifted_pull": camb_shifted_pull(),
           "dr2_mc_error": dr2_mc_error(),
           "aubourg_points": aubourg_points(),
           "controls_count": controls_count(),
           "rust_pr61": rust_pr61(),
           "h0_audit_binding": h0_audit_binding()}
    OUT.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=1)[:6000])


if __name__ == "__main__":
    main()
