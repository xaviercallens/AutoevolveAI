"""Generate every number, Lean listing, axiom transcript and table that main.tex prints (H1, bilayer dipolar excitons).

Inputs (read-only): data/*.json[l] (Stage 2 numerics, copied from the rusty-SUNDIALS worktree), the Lean sources in
formal_cert/Autoresearch/ and formal_cert/Triangular/, the compile transcripts in results/autoresearch/2026-10-25/H1/,
and the upstream definitions in the pinned openai/math checkout. Outputs (in this directory): gen_numbers.tex,
gen/*.lean (verbatim excerpts, proofs elided), gen/*.lst (same, non-ASCII escaped for listings), gen/axioms_*.txt
(verbatim #print axioms output), gen/table_*.tex.
Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I gen_inputs.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = HERE.parents[1]
DATA = HERE / "data"
GEN = HERE / "gen"
H1 = W / "results/autoresearch/2026-10-25/H1"
C1 = H1 / "contribution"
LEAN_PRIOR = W / "formal_cert/Autoresearch/DipolarExciton.lean"
LEAN_MULTI = W / "formal_cert/Autoresearch/DipolarExcitonMultipolar.lean"
LEAN_CTL = W / "formal_cert/Autoresearch/DipolarExcitonMultipolarControls.lean"
ANYD = W / "formal_cert/Triangular/AnyDensity.lean"
LEAN_STEP1 = W / "formal_cert/Autoresearch/DipolarExcitonStep1.lean"  # stage 5 (audit correction C8)
LEAN_STEP1_CTL = W / "formal_cert/Autoresearch/DipolarExcitonStep1Controls.lean"
UP = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/openai_math_pinned/lean/OAI/Analysis/Triangular/Energy")

# sha256 values recorded in contribution/FORMAL.md (stage 1); recomputed and compared below.
FORMAL_SHA = {
    "DipolarExciton.lean": "b85389a50373adaf877e866c79f0696ba0a284d9626bc9a56040821c3e11f27d",
    "DipolarExcitonMultipolar.lean": "7f52ea64903c43cbfe95b76eea74a2ea01040c45d778ae05bbb848aa9554f98a",
    "DipolarExcitonMultipolarControls.lean": "1754e1a9ba6ed844a1d0356872cf2a5662c89d13e85d1fd39747f3fe1215106d",
    "AnyDensity.lean": "0a6d86eef3ee24b2b6828ff602707868e160969bfbebc41db375c05b383c5168",
}
# sha256 of the stage-5 Step-1 module and its controls, recorded when compiled (contribution/compile_step1*.json)
STEP1_SHA = {
    "DipolarExcitonStep1.lean": "ceb2c607498086e8f865ebeee944842548345501d704a54b0dfc465cd9f42f7d",
    "DipolarExcitonStep1Controls.lean": "8a26b6ba14882ad6fc3e57cc69376786c30993695fc50846fc8a75add1ca4987",
}

UMAP = {
    "ℝ": r"$\mathbb{R}$", "→": r"$\to$", "∀": r"$\forall$", "≤": r"$\le$", "≥": r"$\ge$", "⊤": r"$\top$",
    "∈": r"$\in$", "²": r"$^2$", "⁻": r"$^{-}$", "¹": r"$^{1}$", "√": r"$\surd$", "ρ": r"$\rho$", "↦": r"$\mapsto$",
    "⟨": r"$\langle$", "⟩": r"$\rangle$", "¬": r"$\neg$", "∧": r"$\wedge$", "∞": r"$\infty$", "≠": r"$\ne$",
    "·": r"$\cdot$", "∑": r"$\sum$", "∩": r"$\cap$", "≥0∞": r"$_{\ge0}^{\infty}$", "𝓝": r"$\mathcal{N}$",
    "ℕ": r"$\mathbb{N}$", "‖": r"$\Vert$", "•": r"$\bullet$", "∃": r"$\exists$", "×": r"$\times$", "ℤ": r"$\mathbb{Z}$",
    "≥": r"$\ge$", "–": "--", "—": "---", "∫": r"$\int$", "π": r"$\pi$", "′": r"$'$",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def e(x: float, d: int = 1) -> str:
    """Scientific notation as LaTeX math (no $), mantissa with d decimals."""
    if x == 0:
        return "0"
    m, ex = f"{x:.{d}e}".split("e")
    return rf"{m}\times10^{{{int(ex)}}}"


def extract(src: list[str], name: str, kind: str) -> list[str]:
    pat = re.compile(rf"^(theorem|lemma|noncomputable def|def|abbrev) {re.escape(name)}\b")
    for i, line in enumerate(src):
        if pat.match(line):
            out: list[str] = []
            if kind == "def":
                for l in src[i:]:
                    if not l.strip():
                        break
                    out.append(l)
                return out
            for l in src[i:]:
                if ":=" in l:
                    out.append(l[: l.index(":=") + 2] + " -- proof elided")
                    return out
                out.append(l)
    raise SystemExit(f"declaration {name} not found")


def block(src: list[str], decls: list[tuple[str, str]]) -> str:
    lines: list[str] = []
    for name, kind in decls:
        lines += extract(src, name, kind) + [""]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    GEN.mkdir(exist_ok=True)
    prior = LEAN_PRIOR.read_text().splitlines()
    multi = LEAN_MULTI.read_text().splitlines()
    anyd = ANYD.read_text().splitlines()
    step1 = LEAN_STEP1.read_text().splitlines()
    basic = (UP / "Basic.lean").read_text().splitlines()
    univ = (UP / "Universal.lean").read_text().splitlines()

    texts = {
        "upstream": block(basic, [("AdmissiblePotential", "def"), ("diskEnergy", "def"), ("energy", "def"),
                                  ("latticeEnergy", "def")]) + "\n" + block(univ, [("universal_energy_minimum", "thm")])
        + "\n" + block(anyd, [("DensityRho", "def"), ("triangular_optimal_any_density", "thm")]),
        "defs": block(prior, [("g", "def"), ("h", "def")]) + "\n" + block(multi, [("shiftDiff", "def")]),
        "steps": block(prior, [("iteratedDeriv_rpow", "thm"), ("iteratedDeriv_shift", "thm"), ("iteratedDeriv_g", "thm"),
                               ("sign_desc", "thm"), ("diff_nonneg", "thm")]),
        "prior": block(prior, [("dipolar_admissible", "thm"), ("triangular_dipolar_optimal", "thm"), ("h_neg_at", "thm"),
                               ("h_not_admissible", "thm"), ("diff_le", "thm"), ("g_le", "thm"),
                               ("latticeEnergy_dipolar_lt_top", "thm")]),
        "multi": block(multi, [("shiftDiff_admissible", "thm"), ("admissible_const_mul", "thm"), ("g_eq_shiftDiff", "thm"),
                               ("dipolar_admissible_all", "thm"), ("shiftDiff_neg_of_neg", "thm"),
                               ("shiftDiff_not_admissible_of_neg", "thm"), ("triangular_shiftDiff_optimal", "thm")]),
        "density": block(multi, [("triangular_dipolar_optimal_any_density", "thm"), ("g_scaled_le", "thm"),
                                 ("latticeEnergy_dipolar_scaled_lt_top", "thm"), ("energy_dipolar_any_density_lt_top", "thm")]),
        "step1": block(step1, [("g_sqrt", "thm"), ("g_inplane", "thm"), ("g_inplane_pos", "thm")]),
        "controls": "\n".join(l for l in LEAN_CTL.read_text().splitlines() if l.startswith(("theorem", "axiom"))) + "\n",
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

    def axioms_file(src: Path, out: str) -> dict:
        j = json.loads(src.read_text())
        o = j["output"].replace(str(W) + "/", "")
        (GEN / out).write_text(f"rc = {j['rc']}, {j['seconds']} s\n" + o)
        return j

    prod = axioms_file(C1 / "compile_controls.json", "axioms_controls.txt")
    prior_ctl = axioms_file(H1 / "compile_controls.json", "axioms_prior_controls.txt")
    step1_ctl = axioms_file(C1 / "compile_step1_controls.json", "axioms_step1_controls.txt")
    step1_build = json.loads((C1 / "compile_step1.json").read_text())
    rec_status = "not completed before release (still owed)"
    rc_file = C1 / "recompile_controls_paper_stage.json"
    if rc_file.exists():
        j = axioms_file(rc_file, "axioms_recompile_controls.txt")
        same = j["output"].replace(str(W) + "/", "") == prod["output"].replace(str(W) + "/", "")
        rec_status = f"rc {j['rc']} in {j['seconds']} s, axiom output {'identical to' if same else 'DIFFERENT from'} stage 1"
    src_status = "not completed before release (still owed)"
    rs_file = C1 / "recompile_multipolar_paper_stage.json"
    if rs_file.exists():
        j = axioms_file(rs_file, "axioms_recompile_multipolar.txt")
        st1 = json.loads((C1 / "compile_attempt1.json").read_text())["output"]
        same = j["output"] == st1
        src_status = (f"rc {j['rc']} in {j['seconds']} s, axiom output {'identical to' if same else 'DIFFERENT from'} "
                      "the stage-1 compile") if j["rc"] == 0 else f"FAILED or timed out (rc {j['rc']}); still owed"

    shas = {"DipolarExciton.lean": sha(LEAN_PRIOR), "DipolarExcitonMultipolar.lean": sha(LEAN_MULTI),
            "DipolarExcitonMultipolarControls.lean": sha(LEAN_CTL), "AnyDensity.lean": sha(ANYD)}
    sha_ok = all(shas[k] == FORMAL_SHA[k] for k in shas)
    shas1 = {"DipolarExcitonStep1.lean": sha(LEAN_STEP1), "DipolarExcitonStep1Controls.lean": sha(LEAN_STEP1_CTL)}
    sha1_ok = all(shas1[k] == STEP1_SHA[k] for k in shas1)

    # ---- numerics ----
    s = json.loads((DATA / "summary.json").read_text())
    ic = json.loads((DATA / "independent_check.json").read_text())
    refs = [json.loads(l) for l in (DATA / "references.jsonl").read_text().splitlines() if l.strip()]
    grid = [json.loads(l) for l in (DATA / "lattice_gaps.jsonl").read_text().splitlines() if l.strip()]
    phys = json.loads((DATA / "physical_d.json").read_text())
    runs = s["runs"]
    ctl_rows = [r for r in runs if r["family"].startswith("control_")]
    pos = [r for r in ctl_rows if "ctl_pos" in r["family"]]
    comp = [r for r in runs if not r["family"].startswith("control_ctl_pos")]
    quench = [r for r in runs if r["family"] == "uniform"]
    anneal = [r for r in runs if r["family"] == "uniform_annealed"]
    incomm = [r for r in runs if r["family"] == "ctl_neg_incommensurate_box"]
    sqn = [r for r in runs if r["family"] == "control_ctl_neg_square_saddle"]
    at_lat = [r for r in comp if abs(r["rel_gap_exact"]) <= 1e-8]
    above = [r for r in comp if r["rel_gap_exact"] > 1e-8]
    undercut = [r for r in runs if r["rel_gap_exact"] < -1e-9]
    if len(comp) != len(quench) + len(anneal) + len(incomm) + len(sqn):
        raise SystemExit("competitor bookkeeping mismatch")
    sq_ctl = [c for c in s["controls"] if c["label"] == "ctl_neg_square_saddle"]
    m = re.search(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored",
                  (C1 / "rerun_cargo_test_paper_stage.txt").read_text())
    N: dict[str, str] = {
        "NComp": str(len(comp)), "NQuench": str(len(quench)), "NAnneal": str(len(anneal)), "NIncomm": str(len(incomm)),
        "NSqNoise": str(len(sqn)), "NPos": str(len(pos)), "NAtLattice": str(len(at_lat)), "NAbove": str(len(above)),
        "NUndercut": str(len(undercut)), "NOpen": str(len(quench) + len(anneal)),
        "NDesignedNeg": str(len(incomm) + len(sqn)),
        "QuenchLattice": str(sum(1 for r in quench if abs(r["rel_gap_exact"]) <= 1e-8)),
        "QuenchDefected": str(sum(1 for r in quench if r["defects"] > 0)),
        "AnnealLattice": str(sum(1 for r in anneal if abs(r["rel_gap_exact"]) <= 1e-8)),
        "MinRelComp": e(min(r["rel_gap_exact"] for r in comp)),
        "MinRelAll": e(min(r["rel_gap_exact"] for r in runs)),
        "MaxAbsPos": e(max(abs(r["rel_gap_exact"]) for r in pos)),
        "MinAbove": e(min(r["rel_gap_exact"] for r in above), 2),
        "MaxSfDiff": e(max(abs(r["gap_exact"] - r["gap_sf"]) for r in comp)),
        "SqNoiseMin": e(min(r["rel_gap_exact"] for r in sqn), 2), "SqNoiseMax": e(max(r["rel_gap_exact"] for r in sqn), 2),
        "SqNegMin": str(min(c["hess_negative"] for c in sq_ctl)), "SqNegMax": str(max(c["hess_negative"] for c in sq_ctl)),
        "IcEwaldTri": e(max(abs(x["rel_diff_ewald_tri"]) for x in ic)),
        "IcEwaldSq": e(max(abs(x["rel_diff_ewald_square"]) for x in ic)),
        "IcDirect": e(max(max(x["max_abs_diff_direct_tri"], x["max_abs_diff_direct_square"]) for x in ic)),
        "IcNegCtl": e(min(x["neg_ctl_abs_diff"] for x in ic), 2),
        "EtaGrid": e(s["eta_independence_lattice_grid_max_rel"]),
        "EtaRefs": e(max(max(abs(r["e_tri_exact_eta0.6"] - r["e_tri_exact"]), abs(r["e_tri_exact_eta1.2"] - r["e_tri_exact"])) / r["e_tri_exact"] for r in refs)),
        "BoxCell": e(max(abs(r["e_tri_exact_box288"] - r["e_tri_exact"]) / r["e_tri_exact"] for r in refs)),
        "GridN": str(len(grid)), "GridDmin": f"{grid[0]['d']:g}", "GridDmax": f"{grid[-1]['d']:g}",
        "SqRelLo": e(grid[0]["rel_gap_square"], 2), "SqRelHi": e(grid[-1]["rel_gap_square"], 2),
        "HcRelLo": e(grid[0]["rel_gap_honeycomb"], 2), "HcRelHi": e(grid[-1]["rel_gap_honeycomb"], 2),
        "EtriSmallD": f"{grid[0]['e_tri']:.4f}",
        "DproxyA": f"{phys['MoSe2_WSe2_proxy_d_A']:.3f}",
        "DMoSe": f"{phys['homo_stacks']['MoSe2']['d_mean_A']:.4f}", "DWSe": f"{phys['homo_stacks']['WSe2']['d_mean_A']:.4f}",
        "DMoS": f"{phys['homo_stacks']['MoS2']['d_mean_A']:.4f}",
        "DtElev": f"{phys['d_tilde']['1e+11']:.4f}", "DtTwelve": f"{phys['d_tilde']['1e+12']:.4f}",
        "DtThreeTwelve": f"{phys['d_tilde']['3e+12']:.4f}",
        "TestsPassed": m.group(1) if m else "?", "TestsFailed": m.group(2) if m else "?", "TestsIgnored": m.group(3) if m else "?",
        "RecompileCtl": rec_status, "RecompileSrc": src_status,
        "ShaPrior": shas["DipolarExciton.lean"], "ShaMulti": shas["DipolarExcitonMultipolar.lean"],
        "ShaCtl": shas["DipolarExcitonMultipolarControls.lean"], "ShaAnyD": shas["AnyDensity.lean"],
        "ShaMatch": "match" if sha_ok else "DO NOT match",
        "ShaStepOne": shas1["DipolarExcitonStep1.lean"], "ShaStepOneCtl": shas1["DipolarExcitonStep1Controls.lean"],
        "ShaStepOneMatch": "match" if sha1_ok else "DO NOT match",
        "StepOneBuild": f"rc {step1_build['rc']} in {step1_build['seconds']} s",
        "StepOneCtl": f"rc {step1_ctl['rc']} in {step1_ctl['seconds']} s",
    }
    led = HERE / "ledger/ledger.json"
    gate = HERE / "ledger/gate_output.txt"
    if led.exists():
        cl = json.loads(led.read_text())["claims"]
        N["LedgerN"] = str(len(cl))
        for t in "ALCX":
            N[f"Ledger{t}"] = str(sum(1 for c in cl if c["tier"] == t))
    if gate.exists():
        gt = gate.read_text()
        N["GateExit"] = re.search(r"exit_code=(-?\d+)", gt).group(1)
        N["GateBlock"] = str(len(re.findall(r"^\s+block\s", gt, re.M)))
        N["GateFlag"] = str(len(re.findall(r"^\s+flag\s", gt, re.M)))
    pm = s["physical_square_minus_tri_meV_eps1"]
    for key, tag in [("1e+11", "Elev"), ("1e+12", "Twelve"), ("3e+12", "ThreeTwelve")]:
        N[f"meV{tag}"] = f"{pm[key]['meV']:.4f}" if pm[key]["meV"] < 0.01 else f"{pm[key]['meV']:.3f}"

    rows = []
    for r in refs:
        rows.append(f"{r['d']:g} & {r['e_tri_exact']:.12f} & {r['square_minus_tri_exact']:.4e} & "
                    f"{r['honeycomb_minus_tri_exact']:.4e} & {r['square_minus_tri_exact'] / r['e_tri_exact']:.3e} \\\\")
    (GEN / "table_lattice.tex").write_text("\n".join(rows).replace("e-0", "e$-$0").replace("e-", "e$-$") + "\n")

    def fmt_rel(x: float) -> str:
        return f"${e(x)}$" if abs(x) > 0 else "0"
    rrows = []
    for r in sorted(comp, key=lambda r: (r["d"], r["family"], r["label"])):
        fam = {"uniform": "quench", "uniform_annealed": "anneal", "ctl_neg_incommensurate_box": "incomm. box (neg.)",
               "control_ctl_neg_square_saddle": "square+noise (neg.)"}[r["family"]]
        hn = "--" if r.get("hess_negative") is None else str(r["hess_negative"])
        rrows.append(f"{r['d']:g} & {r['label'].replace('_', chr(92) + '_')} & {fam} & {fmt_rel(r['rel_gap_exact'])} & "
                     f"{r['defects']} & {hn} \\\\")
    (GEN / "table_runs.tex").write_text("\n".join(rrows) + "\n")

    hrows = []
    for mat in ["MoSe2", "WSe2", "MoS2"]:
        hs = phys["homo_stacks"][mat]
        ids = ", ".join(n for row in hs["rows"] for n in row["names"] if n.startswith("jdft_3d-12-12-2022"))
        hrows.append(f"{mat.replace('2', '$_2$')} & \\texttt{{{ids.replace('_', chr(92) + '_')}}} & {hs['n_spacings']} & "
                     f"{hs['d_mean_A']:.4f} & {hs['d_min_A']:.4f}--{hs['d_max_A']:.4f} \\\\")
    (GEN / "table_hf.tex").write_text("\n".join(hrows) + "\n")

    with (HERE / "gen_numbers.tex").open("w") as fh:
        fh.write("% generated by gen_inputs.py; do not edit\n")
        for k, v in N.items():
            fh.write(f"\\newcommand{{\\DX{k}}}{{{v}}}\n")
    print(json.dumps({"macros": len(N), "nonascii": "".join(sorted(used)), "sha_match": sha_ok,
                      "recompile_controls": rec_status, "recompile_source": src_status,
                      "competitors": len(comp), "undercuts": len(undercut), "tests": N["TestsPassed"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
