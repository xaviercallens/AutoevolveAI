"""Generate every number used in cosmo_synthesis.tex from the result JSONs.

Writes, next to this script:
  gen_numbers.tex        \\newcommand macros, one per number
  gen_tab_*.tex          tables assembled from those macros
  gen_lean_appendix.tex  Lean statements, extracted verbatim from the committed files
  number_manifest.json   macro -> (file, key, value) for provenance checking

No number is typed here except rule constants that the preregistrations define
(they are read from the preregistration JSONs where a JSON field exists).

Run: /mnt/disks/disk-socrateai-local-1/venv-cosmo/bin/python gen_numbers.py
"""

from __future__ import annotations

import hashlib
import json
import re
import statistics
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RES = ROOT / "results"
FORMAL = ROOT / "formal" / "ANSE"

MACROS: dict[str, str] = {}
MANIFEST: list[dict[str, Any]] = []


def load(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text())


def dig(obj: Any, key: str) -> Any:
    """Follow a dotted key; a segment that is not found is joined with the next
    one, so JSON keys that themselves contain dots (e.g. 'mnu0.06') resolve."""
    cur = obj
    parts = key.split(".")
    i = 0
    while i < len(parts):
        seg = parts[i]
        while True:
            m = re.fullmatch(r"(.+?)\[(\d+)\]", seg)
            base = m.group(1) if m else seg
            if isinstance(cur, dict) and base in cur:
                cur = cur[base][int(m.group(2))] if m else cur[base]
                break
            i += 1
            if i >= len(parts):
                raise KeyError(key)
            seg = seg + "." + parts[i]
        i += 1
    return cur


def macro_name(name: str) -> str:
    if not re.fullmatch(r"[A-Za-z]+", name):
        raise ValueError(f"bad macro name {name}")
    return name


def put(name: str, text: str, src: str, key: str, value: Any) -> str:
    name = macro_name(name)
    if name in MACROS:
        raise ValueError(f"duplicate macro {name}")
    MACROS[name] = text
    MANIFEST.append({"macro": "\\" + name, "tex": text, "file": src, "key": key, "value": value})
    return "\\" + name


def fmt(x: float, nd: int) -> str:
    s = f"{x:.{nd}f}"
    if s.startswith("-") and float(s) == 0.0:
        s = s[1:]
    return s


def sci(x: float, nd: int = 1) -> str:
    mant, exp = f"{x:.{nd}e}".split("e")
    return f"{mant}\\times10^{{{int(exp)}}}"


def num(name: str, src: str, key: str, nd: int, obj: Any | None = None, scale: float = 1.0) -> str:
    data = load(src) if obj is None else obj
    val = float(dig(data, key)) * scale
    return put(name, fmt(val, nd), src, key, val)


def val(src: str, key: str) -> Any:
    return dig(load(src), key)


def derived(name: str, value: float, nd: int, src: str, how: str) -> str:
    return put(name, fmt(value, nd), src, how, value)


def text_macro(name: str, text: str, src: str, key: str) -> str:
    return put(name, text, src, key, text)


def tex_escape(s: str) -> str:
    rep = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
           "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    out = "".join(rep.get(ch, ch) for ch in s)
    out = out.replace("±", r"$\pm$").replace("θ", r"$\theta$").replace("σ", r"$\sigma$").replace("—", "--")
    return out


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


# --------------------------------------------------------------------------- DR1
def dr1() -> None:
    src = "results/bao_flcdm/desi_dr1_flcdm_fit.json"
    d = load(src)
    num("dOneOm", src, "fit_manual_quad.Om_m", 4)
    num("dOneHrd", src, "fit_manual_quad.rd_h_Mpc", 2)
    num("dOneChi", src, "fit_manual_quad.chi2", 2)
    num("dOneDof", src, "fit_manual_quad.dof", 0)
    num("dOneGridOm", src, "cross_check_grid_search.Om_m", 4)
    num("dOneGridHrd", src, "cross_check_grid_search.rd_h_Mpc", 2)
    num("dOneTOm", src, "external_validation_target.Om_m[0]", 3)
    num("dOneTOmS", src, "external_validation_target.Om_m[1]", 3)
    num("dOneTHrd", src, "external_validation_target.rd_h_Mpc[0]", 1)
    num("dOneTHrdS", src, "external_validation_target.rd_h_Mpc[1]", 1)
    om, t, s = d["fit_manual_quad"]["Om_m"], d["external_validation_target"]["Om_m"][0], d["external_validation_target"]["Om_m"][1]
    derived("dOnePullOm", (om - t) / s, 3, src, "(fit_manual_quad.Om_m - external_validation_target.Om_m[0]) / Om_m[1]")
    h, th, sh = d["fit_manual_quad"]["rd_h_Mpc"], d["external_validation_target"]["rd_h_Mpc"][0], d["external_validation_target"]["rd_h_Mpc"][1]
    derived("dOnePullHrd", (h - th) / sh, 3, src, "(fit_manual_quad.rd_h_Mpc - target) / sigma")
    num("dOneAbsPullOm", src, "deviation_from_published_result.Om_m_sigma", 3)
    num("dOneAbsPullHrd", src, "deviation_from_published_result.rd_h_sigma", 3)
    text_macro("dOneSource", tex_escape(d["external_validation_target"]["source"]), src, "external_validation_target.source")
    n = d["data_provenance"]["n_data_points"]
    put("dOneNdata", str(n), src, "data_provenance.n_data_points", n)
    rows = [
        ("$\\Omega_m$", "\\dOneOm", "--", "\\dOneTOm", "\\dOneTOmS", "\\dOnePullOm"),
        ("$h r_d$ [Mpc]", "\\dOneHrd", "--", "\\dOneTHrd", "\\dOneTHrdS", "\\dOnePullHrd"),
    ]
    lines = [r"\begin{tabular}{lccccc}", r"\toprule",
             r"Quantity & Ours ($\chi^2$-min) & $\sigma$ & Target & $\sigma_{\rm target}$ & Pull \\", r"\midrule"]
    for r in rows:
        lines.append(" & ".join(f"${c}$" if c.startswith("\\") else c for c in r) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (HERE / "gen_tab_dr1.tex").write_text("\n".join(lines) + "\n")


# --------------------------------------------------------------------------- DR2
def dr2() -> None:
    src = "results/desi_dr2_bao/fit.json"
    d = load(src)
    names = {"DR2_LCDM_Om": "LOm", "DR2_LCDM_hrd_Mpc": "LHrd", "DR2_wCDM_Om": "WOm", "DR2_wCDM_w": "Ww"}
    label = {"DR2_LCDM_Om": r"$\Lambda$CDM $\Omega_m$", "DR2_LCDM_hrd_Mpc": r"$\Lambda$CDM $h r_d$ [Mpc]",
             "DR2_wCDM_Om": r"$w$CDM $\Omega_m$", "DR2_wCDM_w": r"$w$CDM $w$"}
    nd = {"DR2_LCDM_Om": 5, "DR2_LCDM_hrd_Mpc": 3, "DR2_wCDM_Om": 5, "DR2_wCDM_w": 4}
    ndt = {"DR2_LCDM_Om": 4, "DR2_LCDM_hrd_Mpc": 2, "DR2_wCDM_Om": 4, "DR2_wCDM_w": 3}
    lines = [r"\begin{tabular}{lcccccp{4.2cm}}", r"\toprule",
             r"Quantity & Ours & $\sigma$ & Target & $\sigma_{\rm t}$ & Pull & Source \\", r"\midrule"]
    for i, r in enumerate(d["results"]):
        tag = names[r["name"]]
        k = f"results[{i}]"
        a = num(f"dTwo{tag}", src, f"{k}.value", nd[r["name"]])
        b = num(f"dTwo{tag}S", src, f"{k}.sigma", ndt[r["name"]] + 1)
        c = num(f"dTwo{tag}T", src, f"{k}.target", ndt[r["name"]])
        e = num(f"dTwo{tag}TS", src, f"{k}.target_sigma", ndt[r["name"]])
        p = num(f"dTwo{tag}P", src, f"{k}.pull_sigma", 3)
        num(f"dTwo{tag}W", src, f"{k}.width_ratio", 3)
        num(f"dTwo{tag}G", src, f"{k}.grid_value", nd[r["name"]])
        lines.append(f"{label[r['name']]} & ${a}$ & ${b}$ & ${c}$ & ${e}$ & ${p}$ & \\scriptsize {tex_escape(r['source'])} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (HERE / "gen_tab_dr2.tex").write_text("\n".join(lines) + "\n")
    mx = max(abs(r["pull_sigma"]) for r in d["results"])
    put("dTwoMaxAbsPull", fmt(mx, 3), src, "max |results[*].pull_sigma|", mx)
    num("dTwoWHrd", src, "DR2_wCDM_hrd_report_only.mean", 2)
    num("dTwoWHrdS", src, "DR2_wCDM_hrd_report_only.std", 2)
    num("dTwoCorr", src, "DR2_LCDM_corr_Om_hrd.emcee", 3)
    num("dTwoCorrT", src, "DR2_LCDM_corr_Om_hrd.target", 2)
    num("dTwoChi", src, "DR2_LCDM_bestfit.chi2", 2)
    num("dTwoDof", src, "DR2_LCDM_bestfit.dof", 0)
    num("dTwoBestOm", src, "DR2_LCDM_bestfit.params.Om", 5)
    num("dTwoBestHrd", src, "DR2_LCDM_bestfit.params.h_rd", 3)
    num("dTwoFishOmS", src, "fisher_at_min.DR2_LCDM.sigma.Om", 5)
    num("dTwoFishHrdS", src, "fisher_at_min.DR2_LCDM.sigma.h_rd", 3)
    num("dTwoEmceeGrid", src, "emcee_vs_grid_max_abs_diff_in_emcee_sigma", 3)
    crit = d["criteria"]
    put("dTwoCritPass", str(sum(bool(v) for v in crit.values())), src, "criteria (count true)", sum(bool(v) for v in crit.values()))
    put("dTwoCritN", str(len(crit)), src, "criteria (count)", len(crit))
    num("dTwoNsteps", src, "mcmc_diagnostics.DR2_LCDM.n_steps", 0)
    # DR1 instrument checks inside the DR2 run
    num("dTwoIOm", src, "DR1_instrument_checks.DR1_LCDM_Om.ours", 5)
    num("dTwoIOmP", src, "DR1_instrument_checks.DR1_LCDM_Om.pull", 3)
    num("dTwoIHrd", src, "DR1_instrument_checks.DR1_LCDM_hrd.ours", 2)
    num("dTwoIHrdP", src, "DR1_instrument_checks.DR1_LCDM_hrd.pull", 3)
    # DR1 -> DR2 shift
    s = "DR1_to_DR2_shift"
    num("shOmOne", src, f"{s}.Om_DR1", 5)
    num("shOmTwo", src, f"{s}.Om_DR2", 5)
    num("shDelta", src, f"{s}.Delta_Om", 5)
    num("shPub", src, f"{s}.published_derived_Delta_Om", 4)
    num("shSigNestOwn", src, f"{s}.sigma_nested_own", 5)
    num("shSigNestPre", src, f"{s}.sigma_nested_prereg", 5)
    num("shSigInd", src, f"{s}.sigma_independent_own", 5)
    num("shRatioOwn", src, f"{s}.Delta_over_sigma_nested_own", 3)
    num("shRatioPre", src, f"{s}.Delta_over_sigma_nested_prereg", 3)
    num("shRatioInd", src, f"{s}.Delta_over_sigma_independent_own", 3)
    num("shDhrd", src, f"{s}.Delta_hrd", 3)
    # radiation / neutrino
    num("dTwoRadOm", src, "radiation_sensitivity.DR2_LCDM.shift_Om_in_published_sigma", 3)
    num("dTwoRadHrd", src, "radiation_sensitivity.DR2_LCDM.shift_h_rd_in_published_sigma", 3)
    num("dTwoCambOm", src, "camb_crosscheck.primary_model_vs_camb_mnu0.06_shift_in_published_sigma.lcdm.Om", 3)
    num("dTwoCambHrd", src, "camb_crosscheck.primary_model_vs_camb_mnu0.06_shift_in_published_sigma.lcdm.h_rd", 3)
    v = d["camb_crosscheck"]["massless_nu_max_rel_diff"]["w=-1.0"]
    put("dTwoCambMassless", sci(v), src, "camb_crosscheck.massless_nu_max_rel_diff.w=-1.0", v)
    # controls
    csrc = "results/desi_dr2_bao/controls.json"
    c = load(csrc)
    pcs = c["positive_controls"]
    ncs = c["negative_controls"]
    pc_ids = sorted({re.match(r"(PC\d+)", k).group(1) for k in pcs if re.match(r"PC\d+", k)})
    put("dTwoNPC", str(len(pc_ids)), csrc, "positive_controls (distinct PC<n> ids; PC0 has quad and GL entries)", len(pc_ids))
    put("dTwoNPCkeys", str(len(pcs)), csrc, "positive_controls (JSON key count)", len(pcs))
    put("dTwoNNC", str(len(ncs)), csrc, "negative_controls (count)", len(ncs))
    num("dTwoPCpullStdOm", csrc, "positive_controls.PC3_noisy_LCDM_draws.std_pull.Om", 3)
    num("dTwoPCpullMeanOm", csrc, "positive_controls.PC3_noisy_LCDM_draws.mean_pull.Om", 3)
    put("dTwoPCn", str(pcs["PC3_noisy_LCDM_draws"]["n"]), csrc, "positive_controls.PC3_noisy_LCDM_draws.n", pcs["PC3_noisy_LCDM_draws"]["n"])
    ncs5 = ncs["NC5_scrambled_covariance"]
    put("dTwoNCfiveMed", sci(ncs5["median_pte"]), csrc, "negative_controls.NC5_scrambled_covariance.median_pte", ncs5["median_pte"])
    ptes = [r["pte"] for r in ncs5["runs"]]
    nbad = sum(p > 1e-3 for p in ptes)
    put("dTwoNCfiveBad", str(nbad), csrc, "NC5 runs with pte > 1e-3 (count)", nbad)
    put("dTwoNCfiveN", str(len(ptes)), csrc, "NC5 runs (count)", len(ptes))
    if abs(statistics.median(ptes) - ncs5["median_pte"]) > 1e-12:
        raise ValueError("NC5 median mismatch")
    num("dTwoNCthreeChi", csrc, "negative_controls.NC3_wrong_model_EdS.chi2", 1)
    # referee
    rsrc = "results/desi_dr2_bao/referee_report.json"
    r = load(rsrc)
    put("dTwoRefN", str(len(r["issues"])), rsrc, "issues (count)", len(r["issues"]))
    text_macro("dTwoRefVerdict", r["verdict"], rsrc, "verdict")
    fsrc = "results/desi_dr2_bao/fixround_rerun_check.json"
    text_macro("dTwoRerunIdentical", "yes" if load(fsrc)["all_identical"] else "no", fsrc, "all_identical")


# --------------------------------------------------------------------------- H0
def h0() -> None:
    src = "results/bao_bbn_h0/fit.json"
    pre = "results/bao_bbn_h0/preregistration.json"
    d = load(src)
    p = load(pre)
    for an, tag in (("primary", "P"), ("secondary", "S")):
        for t, tt in (("verdict_T1", "One"), ("verdict_T2", "Two")):
            k = f"{an}.{t}"
            num(f"hz{tag}{tt}", src, f"{k}.H0", 3)
            num(f"hz{tag}{tt}S", src, f"{k}.sigma_H0", 3)
            num(f"hz{tag}{tt}Om", src, f"{k}.Omega_m", 4)
            num(f"hz{tag}{tt}OmS", src, f"{k}.sigma_Om", 4)
            num(f"hz{tag}{tt}D", src, f"{k}.abs_dH0", 3)
            num(f"hz{tag}{tt}P", src, f"{k}.pull_H0", 3)
            num(f"hz{tag}{tt}OmP", src, f"{k}.pull_Om", 3)
            num(f"hz{tag}{tt}R", src, f"{k}.sigma_ratio", 3)
            text_macro(f"hz{tag}{tt}V", dig(d, f"{k}.verdict"), src, f"{k}.verdict")
    tg = {t["id"]: (i, t) for i, t in enumerate(p["targets"])}
    for tid, tag, nd in (("T1", "TOne", 2), ("T2", "TTwo", 2), ("T1b", "TOneb", 4), ("T2b", "TTwob", 3)):
        i, _ = tg[tid]
        num(f"hz{tag}", pre, f"targets[{i}].value", nd)
        num(f"hz{tag}S", pre, f"targets[{i}].sigma", nd if tid in ("T1b", "T2b") else 2)
    num("hzStrict", pre, "tolerance.strict_H0_km_s_Mpc", 2)
    num("hzSoft", pre, "tolerance.soft_H0_km_s_Mpc", 2)
    num("hzStrictSigOne", pre, "tolerance.strict_in_units_of_sigma_pub_T1", 2)
    num("hzStrictSigTwo", pre, "tolerance.strict_in_units_of_sigma_pub_T2", 2)
    num("hzPsuccess", pre, "p_success_prior.PASS_strict_full_conjunction", 2)
    num("hzPsuccessOr", pre, "p_success_prior.PASS_or_PARTIAL", 2)
    num("hzBBNob", pre, "model.bbn_prior.omega_b_mean", 5)
    num("hzBBNobS", pre, "model.bbn_prior.omega_b_sigma", 5)
    text_macro("hzPreTime", p["timestamp_utc"], pre, "timestamp_utc")
    amd = "results/bao_bbn_h0/preregistration_amendment_1.json"
    a = load(amd)
    text_macro("hzAmdTime", a["timestamp_utc"], amd, "timestamp_utc")
    m = re.search(r"sha256 ([0-9a-f]{64})", a["disclosure"])
    lock_sha = m.group(1) if m else ""
    text_macro("hzLockShaShort", lock_sha[:16], amd, "disclosure (sha256 regex), first 16 hex")
    m2 = re.search(r"written (\d\d:\d\d:\d\dZ)", a["disclosure"])
    text_macro("hzLockWritten", m2.group(1) if m2 else "?", amd, "disclosure (written HH:MM:SSZ regex)")
    text_macro("hzLockMatch", "yes" if d["secondary_vs_locked_preamendment"]["sha256_matches"] else "NO", src,
               "secondary_vs_locked_preamendment.sha256_matches")
    lsrc = "results/bao_bbn_h0/fit_attempt1_fittingformula_UNREAD_AT_AMENDMENT.json"
    lk = load(lsrc)
    actual = sha256(lsrc)
    text_macro("hzLockShaNowMatches", "yes" if actual == lock_sha else "NO", lsrc, "sha256(file) == amendment sha256")
    num("hzLockOne", lsrc, "T1_DR2.chain.mean.H0", 3, obj=lk)
    num("hzLockOneS", lsrc, "T1_DR2.chain.std.H0", 3, obj=lk)
    num("hzLockTwo", lsrc, "T2_DR1.chain.mean.H0", 3, obj=lk)
    num("hzLockTwoS", lsrc, "T2_DR1.chain.std.H0", 3, obj=lk)
    num("hzLockDiff", src, "secondary_vs_locked_preamendment.T1_DR2.H0.diff", 1)
    num("hzPmSOne", src, "measured_formula_systematic.primary_minus_secondary_H0_T1", 3)
    num("hzPmSTwo", src, "measured_formula_systematic.primary_minus_secondary_H0_T2", 4)
    num("hzProxySys", src, "measured_formula_systematic.preregistered_proxy_sigma_sys_H0_strict", 3)
    fr = d["rd_camb_validation_summary"]["aub16_minus_camb_fracs"]
    mx = max(abs(x) for x in fr) * 100
    put("hzAubCambMaxPct", fmt(mx, 3), src, "max |rd_camb_validation_summary.aub16_minus_camb_fracs| x100", mx)
    # gates
    for g, tag in (("G1", "GOne"), ("G2", "GTwo")):
        num(f"hz{tag}PullOm", src, f"{g}.pull_Om", 3)
        num(f"hz{tag}PullHrd", src, f"{g}.pull_hrd", 3)
    # boundary / post-hoc
    num("hzTTwoMargin", src, "T2_boundary_resolution.primary.margin_over_strict", 3)
    num("hzTTwoMC", src, "T2_boundary_resolution.primary.our_mc_error_H0", 3)
    dg = "results/bao_bbn_h0/fixround_diagnostics.json"
    num("hzPostHocEight", dg, "slope_and_T2_propagation.T2_propagation[0].implied_H0_excess_km_s_Mpc", 3)
    num("hzPostHocSix", dg, "slope_and_T2_propagation.T2_propagation[1].implied_H0_excess_km_s_Mpc", 3)
    num("hzRebudget", dg, "tolerance_rebudget.rebudget_strict_km_s_Mpc", 3)
    num("hzHrdQuoteEight", dg, "slope_and_T2_propagation.T2_propagation[0].desi_hrd_quoted", 1)
    num("hzHrdQuoteSix", dg, "slope_and_T2_propagation.T2_propagation[1].desi_hrd_quoted", 1)
    m3 = re.search(r"\|Omega_m - 0\.2977\| <= ([0-9.]+)\*", p["tolerance"]["verdicts"]["PASS"])
    if m3 is None:
        raise ValueError("Omega_m tolerance factor not found")
    put("hzOmTol", m3.group(1), pre, "tolerance.verdicts.PASS (regex Omega_m factor)", float(m3.group(1)))
    num("hzPtwoN", "results/bao_bbn_h0/controls/P2_primary.json", "n_mocks", 0)
    # anchors
    num("hzCambAnchor", src, "camb_instrument_anchor.camb_rdrag_this_run", 3)
    num("hzCambAnchorPre", src, "camb_instrument_anchor.preregistration_cited_rdrag", 3)
    # controls
    c = "results/bao_bbn_h0/controls/"
    num("hzNfourD", c + "N4.json", "dH0_wrong_minus_correct", 3)
    n4 = load(c + "N4.json")
    marg = abs(n4["dH0_wrong_minus_correct"]) - n4["strict_tolerance"]
    put("hzNfourMargin", fmt(marg, 3), c + "N4.json", "|dH0_wrong_minus_correct| - strict_tolerance", marg)
    tS = p["targets"][tg["T1"][0]]["sigma"]
    put("hzNfourMarginSig", fmt(marg / tS, 2), c + "N4.json + " + pre, "(|dH0| - strict)/targets[T1].sigma", marg / tS)
    num("hzMnu", pre, "model.fixed.sum_m_nu_eV", 2)
    v = n4["delta_chi2_wrong_minus_correct"]
    put("hzNfourChi", sci(v), c + "N4.json", "delta_chi2_wrong_minus_correct", v)
    text_macro("hzNfourStatus", tex_escape(load(c + "N4_expectation.json")["status"]), c + "N4_expectation.json", "status")
    num("hzPoneD", c + "P1_primary.json", "dH0", 4)
    num("hzPtwoMean", c + "P2_primary.json", "pull_H0_mean", 3)
    num("hzPtwoStd", c + "P2_primary.json", "pull_H0_std", 3)
    num("hzNthree", src, "primary.N3.sigma_H0_ratio_vs_baseline", 1)
    num("hzNtwoChi", c + "N2_primary.json", "chi2", 1)
    num("hzPfour", c + "P4.json", "max_frac_diff", 7)
    v = load(c + "P4.json")["max_frac_diff"]
    MACROS["hzPfour"] = sci(v)
    # referee (H0 referee report lives in the ledger folder)
    rsrc = "results/bao_bbn_h0/ledger/referee_statement_audit_fixround.json"
    r = load(rsrc)
    put("hzRefN", str(len(r["issues"])), rsrc, "issues (count)", len(r["issues"]))
    text_macro("hzRefVerdict", r["verdict"], rsrc, "verdict")
    # table
    rows = []
    for i, pl in enumerate(d["pulls"]):
        pass_str = "--"
        if "within_strict" in pl:
            pass_str = "yes" if pl["within_strict"] else "no"
            if "within_soft" in pl and not pl["within_strict"]:
                pass_str += " (soft: " + ("yes" if pl["within_soft"] else "no") + ")"
        if pl["analysis"] == "primary" and pl["target"] == "T2_H0":
            r3 = load("results/cosmo_synthesis/round3_response_checks.json")["h0_env_rerun"]["cosmo"]["summary"]["primary.T2_DR1"]
            pass_str += " [re-run: " + ("yes" if r3["abs_dH0"] <= float(p["tolerance"]["strict_H0_km_s_Mpc"]) else "no") + r"]$^\ddagger$"
        rows.append((i, pl, pass_str))
    names_seen: dict[str, int] = {}
    lines = [r"\begin{tabular}{llcccccl}", r"\toprule",
             r"Analysis & Target & Ours & $\sigma$ & Target & $\sigma_{\rm t}$ & Pull & Strict rule met \\", r"\midrule"]
    tsrc = {t["id"]: t.get("source", "") for t in p["targets"]}
    for i, pl, ps in rows:
        base = "hzRow" + "abcdefghijklmnop"[i]
        is_h0 = pl["target"].endswith("H0")
        is_hrd = pl["target"].endswith("hrd")
        ndv = 3 if is_h0 else (2 if is_hrd else 4)
        ndt = 2 if (is_h0 or is_hrd) else (4 if pl["target_value"] in (0.2977, 0.2975) else 3)
        a = num(base + "v", src, f"pulls[{i}].value", ndv)
        b = num(base + "s", src, f"pulls[{i}].sigma_fit", ndv)
        tt = num(base + "t", src, f"pulls[{i}].target_value", ndt)
        ts = num(base + "ts", src, f"pulls[{i}].target_sigma", ndt)
        pp = num(base + "p", src, f"pulls[{i}].pull_sigma", 3)
        names_seen[pl["target"]] = names_seen.get(pl["target"], 0) + 1
        tlabel = pl["target"].replace("_", r"\_")
        lines.append(f"{pl['analysis']} & {tlabel} & ${a}$ & ${b}$ & ${tt}$ & ${ts}$ & ${pp}$ & {ps} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (HERE / "gen_tab_h0.tex").write_text("\n".join(lines) + "\n")
    srcl = [r"\begin{tabular}{lp{11cm}}", r"\toprule", r"Target & Source (preregistration) \\", r"\midrule"]
    for tid in ("T1", "T1b", "T2", "T2b", "G1", "G2"):
        srcl.append(f"{tid} & \\scriptsize {tex_escape(tsrc.get(tid, ''))} \\\\")
    srcl += [r"\bottomrule", r"\end{tabular}"]
    (HERE / "gen_tab_h0_sources.tex").write_text("\n".join(srcl) + "\n")


# --------------------------------------------------------------------------- eBOSS
def eboss() -> None:
    src = "results/eboss_vs_desi/fit.json"
    pre = "results/eboss_vs_desi/preregistration.json"
    d = load(src)
    p = load(pre)
    tags = {"SDSS_Om": "SOm", "SDSS_hrd_Mpc": "SHrd", "DESI_DR2_Om": "DOm", "DESI_DR2_hrd_Mpc": "DHrd"}
    psrc = {t["name"]: t["source"] for t in p["targets"]}
    lines = [r"\begin{tabular}{lcccccp{4.3cm}}", r"\toprule",
             r"Quantity & Ours & $\sigma$ & Target & $\sigma_{\rm t}$ & Pull & Source \\", r"\midrule"]
    for i, pl in enumerate(d["pulls"]):
        tag = tags[pl["name"]]
        om = "Om" in pl["name"]
        a = num(f"eb{tag}", src, f"pulls[{i}].value", 4 if om else 2)
        b = num(f"eb{tag}S", src, f"pulls[{i}].sigma", 4 if om else 2)
        c = num(f"eb{tag}T", src, f"pulls[{i}].target", 4 if pl["target"] == 0.2975 else (3 if om else 2))
        e = num(f"eb{tag}TS", src, f"pulls[{i}].target_sigma", 4 if pl["target"] == 0.2975 else (3 if om else 2))
        pp = num(f"eb{tag}P", src, f"pulls[{i}].pull_sigma", 3)
        flag = "" if pl["counts_toward_within_tolerance"] else r"$^\dagger$"
        lab = {"SOm": r"SDSS $\Omega_m$", "SHrd": r"SDSS $h r_d$ [Mpc]", "DOm": r"DESI DR2 $\Omega_m$", "DHrd": r"DESI DR2 $h r_d$ [Mpc]"}[tag]
        lines.append(f"{lab}{flag} & ${a}$ & ${b}$ & ${c}$ & ${e}$ & ${pp}$ & \\scriptsize {tex_escape(psrc[pl['name']])} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (HERE / "gen_tab_eboss.tex").write_text("\n".join(lines) + "\n")
    t = "tension"
    num("ebChi", src, f"{t}.primary_emcee_moments.chi2", 2)
    num("ebPTE", src, f"{t}.primary_emcee_moments.PTE", 3)
    num("ebNsig", src, f"{t}.primary_emcee_moments.N_sigma", 3)
    num("ebNsigGrid", src, f"{t}.grid_moments.N_sigma", 3)
    num("ebNsigMAP", src, f"{t}.MAP_laplace.N_sigma", 3)
    num("ebNsigGauss", src, f"{t}.gaussian_summary_variant_emcee.N_sigma", 3)
    num("ebNsigKDE", src, f"{t}.posterior_parameter_shift_KDE.N_sigma", 3)
    num("ebOneDOm", src, f"{t}.primary_emcee_moments.one_d_sigma.Om", 3)
    num("ebOneDHrd", src, f"{t}.primary_emcee_moments.one_d_sigma.hrd", 3)
    num("ebSCorr", src, "fits.SDSS_eBOSS_DR16_baseline.emcee.corr", 3)
    num("ebBaseVsGauss", src, "baseline_vs_gaussian_summary_shift_in_baseline_sigma.Om", 3)
    lit = p["success_criteria"]["literature_expectation_not_a_criterion"]
    m = re.search(r"2D ([0-9.]+)-([0-9.]+) sigma", lit)
    if m is None:
        raise ValueError("literature band not found")
    put("ebLitLo", m.group(1), pre, "success_criteria.literature_expectation_not_a_criterion (regex 2D lo)", float(m.group(1)))
    put("ebLitHi", m.group(2), pre, "success_criteria.literature_expectation_not_a_criterion (regex 2D hi)", float(m.group(2)))
    num("ebTol", pre, "tolerance_sigma", 1)
    nsrc = "results/eboss_vs_desi/negative_controls.json"
    num("ebInjN", nsrc, "injected_scale_shift_0.93.tension.N_sigma", 1)
    inj_key = next(k for k in load(nsrc) if k.startswith("injected_scale_shift_"))
    put("ebInjScale", inj_key.rsplit("_", 1)[1], nsrc, "key name injected_scale_shift_<factor>", inj_key)
    num("ebEdsGauss", nsrc, "wrong_model_no_Lambda_SDSS_gaussian_summary_gate.delta", 1)
    posrc = "results/eboss_vs_desi/positive_control.json"
    num("ebPosN", posrc, "n_realizations", 0)
    num("ebPosCalFrac", posrc, "tension_calibration.frac_N_sigma_gt_2", 2)
    for f, tag in (("results/eboss_vs_desi/referee_report.json", "One"), ("results/eboss_vs_desi/referee_report_round2.json", "Two")):
        r = load(f)
        put(f"ebRef{tag}N", str(len(r["issues"])), f, "issues (count)", len(r["issues"]))
    for f, tag in (("results/eboss_vs_desi/fixround_outcomes.json", "One"), ("results/eboss_vs_desi/fixround2_outcomes.json", "Two")):
        r = load(f)
        nf = sum(1 for i in r["issues"] if i["fixed"])
        put(f"ebFix{tag}Fixed", str(nf), f, "issues with fixed=true (count)", nf)
        put(f"ebFix{tag}N", str(len(r["issues"])), f, "issues (count)", len(r["issues"]))


# --------------------------------------------------------------------------- Rust
def rust() -> None:
    src = "results/cosmo_synthesis/rust_crosscheck.json"
    d = load(src)
    tab = d["dr2_flat_lcdm_fit_table"]
    cv = "dr2_flat_lcdm_fit_table.Rust, CVODE path"
    qd = "dr2_flat_lcdm_fit_table.Rust, quadrature path"
    num("rsCvOm", src, f"{cv}.Om", 5)
    num("rsCvOmS", src, f"{cv}.sigma_Om", 5)
    num("rsCvHrd", src, f"{cv}.hrd", 3)
    num("rsCvHrdS", src, f"{cv}.sigma_hrd", 3)
    num("rsCvChi", src, f"{cv}.chi2_min", 4)
    num("rsQdOm", src, f"{qd}.Om", 5)
    num("rsQdHrd", src, f"{qd}.hrd", 3)
    py = load("results/desi_dr2_bao/fit.json")["DR2_LCDM_bestfit"]["params"]
    dv = tab["Rust, CVODE path"]["Om"] - py["Om"]
    put("rsCvMinusPyOm", sci(dv), src + " + results/desi_dr2_bao/fit.json",
        "rust CVODE Om (README, 5 decimals) - desi_dr2_bao fit.json DR2_LCDM_bestfit.params.Om", dv)
    dq = tab["Rust, quadrature path"]["Om"] - py["Om"]
    put("rsQdMinusPyOm", sci(dq), src + " + results/desi_dr2_bao/fit.json",
        "rust quadrature Om (README, 5 decimals) - DR2_LCDM_bestfit.params.Om", dq)
    f = d["readme_solver_findings_parsed"]
    put("rsEdsErr", sci(float(f["cvode_eds_worst_rel_err_at_rtol_1e-7"])), src,
        "readme_solver_findings_parsed.cvode_eds_worst_rel_err_at_rtol_1e-7", f["cvode_eds_worst_rel_err_at_rtol_1e-7"])
    put("rsAdamsErr", sci(float(f["adams_rel_err_at_rtol_1e-7"])), src,
        "readme_solver_findings_parsed.adams_rel_err_at_rtol_1e-7", f["adams_rel_err_at_rtol_1e-7"])
    put("rsTestsPass", f["cargo_tests_passed"], src, "readme_solver_findings_parsed.cargo_tests_passed", f["cargo_tests_passed"])
    put("rsTestsIgn", f["cargo_tests_ignored"], src, "readme_solver_findings_parsed.cargo_tests_ignored", f["cargo_tests_ignored"])
    text_macro("rsPortCommit", d["commit_port"]["ref"], src, "commit_port.ref")
    text_macro("rsFixCommit", d["commit_cvode_fix_pr60"]["ref"], src, "commit_cvode_fix_pr60.ref")


# --------------------------------------------------------------------------- Lean
def lean() -> None:
    src = "results/cosmo_synthesis/lean_dual_check.json"
    d = load(src)
    files = [("BAO_FlatLCDM.lean", "A"), ("DESI_DR2_wCDM.lean", "B"), ("BAO_BBN_H0.lean", "C"), ("BAO_Consistency.lean", "D")]
    e1 = "env1_pinned_partial_mathlib"
    e2 = "env2_leanmaster_full_mathlib"
    tot = 0
    clean1 = 0
    clean2 = 0
    wl = set(d["whitelist"])
    lines = [r"\begin{tabular}{lcccccc}", r"\toprule",
             r"File & Theorems & \#print axioms & Env 1 rc & Env 1 time [s] & Env 2 rc & Env 2 time [s] \\", r"\midrule"]
    for fn, tag in files:
        fd = d["files"][fn]
        k = f"files.{fn}"
        n = num(f"ln{tag}N", src, f"{k}.theorem_count", 0)
        pa = num(f"ln{tag}PA", src, f"{k}.print_axioms_commands_in_source", 0)
        r1 = num(f"ln{tag}RcOne", src, f"{k}.envs.{e1}.rc", 0)
        t1 = num(f"ln{tag}TOne", src, f"{k}.envs.{e1}.wall_s", 1)
        r2 = num(f"ln{tag}RcTwo", src, f"{k}.envs.{e2}.rc", 0)
        t2 = num(f"ln{tag}TTwo", src, f"{k}.envs.{e2}.wall_s", 1)
        tot += fd["theorem_count"]
        clean1 += sum(1 for pa_ in fd["envs"][e1]["print_axioms"] if set(pa_["axioms"]) <= wl)
        clean2 += sum(1 for pa_ in fd["envs"][e2]["print_axioms"] if set(pa_["axioms"]) <= wl)
        status2 = fd["envs"][e2].get("status", "")
        extra = " (BLOCKED\\_ENV)" if status2 else ""
        text_macro(f"ln{tag}Sha", fd["sha256"][:12], src, f"{k}.sha256 (first 12 hex)")
        if fd["sha256"] != hashlib.sha256((FORMAL / fn).read_bytes()).hexdigest():
            raise ValueError(f"{fn} changed since the dual check")
        lines.append(f"\\texttt{{{fn.replace('_', chr(92) + '_')}}} & ${n}$ & ${pa}$ & ${r1}$ & ${t1}$ & ${r2}${extra} & ${t2}$ \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (HERE / "gen_tab_lean.tex").write_text("\n".join(lines) + "\n")
    put("lnTotal", str(tot), src, "sum files.*.theorem_count", tot)
    num("lnTotalJson", src, "total_theorems", 0)
    put("lnCleanOne", str(clean1), src, "count env1 print_axioms entries with axioms subset of whitelist", clean1)
    put("lnCleanTwo", str(clean2), src, "count env2 print_axioms entries with axioms subset of whitelist", clean2)
    put("lnBlockedTwo", str(tot - clean2), src, "total - env2 clean", tot - clean2)
    num("lnPairs", src, "accepted_count", 0)
    num("lnPairsTotal", src, "pairs_total", 0)
    recount = sum(1 for f in d["files"].values() for e in f["envs"].values() if e["accepted"])
    if recount != d["accepted_count"]:
        raise ValueError("accepted_count disagrees with per-pair accepted flags")
    nc = d["negative_control"]
    num("lnNegRcOne", src, "negative_control.env1_pinned_partial_mathlib.rc", 0)
    num("lnNegRcTwo", src, "negative_control.env2_leanmaster_full_mathlib.rc", 0)
    num("lnNegTOne", src, "negative_control.env1_pinned_partial_mathlib.wall_s", 1)
    num("lnNegTTwo", src, "negative_control.env2_leanmaster_full_mathlib.wall_s", 1)
    text_macro("lnNegSorry", "yes" if all(nc[e]["sorryAx_seen"] for e in (e1, e2)) else "NO", src, "negative_control.*.sorryAx_seen")
    na = d["negative_control_axiom"]
    num("lnAxRcOne", src, "negative_control_axiom.env1_pinned_partial_mathlib.rc", 0)
    num("lnAxRcTwo", src, "negative_control_axiom.env2_leanmaster_full_mathlib.rc", 0)
    text_macro("lnAxSeen", "yes" if all(na[e]["smuggled_axiom_seen"] for e in (e1, e2)) else "NO", src,
               "negative_control_axiom.*.smuggled_axiom_seen")
    text_macro("lnAxRejected", "yes" if all(na[e]["whitelist_rejects"] for e in (e1, e2)) else "NO", src,
               "negative_control_axiom.*.whitelist_rejects")
    text_macro("lnToolchain", tex_escape(d["toolchain"].split(" ")[0]), src, "toolchain (lean-toolchain file, both envs)")
    envs = d["environments"]
    if envs[e1]["mathlib_rev"] != envs[e2]["mathlib_rev"]:
        raise ValueError("Mathlib revisions differ between environments")
    text_macro("lnMathlibRev", envs[e1]["mathlib_rev"][:12], src, "environments.*.mathlib_rev (first 12 hex; equal in both)")
    text_macro("lnMathlibInput", tex_escape(envs[e1]["mathlib_inputRev"]), src, "environments.*.mathlib_inputRev")
    lv = re.search(r"version ([0-9A-Za-z.\-]+)", envs[e1]["lean_version_output"])
    text_macro("lnLeanVersion", tex_escape(lv.group(1) if lv else "?"), src, "environments.env1.lean_version_output (regex)")
    text_macro("lnLoad", " / ".join(d["load_average_at_end"]) if d.get("load_average_at_end") else "n/a", src,
               "load_average_at_end")
    text_macro("lnVoneSha", d["history"]["revision_1_sha256"][:12], src, "history.revision_1_sha256 (first 12 hex)")
    appendix_lean()


LEAN_MAP = [
    ("ℝ", r"$\mathbb{R}$"), ("⁻¹", r"$^{-1}$"), ("⬝ᵥ", r"$\cdot_v$"), ("*ᵥ", r"$*_v$"), ("∫", r"$\int$"),
    ("≤", r"$\le$"), ("≥", r"$\ge$"), ("≠", r"$\neq$"), ("∧", r"$\wedge$"), ("↔", r"$\leftrightarrow$"),
    ("→", r"$\to$"), ("μ", r"$\mu$"), ("σ", r"$\sigma$"), ("∀", r"$\forall$"), ("∃", r"$\exists$"),
    ("⟨", r"$\langle$"), ("⟩", r"$\rangle$"), ("·", r"$\cdot$"), ("↦", r"$\mapsto$"), ("₁", r"$_1$"), ("₂", r"$_2$"),
]


def lean_statements(path: Path) -> list[str]:
    lines = path.read_text().splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if re.match(r"^(noncomputable def|def|theorem|lemma) ", ln):
            block: list[str] = []
            is_def = "def " in ln.split(" ")[0] + " " or ln.startswith("noncomputable def") or ln.startswith("def ")
            while i < len(lines):
                cur = lines[i]
                if not is_def and ":=" in cur:
                    block.append(cur[: cur.index(":=")].rstrip() + " := ...")
                    break
                if is_def and (cur.strip() == "" or cur.startswith("/--") or cur.startswith("theorem")):
                    break
                block.append(cur)
                i += 1
            out.append("\n".join(block))
        i += 1
    return out


def appendix_lean() -> None:
    parts: list[str] = []
    for fn, ns in (("BAO_FlatLCDM.lean", "ANSE.BAOFlatLCDM"), ("DESI_DR2_wCDM.lean", "ANSE.DESIDR2wCDM"),
                   ("BAO_BBN_H0.lean", "ANSE.BAOBBNH0"), ("BAO_Consistency.lean", "ANSE.BAOConsistency")):
        path = FORMAL / fn
        stm = lean_statements(path)
        body = "\n\n".join(stm)
        for a, b in LEAN_MAP:
            body = body.replace(a, b)
        bad = sorted({ch for ch in body if ord(ch) > 127})
        if bad:
            raise ValueError(f"unmapped characters in {fn}: {bad}")
        if "$$" in body:
            body = body.replace("$$", "")
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        parts.append(f"\\subsection*{{\\texttt{{formal/ANSE/{fn.replace('_', chr(92) + '_')}}}}}\n"
                     f"Namespace \\texttt{{{ns}}}; source sha256\\\\ {{\\scriptsize\\texttt{{{sha}}}}}.\\\\ "
                     f"Proof bodies replaced by \\texttt{{:= ...}}; statements and definitions verbatim.\n"
                     "\\begin{lstlisting}[mathescape]\n" + body + "\n\\end{lstlisting}\n")
    (HERE / "gen_lean_appendix.tex").write_text("\n".join(parts))
    axl: list[str] = []
    d = load("results/cosmo_synthesis/lean_dual_check.json")
    for fn in ("BAO_FlatLCDM.lean", "DESI_DR2_wCDM.lean", "BAO_BBN_H0.lean", "BAO_Consistency.lean"):
        for pa in d["files"][fn]["envs"]["env1_pinned_partial_mathlib"]["print_axioms"]:
            axl.append(pa["line"])
    (HERE / "gen_axioms.tex").write_text("\\begin{lstlisting}\n" + "\n".join(axl) + "\n\\end{lstlisting}\n")


# --------------------------------------------------------------------------- Ledger
def ledger() -> None:
    runs = [("bao_flcdm", "DR1 flat-$\\Lambda$CDM", "lA"), ("desi_dr2_bao", "DESI DR2", "lB"),
            ("bao_bbn_h0", "BAO+BBN $H_0$", "lC"), ("eboss_vs_desi", "eBOSS vs DESI", "lD")]
    lean_file = {"bao_flcdm": "BAO_FlatLCDM.lean", "desi_dr2_bao": "DESI_DR2_wCDM.lean",
                 "bao_bbn_h0": "BAO_BBN_H0.lean", "eboss_vs_desi": "BAO_Consistency.lean"}
    sha_keys = ("audited_file_sha256", "audited_source_sha256", "reviewed_source_sha256")
    auditor_keys = ("by", "auditor", "auditor_kind")
    lines = [r"\begin{tabular}{lcccccccc}", r"\toprule",
             r"Run & Claims & A & B & L & C & A audited (model) & audit hash = current file & gate rc \\", r"\midrule"]
    for run, lab, tag in runs:
        src = f"results/{run}/ledger/ledger.json"
        claims = load(src)["claims"]
        cnt = {t: sum(1 for c in claims if c["tier"] == t) for t in "ABLC"}

        def named(a: Any) -> bool:
            return isinstance(a, dict) and bool(a) and any(isinstance(a.get(k), str) and a.get(k) for k in auditor_keys)

        aud = sum(1 for c in claims if c["tier"] == "A" and named(c.get("audit")))
        cur = hashlib.sha256((FORMAL / lean_file[run]).read_bytes()).hexdigest()
        bound = sum(1 for c in claims if c["tier"] == "A" and named(c.get("audit"))
                    and any(c["audit"].get(k) == cur for k in sha_keys))
        put(f"{tag}Bound", str(bound), src + " + formal/ANSE/" + lean_file[run],
            "audited tier-A rows whose audit sha256 (" + "/".join(sha_keys) + ") equals the current Lean file sha256", bound)
        put(f"{tag}N", str(len(claims)), src, "claims (count)", len(claims))
        for t in "ABLC":
            put(f"{tag}T{t}", str(cnt[t]), src, f"claims with tier {t} (count)", cnt[t])
        put(f"{tag}Aud", str(aud), src, "tier-A claims with a non-empty audit object naming an auditor (count)", aud)
        if run == "bao_flcdm":
            gsrc = "results/desi_dr2_bao/ledger/gate_check.json"
            key = "positive_control_parent_bao_flcdm.rc"
        else:
            gsrc = f"results/{run}/ledger/gate_check.json"
            key = "real.rc"
        rc = dig(load(gsrc), key)
        put(f"{tag}Rc", str(rc), gsrc, key, rc)
        lines.append(f"{lab} & $\\{tag}N$ & $\\{tag}TA$ & $\\{tag}TB$ & $\\{tag}TL$ & $\\{tag}TC$ & $\\{tag}Aud/\\{tag}TA$ & $\\{tag}Bound/\\{tag}Aud$ & $\\{tag}Rc$ \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (HERE / "gen_tab_ledger.tex").write_text("\n".join(lines) + "\n")


# --------------------------------------------------------------------------- round-1 referee checks
def round1() -> None:
    src = "results/cosmo_synthesis/round1_response_checks.json"
    d = load(src)
    g = "h0_gate_propagation"
    num("rgSlope", src, f"{g}.G1.slope", 2)
    num("rgGOneMax", src, f"{g}.G1.max_H0_shift_admitted_by_gate", 2)
    num("rgGTwoMax", src, f"{g}.G2.max_H0_shift_admitted_by_gate", 2)
    num("rgGOneOff", src, f"{g}.G1.observed_hrd_offset_Mpc", 3)
    num("rgGOneOffH", src, f"{g}.G1.implied_H0_shift_from_offset", 3)
    num("rgGTwoOff", src, f"{g}.G2.observed_hrd_offset_Mpc", 3)
    num("rgGTwoOffP", src, f"{g}.G2.observed_offset_pull", 2)
    num("rgGTwoOffH", src, f"{g}.G2.implied_H0_shift_from_offset", 3)
    text_macro("rgGTwoPassed", "passed" if d[g]["G2"]["gate_passed_field"] else "FAILED", src, f"{g}.G2.gate_passed_field")
    c = "dr1_dr2_conventions"
    num("rcSigCone", src, f"{c}.sigma_C1_perfect_correlation", 4)
    num("rcRatioCone", src, f"{c}.ratio_C1", 2)
    ov = d["overlap_sensitivity"]
    if not ov["reproduces_fit_json_at_rho0"] or not all(r["positive_definite"] for r in ov["grid"]):
        raise ValueError("overlap sensitivity check failed")
    i57 = next(i for i, r in enumerate(ov["grid"]) if abs(r["rho"] - 0.57) < 1e-12)
    num("roNsigFiftySeven", src, f"overlap_sensitivity.grid[{i57}].N_sigma", 2)
    num("roPTEFiftySeven", src, f"overlap_sensitivity.grid[{i57}].PTE", 2)
    num("rnMC", src, "n4_margin.T1_mc_error_H0", 4)
    num("rnRatio", src, "n4_margin.margin_over_mc", 1)
    p = "camb_shifted_pull"
    num("rpCambPull", src, f"{p}.pull_if_camb_model", 3)
    num("rpRadPull", src, f"{p}.pull_if_radiation", 3)
    num("rmDRtwoMC", src, "dr2_mc_error.mc_error_in_published_sigma", 3)
    a = "aubourg_points"
    put("raNexceed", str(d[a]["n_exceeding_stated"]), src, f"{a}.n_exceeding_stated", d[a]["n_exceeding_stated"])
    put("raNpts", str(len(d[a]["points"])), src, f"{a}.points (count)", len(d[a]["points"]))
    num("raWorstOb", src, f"{a}.worst.omega_b", 5)
    num("raWorstOc", src, f"{a}.worst.omega_cdm", 3)
    pr = d["rust_pr61"]["result"]
    if pr.get("state") != "MERGED":
        raise ValueError("PR 61 not recorded as merged")
    text_macro("rsPRMerge", pr["mergeCommit"]["oid"][:7], src, "rust_pr61.result.mergeCommit.oid (first 7)")
    text_macro("rsPRMergedAt", pr["mergedAt"], src, "rust_pr61.result.mergedAt")
    b = d["h0_audit_binding"]
    if any(r["audited"] and r["statement_in_prefix_scratch_copy_identical"] is None for r in b["rows"]):
        raise ValueError("h0 audit binding: scratch copy missing or theorem not found")
    nb = sum(1 for r in b["rows"] if r["audited"])
    nsame = sum(1 for r in b["rows"] if r["audited"] and r["statement_in_prefix_scratch_copy_identical"])
    put("rbAudited", str(nb), src, "h0_audit_binding.rows audited (count)", nb)
    put("rbSame", str(nsame), src, "h0_audit_binding.rows audited with identical statement in scratch copy (count)", nsame)
    text_macro("rbAuditSha", b["rows"][0]["audited_source_sha256"][:8], src, "h0_audit_binding.rows[0].audited_source_sha256 (8 hex)")
    text_macro("rbCurSha", b["current_source_sha256"][:8], src, "h0_audit_binding.current_source_sha256 (8 hex)")
    # DR1 chi2 offset
    s2 = "results/cosmo_synthesis/dr1_chi2_offset_check.json"
    e = load(s2)
    num("rdPubChi", s2, "desi_published.chi2", 2)
    num("rdPubOm", s2, "desi_published.Om_bestfit", 3)
    put("rdPubHrd", fmt(e["desi_published"]["H0rd_km_s"] / 100.0, 2), s2, "desi_published.H0rd_km_s / 100", e["desi_published"]["H0rd_km_s"] / 100.0)
    num("rdMzero", s2, "M0_no_radiation.chi2_minus_desi", 3)
    vals = [e[k]["chi2"] for k in ("M1_radiation", "M2_camb_massless_nu", "M3_camb_mnu0.06")]
    dmax = max(abs(v - e["M0_no_radiation"]["chi2"]) for v in vals)
    put("rdMaxChange", fmt(dmax, 3), s2, "max |chi2(M1..M3) - chi2(M0)|", dmax)
    num("rdMthree", s2, "M3_camb_mnu0.06.chi2_minus_desi", 3)
    # referee's ledger mutation M2/M4
    ms = "results/cosmo_synthesis/referee_round1_formal_ledger_mutations.json"
    m = load(ms)
    text_macro("mtMtwo", "/".join(str(m[r]["M2_A_evidence_swapped"]["rc"]) for r in ("desi_dr2_bao", "eboss_vs_desi")),
               ms, "{desi_dr2_bao,eboss_vs_desi}.M2_A_evidence_swapped.rc")
    text_macro("mtMfour", "/".join(str(m[r]["M4_A_audit_empty_object"]["rc"]) for r in ("desi_dr2_bao", "eboss_vs_desi")),
               ms, "{desi_dr2_bao,eboss_vs_desi}.M4_A_audit_empty_object.rc")


# --------------------------------------------------------------------------- round-2 referee checks
def round2() -> None:
    src = "results/cosmo_synthesis/round2_response_checks.json"
    d = load(src)
    g = "g2_attribution"
    num("rtLo", src, f"{g}.rows.rounding_high_101.85.implied_H0_shift", 2)
    num("rtHi", src, f"{g}.rows.rounding_low_101.75.implied_H0_shift", 2)
    num("rtMin", src, f"{g}.implied_min", 2)
    num("rtMax", src, f"{g}.implied_max", 2)
    num("rtMChrd", src, f"{g}.G2_mc_error_hrd_mean", 3)
    num("rtMCH", src, f"{g}.G2_mc_error_propagated_to_H0", 3)
    put("rtGtwoSteps", str(d[g]["G2_chain_n_steps"]), src, f"{g}.G2_chain_n_steps", d[g]["G2_chain_n_steps"])
    num("rtGtwoESS", src, f"{g}.G2_chain_ess", 0)
    t = "t2_resolution"
    num("rtDesiMC", src, f"{t}.desi_mc_error_estimate", 3)
    num("rtComb", src, f"{t}.combined_resolution_quadrature", 3)
    num("rtMarginComb", src, f"{t}.margin_over_combined", 2)
    a = "aubourg_neff"
    put("raNexceedSix", str(d[a]["n_exceeding_vs_camb3046"]), src, f"{a}.n_exceeding_vs_camb3046", d[a]["n_exceeding_vs_camb3046"])
    put("raMaxSixPct", fmt(100 * d[a]["max_abs_frac_vs_camb3046"], 4), src, f"100*{a}.max_abs_frac_vs_camb3046", 100 * d[a]["max_abs_frac_vs_camb3046"])
    sh = [q["camb3044_over_camb3046_minus_1"] for q in d[a]["points"]]
    put("raShiftLo", fmt(1e5 * min(sh), 1), src, f"1e5*min({a}.points[].camb3044_over_camb3046_minus_1)", 1e5 * min(sh))
    put("raShiftHi", fmt(1e5 * max(sh), 1), src, f"1e5*max({a}.points[].camb3044_over_camb3046_minus_1)", 1e5 * max(sh))
    put("raEqSeventeen", fmt(1e5 * d[a]["eq17_factor_rd3044_over_rd3046_minus_1"], 1), src,
        f"1e5*{a}.eq17_factor_rd3044_over_rd3046_minus_1", 1e5 * d[a]["eq17_factor_rd3044_over_rd3046_minus_1"])
    text_macro("raCambVer", d[a]["camb_version"], src, f"{a}.camb_version")
    gs = "dr1_grid_step"
    num("rgStepOm", src, f"{gs}.step_Om", 5)
    num("rgStepHrd", src, f"{gs}.step_hrd", 3)
    put("rgNgrid", str(d[gs]["n"]), src, f"{gs}.n", d[gs]["n"])
    s1 = "results/bao_flcdm/desi_dr1_flcdm_fit.json"
    opt = load(s1)["fit_manual_quad"]
    n_om = abs(d[gs]["grid_Om"] - opt["Om_m"]) / d[gs]["step_Om"]
    n_hrd = abs(d[gs]["grid_hrd"] - opt["rd_h_Mpc"]) / d[gs]["step_hrd"]
    put("rgNodesOm", fmt(n_om, 1), s1, f"|cross_check_grid_search.Om_m - fit_manual_quad.Om_m| / step_Om (step from {src})", n_om)
    put("rgNodesHrd", fmt(n_hrd, 1), s1, f"|cross_check_grid_search.rd_h_Mpc - fit_manual_quad.rd_h_Mpc| / step_hrd (step from {src})", n_hrd)
    num("rgGridChi", s1, "cross_check_grid_search.chi2", 4)
    p2 = "p2_om_moments"
    num("hzPtwoOmMean", src, f"{p2}.pull_Om_mean", 3)
    num("hzPtwoOmStd", src, f"{p2}.pull_Om_std", 3)
    num("hzPtwoOmSE", src, f"{p2}.se_mean", 3)
    z = d["dr2_zgtm1_lean"]
    if not (z["rc"] == 0 and z["whitelist_only"] and z["tactic_E2_identical"] and z["tactic_E_changed_only_lemma_name"]
            and not z["sorry_warning"]):
        raise ValueError("DR2 z>-1 check did not pass")
    put("zgRc", str(z["rc"]), src, "dr2_zgtm1_lean.rc", z["rc"])
    text_macro("zgSha", z["kept_copy_sha256"][:8], src, "dr2_zgtm1_lean.kept_copy_sha256 (8 hex)")
    mb = d["mathlib_builds"]
    put("mbOne", str(mb["env1_pinned"]["n_olean"]), src, "mathlib_builds.env1_pinned.n_olean", mb["env1_pinned"]["n_olean"])
    put("mbTwo", str(mb["env2_leanmaster"]["n_olean"]), src, "mathlib_builds.env2_leanmaster.n_olean", mb["env2_leanmaster"]["n_olean"])
    put("mbSrc", str(mb["env1_pinned"]["n_lean_sources"]), src, "mathlib_builds.env1_pinned.n_lean_sources", mb["env1_pinned"]["n_lean_sources"])
    li = d["lake_root_imports"]
    put("lrMainFlat", str(li["main_checkout"]["ANSE.BAO_FlatLCDM"]), src, "lake_root_imports.main_checkout.ANSE.BAO_FlatLCDM", li["main_checkout"]["ANSE.BAO_FlatLCDM"])
    nnew = sum(li["main_checkout"][m] for m in ("ANSE.DESI_DR2_wCDM", "ANSE.BAO_BBN_H0", "ANSE.BAO_Consistency"))
    put("lrMainNew", str(nnew), src, "lake_root_imports.main_checkout (sum of three new modules)", nnew)


# --------------------------------------------------------------------------- round-3 referee checks
def round3() -> None:
    src = "results/cosmo_synthesis/round3_response_checks.json"
    d = load(src)
    ev = d["env_versions"]
    for env, tag in (("cosmo", "Cos"), ("pta", "Pta")):
        for k, kk in (("python", "Py"), ("numpy", "Np"), ("scipy", "Sp")):
            text_macro(f"ev{tag}{kk}", ev[env][k], src, f"env_versions.{env}.{k}")
    text_macro("evEmcee", ev["cosmo"]["emcee"], src, "env_versions.cosmo.emcee")
    if ev["cosmo"]["emcee"] != ev["pta"]["emcee"]:
        raise ValueError("emcee versions differ; the text assumes they are equal")
    r = d["h0_env_rerun"]
    for env, tag in (("cosmo", "Cos"), ("pta", "Pta")):
        e = r[env]
        put(f"re{tag}Ndiff", str(e["n_numeric_leaves_differing"]), src, f"h0_env_rerun.{env}.n_numeric_leaves_differing", e["n_numeric_leaves_differing"])
        put(f"re{tag}Ncomp", str(e["n_numeric_leaves_compared"]), src, f"h0_env_rerun.{env}.n_numeric_leaves_compared", e["n_numeric_leaves_compared"])
    if r["pta"]["n_numeric_leaves_differing"] != 0:
        raise ValueError("venv-pta re-run does not reproduce fit.json; the provenance sentence would be false")
    cs = r["cosmo"]["summary"]
    for key, tag in (("primary.T1_DR2", "POne"), ("primary.T2_DR1", "PTwo"), ("secondary.T1_DR2", "SOne"), ("secondary.T2_DR1", "STwo")):
        num(f"re{tag}H", src, f"h0_env_rerun.cosmo.summary.{key}.H0_mean", 3, obj=d)
        num(f"re{tag}D", src, f"h0_env_rerun.cosmo.summary.{key}.abs_dH0", 4, obj=d)
        text_macro(f"re{tag}V", cs[key]["verdict"], src, f"h0_env_rerun.cosmo.summary.{key}.verdict")
    num("reGTwoHrd", src, "h0_env_rerun.cosmo.summary.G2.hrd_mean", 2, obj=d)
    if not r["g2_implied_cosmo"]["recorded_matches_round2_g2_attribution"]:
        raise ValueError("G2 implied-shift formula does not reproduce round2 g2_attribution")
    num("reGTwoImpl", src, "h0_env_rerun.g2_implied_cosmo.implied_H0_shift", 3, obj=d)
    v = r["max_abs_map_H0_diff_cosmo"]
    put("reMapMax", sci(v), src, "h0_env_rerun.max_abs_map_H0_diff_cosmo", v)
    fp = r["formula_prediction"]
    put("fpEpsPct", fmt(-100 * fp["eps_point_0"], 3), src, "-100*h0_env_rerun.formula_prediction.eps_point_0", -100 * fp["eps_point_0"])
    num("fpPredOne", src, "h0_env_rerun.formula_prediction.T1_DR2.pred_from_point_0", 4, obj=d)
    num("fpPredTwo", src, "h0_env_rerun.formula_prediction.T2_DR1.pred_from_point_0", 4, obj=d)
    num("fpStatedOne", src, "h0_env_rerun.formula_prediction.T1_DR2.pred_from_stated_0.021pct", 3, obj=d)
    num("reShiftMC", src, "h0_env_rerun.primary_T2_shift_in_committed_mc_errors", 1, obj=d, scale=-1.0)
    num("reShift", src, "h0_env_rerun.primary_T2_shift_cosmo_minus_committed", 3, obj=d)
    num("reLockTwo", src, "h0_env_rerun.cosmo.secondary_vs_locked_T2_H0_diff", 4, obj=d)
    num("reLockOne", src, "h0_env_rerun.cosmo.secondary_vs_locked_T1_H0_diff", 4, obj=d)
    f = "formula_shift.committed"
    num("fsMapOne", src, f"{f}.T1_DR2.map_diff", 4, obj=d)
    num("fsMapTwo", src, f"{f}.T2_DR1.map_diff", 4, obj=d)
    num("fsMcOne", src, f"{f}.T1_DR2.mean_diff_mc_error", 3, obj=d)
    num("fsMcTwo", src, f"{f}.T2_DR1.mean_diff_mc_error", 3, obj=d)
    num("fsCosOne", src, "formula_shift.venv_cosmo_rerun.T1_DR2.mean_diff", 3, obj=d)
    num("fsCosTwo", src, "formula_shift.venv_cosmo_rerun.T2_DR1.mean_diff", 3, obj=d)
    a = d["aubourg_omega_cb"]
    put("aoMatchedPct", fmt(100 * a["max_abs_frac_matched_vs_camb3046"], 4), src, "100*aubourg_omega_cb.max_abs_frac_matched_vs_camb3046", 100 * a["max_abs_frac_matched_vs_camb3046"])
    put("aoNexceed", str(a["n_exceeding_matched_vs_camb3046"]), src, "aubourg_omega_cb.n_exceeding_matched_vs_camb3046", a["n_exceeding_matched_vs_camb3046"])
    put("aoOffset", sci(a["omega_cb_offset_in_stored"]), src, "aubourg_omega_cb.omega_cb_offset_in_stored", a["omega_cb_offset_in_stored"])
    num("olXonly", src, "overlap_x_only.X_only.N_sigma", 2, obj=d)
    num("olXonlyPTE", src, "overlap_x_only.X_only.PTE", 2, obj=d)
    num("swMC", src, "strict_window.mc_term", 2, obj=d)
    num("swFormula", src, "strict_window.formula_term", 3, obj=d)
    num("swInterp", src, "strict_window.rebudget_terms.interp", 4, obj=d)
    di = d["dr1_interpreter"]
    if not (di["venv_cosmo_rc"] == 0 and di["venv_cosmo_differing_leaves"] == ["generated_at"] and di["venv_pta_rc"] != 0):
        raise ValueError("DR1 interpreter check changed")
    msrc = "results/cosmo_synthesis/round3_m6_mutation.json"
    m = load(msrc)
    und = sum(1 for v in m.values() if not v["gate_detected"])
    put("msixUndetected", str(und), msrc, "count of runs where gate_detected is false", und)
    put("msixN", str(len(m)), msrc, "count of runs", len(m))
    tb = sum(int(MACROS[f"{t}TB"]) for t in ("lA", "lB", "lC", "lD"))
    put("tierBTotal", str(tb), "results/*/ledger/ledger.json", "sum of lATB..lDTB", tb)


# --------------------------------------------------------------------------- tier provenance
def tiers() -> None:
    src = "results/cosmo_synthesis/model_tier_provenance.json"
    d = load(src)
    text_macro("tierQuote", tex_escape(d["quote_verbatim"].lstrip("- ").replace("**", "")), src, "quote_verbatim")
    text_macro("tierTime", d["timestamp_utc"], src, "timestamp_utc")
    text_macro("tierShaShort", d["quote_sha256"][:16], src, "quote_sha256 (first 16 hex)")


# --------------------------------------------------------------------------- hashes
def hashes() -> None:
    files = [
        "results/bao_flcdm/desi_dr1_flcdm_fit.json",
        "results/desi_dr2_bao/preregistration.json",
        "results/desi_dr2_bao/fit.json",
        "results/desi_dr2_bao/controls.json",
        "results/bao_bbn_h0/preregistration.json",
        "results/bao_bbn_h0/preregistration_amendment_1.json",
        "results/bao_bbn_h0/fit_attempt1_fittingformula_UNREAD_AT_AMENDMENT.json",
        "results/bao_bbn_h0/fit.json",
        "results/eboss_vs_desi/preregistration.json",
        "results/eboss_vs_desi/fit.json",
        "results/cosmo_synthesis/lean_dual_check.json",
        "results/cosmo_synthesis/rust_crosscheck.json",
        "results/cosmo_synthesis/model_tier_provenance.json",
        "results/cosmo_synthesis/round1_response_checks.json",
        "results/cosmo_synthesis/dr1_chi2_offset_check.json",
        "results/cosmo_synthesis/lean_dual_check_v1_handedited.json",
        "results/cosmo_synthesis/round2_response_checks.json",
        "results/cosmo_synthesis/dr2_zgtm1_check.lean",
        "results/cosmo_synthesis/round3_response_checks.json",
        "results/cosmo_synthesis/round3_m6_mutation.json",
        "results/cosmo_synthesis/round3_rerun_fit_venv_pta.json",
        "results/cosmo_synthesis/round3_rerun_fit_venv_cosmo.json",
    ]
    checks = {
        "results/desi_dr2_bao/preregistration.json": ("results/desi_dr2_bao/fit.json", "preregistration_sha256"),
        "results/bao_bbn_h0/preregistration.json": ("results/bao_bbn_h0/fit.json", "preregistration_sha256"),
        "results/bao_bbn_h0/preregistration_amendment_1.json": ("results/bao_bbn_h0/fit.json", "amendment_1_sha256"),
        "results/eboss_vs_desi/preregistration.json": ("results/eboss_vs_desi/fit.json", "preregistration_sha256"),
    }
    lines = [r"\begin{tabular}{lll}", r"\toprule", r"File & sha256 & Matches pin in fit \\", r"\midrule"]
    for f in files:
        h = sha256(f)
        MANIFEST.append({"macro": "(table gen_tab_sha)", "tex": h, "file": f, "key": "sha256(file)", "value": h})
        pin = ""
        if f in checks:
            ff, kk = checks[f]
            pin = "yes" if dig(load(ff), kk) == h else "NO"
        lines.append(f"\\scriptsize\\texttt{{{f.replace('_', chr(92) + '_')}}} & \\scriptsize\\texttt{{{h}}} & {pin} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (HERE / "gen_tab_sha.tex").write_text("\n".join(lines) + "\n")
    # data files
    ds = load("results/bao_bbn_h0/fit.json")["data_sha256"]
    dl = [r"\begin{tabular}{ll}", r"\toprule", r"DESI data file (as used by all DESI fits) & sha256 \\", r"\midrule"]
    for k, v in ds.items():
        name = Path(k).name.replace("_", r"\_")
        dl.append(f"\\scriptsize\\texttt{{{name}}} & \\scriptsize\\texttt{{{v}}} \\\\")
        MANIFEST.append({"macro": "(table gen_tab_data)", "tex": v, "file": "results/bao_bbn_h0/fit.json", "key": f"data_sha256.{k}", "value": v})
    dl += [r"\bottomrule", r"\end{tabular}"]
    (HERE / "gen_tab_data.tex").write_text("\n".join(dl) + "\n")


def guards() -> None:
    """Parse the recorded guard and pytest logs of the three preregistered runs."""
    logs = {
        "Two": ("results/desi_dr2_bao/guard_antigravity_fixround.txt", "results/desi_dr2_bao/guard_test_rigor_fixround.txt",
                "results/desi_dr2_bao/pytest_fixround_continue.txt"),
        "Hz": ("results/bao_bbn_h0/guard_antigravity_fixround.txt", "results/bao_bbn_h0/guard_test_rigor_fixround.txt",
               "results/bao_bbn_h0/pytest_full_fixround.txt"),
        "Eb": ("results/eboss_vs_desi/antigravity_guard.log", "results/eboss_vs_desi/test_rigor_guard.log",
               "results/eboss_vs_desi/pytest_tests.log"),
    }
    ansi = re.compile(r"\x1b\[[0-9;]*m")
    for tag, (ag, tr, pt) in logs.items():
        agt = (ROOT / ag).read_text()
        text_macro(f"g{tag}Anti", "FAIL" if "[FAIL]" in agt else ("PASS" if "[PASS]" in agt else "unknown"), ag, "contains [FAIL]/[PASS]")
        trt = (ROOT / tr).read_text()
        text_macro(f"g{tag}Rigor", "PASS" if "[PASS]" in trt else ("FAIL" if "[FAIL]" in trt else "unknown"), tr, "contains [PASS]/[FAIL]")
        ptt = ansi.sub("", (ROOT / pt).read_text())
        last = [ln for ln in ptt.splitlines() if re.search(r"(passed|failed|errors? during collection|error)", ln) and " in " in ln]
        summ = last[-1].strip(" =") if last else "no summary line"
        summ = re.sub(r"\s+in [0-9.]+s.*$", "", summ)
        text_macro(f"g{tag}Pytest", tex_escape(summ), pt, "last pytest summary line (ANSI stripped)")


def check_appendix() -> None:
    """The appendix must contain exactly the theorems the dual check printed axioms for."""
    body = (HERE / "gen_lean_appendix.tex").read_text()
    names = re.findall(r"^theorem (\S+)", body, flags=re.M)
    d = load("results/cosmo_synthesis/lean_dual_check.json")
    decls = [pa["decl"].split(".")[-1] for fn in d["files"].values()
             for pa in fn["envs"]["env1_pinned_partial_mathlib"]["print_axioms"]]
    if sorted(names) != sorted(decls) or len(names) != d["total_theorems"]:
        raise ValueError(f"appendix theorems {len(names)} do not match dual-check decls {len(decls)}")
    put("lnAppendixN", str(len(names)), "papers/cosmo_synthesis/gen_lean_appendix.tex", "count of theorem blocks (checked against lean_dual_check decls)", len(names))


def derived_table() -> None:
    lines = [r"\begin{tabular}{p{6.3cm}cp{8.8cm}}", r"\toprule", r"Quantity & Value & Definition / source key \\", r"\midrule",
             r"DR1$\to$DR2 shift $\Delta\Omega_m$ (DR2 run, emcee means) & $\shDelta$ & \scriptsize \texttt{DR1\_to\_DR2\_shift.Delta\_Om} \\",
             r"$\Delta\Omega_m/\sigma_{\rm nested}$ (own $\sigma_{\rm nested}=\shSigNestOwn$) & $\shRatioOwn$ & \scriptsize $\sigma_{\rm nested}^2=\sigma_{\rm DR1}^2-\sigma_{\rm DR2}^2$; \texttt{Delta\_over\_sigma\_nested\_own} \\",
             r"$\Delta\Omega_m/\sigma_{\rm nested}$ (preregistered $\sigma=\shSigNestPre$) & $\shRatioPre$ & \scriptsize \texttt{Delta\_over\_sigma\_nested\_prereg} \\",
             r"$\Delta\Omega_m/\sigma_{\rm indep}$ (wrong if nested; for comparison) & $\shRatioInd$ & \scriptsize \texttt{Delta\_over\_sigma\_independent\_own} \\",
             r"$\Delta\Omega_m/|\sigma_{\rm DR1}-\sigma_{\rm DR2}|$ ($C=1$ bracket) & $\rcRatioCone$ & \scriptsize \texttt{round1\_response\_checks.json: dr1\_dr2\_conventions.ratio\_C1} \\",
             r"SDSS--DESI DR2 tension, $(\Omega_m, h r_d)$, 2 dof & $N_\sigma=\ebNsig$ & \scriptsize $\chi^2=\ebChi$, PTE $=\ebPTE$; \texttt{tension.primary\_emcee\_moments} \\",
             r"\quad same, grid / MAP+Laplace / KDE shift & $\ebNsigGrid$ / $\ebNsigMAP$ / $\ebNsigKDE$ & \scriptsize \texttt{tension.\{grid\_moments, MAP\_laplace, posterior\_parameter\_shift\_KDE\}} \\",
             r"\quad same, with $X+X^{\rm T}$, $X=\rho\sqrt{C_S}\sqrt{C_D}$, subtracted, $\rho=0.57$ (illustration) & $N_\sigma=\roNsigFiftySeven$ & \scriptsize \texttt{round1\_response\_checks.json: overlap\_sensitivity} \\",
             r"$H_0$ shift, exact CAMB $r_d$ minus fitting formula, DR2, MAP (deterministic; equals the propagated measured formula error, which exceeds Aubourg's stated 0.021\%; not new) & $\fsMapOne$ km/s/Mpc & \scriptsize \texttt{round3\_response\_checks.json}, key \texttt{formula\_shift}, \texttt{map\_diff} \\",
             r"\quad same, DR1, MAP & $\fsMapTwo$ km/s/Mpc & \scriptsize \texttt{...T2\_DR1.map\_diff} \\",
             r"\quad posterior-mean differences DR2 / DR1 (MC-noise dominated) & $\hzPmSOne\pm\fsMcOne$ / $\hzPmSTwo\pm\fsMcTwo$ & \scriptsize \texttt{measured\_formula\_systematic}; MC error from chain std/$\sqrt{\rm ESS}$ \\",
             r"Wrong neutrino bookkeeping (N4), $\Delta H_0$ (MAP) & $\hzNfourD$ km/s/Mpc & \scriptsize $\Delta\chi^2=\hzNfourChi$; \texttt{controls/N4.json} \\",
             r"\bottomrule", r"\end{tabular}"]
    (HERE / "gen_tab_derived.tex").write_text("\n".join(lines) + "\n")


def main() -> None:
    dr1()
    dr2()
    h0()
    eboss()
    rust()
    lean()
    ledger()
    round1()
    round2()
    round3()
    tiers()
    hashes()
    guards()
    check_appendix()
    derived_table()
    out = ["% generated by gen_numbers.py -- do not edit"]
    for k, v in MACROS.items():
        out.append(f"\\newcommand{{\\{k}}}{{{v}}}")
    (HERE / "gen_numbers.tex").write_text("\n".join(out) + "\n")
    for m in MANIFEST:
        if m["macro"].startswith("\\") and m["macro"][1:] in MACROS:
            m["tex"] = MACROS[m["macro"][1:]]
    (HERE / "number_manifest.json").write_text(json.dumps(MANIFEST, indent=1, default=str) + "\n")
    print(f"{len(MACROS)} macros, {len(MANIFEST)} manifest rows")


if __name__ == "__main__":
    main()
