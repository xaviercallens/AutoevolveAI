"""Generate every number, Lean listing and axiom transcript that main.tex prints.

Inputs (read-only): data/*.json (Stage 2 numerics), the Lean sources in formal_cert/Autoresearch/, the compile
transcripts in results/autoresearch/2026-10-25/H3/contribution/, and the upstream definitions in the pinned openai/math
checkout. Outputs (in this directory): gen_numbers.tex, gen/*.lean (verbatim excerpts, proofs elided), gen/*.txt
(verbatim axiom output), gen/lean_literate.tex (listings mapping for every non-ASCII codepoint that occurs).
Run: .venv/bin/python -I gen_inputs.py
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
CONTRIB = W / "results/autoresearch/2026-10-25/H3/contribution"
LEAN = W / "formal_cert/Autoresearch/KeldyshCM.lean"
CTL = W / "formal_cert/Autoresearch/KeldyshCMControls.lean"
YUK = W / "formal_cert/Autoresearch/Yukawa.lean"
UP = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/openai_math_pinned/lean/OAI/Analysis/Triangular/Energy")

# listings cannot read multibyte UTF-8 under pdflatex: map every codepoint we print to LaTeX.
UMAP = {
    "ℝ": r"$\mathbb{R}$", "→": r"$\to$", "←": r"$\leftarrow$", "∀": r"$\forall$", "ᵐ": r"$^{\mathrm{m}}$",
    "∂": r"$\partial$", "≤": r"$\le$", "≥": r"$\ge$", "⊤": r"$\top$", "∫": r"$\int$", "∈": r"$\in$",
    "₀": r"$_0$", "²": r"$^2$", "⁻": r"$^{-}$", "√": r"$\surd$", "π": r"$\pi$", "ε": r"$\varepsilon$",
    "μ": r"$\mu$", "α": r"$\alpha$", "↦": r"$\mapsto$", "⟨": r"$\langle$", "⟩": r"$\rangle$", "¬": r"$\neg$",
    "∧": r"$\wedge$", "∞": r"$\infty$", "≠": r"$\ne$", "·": r"$\cdot$", "∃": r"$\exists$", "∑": r"$\sum$",
    "∩": r"$\cap$", "≥0∞": r"$_{\ge0}^{\infty}$", "𝓝": r"$\mathcal{N}$", "ᶠ": r"$^{f}$", "′": r"$'$",
    "–": "--", "ℕ": r"$\mathbb{N}$", "‖": r"$\Vert$", "⁻¹": r"$^{-1}$", "ω": r"$\omega$", "∘": r"$\circ$", "×": r"$\times$",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def e(x: float, d: int = 1) -> str:
    """Scientific notation as LaTeX math, mantissa with d decimals."""
    if x == 0:
        return "0"
    s = f"{x:.{d}e}"
    m, ex = s.split("e")
    return rf"{m}\times10^{{{int(ex)}}}"


def extract(src: list[str], name: str, kind: str) -> list[str]:
    pat = re.compile(rf"^(theorem|lemma|noncomputable def|def|structure) {re.escape(name)}\b")
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


def main() -> int:
    GEN.mkdir(exist_ok=True)
    a = json.loads((DATA / "analysis.json").read_text())
    src = LEAN.read_text().splitlines()
    ups = (UP / "Basic.lean").read_text().splitlines()
    upu = (UP / "Universal.lean").read_text().splitlines()

    blocks = {
        "defs": [("MixtureData", "def"), ("erfcx", "def"), ("w", "def"), ("keldysh", "def"), ("keldyshReg", "def"),
                 ("signedMix", "def")],
        "generic": [("laplace_admissible", "thm"), ("laplace_iteratedDeriv", "thm"), ("expNeg_admissible", "thm"),
                    ("signedMix_not_admissible", "thm")],
        "keldysh": [("erfcx_le_one", "thm"), ("erfcx_le_inv", "thm"), ("w_le", "thm"), ("w_le_sqrt", "thm"),
                    ("keldysh_integrable", "thm"), ("hasDerivAt_G", "thm"), ("G_sign", "thm"),
                    ("keldysh_admissible", "thm"), ("keldysh_pos", "thm")],
        "corollaries": [("triangular_keldysh_optimal", "thm"), ("keldyshReg_admissible", "thm"),
                        ("triangular_keldyshReg_optimal", "thm")],
    }
    used: set[str] = set()
    for key, decls in blocks.items():
        lines: list[str] = []
        for name, kind in decls:
            lines += extract(src, name, kind) + [""]
        txt = "\n".join(lines).rstrip() + "\n"
        used |= {c for c in txt if ord(c) > 127}
        (GEN / f"{key}.lean").write_text(txt)
    up_lines = extract(ups, "AdmissiblePotential", "def") + [""] + extract(upu, "universal_energy_minimum", "thm")
    up_txt = "\n".join(up_lines) + "\n"
    used |= {c for c in up_txt if ord(c) > 127}
    (GEN / "upstream.lean").write_text(up_txt)
    ctl_txt = "\n".join(l for l in CTL.read_text().splitlines() if l.startswith(("theorem", "axiom"))) + "\n"
    used |= {c for c in ctl_txt if ord(c) > 127}
    (GEN / "controls.lean").write_text(ctl_txt)

    missing = sorted(c for c in used if c not in UMAP)
    if missing:
        raise SystemExit(f"unmapped codepoints: {[hex(ord(c)) + ' ' + c for c in missing]}")
    # pdflatex listings cannot take 3-byte UTF-8 keys: write .lst copies in which each non-ASCII codepoint becomes
    # an escape (*@<LaTeX>@*). The .lean files beside them stay byte-for-byte verbatim.
    for f in sorted(GEN.glob("*.lean")):
        t = f.read_text()
        for c in used:
            t = t.replace(c, "(*@" + UMAP[c] + "@*)")
        f.with_suffix(".lst").write_text(t)
    (GEN / "lean_literate.tex").write_text("% codepoints escaped in gen/*.lst: " + " ".join(
        f"U+{ord(c):04X}" for c in sorted(used)) + "\n")

    for jname, out in [("compile_keldysh.json", "axioms_producer.txt"), ("compile_controls.json", "axioms_controls.txt")]:
        j = json.loads((CONTRIB / jname).read_text())
        o = j["output"].replace(str(W) + "/", "")
        (GEN / out).write_text(f"rc = {j['rc']}, {j['seconds']} s\n" + o)
    rec = CONTRIB / "recompile_paper_stage.json"
    rec_ok = "not completed before release (still owed)"
    if rec.exists():
        j = json.loads(rec.read_text())
        prod = json.loads((CONTRIB / "compile_keldysh.json").read_text())["output"]
        if j["rc"] == -9:
            rec_ok = "timed out (IO-starved disk); still owed"
        elif j["rc"] == 0 and j["output"] == prod:
            rec_ok = f"rc 0 in {j['seconds']} s, axiom output identical to the producer's"
        else:
            rec_ok = f"DIFFERENT (rc {j['rc']}); see recompile\\_paper\\_stage.json"
        (GEN / "axioms_recompile.txt").write_text(f"rc = {j['rc']}, {j['seconds']} s\n" + j["output"])

    rr = json.loads((CONTRIB / "rerun_cargo.json").read_text())
    m = re.search(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored", rr["test"]["stdout_tail"])
    scan_same = json.loads((CONTRIB / "rerun_scan.json").read_text()) == json.loads((DATA / "scan.json").read_text())

    cp = a["coulomb_positive_control"]
    lg = a["log_gas_limit"]
    mats = a["materials"]
    i12 = mats["MoS2"]["n_cm2"].index(1e12)
    i11 = mats["MoS2"]["n_cm2"].index(1e11)
    scan = json.loads((DATA / "scan.json").read_text())
    coul = scan["coulomb"]
    N: dict[str, str] = {
        "VdlmfErr": e(a["rust_vs_mpmath_V_max_rel_err"]["dlmf"]),
        "VmixErr": e(a["rust_vs_mpmath_V_max_rel_err"]["mixture"]),
        "Vnpts": str(a["rust_vs_mpmath_V_max_rel_err"]["n_points"]),
        "KernelErr": e(a["kernel_identity_max_rel_err"]),
        "BoxDiff": e(cp["lattice_tri_minus_jellium_rs_box"]),
        "LitTri": e(abs(cp["lattice_tri_minus_literature"])),
        "LitSq": e(abs(cp["lattice_sq_minus_literature"])),
        "dEnine": e(cp["r0_1e-9_dE_tri"], 2),
        "SlopeEight": f"{cp['slope_over_pi_at_r0']['1e-08']:.8f}",
        "SlopeTwo": f"{cp['slope_over_pi_at_r0']['1e-02']:.5f}",
        "AlphaSpread": e(a["alpha_independence_max_rel_spread"]),
        "NegSign": e(a["neg_wrong_sign_recip_min_rel_spread"]),
        "NegBg": f"{a['neg_no_background_min_rel_spread']:.3f}",
        "WrongKernelE": f"{a['neg_wrong_sign_kernel']['E']:+.4f}",
        "ScalingErr": e(a["scaling_n4"]["rel_diff"]),
        "LogGas": f"{lg['eta_formula_W_sq_minus_W_tri']:.10f}",
        "LogGasDevTwo": e(lg["r0_times_gap"][0][2]),
        "LogGasDevSix": e(lg["r0_times_gap"][-1][2]),
        "MinGap": e(a["min_gap_over_scan"], 2),
        "NScan": str(len(scan["scan"])),
        "AllGapsPos": "yes" if a["all_gaps_positive"] else "NO",
        "EtriC": f"{coul['lattice_r0_0_tri']:.10f}",
        "EsqC": f"{coul['lattice_r0_0_sq']:.10f}",
        "GapC": f"{coul['lattice_r0_0_sq'] - coul['lattice_r0_0_tri']:.4e}".replace("e-02", r"\times10^{-2}"),
        "TestsPassed": m.group(1) if m else "?", "TestsFailed": m.group(2) if m else "?",
        "TestsIgnored": m.group(3) if m else "?",
        "ScanSame": "bit-identical" if scan_same else "DIFFERENT",
        "RecompileStatus": rec_ok,
        "ShaKeldysh": sha(LEAN), "ShaControls": sha(CTL), "ShaYukawa": sha(YUK),
    }
    re_chk = json.loads((CONTRIB / "route_e_check.json").read_text())
    N["RouteEPosErr"] = e(re_chk["positive_max_rel_err"])
    N["RouteENegInner"] = f"{re_chk['negative_min_rel_err_inner_perturbed']:.2f}"
    N["RouteENegSub"] = f"{re_chk['negative_min_rel_err_subordination_power']:.2f}"
    rows = []
    for mat in ["MoS2", "MoSe2", "WS2", "WSe2", "MoS2 (GW chi)"]:
        d = mats[mat]
        lab = mat.replace("2", "$_2$").replace(" (GW chi)", r" (GW $\chi_{2D}$)")
        rows.append(f"{lab} & {d['r0_A']:.2f} & {d['r0_sqrt_n'][i12]:.3f} & {d['E_tri_meV'][i12]:.2f} & "
                    f"{d['E_coulomb_tri_meV'][i12]:.2f} & {d['gap_sq_minus_tri_meV'][i12]:.3f} \\\\")
    (GEN / "table_materials.tex").write_text("\n".join(rows) + "\n")
    N["MoSElevenTri"] = f"{mats['MoS2']['E_tri_meV'][i11]:.2f}"
    N["MoSElevenGap"] = f"{mats['MoS2']['gap_sq_minus_tri_meV'][i11]:.3f}"
    hrows = []
    for r in sorted(a["hf_2h_rows"], key=lambda r: ["MoS2", "MoSe2", "WS2", "WSe2"].index(r["material"])):
        mname = r["material"].replace("2", "$_2$")
        rowid = r["c2db_name"][0].replace("_", r"\_")
        hrows.append(f"{mname} & \\texttt{{{rowid}}} & "
                     f"{r['a_pbe_A']:.3f} & {r['a_table2_A']:.2f} & {r['band_gap_pbe_eV']:.3f} \\\\")
    (GEN / "table_hf.tex").write_text("\n".join(hrows) + "\n")
    lg_rows = [f"$10^{{{int(round(__import__('math').log10(r0)))}}}$ & {g:.10f} & ${e(dev)}$ \\\\"
               for r0, g, dev in lg["r0_times_gap"]]
    (GEN / "table_loggas.tex").write_text("\n".join(lg_rows) + "\n")
    with (HERE / "gen_numbers.tex").open("w") as fh:
        fh.write("% generated by gen_inputs.py; do not edit\n")
        for k, v in N.items():
            fh.write(f"\\newcommand{{\\KT{k}}}{{{v}}}\n")
    print(json.dumps({"macros": len(N), "nonascii": "".join(sorted(used)), "recompile": rec_ok,
                      "tests": N["TestsPassed"], "scan": N["ScanSame"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
