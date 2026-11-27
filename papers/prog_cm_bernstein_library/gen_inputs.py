"""Generate every number, Lean listing, axiom transcript, table and figure that main.tex prints (programme P3).

Inputs (read-only): the Lean sources in formal_cert/Programmes/CompletelyMonotone/, the compile logs and gate.json in
results/programmes/2026-10-25/P3/, the P3 numerics in results/programmes/2026-10-25/P3/applications/, the paper-stage
recompiles in ledger/recompile/. Outputs (in this directory): gen_numbers.tex, gen/*.lean + gen/*.lst (verbatim
excerpts), gen/axioms_*.txt (verbatim #print axioms output), gen/table_*.tex, fig_*.pdf/png, data/*.
Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I gen_inputs.py
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
W = HERE.parents[1]
GEN = HERE / "gen"
DATA = HERE / "data"
P3 = W / "results/programmes/2026-10-25/P3"
LOGS = P3 / "compile_logs"
APP = P3 / "applications"
SRC = W / "formal_cert/Programmes/CompletelyMonotone"
REC = HERE / "ledger/recompile"
MATHLIB = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/openai_math_pinned/lean/.lake/packages/mathlib")

UMAP = {
    "ℝ": r"$\mathbb{R}$", "→": r"$\to$", "∀": r"$\forall$", "≤": r"$\le$", "≥": r"$\ge$", "⊤": r"$\top$",
    "∈": r"$\in$", "²": r"$^2$", "⁻": r"$^{-}$", "¹": r"$^{1}$", "√": r"$\surd$", "ρ": r"$\rho$", "↦": r"$\mapsto$",
    "⟨": r"$\langle$", "⟩": r"$\rangle$", "¬": r"$\neg$", "∧": r"$\wedge$", "∞": r"$\infty$", "≠": r"$\ne$",
    "·": r"$\cdot$", "∑": r"$\sum$", "∩": r"$\cap$", "ℕ": r"$\mathbb{N}$", "‖": r"$\Vert$", "∃": r"$\exists$",
    "×": r"$\times$", "ℤ": r"$\mathbb{Z}$", "–": "--", "—": "---", "∫": r"$\int$", "π": r"$\pi$", "′": r"$'$",
    "κ": r"$\kappa$", "α": r"$\alpha$", "ψ": r"$\psi$", "ε": r"$\varepsilon$", "μ": r"$\mu$", "∂": r"$\partial$",
    "ι": r"$\iota$", "↔": r"$\leftrightarrow$", "λ": r"$\lambda$", "ᵐ": r"$^{m}$", "∘": r"$\circ$", "⁺": r"$^{+}$",
    "⊆": r"$\subseteq$", "∪": r"$\cup$", "∅": r"$\emptyset$", "⁰": r"$^{0}$", "⦃": r"$\{\!|$", "⦄": r"$|\!\}$",
    "←": r"$\leftarrow$", "✝": "", "⋯": r"$\cdots$", "≡": r"$\equiv$", "∣": r"$|$", "∉": r"$\notin$", "𝓝": r"$\mathcal{N}$",
    "Σ": r"$\Sigma$", "Δ": r"$\Delta$", "β": r"$\beta$", "γ": r"$\gamma$", "δ": r"$\delta$", "∨": r"$\vee$",
    "′": r"$'$", "ₖ": r"$_k$", "ᵢ": r"$_i$", "ₙ": r"$_n$", "₀": r"$_0$", "₁": r"$_1$", "₂": r"$_2$",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def e(x: float, d: int = 1) -> str:
    if x == 0:
        return "0"
    m, ex = f"{x:.{d}e}".split("e")
    return rf"{m}\times10^{{{int(ex)}}}"


def tfmt(v: float) -> str:
    """t value as LaTeX math: 3.16, 10, $10^{4}$."""
    ex = int(np.floor(np.log10(v) + 1e-9))
    if abs(v - 10.0 ** ex) < 1e-9 * v and (ex < 0 or ex > 2):
        return f"$10^{{{ex}}}$"
    return f"{v:.3g}"


DECL = r"^(theorem|lemma|noncomputable def|def|abbrev|axiom)\s+"


def find_decl(src: list[str], name: str) -> int:
    pat = re.compile(DECL + re.escape(name) + r"(?![\w'.])")
    for i, line in enumerate(src):
        if pat.match(line):
            return i
    raise SystemExit(f"declaration {name} not found")


def extract(src: list[str], name: str, mode: str) -> list[str]:
    """mode 'stmt' = up to and including ':=' with the proof elided; 'full' = the whole declaration."""
    i = find_decl(src, name)
    start = i
    if i > 0 and src[i - 1].strip().endswith("-/"):
        k = i - 1
        while k >= 0 and not src[k].lstrip().startswith("/--"):
            k -= 1
        if k >= 0:
            start = k
    if mode == "stmt":
        out = [l for l in src[start:i]]
        for l in src[i:]:
            if ":=" in l:
                out.append(l[: l.index(":=") + 2] + " -- proof elided")
                return out
            out.append(l)
        raise SystemExit(f"no := in {name}")
    out = list(src[start:i])
    j = i
    while j < len(src):
        out.append(src[j])
        nxt = j + 1
        if nxt >= len(src):
            break
        if not src[nxt].strip():
            # end of declaration when the next non-blank line is not indented
            m = nxt
            while m < len(src) and not src[m].strip():
                m += 1
            if m >= len(src) or not src[m].startswith((" ", "\t")):
                break
        j += 1
    return [l for l in out if not l.startswith("#print")]


def block(src: list[str], decls: list[tuple[str, str]]) -> str:
    lines: list[str] = []
    for name, mode in decls:
        lines += extract(src, name, mode) + [""]
    return "\n".join(lines).rstrip() + "\n"


def lean_src(mod: str) -> list[str]:
    return (SRC / f"{mod}.lean").read_text().splitlines()


def ax_re_lines(mod: str, names: list[str]) -> list[str]:
    out = json.loads((LOGS / f"{mod}.json").read_text())["output"].replace("\n ", " ")
    res = []
    for n in names:
        ls = [l.strip() for l in out.split("\n") if l.startswith(f"'{n}' depends")]
        if len(ls) != 1:
            raise SystemExit(f"axiom line for {n} in {mod}: {ls}")
        res.append(ls[0])
    return res


def main() -> int:
    GEN.mkdir(exist_ok=True)
    DATA.mkdir(exist_ok=True)
    basic, bern, lap, lim, ex, cor, neg, app = (lean_src(m) for m in
        ["Basic", "Bernstein", "Laplace", "Limits", "Examples", "Corollaries", "NegativeControls", "Applications"])
    ctl = (SRC / "Controls.lean").read_text()

    texts = {
        "defs": block(basic, [("IsCompletelyMonotoneOn", "full"), ("isCompletelyMonotoneOn_iff_admissible", "full")])
        + "\n" + block(bern, [("IsBernsteinOn", "full")]),
        "closure": block(basic, [("congr", "stmt"), ("const_mul", "stmt"),
                                 ("add", "stmt"), ("mul", "full"),
                                 ("comp_add_const", "stmt"), ("neg_deriv", "stmt"),
                                 ("antitoneOn_sign", "stmt"), ("sub_comp_add_const", "full"),
                                 ("sum", "stmt"), ("exp_neg_mul", "full"), ("rpow_neg", "stmt")]),
        "subord": block(bern, [("comp_sign", "full"), ("IsCompletelyMonotoneOn.comp_bernstein", "full")]),
        "instances": block(bern, [("affine", "stmt"), ("rpow", "stmt"), ("sqrt", "stmt"), ("comp", "stmt"),
                                  ("exp_neg_comp", "stmt"), ("IsCompletelyMonotoneOn.comp_sqrt", "stmt"), ("phi_cm", "full")]),
        "laplace": block(lap, [("integrable_pow_mul", "stmt"), ("laplace", "stmt"), ("laplace_measure", "stmt")])
        + "\n" + block(lim, [("of_tendstoLocallyUniformlyOn", "stmt")]),
        "corollaries": block(cor, [("riesz_cm", "full"), ("yukawa_cm", "full"), ("dipolar_cm", "full"), ("shiftDiff_cm", "full"),
                                   ("keldysh_cm", "stmt"), ("yukawa_softcore_cm", "full"), ("stretchedExp_cm", "full"),
                                   ("triangular_yukawa_softcore_optimal", "stmt")]),
        "triopt": block(basic, [("triangular_optimal", "full")]),
        "apps": block(app, [("H2_yukawa_admissible", "full"), ("H1_dipolar_admissible", "full"), ("H3_keldysh_admissible", "full"),
                            ("screenedDipolar_cm", "full"), ("yukawaSpectrum_cm", "stmt"), ("secondDiff_cm", "full")]),
        "quad": block(app, [("quadrupole", "full"), ("quadrupole_not_cm", "full"), ("quadrupoleC_not_cm", "stmt"),
                            ("quadrupolarPair", "full"), ("quadrupolarPair_cm", "full"), ("quadrupolarCoulomb_cm", "full")]),
        "negctl": block(neg, [("cos_not_cm", "stmt"), ("sqrt_not_cm", "stmt"), ("expNeg_not_bernstein", "stmt"),
                              ("expNegInv_not_cm", "stmt"), ("junk_comp_zero_not_cm", "stmt"), ("signedMix_not_cm", "stmt")]),
        "controls": "\n".join(l for l in ctl.splitlines() if l.startswith(("theorem", "axiom", "#print"))) + "\n",
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

    # ---- axiom transcripts (verbatim from the compile logs) ----
    key_names = {
        "Basic": ["ProgCM.isCompletelyMonotoneOn_iff_admissible", "ProgCM.IsCompletelyMonotoneOn.mul",
                  "ProgCM.IsCompletelyMonotoneOn.sub_comp_add_const", "ProgCM.triangular_optimal"],
        "Bernstein": ["ProgCM.IsBernsteinOn.comp_sign", "ProgCM.IsCompletelyMonotoneOn.comp_bernstein"],
        "Laplace": ["ProgCM.laplace", "ProgCM.laplace_measure"],
        "Limits": [],
        "Corollaries": ["ProgCM.dipolar_cm", "ProgCM.yukawa_cm", "ProgCM.keldysh_cm"],
        "Applications": ["ProgCM.Applications.quadrupolarPair_cm", "ProgCM.Applications.quadrupoleC_not_cm"],
    }
    lim_out = json.loads((LOGS / "Limits.json").read_text())["output"]
    lim_names = [m for m in re.findall(r"^'(\S+?)' depends", lim_out, flags=re.M)]
    key_names["Limits"] = [n for n in lim_names if n.endswith("of_tendstoLocallyUniformlyOn")]
    ax_lines: list[str] = []
    for mod, names in key_names.items():
        ax_lines += ax_re_lines(mod, names)
    (GEN / "axioms_key.txt").write_text("\n".join(ax_lines) + "\n")

    ctl_log = json.loads((LOGS / "Controls.json").read_text())
    (GEN / "axioms_controls.txt").write_text(f"rc = {ctl_log['rc']}, {ctl_log['seconds']} s\n" + ctl_log["output"].replace(str(W) + "/", ""))
    rec_ctl = json.loads((REC / "Controls.json").read_text())
    (GEN / "axioms_recompile_controls.txt").write_text(f"rc = {rec_ctl['rc']}, {rec_ctl['seconds']} s\n" + rec_ctl["output"].replace(str(W) + "/", ""))
    ctl_same = ctl_log["output"] == rec_ctl["output"]

    # recompile of Bernstein and Applications: outputs compared with the WORK stage logs
    rec = {}
    for mod in ["Bernstein", "Applications", "Controls"]:
        r = json.loads((REC / f"{mod}.json").read_text())
        o = json.loads((LOGS / f"{mod}.json").read_text())
        rec[mod] = {"rc": r["rc"], "seconds": r["seconds"], "same_output": r["output"] == o["output"],
                    "n_print": len(re.findall(r"^'\S+?' depends on axioms", r["output"], flags=re.M)),
                    "warnings": len(re.findall(r": warning", r["output"]))}

    gate = json.loads((P3 / "gate.json").read_text())
    mods = gate["modules"]
    lib = ["Basic", "Bernstein", "Laplace", "Limits", "Examples", "Corollaries", "NegativeControls", "MathlibOnly",
           "MathlibOnlyBridge", "Applications"]
    tot_decl = sum(mods[m]["n_declared"] for m in lib)
    tot_print = sum(mods[m]["n_print_axioms"] for m in lib)
    tot_work1 = tot_decl - mods["Applications"]["n_declared"]
    off = sum(len(mods[m]["off_whitelist"]) for m in lib)
    all_wl = all(sorted(a) == sorted(gate["whitelist"]) for m in lib for a in mods[m]["axioms"].values())
    warns = 0
    for m in lib:
        warns += len(re.findall(r": warning", json.loads((LOGS / f"{m}.json").read_text())["output"]))
    secs = [float(mods[m]["seconds"]) for m in lib]

    # ---- table of modules ----
    rows = []
    for m in lib:
        d = mods[m]
        rows.append(rf"\lean{{{m}}} & {d['n_declared']} & {d['n_print_axioms']} & {d['rc']} & {float(d['seconds']):.1f} & \texttt{{{d['source_sha256'][:12]}}} \\")
    d = mods["Controls"]
    rows.append(rf"\lean{{Controls}} (planted) & -- & {d['n_print_axioms']} & {d['rc']} & {float(d['seconds']):.1f} & \texttt{{{d['source_sha256'][:12]}}} \\")
    (GEN / "table_modules.tex").write_text("\n".join(rows) + "\n")

    # ---- numerics: the Tier X screen ----
    chk = json.loads((APP / "numeric_check.json").read_text())
    for fn in ["numeric_check.json", "proof_length.json", "proof_length_union.json", "cm_numeric_check.py", "proof_length.py",
               "Closure.lean.txt"]:
        shutil.copy(APP / fn, DATA / fn)
    shutil.copy(P3 / "gate.json", DATA / "gate.json")
    shutil.copy(P3 / "gate.py", DATA / "gate.py")
    labels = {
        "ctl_pos_riesz1": ("control (CM)", r"$t^{-1/2}$"),
        "ctl_pos_yukawa_k1": ("control (CM)", r"$e^{-\sqrt t}/\sqrt t$"),
        "ctl_neg_cos": ("control (not CM)", r"$\cos t$"),
        "ctl_neg_h_dipolar_d1": ("control (not CM)", r"$t^{-1/2}-2(t+1)^{-1/2}$"),
        "ctl_neg_yukawa_signed_mix": ("control (not CM)", r"$g_1-2g_2$"),
        "quadrupole_0_c_4c_c1": ("candidate", r"$t^{-1/2}-2(t+1)^{-1/2}+(t+4)^{-1/2}$"),
        "quadrupolar_pair_interaction_c1": ("candidate", r"$2(3f(t)-4f(t+1)+f(t+4))$, $f=t^{-1/2}$"),
        "quadrupolar_pair_interaction_screened_k1_c1": ("candidate", r"same with $f=g_1$"),
        "ctl_neg_weights_2_m3_1_c1": ("control (not CM)", r"$2f(t)-3f(t+1)+f(t+4)$, $f=t^{-1/2}$"),
        "seconddiff_0_c_2c_c1": ("candidate", r"$f(t)-2f(t+1)+f(t+2)$, $f=t^{-1/2}$"),
        "screened_dipolar_k1_d1": ("candidate", r"$2(g_1(t)-g_1(t+1))$"),
        "screened_dipolar_k3_d2": ("candidate", r"$2(g_3(t)-g_3(t+4))$"),
        "yukawa_exp_spectrum": ("candidate", r"$1/(\sqrt t(1+\sqrt t))$"),
        "yukawa_box_spectrum_0_to_2": ("candidate", r"$(1-e^{-2\sqrt t})/t$"),
    }
    trows = []
    for k, v in chk.items():
        kind, form = labels[k]
        s = float(v["min_signed"])
        sv = f"${e(s, 2)}$" if abs(s) < 1e-3 or abs(s) > 1e3 else f"${s:.4f}$"
        trows.append(rf"{form} & {kind} & {sv} & {v['at_n']} & {tfmt(float(v['at_t']))} & {'yes' if v['negative_found'] else 'no'} \\")
    (GEN / "table_screen.tex").write_text("\n".join(trows) + "\n")
    pos_clean = all(not chk[k]["negative_found"] for k in ["ctl_pos_riesz1", "ctl_pos_yukawa_k1"])
    neg_caught = all(chk[k]["negative_found"] for k in ["ctl_neg_cos", "ctl_neg_h_dipolar_d1", "ctl_neg_yukawa_signed_mix", "ctl_neg_weights_2_m3_1_c1"])
    cand_keys = [k for k, v in labels.items() if v[0] == "candidate"]
    cand_neg = [k for k in cand_keys if chk[k]["negative_found"]]
    if not (pos_clean and neg_caught):
        raise SystemExit("screen controls did not behave as designed")

    # ---- proof lengths ----
    pl = json.loads((APP / "proof_length.json").read_text())
    plu = json.loads((APP / "proof_length_union.json").read_text())

    # ---- figures ----
    plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
    x = np.linspace(0, 1, 401)
    syms = {
        r"dipolar $2(1-x)$ (CM)": 2 * (1 - x),
        r"pair of quadrupoles $2(3-4x+x^4)$ (CM)": 2 * (3 - 4 * x + x ** 4),
        r"second difference $(1-x)^2$ (CM)": (1 - x) ** 2,
        r"charge quadrupole $1-2x+x^4$ (not CM)": 1 - 2 * x + x ** 4,
        r"wrong weights $2-3x+x^4$ (control, not CM)": 2 - 3 * x + x ** 4,
    }
    fig, ax = plt.subplots(figsize=(5.4, 3.1))
    styles = ["-", "-", "-", "--", ":"]
    for (lab, y), ls in zip(syms.items(), styles):
        ax.plot(x, y, ls, lw=1.5, label=lab)
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xlabel(r"$x=e^{-uc}$ (shift factor of the Laplace variable $u$)")
    ax.set_ylabel("symbol $p(x)$")
    ax.set_ylim(-0.4, 6.4)
    ax.legend(frameon=False, fontsize=6.5, loc="upper right")
    fig.tight_layout()
    fig.savefig(HERE / "fig_symbols.pdf")
    fig.savefig(HERE / "fig_symbols.png", dpi=160)
    plt.close(fig)
    neg_sym = {lab: float(y.min()) for lab, y in syms.items()}
    min_charge = float((1 - 2 * x + x ** 4).min())
    x_at = float(x[int(np.argmin(1 - 2 * x + x ** 4))])
    min_pair = float((3 - 4 * x + x ** 4).min())
    min_wrong = float((2 - 3 * x + x ** 4).min())
    x_wrong = float(x[int(np.argmin(2 - 3 * x + x ** 4))])

    t = np.logspace(-2, 3, 600)
    f = lambda s: s ** -0.5  # noqa: E731
    charge = f(t) - 2 * f(t + 1) + f(t + 4)
    pair = 2 * (3 * f(t) - 4 * f(t + 1) + f(t + 4))
    wrong = 2 * f(t) - 3 * f(t + 1) + f(t + 4)
    hdip = f(t) - 2 * f(t + 1)
    fig, ax = plt.subplots(figsize=(5.4, 3.1))
    ax.semilogx(t, t ** 1.5 * pair, lw=1.5, label=r"pair of quadrupoles (CM, Lean)")
    ax.semilogx(t, t ** 1.5 * charge, "--", lw=1.5, label=r"charge quadrupole (not CM, Lean)")
    ax.semilogx(t, t ** 1.5 * wrong, ":", lw=1.5, label=r"wrong weights $2,-3,1$ (control)")
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xlabel(r"$t=r^2$ ($c=d^2=1$)")
    ax.set_ylabel(r"$t^{3/2}\,F(t)$")
    ax.set_ylim(-1.3, 1.7)
    ax.legend(frameon=False, fontsize=6.5, loc="upper right")
    fig.tight_layout()
    fig.savefig(HERE / "fig_profiles.pdf")
    fig.savefig(HERE / "fig_profiles.png", dpi=160)
    plt.close(fig)
    far_charge = float((t ** 1.5 * charge)[-1])
    far_pair = float((t ** 1.5 * pair)[-1])
    i_min = int(np.argmin(charge))
    t_min_charge = float(t[i_min])
    val_min_charge = float(charge[i_min])

    names = ["H2 Yukawa", "H1 dipolar (all d)", "H3 Keldysh"]
    orig = [pl[n]["original_stats"]["closure_lines_total"] for n in names] + [plu["original_H1all_H2_H3"]["lines"]]
    libr = [pl[n]["library_stats"]["closure_lines_total"] for n in names] + [plu["library_H1_H2_H3"]["lines"]]
    labs = ["H2 Yukawa", "H1 (all d)", "H3 Keldysh", "union of\nthe three"]
    xx = np.arange(len(labs))
    fig, ax = plt.subplots(figsize=(5.4, 2.8))
    ax.bar(xx - 0.2, orig, 0.4, label="original proofs")
    ax.bar(xx + 0.2, libr, 0.4, label="through the library")
    for i, (a, b) in enumerate(zip(orig, libr)):
        ax.text(i - 0.2, a + 6, str(a), ha="center", fontsize=7)
        ax.text(i + 0.2, b + 6, str(b), ha="center", fontsize=7)
    ax.set_xticks(xx)
    ax.set_xticklabels(labs)
    ax.set_ylabel("lines in the dependency closure")
    ax.set_ylim(0, 580)
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(HERE / "fig_prooflen.pdf")
    fig.savefig(HERE / "fig_prooflen.png", dpi=160)
    plt.close(fig)

    # ---- hashes of the Lean files ----
    shas = {m: sha(SRC / f"{m}.lean") for m in lib + ["Controls"]}
    sha_rows = "\n".join(rf"\item \texttt{{{m}.lean}}: \texttt{{{h}}}" for m, h in shas.items())
    (GEN / "shas.tex").write_text(sha_rows + "\n")
    (DATA / "lean_sha256.json").write_text(json.dumps(shas, indent=1))

    # ---- Mathlib file facts ----
    am = MATHLIB / "Mathlib/Analysis/Calculus/AbsolutelyMonotone.lean"
    am_lines = am.read_text().splitlines()
    am_def_line = next(i + 1 for i, l in enumerate(am_lines) if l.startswith("def AbsolutelyMonotoneOn"))
    am_decls = [l for l in am_lines if re.match(r"^(theorem|lemma)\s", l)]

    # ---- macros ----
    go = HERE / "ledger/gate_output.txt"
    gtxt = go.read_text() if go.exists() else ""
    n_block = len(re.findall(r"^\s*block\s", gtxt, flags=re.M)) if go.exists() else 0
    n_flag = len(re.findall(r"^\s*flag\s", gtxt, flags=re.M)) if go.exists() else 0
    m_exit = re.search(r"exit_code=(\d+)", gtxt)
    over = [r"\newcommand{\Pn%s}{%s}" % (k, v) for k, v in {
        "GateBlock": str(n_block), "GateFlags": str(n_flag), "GateExit": m_exit.group(1) if m_exit else "?",
        "BaseShort": "9d24574",
        "TotDecl": str(tot_decl), "TotPrint": str(tot_print), "TotWorkOne": str(tot_work1),
        "AppDecl": str(mods["Applications"]["n_declared"]), "MathlibOnlyDecl": str(mods["MathlibOnly"]["n_declared"]),
        "BridgeDecl": str(mods["MathlibOnlyBridge"]["n_declared"]), "OffWhitelist": str(off), "Warnings": str(warns),
        "SecMin": f"{min(secs):.1f}", "SecMax": f"{max(secs):.1f}",
        "AllWhitelist": "all" if all_wl else "NOT all", "GateOverall": gate["overall"],
        "RecBernRc": str(rec["Bernstein"]["rc"]), "RecBernSec": str(rec["Bernstein"]["seconds"]),
        "RecBernSame": "identical to" if rec["Bernstein"]["same_output"] else "DIFFERENT from",
        "RecBernPrint": str(rec["Bernstein"]["n_print"]),
        "RecAppRc": str(rec["Applications"]["rc"]), "RecAppSec": str(rec["Applications"]["seconds"]),
        "RecAppSame": "identical to" if rec["Applications"]["same_output"] else "DIFFERENT from",
        "RecAppPrint": str(rec["Applications"]["n_print"]),
        "RecCtlRc": str(rec["Controls"]["rc"]), "RecCtlSec": str(rec["Controls"]["seconds"]),
        "RecCtlSame": "identical to" if ctl_same else "DIFFERENT from",
        "ScreenN": str(len(chk)), "ScreenCand": str(len(cand_keys)), "ScreenCandNeg": str(len(cand_neg)),
        "MinCharge": f"{float(chk['quadrupole_0_c_4c_c1']['min_signed']):.4f}",
        "MinWrong": f"{float(chk['ctl_neg_weights_2_m3_1_c1']['min_signed']):.4f}",
        "ChargeT": f"{t_min_charge:.2f}", "ChargeVal": f"{val_min_charge:.4f}",
        "FarCharge": f"{far_charge:.3f}", "FarPair": f"{far_pair:.3f}",
        "SymMinCharge": f"{min_charge:.4f}", "SymXCharge": f"{x_at:.2f}", "SymMinPair": f"{min_pair:.1f}",
        "SymMinWrong": f"{min_wrong:.4f}", "SymXWrong": f"{x_wrong:.2f}",
        "LenOrigUnion": str(plu["original_H1all_H2_H3"]["lines"]), "LenLibUnion": str(plu["library_H1_H2_H3"]["lines"]),
        "LenOrigUnionDecl": str(plu["original_H1all_H2_H3"]["decls"]), "LenLibUnionDecl": str(plu["library_H1_H2_H3"]["decls"]),
        "LenLibNewA": str(plu["library_H1_H2_H3_plus_screened_spectrum"]["lines"]),
        "LenLibNewADecl": str(plu["library_H1_H2_H3_plus_screened_spectrum"]["decls"]),
        "LenLibNewB": str(plu["library_H1_H2_H3_plus_screened_spectrum_quadrupolar"]["lines"]),
        "LenLibNewBDecl": str(plu["library_H1_H2_H3_plus_screened_spectrum_quadrupolar"]["decls"]),
        "AmDefLine": str(am_def_line), "AmNDecl": str(len(am_decls)),
        "MathlibSha": "d13f23b723b8a846827a245b89c10fc7d3f11612",
    }.items()]
    for n in names + ["H1 dipolar (d>0)"]:
        key = re.sub(r"[^A-Za-z]", "", n)
        over.append(r"\newcommand{\Pn%sHeadO}{%d}" % (key, pl[n]["original_stats"]["headline_lines"]))
        over.append(r"\newcommand{\Pn%sHeadL}{%d}" % (key, pl[n]["library_stats"]["headline_lines"]))
        over.append(r"\newcommand{\Pn%sClosO}{%d}" % (key, pl[n]["original_stats"]["closure_lines_total"]))
        over.append(r"\newcommand{\Pn%sClosL}{%d}" % (key, pl[n]["library_stats"]["closure_lines_total"]))
        over.append(r"\newcommand{\Pn%sDeclO}{%d}" % (key, pl[n]["original_stats"]["closure_decls"]))
        over.append(r"\newcommand{\Pn%sDeclL}{%d}" % (key, pl[n]["library_stats"]["closure_decls"]))
    (HERE / "gen_numbers.tex").write_text("\n".join(over) + "\n")
    summary = {"decl": tot_decl, "printed": tot_print, "off": off, "warnings": warns, "recompile": rec,
               "screen_cand_neg": cand_neg, "gate": gate["overall"]}
    (DATA / "gen_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
