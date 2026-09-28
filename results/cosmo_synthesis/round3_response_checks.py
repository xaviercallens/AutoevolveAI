"""Round-3 response checks for papers/cosmo_synthesis/cosmo_synthesis.tex.

Writes results/cosmo_synthesis/round3_response_checks.json with:
  env_versions        Python / numpy / scipy / emcee / camb versions of the two interpreters on this machine
  h0_env_rerun        the frozen scripts/bao_bbn_h0/fit_real.py re-run under both interpreters (isolated copies
                      built by round3_env_rerun_setup.py; only the chain directory patched), compared with the
                      committed results/bao_bbn_h0/fit.json: chain means, |dH0|, verdicts, MAPs, gate h r_d,
                      number of differing numeric leaves, bit-identity
  formula_shift       exact-CAMB minus fitting-formula H0: MAP differences (deterministic) and posterior-mean
                      differences with their Monte Carlo errors
  aubourg_omega_cb    Aubourg eq.16 evaluated at omega_cb = omega_b + omega_cdm of the CAMB grid point (instead of
                      rd_camb_table.py's omega_b + omega_cdm + omega_nu_CAMB - omega_nu_Aubourg), against the
                      N_eff = 3.046 CAMB values of round2_response_checks.json
  overlap_x_only      the rho = 0.57 overlap statistic with X subtracted once (the wording the paper used) versus
                      X + X^T (what round1_response_checks.py computes)
  strict_window       the preregistered strict-window construction and the post-hoc re-budget terms
  dr1_interpreter     scripts/bao_flcdm/fit_desi_bao.py re-run under venv-cosmo (isolated copy) vs the committed
                      JSON, and whether venv-pta can import datetime.UTC
Run: /mnt/disks/disk-socrateai-local-1/venv-cosmo/bin/python results/cosmo_synthesis/round3_response_checks.py
(after running fit_real.py in /tmp/r3resp/{cosmo,pta}; see round3_env_rerun_setup.py)
"""
from __future__ import annotations

import datetime
import hashlib
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.linalg import sqrtm
from scipy.stats import chi2 as chi2dist
from scipy.stats import norm

WT = Path(__file__).resolve().parents[2]
OUT = WT / "results/cosmo_synthesis/round3_response_checks.json"
BASE = Path("/tmp/r3resp")
PY = {"cosmo": "/mnt/disks/disk-socrateai-local-1/venv-cosmo/bin/python",
      "pta": "/mnt/disks/disk-socrateai-local-1/venv-pta/bin/python"}
STRICT = 0.15


def load(rel: str) -> Any:
    return json.loads((WT / rel).read_text())


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def env_versions() -> dict[str, Any]:
    code = ("import sys, json\nout={'python': sys.version.split()[0]}\n"
            "for m in ('numpy','scipy','emcee','camb'):\n"
            "    try:\n        mod=__import__(m); out[m]=mod.__version__\n"
            "    except Exception as e:\n        out[m]='unavailable: '+type(e).__name__\n"
            "try:\n    from datetime import UTC\n    out['datetime_UTC_importable']=True\n"
            "except ImportError:\n    out['datetime_UTC_importable']=False\n"
            "print(json.dumps(out))")
    res = {}
    for k, py in PY.items():
        r = subprocess.run([py, "-c", code], capture_output=True, text=True, check=True)
        res[k] = {"interpreter": py, **json.loads(r.stdout)}
    return res


def leaves(obj: Any, prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(leaves(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(leaves(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = obj
    return out


def summarize(fit: dict[str, Any]) -> dict[str, Any]:
    s: dict[str, Any] = {}
    for an in ("primary", "secondary"):
        for t, v in (("T1_DR2", "verdict_T1"), ("T2_DR1", "verdict_T2")):
            ch = fit[an][t]["chain"]
            s[f"{an}.{t}"] = {"H0_mean": ch["mean"]["H0"], "H0_std": ch["std"]["H0"], "ess": ch["ess"],
                              "mc_error_H0": ch["std"]["H0"] / math.sqrt(ch["ess"]),
                              "H0_map": fit[an][t]["map"]["H0"],
                              "abs_dH0": fit[an][v]["abs_dH0"], "verdict": fit[an][v]["verdict"]}
    for g in ("G1", "G2"):
        s[g] = {"hrd_mean": fit[g]["chain"]["mean"]["hrd"], "passed": fit[g].get("passed")}
    return s


def h0_env_rerun() -> dict[str, Any]:
    committed = load("results/bao_bbn_h0/fit.json")
    cl = leaves(committed)
    out: dict[str, Any] = {"committed": summarize(committed)}
    for env in ("cosmo", "pta"):
        p = BASE / env / "results/bao_bbn_h0/fit.json"
        f = json.loads(p.read_text())
        fl = leaves(f)
        skip = ("runtime_s", "secondary_vs_locked_preamendment.path", "script")
        numeric = [k for k in cl if k in fl and isinstance(cl[k], float) and not k.startswith(skip)]
        diff = [k for k in numeric if cl[k] != fl[k]]
        other = [k for k in cl if k in fl and not isinstance(cl[k], float) and cl[k] != fl[k]
                 and not k.startswith(skip)]
        out[env] = {"fit_json": str(p), "fit_json_sha256": sha(p), "summary": summarize(f),
                    "n_numeric_leaves_compared": len(numeric), "n_numeric_leaves_differing": len(diff),
                    "max_abs_leaf_difference": max((abs(cl[k] - fl[k]) for k in diff), default=0.0),
                    "non_numeric_leaves_differing": other,
                    "bit_identical_numeric": len(diff) == 0,
                    "secondary_vs_locked_T2_H0_diff": f["secondary_vs_locked_preamendment"]["T2_DR1"]["H0"]["diff"],
                    "secondary_vs_locked_T1_H0_diff": f["secondary_vs_locked_preamendment"]["T1_DR2"]["H0"]["diff"],
                    "runtime_s": f.get("runtime_s")}
    c = out["committed"]["primary.T2_DR1"]
    r = out["cosmo"]["summary"]["primary.T2_DR1"]
    out["primary_T2_shift_cosmo_minus_committed"] = r["H0_mean"] - c["H0_mean"]
    out["primary_T2_shift_in_committed_mc_errors"] = (r["H0_mean"] - c["H0_mean"]) / c["mc_error_H0"]
    out["note"] = ("Same scripts, same seeds, same inputs; only the interpreter differs. The chain output directory of "
                   "fit_real.py was redirected to /tmp so the recorded chains on disk 2 are untouched.")
    return out


def formula_shift(fit: dict[str, Any]) -> dict[str, Any]:
    res = {}
    for t in ("T1_DR2", "T2_DR1"):
        p, s = fit["primary"][t], fit["secondary"][t]
        mc = math.hypot(p["chain"]["std"]["H0"] / math.sqrt(p["chain"]["ess"]),
                        s["chain"]["std"]["H0"] / math.sqrt(s["chain"]["ess"]))
        res[t] = {"map_diff": p["map"]["H0"] - s["map"]["H0"],
                  "mean_diff": p["chain"]["mean"]["H0"] - s["chain"]["mean"]["H0"],
                  "mean_diff_mc_error": mc}
    return res


def aubourg_omega_cb() -> dict[str, Any]:
    sys.path.insert(0, str(WT / "scripts/bao_bbn_h0"))
    import common as cm  # noqa: PLC0415
    r2 = load("results/cosmo_synthesis/round2_response_checks.json")["aubourg_neff"]["points"]
    z = np.load(WT / "results/bao_bbn_h0/rd_camb_table.npz")
    omnu_camb = float(z["omega_nu_camb"])
    pts = []
    for q in r2:
        wb, wc = q["omega_b"], q["omega_cdm"]
        ra_matched = float(cm.rd_aubourg16(wb + wc, wb))
        ra_stored = float(cm.rd_aubourg16(wb + wc + omnu_camb - cm.OMEGA_NU_AUBOURG, wb))
        pts.append({"omega_b": wb, "omega_cdm": wc, "aubourg_stored_recomputed": ra_stored,
                    "aubourg_stored_json": q["aubourg16"], "aubourg_omega_cb_matched": ra_matched,
                    "frac_matched_vs_camb3046": ra_matched / q["camb_neff3046_rerun"] - 1.0,
                    "frac_stored_vs_camb3046": q["frac_vs_camb3046"]})
    worst = max(pts, key=lambda x: abs(x["frac_stored_vs_camb3046"]))
    return {"omega_nu_camb": omnu_camb, "omega_nu_aubourg": cm.OMEGA_NU_AUBOURG,
            "omega_cb_offset_in_stored": omnu_camb - cm.OMEGA_NU_AUBOURG, "points": pts,
            "n_exceeding_matched_vs_camb3046": sum(1 for x in pts if abs(x["frac_matched_vs_camb3046"]) > 0.00021),
            "max_abs_frac_matched_vs_camb3046": max(abs(x["frac_matched_vs_camb3046"]) for x in pts),
            "worst_point_stored": worst,
            "note": ("rd_camb_table.py compares at equal Omega_m h^2 (the fit's sampled quantity), which puts the formula "
                     "at omega_cb = omega_b + omega_cdm + (omega_nu_CAMB - omega_nu_Aubourg); Aubourg's accuracy statement "
                     "is at given omega_cb, i.e. omega_b + omega_cdm.")}


def overlap_x_only() -> dict[str, Any]:
    f = load("results/eboss_vs_desi/fit.json")
    S = f["fits"]["SDSS_eBOSS_DR16_baseline"]["emcee"]
    D = f["fits"]["DESI_DR2"]["emcee"]

    def cov(e: dict[str, Any]) -> np.ndarray:
        a, b, r = e["std_Om"], e["std_hrd"], e["corr"]
        return np.array([[a * a, r * a * b], [r * a * b, b * b]])

    cs, cd = cov(S), cov(D)
    dv = np.array([S["mean_Om"] - D["mean_Om"], S["mean_hrd"] - D["mean_hrd"]])
    x = 0.57 * np.real(sqrtm(cs)) @ np.real(sqrtm(cd))
    res = {}
    for name, c in (("X_plus_XT", cs + cd - x - x.T), ("X_only", cs + cd - x)):
        ch = float(dv @ np.linalg.solve(c, dv))  # X_only: literal (non-symmetric) matrix, as the wording implies
        pte = float(chi2dist.sf(ch, 2))
        res[name] = {"chi2": ch, "PTE": pte, "N_sigma": float(norm.isf(pte / 2))}
    return res


def strict_window() -> dict[str, Any]:
    p = load("results/bao_bbn_h0/preregistration.json")["tolerance"]
    d = load("results/bao_bbn_h0/fixround_diagnostics.json")["tolerance_rebudget"]
    return {"strict_definition": p["strict_definition"], "soft_definition": p["soft_definition"],
            "formula_term": 0.139, "mc_term": d["sigma_mc_from_preregistration"],
            "strict_recomputed": math.hypot(0.139, d["sigma_mc_from_preregistration"]),
            "rebudget_terms": {"mc": d["sigma_mc_from_preregistration"], "interp": d["interp_term_km_s_Mpc"]},
            "rebudget": d["rebudget_strict_km_s_Mpc"],
            "rebudget_recomputed": math.hypot(d["sigma_mc_from_preregistration"], d["interp_term_km_s_Mpc"])}


def dr1_interpreter() -> dict[str, Any]:
    root = BASE / "dr1"
    if root.exists():
        shutil.rmtree(root)
    (root / "results/bao_flcdm").mkdir(parents=True)
    shutil.copy2(WT / "scripts/bao_flcdm/fit_desi_bao.py", root / "fit_desi_bao.py")
    r = subprocess.run([PY["cosmo"], str(root / "fit_desi_bao.py")], cwd=root, capture_output=True, text=True)
    new = json.loads((root / "results/bao_flcdm/desi_dr1_flcdm_fit.json").read_text()) if r.returncode == 0 else {}
    old = load("results/bao_flcdm/desi_dr1_flcdm_fit.json")
    ol, nl = leaves(old), leaves(new)
    diff = [k for k in ol if k in nl and ol[k] != nl[k]]
    rp = subprocess.run([PY["pta"], str(root / "fit_desi_bao.py")], cwd=root, capture_output=True, text=True)
    last = (rp.stderr.strip().splitlines() or [""])[-1]
    return {"venv_cosmo_rc": r.returncode, "venv_cosmo_differing_leaves": diff,
            "venv_pta_rc": rp.returncode, "venv_pta_last_stderr_line": last,
            "docstring_names_venv_pta": "venv-pta" in (WT / "scripts/bao_flcdm/fit_desi_bao.py").read_text()}


def formula_prediction(fit: dict[str, Any]) -> dict[str, Any]:
    """Predicted primary-minus-secondary H0 from a fractional r_d error eps (formula minus CAMB): at fixed h r_d,
    Delta ln h = -eps / (d ln(h r_d)/d ln h), so primary - secondary = H0 * eps / slope (secondary sits higher when eps < 0)."""
    sl = load("results/bao_bbn_h0/fixround_diagnostics.json")["slope_and_T2_propagation"]
    fr = fit["measured_formula_systematic"]["aub16_minus_camb_frac_at_5_points"]
    v = load("results/bao_bbn_h0/rd_camb_validation.json")["class_and_aubourg_vs_camb"]
    out = {"validation_point_0": {k: v[0][k] for k in ("omega_b", "omega_cdm", "h")}, "eps_point_0": fr[0],
           "eps_stated_aubourg": -0.00021}
    for t, key in (("T1_DR2", "primary_T1_DR2_dlnhrd_dlnh"), ("T2_DR1", "primary_T2_DR1_dlnhrd_dlnh")):
        h0 = fit["primary"][t]["map"]["H0"]
        out[t] = {"slope": sl[key], "pred_from_point_0": h0 * fr[0] / sl[key],
                  "pred_from_stated_0.021pct": h0 * (-0.00021) / sl[key],
                  "map_diff": fit["primary"][t]["map"]["H0"] - fit["secondary"][t]["map"]["H0"]}
    return out


def g2_implied_cosmo(rer: dict[str, Any]) -> dict[str, Any]:
    dg = load("results/bao_bbn_h0/fixround_diagnostics.json")["slope_and_T2_propagation"]
    row = dg["T2_propagation"][0]
    h0t = next(t for t in load("results/bao_bbn_h0/preregistration.json")["targets"] if t["id"] == "T2")["value"]
    g2 = rer["cosmo"]["summary"]["G2"]["hrd_mean"]
    frac = (g2 - row["desi_hrd_quoted"]) / row["desi_hrd_quoted"]
    rec = (row["our_G2_hrd"] - row["desi_hrd_quoted"]) / row["desi_hrd_quoted"] / row["slope"] * h0t
    return {"G2_hrd_cosmo": g2, "offset_Mpc": g2 - row["desi_hrd_quoted"],
            "implied_H0_shift": frac / row["slope"] * h0t, "recorded_formula_check": rec,
            "recorded_matches_round2_g2_attribution": abs(rec - load("results/cosmo_synthesis/round2_response_checks.json")["g2_attribution"]["rows"]["DR1_Sec8_101.8"]["implied_H0_shift"]) < 1e-9,
            "note": "same formula as round2_response_checks.g2_attribution (H0 target times fractional offset over slope)"}


def map_agreement(rer: dict[str, Any]) -> float:
    c, r = rer["committed"], rer["cosmo"]["summary"]
    return max(abs(c[k]["H0_map"] - r[k]["H0_map"]) for k in c if "." in k)


def main() -> None:
    fit = load("results/bao_bbn_h0/fit.json")
    rer = h0_env_rerun()
    rer["max_abs_map_H0_diff_cosmo"] = map_agreement(rer)
    rer["g2_implied_cosmo"] = g2_implied_cosmo(rer)
    rer["formula_prediction"] = formula_prediction(fit)
    out = {"generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "script": "results/cosmo_synthesis/round3_response_checks.py",
           "env_versions": env_versions(),
           "h0_env_rerun": rer,
           "formula_shift": {"committed": formula_shift(fit),
                             "venv_cosmo_rerun": formula_shift(json.loads(Path(rer["cosmo"]["fit_json"]).read_text()))},
           "aubourg_omega_cb": aubourg_omega_cb(),
           "overlap_x_only": overlap_x_only(),
           "strict_window": strict_window(),
           "dr1_interpreter": dr1_interpreter()}
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("env_versions", "formula_shift", "overlap_x_only", "strict_window")}, indent=1))
    for env in ("cosmo", "pta"):
        e = rer[env]
        print(env, e["n_numeric_leaves_differing"], "/", e["n_numeric_leaves_compared"], "differ;",
              {k: (round(v["H0_mean"], 4), round(v["abs_dH0"], 4), v["verdict"]) for k, v in e["summary"].items() if "." in k})
    print("aubourg", out["aubourg_omega_cb"]["max_abs_frac_matched_vs_camb3046"], out["aubourg_omega_cb"]["n_exceeding_matched_vs_camb3046"])
    print("dr1", out["dr1_interpreter"])


if __name__ == "__main__":
    main()
