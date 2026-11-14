"""Generate every number, Lean listing, axiom transcript and table that main.tex prints (lane P6, superfluid S(k)).

Inputs (read-only): results/programmes/2026-10-25/P6/{results.json,data/*.csv,lean/*.json}, the Lean sources in
formal_cert/Programmes/FeynmanBijl/, and (optional) rerun/*.json from rerun_lean.py. Copies the inputs it needs into
data/ so the paper directory is self-contained. Outputs: gen_numbers.tex, gen/*.lean, gen/*.lst (non-ASCII mapped for
listings), gen/axioms_*.txt (verbatim #print axioms output), gen/table_*.tex.
Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I gen_inputs.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = HERE.parents[1]
P6 = W / "results/programmes/2026-10-25/P6"
LEAN = W / "formal_cert/Programmes/FeynmanBijl"
DATA = HERE / "data"
GEN = HERE / "gen"
RERUN = HERE / "rerun"

# sha256 recorded in FEYNMAN_BIJL.md at stage WORK2 (compared with the live values below)
STAGE_SHA = {
    "Basic.lean": "a8ed4357bce846e675af161a81dbeddeedcba07c0a2e7f2ae09fce21c5cb6432",
    "NegativeControls.lean": "182f8135dd3c778703a8523e46724f600227a3bdcaadc4da5a8bc843373bfc3a",
    "PositiveControls.lean": "1555d75cda679a600b667ac0f559b7bd72f9cee3982c644531ee6f81d4bffc05",
    "Controls.lean": "a0f2e8edab9b5aa211fd1a5b39d8836cc22220b483390413edda46135e0c0099",
}

UMAP = {
    "ℝ": r"$\mathbb{R}$", "ℂ": r"$\mathbb{C}$", "→": r"$\to$", "∀": r"$\forall$", "≤": r"$\le$", "≥": r"$\ge$",
    "∈": r"$\in$", "²": r"$^2$", "⁻": r"$^{-}$", "¹": r"$^{1}$", "√": r"$\surd$", "ρ": r"$\rho$", "ψ": r"$\psi$",
    "φ": r"$\varphi$", "λ": r"$\lambda$", "ħ": r"$\hbar$", "ε": r"$\epsilon$", "₀": r"$_0$", "₁": r"$_1$", "ᵢ": r"$_i$",
    "⟪": r"$\langle$", "⟫": r"$\rangle$", "†": r"$\dagger$", "⟨": r"$\langle$", "⟩": r"$\rangle$", "¬": r"$\neg$",
    "∧": r"$\wedge$", "↔": r"$\leftrightarrow$", "≠": r"$\ne$", "·": r"$\cdot$", "∑": r"$\sum$", "‖": r"$\Vert$",
    "∃": r"$\exists$", "∘": r"$\circ$", "•": r"$\bullet$", "–": "--", "—": "---", "•": r"$\bullet$", "ₗ": r"$_\ell$",
    "ℓ": r"$\ell$", "↑": r"$\uparrow$", "∞": r"$\infty$", "ᶜ": r"$^c$", "⁻¹": r"$^{-1}$", "σ": r"$\sigma$",
    "ι": r"$\iota$", "×": r"$\times$", "∂": r"$\partial$", "Σ": r"$\Sigma$", "∨": r"$\vee$", "▸": r"$\triangleright$",
    "⊥": r"$\perp$", "∣": r"$\mid$", "Ψ": r"$\Psi$", "∅": r"$\emptyset$", "∖": r"$\setminus$", "∑": r"$\sum$",
    "ₛ": r"$_s$", "𝕜": r"$\mathbb{k}$", "⁴": r"$^4$", "∗": r"$*$", "⟶": r"$\longrightarrow$", "⇒": r"$\Rightarrow$",
    "≈": r"$\approx$", "←": r"$\leftarrow$", "⊆": r"$\subseteq$", "ℕ": r"$\mathbb{N}$", "½": r"$\frac12$", "μ": r"$\mu$", "θ": r"$\theta$",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def extract(src: list[str], name: str, kind: str) -> list[str]:
    """kind: def (until blank line), thm (statement up to ':= ...' line, proof elided), full (whole declaration)."""
    pat = re.compile(rf"^(theorem|lemma|noncomputable def|def|abbrev|axiom) {re.escape(name)}\b")
    for i, line in enumerate(src):
        if not pat.match(line):
            continue
        out: list[str] = []
        if kind == "def":
            for l in src[i:]:
                if not l.strip():
                    break
                out.append(l)
            return out
        if kind == "full":
            for j, l in enumerate(src[i:]):
                if j > 0 and l and not l.startswith((" ", "\t")):
                    break
                out.append(l)
            while out and not out[-1].strip():
                out.pop()
            return out
        for l in src[i:]:
            if re.search(r":=(\s*by)?(\s*sorry)?(\s*\S+\.elim)?\s*$", l) or ":= by" in l:
                out.append(l[: l.index(":=") + 2] + " ... -- proof elided")
                return out
            out.append(l)
    raise SystemExit(f"declaration {name} not found")


def block(src: list[str], decls: list[tuple[str, str]]) -> str:
    lines: list[str] = []
    for name, kind in decls:
        lines += extract(src, name, kind) + [""]
    return "\n".join(lines).rstrip() + "\n"


def f(x: float, d: int = 3) -> str:
    return f"{x:.{d}f}"


def main() -> int:
    GEN.mkdir(exist_ok=True)
    DATA.mkdir(exist_ok=True)
    for p in ["results.json", "DATA.md", "FEYNMAN_BIJL.md"]:
        shutil.copy(P6 / p, DATA / p)
    for p in (P6 / "data").glob("*.csv"):
        shutil.copy(p, DATA / p.name)
    for p in (P6 / "lean").glob("*.json"):
        shutil.copy(p, DATA / ("lean_" + p.name))
    shutil.copy(P6 / "raw/parsed.json", DATA / "donnelly_parsed.json")
    for p in (P6 / "scripts").glob("*.py"):
        shutil.copy(p, DATA / ("script_" + p.name))

    R = json.loads((P6 / "results.json").read_text())
    he, bec = R["he4"], R["bec"]
    gate = json.loads((P6 / "lean/axiom_gate.json").read_text())
    num = json.loads((P6 / "lean/feynman_bijl_numeric.json").read_text())

    basic = (LEAN / "Basic.lean").read_text().splitlines()
    neg = (LEAN / "NegativeControls.lean").read_text().splitlines()
    pos = (LEAN / "PositiveControls.lean").read_text().splitlines()
    ctl = (LEAN / "Controls.lean").read_text().splitlines()

    texts = {
        "defs": block(basic, [("comm", "def"), ("excess", "def")]),
        "dce": block(basic, [("double_comm_expect", "full")]),
        "half": block(basic, [("excess_eq_half", "full")]),
        "trial": block(basic, [("trial_energy_eq", "thm")]),
        "ground": block(basic, [("trial_energy_le_of_ground", "thm")]),
        "sector": block(basic, [("exists_le_weighted_mean", "thm"), ("rayleigh_expansion", "thm"), ("sector_eigenvalue_le", "thm")]),
        "bound": block(basic, [("feynman_bijl_bound", "thm")]),
        "boundg": block(basic, [("feynman_bijl_bound_ground", "thm")]),
        "gap": block(basic, [("feynman_bijl_gap", "thm")]),
        "bogdefs": block(basic, [("epsFree", "def"), ("epsBog", "def"), ("sBog", "def")]),
        "bogeq": block(basic, [("epsFree_units", "thm"), ("feynman_sBog_eq", "thm"), ("feynman_le_epsBog_iff", "thm"),
                               ("feynman_sBog_units", "thm")]),
        "bogbound": block(basic, [("sBog_sq", "thm"), ("sBog_le_sqrt", "full")]),
        "neg": block(neg, [("symmetry_needed", "thm"), ("symmetry_needed_fin2", "thm")]),
        "pos": block(pos, [("gap_witness", "thm"), ("gap_witness_applies", "thm"), ("orthonormal_pair_fin2", "thm")]),
        "ctl": block(ctl, [("ctl_sorry", "full"), ("ctl_cheat", "full"), ("ctl_axiom", "full")]),
    }
    used: set[str] = set()
    for key, txt in texts.items():
        (GEN / f"{key}.lean").write_text(txt)
        used |= {c for c in txt if ord(c) > 127}
    missing = sorted(c for c in used if c not in UMAP)
    if missing:
        raise SystemExit(f"unmapped codepoints: {[hex(ord(c)) + ' ' + c for c in missing]}")
    for key, txt in texts.items():
        t = txt
        for c in sorted(used, key=len, reverse=True):
            t = t.replace(c, "(*@" + UMAP[c] + "@*)")
        (GEN / f"{key}.lst").write_text(t)

    # verbatim #print axioms transcripts
    comp = {}
    for tag in ["basic", "negctl", "posctl", "controls"]:
        j = json.loads((P6 / f"lean/compile_{tag}.json").read_text())
        comp[tag] = j
        o = j["output"].replace(str(W) + "/", "")
        (GEN / f"axioms_{tag}.txt").write_text(f"rc = {j['rc']}, {j['seconds']} s\n" + o)

    # live shas
    live = {n: sha(LEAN / n) for n in STAGE_SHA}
    sha_match = all(live[n] == STAGE_SHA[n] for n in STAGE_SHA)

    # optional rerun
    rer = {}
    for tag in ["basic", "negctl", "posctl", "controls"]:
        p = RERUN / f"compile_{tag}.json"
        if p.exists():
            rer[tag] = json.loads(p.read_text())
    rerun_same = None
    if len(rer) == 4:
        def axl(j: dict) -> list[str]:
            return sorted(l for l in j["output"].replace(str(W) + "/", "").splitlines() if "depends on axioms" in l)
        rerun_same = all(axl(rer[t]) == axl(comp[t]) and rer[t]["rc"] == 0 for t in rer)
        for tag, j in rer.items():
            o = j["output"].replace(str(W) + "/", "")
            (GEN / f"axioms_rerun_{tag}.txt").write_text(f"rc = {j['rc']}, {j['seconds']} s\n" + o)

    # He-4 table regions
    rows = list(csv.DictReader((DATA / "test_he4.csv").open()))
    for r in rows:
        r["Q"] = float(r["Q_invA"]); r["S_"] = float(r["S"]); r["ratio_"] = float(r["ratio"]); r["margin_"] = float(r["margin"])
    ks = he["kstar_inv_A"]
    regions = [("0.21--1.40", 0.0, 1.4005), ("1.47--1.65", 1.4005, 1.6995), ("1.70--2.40 (peak)", 1.6995, 2.4005),
               ("2.40--5.13", 2.4005, 5.15), ("5.18--5.94 ($<2k_*$)", 5.15, 2 * ks), ("$\\ge2k_*$", 2 * ks, 99.0)]
    lines = []
    for name, lo, hi in regions:
        sel = [r for r in rows if lo < r["Q"] <= hi]
        if not sel:
            continue
        c = {v: sum(1 for r in sel if r["verdict"] == v) for v in ["CONSISTENT", "UNDECIDED", "REFUTED"]}
        rs = [r["ratio_"] for r in sel]
        lines.append(f"{name} & {len(sel)} & {c['CONSISTENT']} & {c['UNDECIDED']} & {c['REFUTED']} & {min(rs):.2f}--{max(rs):.2f}\\\\")
    (GEN / "table_regions.tex").write_text("\n".join(lines) + "\n")
    n_xr = sum(1 for r in rows if r["key"] == "1"); n_nu = sum(1 for r in rows if r["key"] == "2")
    ref = [r for r in rows if r["verdict"] == "REFUTED"]
    refx = sum(1 for r in ref if r["key"] == "1")
    peak = max(rows, key=lambda r: r["S_"])

    # BEC Stamper-Kurn table
    sk = list(csv.DictReader((DATA / "bec_stamper_kurn_fig3a_tierX.csv").open()))
    sk_lines = []
    for r in sk:
        sk_lines.append(f"{float(r['peak_density_1e14_cm3']):.2f} & {float(r['mu_over_h_kHz']):.2f} & {float(r['S']):.3f} & {float(r['sigma']):.3f} & "
                        f"{float(r['S_lda_bogoliubov']):.3f} & {float(r['bound_lda_average']):.3f} & {float(r['z_vs_lda_bound']):.2f} & "
                        f"{float(r['ratio_model_over_bound']):.2f}\\\\")
    (GEN / "table_sk.tex").write_text("\n".join(sk_lines) + "\n")
    skr = [float(r["ratio_model_over_bound"]) for r in sk]
    skb = [float(r["bound_lda_average"]) for r in sk]

    # Lean decl counts
    decl = re.compile(r"^(theorem|lemma|noncomputable def|def|abbrev) ", re.M)
    ncount = {n: len(decl.findall((LEAN / n).read_text())) for n in ["Basic.lean", "NegativeControls.lean", "PositiveControls.lean"]}
    nlines = {n: len((LEAN / n).read_text().splitlines()) for n in ["Basic.lean", "NegativeControls.lean", "PositiveControls.lean", "Controls.lean"]}

    M: dict[str, str] = {}
    def put(k: str, v: str) -> None:
        M[k] = v
    put("PHKstar", f(ks, 5)); put("PHKstarLo", f(he["kstar_range_inv_A"][0], 4)); put("PHKstarHi", f(he["kstar_range_inv_A"][1], 4))
    put("PHTwoKstar", f(2 * ks, 3)); put("PHhbarc", f(he["hbar_c_meV_A"], 4)); put("PHhbarTwoM", f(he["hbar2_over_2m_meV_A2"], 5))
    vc = he["verdict_counts"]
    put("PHNPoints", str(he["n_points"])); put("PHNXray", str(he["n_xray"])); put("PHNNeutron", str(he["n_neutron"]))
    put("PHNCons", str(vc["CONSISTENT"])); put("PHNUnd", str(vc["UNDECIDED"])); put("PHNRef", str(vc["REFUTED"]))
    put("PHNRefXray", str(refx)); put("PHNRefNeutron", str(len(ref) - refx))
    put("PHDeltaDS", f(he["peak"]["delta_ds"], 3)); put("PHPeakX", f(he["peak"]["xray_max"], 3)); put("PHPeakXQ", f(he["peak"]["xray_at"], 3))
    put("PHPeakN", f(he["peak"]["neutron_max"], 3)); put("PHPeakNQ", f(he["peak"]["neutron_at"], 3))
    put("PHRmsSpline", f(he["peak"]["rms_resid_all"], 3))
    on = he["onset"]
    put("PHLastConsQ", f(on["last_consistent_below"]["Q"], 3)); put("PHLastConsS", f(on["last_consistent_below"]["S"], 3)); put("PHLastConsB", f(on["last_consistent_below"]["bound"], 3))
    put("PHFirstExQ", f(on["first_nominal_exceed"]["Q"], 3)); put("PHFirstExS", f(on["first_nominal_exceed"]["S"], 3)); put("PHFirstExB", f(on["first_nominal_exceed"]["bound"], 3))
    put("PHStrictLo", f(he["strict_refuted_runs_Q"][0][0], 3)); put("PHStrictHi", f(he["strict_refuted_runs_Q"][0][1], 3))
    put("PHNominalHi", f(he["nominal_exceed_runs_Q"][0][1], 2))
    rr = he["roton_region_1p7_2p4"]
    put("PHRotonN", str(rr["n"])); put("PHRotonRatioLo", f(rr["min_ratio"], 2)); put("PHRotonRatioHi", f(rr["max_ratio"], 2)); put("PHRotonMinMargin", f(rr["min_margin"], 3))
    put("PHPeakBound", f(peak["S_"] - peak["margin_"], 3)); put("PHPeakS", f(peak["S_"], 3)); put("PHPeakQ", f(peak["Q"], 3))
    c = he["controls"]
    put("PHCtlBogViol", str(c["positive_bogoliubov_homog"]["violations_nominal"])); put("PHCtlBogN", str(c["positive_bogoliubov_homog"]["n"]))
    put("PHCtlBogMax", f(c["positive_bogoliubov_homog"]["max_S_over_bound"], 7))
    pn = {d["sigma"]: d["frac_trials_with_REFUTED"] for d in c["positive_with_noise"]}
    put("PHFpOne", f"{pn[0.01]:g}"); put("PHFpTwo", f"{pn[0.02]:g}"); put("PHFpFour", f"{pn[0.04]:.2f}")
    put("PHCtlFreeNom", str(c["negative_free_S_equals_1"]["nominal_violations"])); put("PHCtlFreeStrict", str(c["negative_free_S_equals_1"]["strict_violations"]))
    put("PHCtlPlantNom", str(c["planted_1p5_times_Bogoliubov"]["nominal_violations"])); put("PHCtlPlantStrict", str(c["planted_1p5_times_Bogoliubov"]["strict_violations"]))
    pr = he["parse_report"]
    put("PHParseA", str(pr["len_A1"])); put("PHParseB", str(pr["len_A3"]))
    fc = he["feynman_check"]
    put("PHFeynN", str(fc["n"])); put("PHFeynExceed", str(fc["n_exceed"])); put("PHFeynQa", f(fc["exceed_Q"][0], 3)); put("PHFeynQb", f(fc["exceed_Q"][1], 3))
    # BEC
    cf = bec["convention_failures_of_trapped_model"]
    put("PBPeakFail", str(cf["bound_peak"])); put("PBMeanFail", str(cf["bound_mean_density"])); put("PBCeffFail", str(cf["bound_c_eff"]))
    put("PBLdaFail", str(cf["bound_lda_average"])); put("PBNCurve", str(cf["n_curve_points"]))
    put("PBSolidMax", f(max(abs(d["diff"]) for d in bec["solid_curve_control"]), 4))
    cfc = bec["lda_closed_form_check"]
    put("PBClosedA", f"{abs(cfc[0]['S_lda'] / cfc[0]['S_phonon_closed_form'] - 1):.1e}")
    put("PBClosedB", f"{abs(cfc[1]['S_lda'] / cfc[1]['S_phonon_closed_form'] - 1):.1e}")
    put("PBQ", f(bec["stamper_kurn_q_inv_um"], 3))
    bc = bec["controls"]
    put("PBGridViol", str(bc["lda_bogoliubov_violations"])); put("PBGridN", str(bc["grid_points"])); put("PBGridFree", str(bc["free_S1_exceeds_bound_count"]))
    put("PBSkRatioLo", f"{min(skr):.2f}"); put("PBSkRatioHi", f"{max(skr):.2f}")
    put("PBSkBoundLo", f"{min(skb):.2f}"); put("PBSkBoundHi", f"{max(skb):.2f}")
    sc = bec["steinhauer_closed_summary"]
    put("PBStN", str(sc["n"])); put("PBStNominal", str(sc["n_exceeds_bound_nominal"])); put("PBStOne", str(sc["n_exceeds_bound_1sigma"]))
    put("PBStRaw", str(sc["n_raw_exceeds"])); put("PBStMaxZ", f(sc["max_z"], 2))
    so = bec["steinhauer_open_vs_lda"]
    put("PBStOpenRms", f(so["rms_diff"], 3)); put("PBStOpenMax", f(so["max_abs_diff"], 3))
    # Lean
    put("PLNBasic", str(gate["Basic"]["declared"])); put("PLNNeg", str(gate["NegativeControls"]["declared"])); put("PLNPos", str(gate["PositiveControls"]["declared"]))
    put("PLGate", gate["GATE"])
    for tag, k in [("basic", "Basic"), ("negctl", "Neg"), ("posctl", "Pos"), ("controls", "Ctl")]:
        put(f"PLSec{k}", f"{comp[tag]['seconds']:.1f}"); put(f"PLRc{k}", str(comp[tag]["rc"]))
    for n, k in [("Basic.lean", "Basic"), ("NegativeControls.lean", "Neg"), ("PositiveControls.lean", "Pos"), ("Controls.lean", "Ctl")]:
        put(f"PLSha{k}", live[n]); put(f"PLShaShort{k}", live[n][:12]); put(f"PLLines{k}", str(nlines[n]))
    put("PLShaMatch", "match" if sha_match else "DO NOT match")
    put("PLRerun", "reproduced the same rc and axiom lines" if rerun_same else ("DIFFERED" if rerun_same is False else "was not run"))
    for tag, k in [("basic", "Basic"), ("negctl", "Neg"), ("posctl", "Pos"), ("controls", "Ctl")]:
        if tag in rer:
            put(f"PLReSec{k}", f"{rer[tag]['seconds']:.1f}"); put(f"PLReRc{k}", str(rer[tag]["rc"]))
        else:
            put(f"PLReSec{k}", "n/a"); put(f"PLReRc{k}", "n/a")
    # float cross-check
    put("PXPosOne", f"{num['POS-1_max_rel_residual']:.1e}"); put("PXPosTwo", f"{num['POS-2_max_rel_residual_A_eq_f_half']:.1e}")
    put("PXPosTrial", f"{num['POS-2_max_rel_residual_trial_energy']:.1e}"); put("PXSector", num["POS-2_sector_bound_holds"].replace("/", "\\slash "))
    put("PXPosBog", f"{num['POS-3_max_rel_resid_feynman_eq_epsB']:.1e}"); put("PXHeight", num["POS-3_H8_bound_holds"].replace("/", "\\slash "))
    put("PXNegMin", f"{num['NEG-2_rel_gap_A_minus_f_half_min_median'][0]:.4f}"); put("PXNegMed", f"{num['NEG-2_rel_gap_A_minus_f_half_min_median'][1]:.3f}")
    put("PXNegCaught", num["NEG-3_planted_A_eq_f_caught"].replace("/", "\\slash "))

    tc = HERE / "ledger/tier_counts.json"
    go = HERE / "ledger/gate_output.txt"
    if tc.exists() and go.exists():
        t = json.loads(tc.read_text()); g = go.read_text()
        put("PLedN", str(t["total"])); put("PLedA", str(t["A"])); put("PLedL", str(t["L"])); put("PLedC", str(t["C"])); put("PLedX", str(t["X"]))
        put("PGateExit", re.search(r"exit_code=(\d+)", g).group(1))
        put("PGateBlock", str(len(re.findall(r"^\s*block\s", g, re.M)))); put("PGateFlag", str(len(re.findall(r"^\s*flag\s", g, re.M))))
    out = ["% generated by gen_inputs.py -- do not edit"]
    for k, v in M.items():
        out.append(f"\\newcommand{{\\{k}}}{{{v}}}")
    (HERE / "gen_numbers.tex").write_text("\n".join(out) + "\n")
    summ = {"n_macros": len(M), "sha_match": sha_match, "rerun_same": rerun_same, "decl_counts": ncount, "n_xray": n_xr, "n_neutron": n_nu}
    (GEN / "summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
