"""Computations requested by the round-2 referees of cosmo_synthesis.tex.

Every number the round-2 revision adds that is not already in a run's result JSON or in
round1_response_checks.json is computed here and written to
results/cosmo_synthesis/round2_response_checks.json. Nothing outside results/cosmo_synthesis/
and a scratch directory under /tmp is written.

Sections
  g2_attribution       implied H0 shift of the G2 h r_d offset for each DR1 reference value
                       (Sec. 8: 101.8, Sec. 6: 101.9, and the +-0.05 rounding ends of 101.8), and
                       the MC error of the G2 chain mean propagated to H0
  t2_resolution        T2 margin vs the combined resolution including an estimate of DESI's own
                       posterior-mean MC error (DR1 Sec. 2.5: ESS >~ 1e3)
  aubourg_neff         Aubourg eq.16 vs CAMB at the validation points, CAMB re-run at
                       N_eff = 3.046 (the value Aubourg's 0.021% statement assumes), and the
                       eq.17 N_eff factor as an analytic proxy
  dr1_grid_step        grid spacing of the DR1 brute-force cross-check (fit_desi_bao.py)
  p2_om_moments        Omega_m pull moments of the H0 P2 noisy-mock control (report-only)
  dr2_zgtm1_lean       DR2 E2_pos / E_pos restated with hypothesis -1 < z, same tactic scripts,
                       kernel-checked in the pinned build (scratch copy under /tmp)
  mathlib_builds       number of Mathlib .olean files in the two Lean environments
  lake_root_imports    whether formal/ANSE.lean (worktree and main checkout) imports the four modules
Run: /mnt/disks/disk-socrateai-local-1/venv-cosmo/bin/python results/cosmo_synthesis/round2_response_checks.py
"""
from __future__ import annotations

import datetime
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

WT = Path(__file__).resolve().parents[2]
OUT = WT / "results/cosmo_synthesis/round2_response_checks.json"
SCRATCH = Path("/tmp/cosmo_synthesis_round2")
ENV1 = Path("/home/callensxavier_gmail_com/AutoevolveAI/formal")
ENV2 = Path("/home/callensxavier_gmail_com/SocrateAI-Scientific-Agora-LeanMaster")
WHITELIST = {"propext", "Classical.choice", "Quot.sound"}


def load(rel: str) -> Any:
    return json.loads((WT / rel).read_text())


def g2_attribution() -> dict[str, Any]:
    fit = load("results/bao_bbn_h0/fit.json")
    dg = load("results/bao_bbn_h0/fixround_diagnostics.json")["slope_and_T2_propagation"]
    pre = load("results/bao_bbn_h0/preregistration.json")
    h0t = next(t for t in pre["targets"] if t["id"] == "T2")["value"]
    slope = dg["primary_T2_DR1_dlnhrd_dlnh"]
    ch = fit["G2"]["chain"]
    mean = ch["mean"]["hrd"]
    mc_hrd = ch["std"]["hrd"] / math.sqrt(ch["ess"])
    refs = {"DR1_Sec8_101.8": 101.8, "DR1_Sec6_101.9": 101.9,
            "rounding_low_101.75": 101.75, "rounding_high_101.85": 101.85}
    rows = {}
    for k, ref in refs.items():
        off = mean - ref
        rows[k] = {"reference_hrd": ref, "offset_Mpc": off, "implied_H0_shift": h0t * (off / ref) / slope}
    mc_h0 = h0t * (mc_hrd / 101.8) / slope
    obs = fit["T2_boundary_resolution"]["primary"]["abs_dH0"]
    vals = [r["implied_H0_shift"] for r in rows.values()]
    return {"G2_chain_mean_hrd": mean, "G2_chain_std_hrd": ch["std"]["hrd"], "G2_chain_ess": ch["ess"],
            "G2_chain_n_steps": ch["n_steps"], "G2_mc_error_hrd_mean": mc_hrd,
            "G2_mc_error_propagated_to_H0": mc_h0, "slope_T2": slope, "H0_target_T2": h0t,
            "rows": rows, "implied_min": min(vals), "implied_max": max(vals), "observed_T2_abs_dH0": obs,
            "note": ("101.8 and 101.9 are the two DR1 LCDM h r_d values (arXiv:2404.03002 Sec. 8 and Sec. 6); the "
                     "+-0.05 ends bracket the rounding of 101.8. The implied shift therefore spans implied_min.."
                     "implied_max, plus the MC error; the agreement of one value with the observed shift is not "
                     "evidence for the mechanism.")}


def t2_resolution() -> dict[str, Any]:
    fit = load("results/bao_bbn_h0/fit.json")
    p = fit["T2_boundary_resolution"]["primary"]
    pre = load("results/bao_bbn_h0/preregistration.json")
    t2 = next(t for t in pre["targets"] if t["id"] == "T2")
    desi_sigma = t2["sigma"]
    ess_desi_min = 1000.0  # DR1 Sec. 2.5: ESS >~ 10^3 (rule constant, re-read via alphaXiv 2026-09-27)
    desi_mc = desi_sigma / math.sqrt(ess_desi_min)
    comb = math.sqrt(p["our_mc_error_H0"] ** 2 + desi_mc ** 2 + p["published_rounding_half_unit"] ** 2)
    return {"margin_over_strict": p["margin_over_strict"], "our_mc_error_H0": p["our_mc_error_H0"],
            "desi_sigma_H0": desi_sigma, "desi_ess_lower_bound": ess_desi_min,
            "desi_mc_error_estimate": desi_mc, "rounding": p["published_rounding_half_unit"],
            "combined_resolution_quadrature": comb, "margin_over_combined": p["margin_over_strict"] / comb,
            "note": ("DESI's MC error is estimated from its stated convergence floor ESS >~ 1e3, so it is an upper "
                     "estimate; DESI does not publish its MC error. fit.json already notes the boundary is not "
                     "statistically resolved.")}


def aubourg_neff() -> dict[str, Any]:
    sys.path.insert(0, str(WT / "scripts/bao_bbn_h0"))
    import camb  # noqa: PLC0415
    import common as cm  # noqa: PLC0415
    v = load("results/bao_bbn_h0/rd_camb_validation.json")["class_and_aubourg_vs_camb"]
    factor = 1.0 / (1.0 + (cm.NEFF - 3.046) / 30.60)  # eq.17: r_d proportional to 1/[1+(N_eff-3.046)/30.60]
    pts = []
    for x in v:
        p = camb.CAMBparams()
        p.set_cosmology(H0=100.0 * x["h"], ombh2=x["omega_b"], omch2=x["omega_cdm"], mnu=cm.MNU, nnu=3.046,
                        num_massive_neutrinos=1, TCMB=cm.T_CMB, omk=0.0)
        rd3046 = float(camb.get_background(p, no_thermo=False).get_derived_params()["rdrag"])
        pts.append({"omega_b": x["omega_b"], "omega_cdm": x["omega_cdm"], "h": x["h"],
                    "camb_neff3044": x["camb"], "camb_neff3046_rerun": rd3046, "aubourg16": x["aubourg16"],
                    "frac_vs_camb3044": x["frac_aub16_minus_camb"],
                    "frac_vs_camb3046": x["aubourg16"] / rd3046 - 1.0,
                    "camb3044_over_camb3046_minus_1": x["camb"] / rd3046 - 1.0,
                    "frac_eq17_proxy": x["aubourg16"] / (x["camb"] / factor) - 1.0})
    stated = 0.00021
    return {"camb_version": camb.__version__, "eq17_factor_rd3044_over_rd3046_minus_1": factor - 1.0,
            "points": pts, "stated_accuracy_frac": stated,
            "n_exceeding_vs_camb3044": sum(1 for q in pts if abs(q["frac_vs_camb3044"]) > stated),
            "n_exceeding_vs_camb3046": sum(1 for q in pts if abs(q["frac_vs_camb3046"]) > stated),
            "max_abs_frac_vs_camb3046": max(abs(q["frac_vs_camb3046"]) for q in pts),
            "note": "CAMB re-run with nnu=3.046 and otherwise the settings of rd_camb_table.camb_params."}


def dr1_grid_step() -> dict[str, Any]:
    src = (WT / "scripts/bao_flcdm/fit_desi_bao.py").read_text()
    m = re.search(r"om_range=\(([\d.]+),\s*([\d.]+)\),\s*rdh_range=\(([\d.]+),\s*([\d.]+)\),\s*n=(\d+)", src)
    if m is None:
        raise ValueError("grid signature not found in fit_desi_bao.py")
    o0, o1, r0, r1, n = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), int(m.group(5))
    d = load("results/bao_flcdm/desi_dr1_flcdm_fit.json")
    g = d["cross_check_grid_search"]
    return {"om_range": [o0, o1], "rdh_range": [r0, r1], "n": n, "step_Om": (o1 - o0) / (n - 1),
            "step_hrd": (r1 - r0) / (n - 1), "grid_Om": g["Om_m"], "grid_hrd": g["rd_h_Mpc"], "grid_chi2": g["chi2"],
            "source": "scripts/bao_flcdm/fit_desi_bao.py grid_search defaults"}


def p2_om_moments() -> dict[str, Any]:
    p = load("results/bao_bbn_h0/controls/P2_primary.json")
    n = p.get("n_mocks", p.get("n"))
    return {"pull_Om_mean": p["pull_Om_mean"], "pull_Om_std": p["pull_Om_std"], "n_mocks": n,
            "se_mean": (p["pull_Om_std"] / math.sqrt(n)) if n else None,
            "note": "report-only; the preregistered P2 rule covers H0 only"}


def _axioms(out: str) -> list[dict[str, Any]]:
    res = []
    for m in re.finditer(r"'([\w.]+)' (does not depend on any axioms|depends on axioms: \[([^\]]*)\])", out):
        axs = [a.strip() for a in (m.group(3) or "").replace("\n", " ").split(",") if a.strip()]
        res.append({"decl": m.group(1), "axioms": axs})
    return res


def dr2_zgtm1_lean() -> dict[str, Any]:
    src = (WT / "formal/ANSE/DESI_DR2_wCDM.lean").read_text()
    body_e2 = re.search(r"theorem E2_pos [\s\S]*?:= by\n((?:  [^\n]*\n)+)", src).group(1)
    body_e = re.search(r"theorem E_pos [\s\S]*?:= by\n((?:  [^\n]*\n)+)", src).group(1)
    body_e_new = body_e.replace("exact E2_pos hOm0 hOm1 hz", "exact E2_pos_zgtm1 hOm0 hOm1 hz")
    addition = (
        "\n\ntheorem E2_pos_zgtm1 {Om w z : ℝ} (hOm0 : 0 < Om) (hOm1 : Om < 1) (hz : -1 < z) :\n"
        "    0 < E2 Om w z := by\n" + body_e2 +
        "\ntheorem E_pos_zgtm1 {Om w z : ℝ} (hOm0 : 0 < Om) (hOm1 : Om < 1) (hz : -1 < z) :\n"
        "    0 < E Om w z := by\n" + body_e_new +
        "\n#print axioms ANSE.DESIDR2wCDM.E2_pos_zgtm1\n#print axioms ANSE.DESIDR2wCDM.E_pos_zgtm1\n")
    marker = "end ANSE.DESIDR2wCDM"
    if marker not in src:
        raise ValueError("namespace end not found")
    new = src.replace(marker, addition + "\n" + marker)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    f = SCRATCH / "DESI_DR2_wCDM_zgtm1.lean"
    f.write_text(new)
    p = subprocess.run(["timeout", "1800", "lake", "env", "lean", str(f)], cwd=ENV1, capture_output=True, text=True)
    out = p.stdout + p.stderr
    axs = [a for a in _axioms(out) if a["decl"].endswith("_zgtm1")]
    kept = WT / "results/cosmo_synthesis/dr2_zgtm1_check.lean"  # committed copy of the exact bytes checked
    kept.write_bytes(f.read_bytes())
    return {"scratch_file": str(f), "kept_copy": str(kept.relative_to(WT)),
            "kept_copy_sha256": hashlib.sha256(kept.read_bytes()).hexdigest(),
            "shipped_file_sha256": hashlib.sha256((WT / "formal/ANSE/DESI_DR2_wCDM.lean").read_bytes()).hexdigest(),
            "command": f"cd {ENV1} && timeout 1800 lake env lean {f}",
            "output_tail": out[-1200:], "cwd": str(ENV1), "rc": p.returncode,
            "tactic_E2_identical": body_e2 in new,
            "tactic_E_changed_only_lemma_name": body_e_new != body_e
            and body_e_new.replace("E2_pos_zgtm1", "E2_pos") == body_e,
            "zgtm1_axioms": axs,
            "whitelist_only": bool(axs) and all(set(a["axioms"]) <= WHITELIST for a in axs) and len(axs) == 2,
            "sorry_warning": "declaration uses 'sorry'" in out, "errors": [ln for ln in out.splitlines() if "error" in ln][:10]}


def mathlib_builds() -> dict[str, Any]:
    out = {}
    for name, root in (("env1_pinned", ENV1), ("env2_leanmaster", ENV2)):
        lib = root / ".lake/packages/mathlib/.lake/build/lib/lean/Mathlib"
        src = root / ".lake/packages/mathlib/Mathlib"
        out[name] = {"olean_dir": str(lib), "n_olean": sum(1 for _ in lib.rglob("*.olean")) if lib.exists() else None,
                     "n_lean_sources": sum(1 for _ in src.rglob("*.lean")) if src.exists() else None}
    return out


def lake_root_imports() -> dict[str, Any]:
    mods = ["ANSE.BAO_FlatLCDM", "ANSE.DESI_DR2_wCDM", "ANSE.BAO_BBN_H0", "ANSE.BAO_Consistency"]
    res = {}
    for name, p in (("worktree", WT / "formal/ANSE.lean"), ("main_checkout", ENV1 / "ANSE.lean")):
        lines = [ln.strip() for ln in p.read_text().splitlines()]
        res[name] = {m: sum(1 for ln in lines if ln == f"import {m}") for m in mods}
    res["note"] = "No `lake build` of formal/ANSE.lean including the three new modules is recorded in any artifact."
    return res


def main() -> None:
    out = {"script": "results/cosmo_synthesis/round2_response_checks.py",
           "date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "g2_attribution": g2_attribution(), "t2_resolution": t2_resolution(),
           "aubourg_neff": aubourg_neff(), "dr1_grid_step": dr1_grid_step(),
           "p2_om_moments": p2_om_moments(), "dr2_zgtm1_lean": dr2_zgtm1_lean(),
           "mathlib_builds": mathlib_builds(), "lake_root_imports": lake_root_imports()}
    OUT.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=1)[:7000])


if __name__ == "__main__":
    main()
