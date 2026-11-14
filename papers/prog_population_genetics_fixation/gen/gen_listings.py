"""Generate verbatim Lean listings (statements only, proofs elided), axiom transcripts and the source-hash table.

Everything printed in main.tex that comes from Lean is produced here from the hashed files in
formal_cert/Programmes/PopGen/ and the compile transcripts in results/programmes/2026-10-25/P7/.
Outputs (this directory): <key>.lean (UTF-8 excerpt), <key>.lst (non-ASCII escaped for `listings`),
axioms_<name>.txt (verbatim #print axioms transcript), table_sources.tex (file, module, sha256, rc, axiom lines).
Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I gen_listings.py
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = HERE.parents[2]
LEAN = W / "formal_cert/Programmes/PopGen"
P7 = W / "results/programmes/2026-10-25/P7"
PS = P7 / "paper_stage"

UMAP = {
    "ℝ": r"$\mathbb{R}$", "ℕ": r"$\mathbb{N}$", "ℚ": r"$\mathbb{Q}$", "→": r"$\to$", "∀": r"$\forall$", "∃": r"$\exists$",
    "≤": r"$\le$", "≥": r"$\ge$", "≠": r"$\ne$", "∈": r"$\in$", "∑": r"$\sum$", "⁻": r"$^{-}$", "¹": r"$^{1}$",
    "²": r"$^2$", "·": r"$\cdot$", "𝓝": r"$\mathcal{N}$", "⟨": r"$\langle$", "⟩": r"$\rangle$", "¬": r"$\neg$",
    "∧": r"$\wedge$", "∨": r"$\vee$", "↑": r"$\uparrow$", "ε": r"$\varepsilon$", "ₙ": r"$_n$", "₁": r"$_1$", "₂": r"$_2$",
    "w̄": r"$\bar w$", "̄": "", "≈": r"$\approx$", "∞": r"$\infty$", "ρ": r"$\rho$", "ι": r"$\iota$", "′": r"$'$",
    "⊢": r"$\vdash$", "↔": r"$\leftrightarrow$", "∣": r"$\mid$", "∑": r"$\sum$", "∏": r"$\prod$", "λ": r"$\lambda$",
    "₀": r"$_0$", "ᵢ": r"$_i$", "ⱼ": r"$_j$", "ₖ": r"$_k$", "ℓ": r"$\ell$", "−": "-", "×": r"$\times$", "⁺": r"$^{+}$",
    "∘": r"$\circ$", "▸": r"$\triangleright$", "≃": r"$\simeq$", "⊆": r"$\subseteq$", "∪": r"$\cup$", "∩": r"$\cap$",
    "∖": r"$\setminus$", "⁰": r"$^0$", "³": r"$^3$", "π": r"$\pi$", "μ": r"$\mu$", "σ": r"$\sigma$", "φ": r"$\varphi$",
    "δ": r"$\delta$", "κ": r"$\kappa$", "ν": r"$\nu$", "β": r"$\beta$", "α": r"$\alpha$", "γ": r"$\gamma$",
    "θ": r"$\theta$", "ω": r"$\omega$", "—": "---", "–": "--", "≡": r"$\equiv$", "∅": r"$\emptyset$", "⊤": r"$\top$",
    "⊥": r"$\bot$", "↦": r"$\mapsto$", "…": "...", "⁴": r"$^4$", "∂": r"$\partial$", "√": r"$\surd$", "‖": r"$\Vert$",
    "ᶜ": r"$^c$", "ᵀ": r"$^T$", "⌊": r"$\lfloor$", "⌋": r"$\rfloor$", "⌈": r"$\lceil$", "⌉": r"$\rceil$",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def extract(src: list[str], name: str, kind: str) -> list[str]:
    pat = re.compile(rf"^\s*(theorem|lemma|noncomputable def|def|abbrev|structure) {re.escape(name)}\b")
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


def _ns_body(src: list[str]) -> list[str]:
    """Lines strictly between the `namespace` line and the matching `end` line, blank lines at the edges removed."""
    start = next(i for i, l in enumerate(src) if l.startswith("namespace "))
    end = next(i for i, l in enumerate(src) if l.startswith("end ") and i > start)
    body = src[start + 1 : end]
    while body and not body[0].strip():
        body = body[1:]
    while body and not body[-1].strip():
        body = body[:-1]
    return body


def main() -> int:
    A = (LEAN / "Absorption.lean").read_text().splitlines()
    WF = (LEAN / "WrightFisherFixation.lean").read_text().splitlines()
    MM = (LEAN / "MoranModel.lean").read_text().splitlines()
    MF = (LEAN / "MoranFixation.lean").read_text().splitlines()
    PR = (LEAN / "Price.lean").read_text().splitlines()
    DC = (LEAN / "FixationDataCert.lean").read_text().splitlines()
    texts = {
        "abs_defs": block(A, [("kPow", "def"), ("AbsorbingChain", "def"), ("InteriorHarmonic", "def")]),
        "abs_thms": block(A, [("kPow_harmonic", "thm"), ("second_moment", "thm"), ("interiorMass_tendsto_zero", "thm"),
                              ("absorption_tendsto", "thm"), ("fixation_limit", "thm"), ("harmonic_unique_of_var", "thm")]),
        "wf": block(WF, [("wf_var_pos", "thm"), ("wright_fisher_fixation_limit", "thm")]),
        "moran_defs": block(MM, [("bdP", "def"), ("moranUp", "def"), ("moranDown", "def"), ("moranP", "def"),
                                 ("geomS", "def"), ("moranFix", "def")]),
        "moran_lemmas": block(MM, [("moranFix_harmonic_nat", "thm"), ("moran_var_pos_nat", "thm"), ("moranFix_closed", "thm"),
                                   ("moranFix_neutral", "thm"), ("moran_closed_tendsto_neutral", "thm")]),
        "moran_thms": block(MF, [("moran_fixation_limit", "thm"), ("moran_fixation_limit_closed", "thm"),
                                 ("moran_fixation_limit_neutral", "thm"), ("moran_fixation_unique", "thm")]),
        "neg_ctl": block(A, [("ctl_neg_identity_no_absorption", "thm")]) + "\n"
        + block(MM, [("ctl_neg_flipped_value", "thm"), ("ctl_neg_flipped_not_harmonic", "thm"), ("ctl_neg_neutral_not_harmonic", "thm")])
        + "\n" + block(MF, [("ctl_neg_wrong_limits", "thm")]),
        "price_defs": block(PR, [("wmean", "def"), ("wcov", "def"), ("wvar", "def"), ("zbarNext", "def"), ("wbarNext", "def")]),
        "price_thms": block(PR, [("price_equation", "thm"), ("wcov_eq_moment", "thm"), ("fisher_haploid", "thm"),
                                 ("fisher_haploid_div", "thm"), ("fisher_haploid_nondecreasing", "thm"),
                                 ("price_equation_pos", "thm")]),
        "price_ctl": block(PR, [("ctl_pos_three_types", "thm"), ("ctl_neg_transmission_bias", "thm"), ("ctl_neg_missing_wbar", "thm")]),
        "alix": block(PR, [("meanFit", "def"), ("selectP", "def"), ("aurelia_mean_fitness_increment", "thm"),
                           ("kal_increment_is_variance", "thm")]),
        "datacert": block(DC, [("cert_N3_r2_i1", "thm"), ("cert_N10_r1p5_i1", "thm"), ("ctl_neg_wrong_literal", "thm")]),
        "controls": "\n".join(_ns_body((LEAN / "PopGenProgControls.lean").read_text().splitlines())) + "\n",
    }
    used: set[str] = set()
    for key, txt in texts.items():
        (HERE / f"{key}.lean").write_text(txt)
        used |= {c for c in txt if ord(c) > 127}
    missing = sorted(c for c in used if c not in UMAP)
    if missing:
        raise SystemExit(f"unmapped codepoints: {[hex(ord(c)) + ' ' + c for c in missing]}")
    for key, txt in texts.items():
        t = txt
        for c in sorted(used, key=len, reverse=True):
            t = t.replace(c, "(*@" + UMAP[c] + "@*)")
        (HERE / f"{key}.lst").write_text(t)

    # axiom transcripts (verbatim, repo prefix stripped)
    def dump(src: Path, out: str) -> None:
        j = json.loads(src.read_text())
        o = j["output"].replace(str(W) + "/", "")
        (HERE / out).write_text(f"rc = {j['rc']}, {j['seconds']} s\n" + o)

    dump(P7 / "compile_controls.json", "axioms_controls_fix.txt")
    dump(P7 / "compile_price_controls.json", "axioms_controls_price.txt")
    dump(P7 / "compile_FixationDataCertControls.json", "axioms_controls_cert.txt")
    dump(P7 / "compile_FixationDataCert.json", "axioms_datacert.txt")
    dump(P7 / "compile_MoranFixation.json", "axioms_moranfix.txt")

    # source table
    rows = []
    mods = [("Absorption", "Programmes.PopGen.Absorption"), ("WrightFisherFixation", "Programmes.PopGen.WrightFisherFixation"),
            ("MoranModel", "Programmes.PopGen.MoranModel"), ("MoranFixation", "Programmes.PopGen.MoranFixation"),
            ("Price", "Programmes.PopGen.Price"), ("FixationDataCert", "check only"), ("PopGenProgImportAll", "check only"),
            ("PriceImportAll", "check only"), ("PopGenProgControls", "planted, not imported"),
            ("PriceControls", "planted, not imported"), ("FixationDataCertControls", "planted, not imported")]
    summ = json.loads((PS / "summary.json").read_text())
    for f, m in mods:
        p = LEAN / f"{f}.lean"
        s = summ[f]
        assert s["sha256"] == sha(p), f
        mshort = m.replace("Programmes.PopGen.", "").replace("_", chr(92) + "_")
        rows.append(f"\\texttt{{{f}.lean}} & {mshort} & \\texttt{{{sha(p)[:16]}}} & {s['rc']} & {s['axiom_lines']} \\\\")
    (HERE / "table_sources.tex").write_text(
        "\\begin{tabular}{llrrr}\n\\toprule\nfile & role & sha256 (first 16) & rc & axiom lines\\\\\n\\midrule\n"
        + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    print("ok", {k: len(v.splitlines()) for k, v in texts.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
