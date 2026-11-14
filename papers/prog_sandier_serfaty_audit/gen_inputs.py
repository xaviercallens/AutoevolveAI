"""Generate every number, table, listing and figure that main.tex prints (P1: reproduction of the finite certificate,
adversarial audit of the reduction, Lean statement of the Sandier-Serfaty conjecture, LeanFlow data certificates).

Inputs (read-only): data/ (copy of results/programmes/2026-10-25/P1/), rerun/ (paper-stage reruns), the Lean sources in
formal_cert/Programmes/, the saved certificate record in the openai/math corpus.
Outputs (in this directory): gen_numbers.tex, gen/*.lst (verbatim Lean, docstrings elided, non-ASCII mapped; the script
FAILS on any unmapped character), gen/table_*.tex, gen/fig_*.pdf, gen/gen_log.json.
Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I gen_inputs.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from decimal import Decimal, getcontext
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

getcontext().prec = 60
HERE = Path(__file__).resolve().parent
W = HERE.parents[1]
DATA = HERE / "data"
GEN = HERE / "gen"
RERUN = HERE / "rerun"
LEAN_MAIN = W / "formal_cert/Programmes/SandierSerfatyStatement.lean"
LEAN_CTL = W / "formal_cert/Programmes/SandierSerfatyStatementControls.lean"
RECORD = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/SocrateAI-Scientific-Agora-LeanMaster/lean4basesource/"
              "openai-math/preprints/Triangular-minimality-for-planar-Coulomb-renormalized-energy-September-23-2026/"
              "verification/data/certificate-record.txt")
LEANFLOW_COMMIT = "84e0c2899830fba671022eefcd408af9ecd565c8"  # fix commit (audit B2); confirmed with git rev-parse HEAD at the revise stage
LEANFLOW_FIX_COMMIT = "2c168be2de8104dddc48daecee1423c8d8f076b7"  # the sentinel fix itself; HEAD adds a docstring/docs follow-up
LEANFLOW_OLD_COMMIT = "542cea97aa78e30d8935ec81278aeb697a9f5dc7"  # pre-fix commit (the one the audit probed)

OKABE = {"blue": "#0072B2", "orange": "#E69F00", "green": "#009E73", "verm": "#D55E00", "sky": "#56B4E9",
         "pink": "#CC79A7", "grey": "#555555"}

UMAP = {
    "ℝ": r"$\mathbb{R}$", "ℤ": r"$\mathbb{Z}$", "ℕ": r"$\mathbb{N}$", "→": r"$\to$", "←": r"$\leftarrow$",
    "↔": r"$\leftrightarrow$", "∀": r"$\forall$", "∃": r"$\exists$", "∧": r"$\wedge$", "∨": r"$\vee$", "¬": r"$\neg$",
    "≤": r"$\le$", "≥": r"$\ge$", "≠": r"$\ne$", "∈": r"$\in$", "∉": r"$\notin$", "⊆": r"$\subseteq$",
    "∩": r"$\cap$", "∪": r"$\cup$", "∅": r"$\emptyset$", "⋃": r"$\bigcup$", "∑": r"$\sum$", "∫": r"$\int$",
    "∂": r"$\partial$", "∇": r"$\nabla$", "∞": r"$\infty$", "⊤": r"$\top$", "⊥": r"$\bot$", "π": r"$\pi$",
    "Λ": r"$\Lambda$", "χ": r"$\chi$", "η": r"$\eta$", "ν": r"$\nu$", "φ": r"$\varphi$", "σ": r"$\sigma$",
    "ε": r"$\varepsilon$", "Γ": r"$\Gamma$", "△": r"$\triangle$", "√": r"$\surd$", "²": r"$^2$", "³": r"$^3$",
    "⁻": r"$^{-}$", "¹": r"$^{1}$", "·": r"$\cdot$", "‖": r"$\Vert$", "⟨": r"$\langle$", "⟩": r"$\rangle$",
    "𝓝": r"$\mathcal{N}$", "∘": r"$\circ$", "×": r"$\times$", "•": r"$\bullet$", "ᶠ": r"$^{\mathrm{f}}$",
    "ᶜ": r"$^{\mathrm{c}}$", "ᵐ": r"$^{\mathrm{m}}$", "₀": r"$_0$", "₁": r"$_1$", "₂": r"$_2$", "≈": r"$\approx$",
    "↦": r"$\mapsto$", "λ": r"$\lambda$", "μ": r"$\mu$", "ρ": r"$\rho$", "⁻¹": r"$^{-1}$", "∣": r"$\mid$",
    "‹": "<", "›": ">", "—": "---", "–": "--", "′": "'", "□": r"$\square$", "∖": r"$\setminus$",
    "∗": "*", "⊢": r"$\vdash$", "⊂": r"$\subset$", "δ": r"$\delta$", "α": r"$\alpha$", "β": r"$\beta$",
    "ξ": r"$\xi$", "θ": r"$\theta$", "τ": r"$\tau$", "ψ": r"$\psi$", "ω": r"$\omega$", "Σ": r"$\Sigma$",
    "ᵢ": r"$_i$", "ₖ": r"$_k$", "⁺": r"$^{+}$", "ℓ": r"$\ell$", "…": "...", "·": r"$\cdot$", "⦃": r"$\{\!|$",
    "⦄": r"$|\!\}$", "⌊": r"$\lfloor$", "⌋": r"$\rfloor$", "∥": r"$\Vert$", "∑ᶠ": r"$\sum^{\mathrm f}$",
}


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_file(p: Path) -> str:
    return sha_bytes(p.read_bytes())


def lst_escape(text: str) -> str:
    """Map non-ASCII characters into (*@ ... @*) escapes for listings; fail closed on any unmapped character."""
    out: list[str] = []
    for ch in text:
        if ord(ch) < 128:
            out.append(ch)
        elif ch in UMAP:
            out.append(f"(*@{UMAP[ch]}@*)")
        else:
            raise SystemExit(f"unmapped non-ASCII character {ch!r} (U+{ord(ch):04X}) in a listing; extend UMAP")
    s = "".join(out)
    if "@*)(*@" in s:  # adjacent escapes merge harmlessly
        s = s.replace("@*)(*@", "")
    return s


def strip_docs(src: str) -> str:
    src = re.sub(r"/-!.*?-/", "", src, flags=re.S)
    src = re.sub(r"/--.*?-/", "", src, flags=re.S)
    src = re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", src)
    return src.strip("\n") + "\n"


def lean_defs() -> str:
    src = LEAN_MAIN.read_text()
    a = src.index("namespace ProgSandierSerfaty")
    b = src.index("/-! ## Proved non-degeneracy lemmas")
    region = src[a:b]
    return strip_docs(region)


def lean_lemmas() -> str:
    src = LEAN_MAIN.read_text()
    names = ["negPi_admissibleBg_iff", "negPi_admissible", "negPi_not_admissible_noBackground",
             "negPi_not_admissible_wrongSign", "negPi_hasLocalEnergy", "competitor_nonvacuous",
             "triBasis_covolume", "ssBasis_covolume", "exists_squareCutoffFamily", "exists_ballCutoffFamily"]
    out: list[str] = []
    for n in names:
        m = re.search(rf"^(theorem|lemma) {re.escape(n)}\b", src, flags=re.M)
        if not m:
            raise SystemExit(f"lemma {n} not found")
        start = m.start()
        end = src.index(":=", start)
        sig = src[start:end].rstrip()
        out.append(sig + " := -- proof elided")
    return "\n".join(out) + "\n"


def lean_controls() -> str:
    return strip_docs(LEAN_CTL.read_text())


def write_lst(name: str, text: str) -> int:
    GEN.mkdir(exist_ok=True)
    (GEN / f"{name}.lean").write_text(text)
    (GEN / f"{name}.lst").write_text(lst_escape(text))
    return len(text.splitlines())


# ----------------------------------------------------------------------------------------------- certificate logs
LABELS = {
    "lambda,mu,K,bcon,f0(l),slope,f(l)": ["lambda", "mu", "K", "bcon", "f0l", "slope", "fl"],
    "bounds:": ["G", "Gd", "Gs", "Gdd", "Gss"],
    "gmin,drneg,factor,er_drop,gmin-factor,drneg+er_drop+K": ["gmin", "drneg", "factor", "er_drop", "gmin_minus_factor", "drneg_sum"],
    "hess hulls": ["g_dd", "g_dx", "g_xx", "det"],
}


def parse_log(path: Path) -> dict[str, tuple[int, int]]:
    lines = path.read_text().splitlines()
    out: dict[str, tuple[int, int]] = {}
    for i, ln in enumerate(lines):
        if ln in LABELS and i + 1 < len(lines) and lines[i + 1].startswith("["):
            pairs = [(int(a), int(b)) for a, b in re.findall(r"\((-?\d+), (-?\d+)\)", lines[i + 1])]
            names = LABELS[ln]
            assert len(pairs) == len(names), (ln, pairs)
            out.update(dict(zip(names, pairs)))
    return out


def parse_record() -> list[tuple[int, int]]:
    text = RECORD.read_text()
    start = text.index("### Saved output rows")
    return [(int(a), int(b)) for a, b in re.findall(r"`\((-?\d+), (-?\d+)\)`", text[start:])]


def timing(path: Path, label: str) -> float:
    m = re.search(rf"TIMING {re.escape(label)} ([0-9.]+) seconds", path.read_text())
    return float(m.group(1)) if m else float("nan")


def fmt_pair(p: tuple[int, int]) -> str:
    return f"$({p[0]},\\,{p[1]})$"


def sig(value: str, digits: int) -> str:
    """Round a decimal string (any exponent) to `digits` significant digits, ROUNDING rather than slicing the string.

    The first version sliced strings (``s[:10]``), which dropped exponents (G(p,x0) = -1.008e-53 printed as -1.0081311)
    and truncated instead of rounding (audit blocking B1, nonblocking N2).
    """
    d = Decimal(value)
    if d == 0:
        return "0"
    exp = d.adjusted()
    q = d.quantize(Decimal(1).scaleb(exp - digits + 1))
    if q.adjusted() != exp:  # rounding carried into a new decade (9.99 -> 10.0)
        q = d.quantize(Decimal(1).scaleb(q.adjusted() - digits + 1))
    return format(q, "f") if -5 < q.adjusted() < 15 else f"{q:.{digits - 1}e}"


def sci(value: str, digits: int, absolute: bool = False) -> str:
    """LaTeX math-mode scientific notation, rounded to `digits` significant digits (never slices the string)."""
    d = Decimal(value)
    if absolute:
        d = abs(d)
    mant, exp = f"{d:.{digits - 1}e}".split("e")
    return f"{mant}\\times10^{{{int(exp)}}}"


def main() -> int:
    GEN.mkdir(exist_ok=True)
    macros: dict[str, str] = {}

    def mac(name: str, value: str) -> None:
        macros[name] = value

    # ---- Lean listings
    n_defs = write_lst("defs", lean_defs())
    n_lem = write_lst("lemmas", lean_lemmas())
    n_ctl = write_lst("controls", lean_controls())
    cs = json.loads((DATA / "s3/compile_statement.json").read_text())
    cc = json.loads((DATA / "s3/compile_controls.json").read_text())
    rs = json.loads((RERUN / "compile_statement.json").read_text())
    rc = json.loads((RERUN / "compile_controls.json").read_text())
    ax_text = rs["output"]
    ax_lines = [ln.replace("ProgSandierSerfaty.", "PSS.") for ln in ax_text.strip().splitlines()]
    ctl_lines = [ln.replace(str(W) + "/", "").replace("ProgSandierSerfaty.", "PSS.") for ln in rc["output"].strip().splitlines()]
    write_lst("axioms_main", "\n".join(ax_lines) + "\n")
    write_lst("axioms_controls", "\n".join(ctl_lines) + "\n")
    same_main = cs["output"] == rs["output"]
    same_ctl = cc["output"].replace(str(W) + "/", "") == rc["output"].replace(str(W) + "/", "")
    sh_main, sh_ctl = sha_file(LEAN_MAIN), sha_file(LEAN_CTL)
    lock = json.loads((DATA / "STATEMENT_LOCK.json").read_text())
    mac("SSAShaMain", sh_main)
    mac("SSAShaCtl", sh_ctl)
    mac("SSAShaRegion", lock["statement_region_sha256"])
    mac("SSAShaMatch", "match" if (sh_main == lock["main_file_sha256"] and sh_ctl == lock["controls_file_sha256"]) else "DO NOT MATCH")
    mac("SSACompileMain", f"rc {rs['rc']} in {rs['seconds']:.1f}~s (stage S3: rc {cs['rc']} in {cs['seconds']:.1f}~s)")
    mac("SSACompileCtl", f"rc {rc['rc']} in {rc['seconds']:.1f}~s (stage S3: rc {cc['rc']} in {cc['seconds']:.1f}~s)")
    mac("SSAAxiomsSame", "identical" if same_main else "DIFFERENT")
    mac("SSACtlSame", "identical" if same_ctl else "DIFFERENT")
    lockchk = json.loads((RERUN / "statement_lock_check.txt").read_text())
    mac("SSALockCheck", "match: true" if lockchk.get("match") else "match: false")
    mac("SSANDefsLines", str(n_defs))

    # ---- certificate runs
    runs = {
        "pos": ("s1_positive", "positive run (unchanged source)", "none"),
        "neg": ("s1_neg", r"S1-neg: midpoint constant $1/24\to1$ ($\times24$)", r"\texttt{er0}"),
        "A": ("s1_neg/A_midpoint_x2", r"A: midpoint constant $1/24\to1/12$ ($\times2$)", r"\texttt{er0}"),
        "B": ("s1_neg/B_lipschitz_x2", r"B: \texttt{er\_drop} allowance $\times2$", r"\texttt{er\_drop}"),
    }
    vals: dict[str, dict[str, tuple[int, int]]] = {}
    rec: dict[str, dict] = {}
    for k, (d, _, _) in runs.items():
        vals[k] = parse_log(DATA / d / "run.log")
        rec[k] = json.loads((DATA / d / "run-receipt.json").read_text())
    record_pairs = parse_record()
    log_order = ["lambda", "mu", "K", "bcon", "f0l", "slope", "fl", "G", "Gd", "Gs", "Gdd", "Gss", "gmin", "drneg",
                 "factor", "er_drop", "gmin_minus_factor", "drneg_sum", "g_dd", "g_dx", "g_xx", "det"]
    pos_pairs = [vals["pos"][n] for n in log_order]
    n_equal = sum(1 for a, b in zip(pos_pairs, record_pairs) if a == b)
    mac("SSAPairsEqual", str(n_equal))
    mac("SSAPairsTotal", str(len(record_pairs)))
    mac("SSARecordSha", sha_file(RECORD))
    p = rec["pos"]
    mac("SSAPosElapsed", f"{p['elapsed_seconds']:.2f}")
    mac("SSAPosChild", f"{timing(DATA / 's1_positive/run.log', 'full certificate'):.3f}")
    for lab, key in [("InitCore", "init_core including core_test"), ("CalcLam", "calcLam"), ("CalcK", "calcK"),
                     ("Bdsup", "bdsup"), ("GlobalGrid", "global_grid"), ("InsideHess", "inside_hess")]:
        mac("SSAT" + lab, f"{timing(DATA / 's1_positive/run.log', key):.1f}")
    mac("SSAPosExe", p["executable_sha256"])
    mac("SSAPosLog", p["log_sha256"])
    mac("SSAPosStart", p["start_utc"][:19].replace("T", " ") + " UTC")
    mac("SSAPosEnd", p["end_utc"][:19].replace("T", " ") + " UTC")
    mac("SSAPosStages", "passed" if p["stage_validation"]["passed"] else "FAILED")
    mac("SSAPosUnchanged", "true" if p["sources_unchanged"] else "false")
    mac("SSACompiler", p["compiler"])
    mac("SSAPython", p["python"])
    src_sha = p["source_sha256_before"]
    for fname, mname in [("certificate.cpp", "ShaCert"), ("core.hpp", "ShaCore"), ("grids.hpp", "ShaGrids"), ("run-certificate.py", "ShaRun")]:
        mac("SSA" + mname, src_sha[fname])
        assert src_sha[fname] == p["source_sha256_after"][fname], fname
    for k in ("neg", "A", "B"):
        r = rec[k]
        mac(f"SSAEl{k}", f"{r['elapsed_seconds']:.0f}")
        mac(f"SSARc{k}", str(r["wrapper_exit_status"]))
        mac(f"SSATok{k}", "true" if r["terminal_OK"] else "false")
        mac(f"SSAStg{k}", "passed" if r["stage_validation"]["passed"] else "failed")

    # ---- table: dose-response
    rows = []
    for k in ("pos", "neg", "A", "B"):
        v = vals[k]
        r = rec[k]
        outcome = "accepted, \\texttt{OK}" if r["terminal_OK"] else "\\textbf{rejected} (SIGABRT, exit $-6$)"
        rows.append(f"{runs[k][1]} & {fmt_pair(v['factor'])} & {fmt_pair(v['gmin_minus_factor'])} & {fmt_pair(v['er_drop'])} & "
                    f"{fmt_pair(v['drneg_sum'])} & {outcome} & {r['elapsed_seconds']:.0f} \\\\")
    (GEN / "table_runs.tex").write_text("\n".join(rows) + "\n")

    # ---- table: record vs run
    names_tex = {"lambda": r"$\lambda$", "mu": r"$\mu$", "K": "$K$", "bcon": "$B(\\ell)$", "f0l": "$f_0(\\ell)$",
                 "slope": "slope", "fl": "$f(\\ell)$", "gmin": "gmin", "drneg": "drneg", "factor": "factor",
                 "er_drop": "\\texttt{er\\_drop}", "gmin_minus_factor": "gmin$-$factor", "drneg_sum": "drneg$+$\\texttt{er\\_drop}$+K$",
                 "g_dd": "$g_{dd}$", "g_xx": "$g_{xx}$", "det": "det Hess"}
    rows = []
    for n in names_tex:
        i = log_order.index(n)
        eq = "yes" if record_pairs[i] == pos_pairs[i] else "NO"
        rows.append(f"{names_tex[n]} & {fmt_pair(record_pairs[i])} & {fmt_pair(pos_pairs[i])} & {eq} \\\\")
    (GEN / "table_pairs.tex").write_text("\n".join(rows) + "\n")

    # ---- dose-response fit + figure
    f1, f24 = vals["pos"]["factor"][1], vals["neg"]["factor"][1]
    er0 = (f24 - f1) / 23.0
    eri = f1 - er0
    gmin_lo = vals["pos"]["gmin"][0]
    m_star = (gmin_lo - eri) / er0
    fa_obs = vals["A"]["factor"][1]
    fa_pred = eri + 2 * er0
    s_hi = vals["pos"]["drneg_sum"][1]
    allow = vals["pos"]["er_drop"][1]
    m_drop = 1 - s_hi / allow
    b_pred = s_hi + allow
    b_obs = vals["B"]["drneg_sum"][1]
    mac("SSAErMid", f"{er0:.2f}")
    mac("SSAErInt", f"{eri:.2f}")
    mac("SSAMstar", f"{m_star:.1f}")
    mac("SSAFactorAPred", f"{fa_pred:.1f}")
    mac("SSAFactorAObs", str(fa_obs))
    mac("SSAMdrop", f"{m_drop:.2f}")
    mac("SSABPred", str(b_pred))
    mac("SSABObs", str(b_obs))
    mac("SSASlack", str(-s_hi))
    mac("SSAAllow", str(allow))

    plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.7))
    ms = [1, 2, 24]
    xs = [0.6 + i * 0.1 for i in range(0, 261)]
    ax[0].plot(xs, [eri + m * er0 for m in xs], color=OKABE["grey"], lw=1, label="line through m=1 and m=24")
    ax[0].axhline(gmin_lo, color=OKABE["verm"], lw=1, ls="--")
    ax[0].text(0.8, gmin_lo + 22, "assertion fails once factor exceeds gmin lower end (134)", color=OKABE["verm"], fontsize=6.5)
    ax[0].scatter(ms, [vals["pos"]["factor"][1], vals["A"]["factor"][1], vals["neg"]["factor"][1]], color=OKABE["blue"], zorder=3, s=22,
                  label="printed (m=1, 2, 24)")
    ax[0].scatter([m_star], [gmin_lo], facecolors="none", edgecolors=OKABE["verm"], zorder=3, s=30, label=f"fitted break-even m={m_star:.1f}")
    ax[0].set_xlabel("multiplier m of the midpoint constant")
    ax[0].set_ylabel("factor, upper end (1e-7 units)")
    ax[0].set_ylim(0, 175)
    ax[0].legend(frameon=False, fontsize=6.5, loc="lower right")
    xs2 = [0.6 + i * 0.02 for i in range(0, 110)]
    ax[1].plot(xs2, [s_hi + allow * (m - 1) for m in xs2], color=OKABE["grey"], lw=1, label="line through m=1 and m=2")
    ax[1].axhline(0, color=OKABE["verm"], lw=1, ls="--")
    ax[1].text(0.62, 250, "final assertion needs a value below 0", color=OKABE["verm"], fontsize=6.5)
    ax[1].scatter([1, 2], [s_hi, b_obs], color=OKABE["blue"], zorder=3, s=22, label="printed (m=1, 2)")
    ax[1].scatter([m_drop], [0], facecolors="none", edgecolors=OKABE["verm"], zorder=3, s=30, label=f"fitted break-even m={m_drop:.2f}")
    ax[1].set_xlabel("multiplier m of the Lipschitz allowance")
    ax[1].set_ylabel("drneg+er_drop+K, upper end (1e-7)")
    ax[1].legend(frameon=False, fontsize=6.5, loc="lower right")
    ax[1].set_ylim(-5500, 1500)
    fig.tight_layout()
    fig.savefig(GEN / "fig_dose.pdf")
    plt.close(fig)

    # ---- calibration figure
    cal = json.loads((DATA / "s2_audit/calibration_check.out.json").read_text())
    wtri = Decimal(cal["W_tri_BS2018_closed_form"])
    lo, hi = (Decimal(x) - wtri for x in cal["interval_6K_plus_lambda_plus_2pi_mu"])
    neg = cal["negative_controls"]
    off = {k: abs(float(Decimal(v["value"]) - wtri)) for k, v in neg.items()}
    mac("SSACalLo", f"{Decimal(cal['interval_6K_plus_lambda_plus_2pi_mu'][0]):.8f}")
    mac("SSACalHi", f"{Decimal(cal['interval_6K_plus_lambda_plus_2pi_mu'][1]):.8f}")
    mac("SSAWtri", "-4.1504128076789633794")
    mac("SSACalWidth", cal["interval_width"])
    mac("SSACalOffLo", f"{float(lo):.2e}")
    mac("SSACalOffHi", f"{float(hi):.2e}")
    mac("SSANegSquare", cal["negative_controls"]["square_lattice_W"]["value"])
    mac("SSANegNoTwoPi", cal["negative_controls"]["triangular_SS_normalized_no_2pi_scaling"]["value"])
    mac("SSANegShift", cal["negative_controls"]["triangular_missing_quarter_log_2pi_shift"]["value"])
    mac("SSAEwaldDiff", cal["pos_ctl_ewald_vs_closed_form_absdiff"])
    mac("SSASSTri", cal["pos_ctl_SS_normalized_tri (SS Remark 1.5 says ~ -0.2011)"])
    mac("SSASSSq", cal["pos_ctl_SS_normalized_square (SS Remark 1.5 says ~ -0.1958)"])
    mac("SSACdiff", cal["C_absdiff"])
    cr = json.loads((DATA / "s2_audit/constants_reimpl.out.json").read_text())
    bl = json.loads((DATA / "s2_audit/bl_check.out.json").read_text())
    mac("SSAReLam", sig(cr["main"]["lambda"], 12))
    mac("SSAReMu", sig(cr["main"]["mu"], 12))
    mac("SSAReK", sig(cr["main"]["K"], 9))
    mac("SSAReG", sci(cr["main"]["G_at_x0"], 4, absolute=True))
    mac("SSAReId", sci(cr["main"]["identity_minus_W_tri"], 4))
    mac("SSAReNoAngLam", sig(cr["NEG_no_angular_e"]["lambda"], 7))
    mac("SSAReNoAngK", sig(cr["NEG_no_angular_e"]["K"], 5))
    mac("SSAReDropLam", sig(cr["NEG_drop_mode_m1"]["lambda"], 7))
    mac("SSAReDropK", sig(cr["NEG_drop_mode_m1"]["K"], 4))
    mac("SSABl", sig(bl["B_l"], 12))
    mac("SSAClOne", sig(bl["c1"], 6))
    mac("SSABlNegA", sig(bl["neg_ctl_drop_m1"]["value"], 5))
    mac("SSABlNegB", sig(bl["neg_ctl_wrong_a"]["value"], 5))

    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.4))
    labels = ["square lattice", "no 2pi scaling", "1/4 log 2pi shift dropped"]
    vals_a = [off["square_lattice_W"], off["triangular_SS_normalized_no_2pi_scaling"], off["triangular_missing_quarter_log_2pi_shift"]]
    half = float(max(-lo, hi))
    ya = [2, 1, 0]
    ax[0].scatter(vals_a, ya, color=OKABE["verm"], s=20, zorder=3)
    ax[0].axvline(half, color=OKABE["blue"], lw=1, ls="--")
    ax[0].text(half * 1.5, 2.45, "half-width of the\ncertificate interval", color=OKABE["blue"], fontsize=6.5, va="top")
    ax[0].set_xscale("log")
    ax[0].set_xlim(1e-7, 1e2)
    ax[0].set_ylim(-0.6, 2.6)
    ax[0].set_yticks(ya, labels, fontsize=6.5)
    ax[0].set_xlabel("|value - W(E_tri)|")
    ax[0].set_title("(a) calibration identity: wrong normalisations", fontsize=7.5)
    items = [("main", cr["main"]), ("no angular term e", cr["NEG_no_angular_e"]), ("mode m=1 dropped", cr["NEG_drop_mode_m1"])]
    y2 = [2, 1, 0]
    for yi, (lab, d) in zip(y2, items):
        v = abs(float(d["identity_minus_W_tri"]))
        ax[1].scatter([v], [yi], color=OKABE["blue"] if lab == "main" else OKABE["verm"], s=20, zorder=3)
    ax[1].set_xscale("log")
    ax[1].set_xlim(1e-28, 1e0)
    ax[1].set_ylim(-0.6, 2.6)
    ax[1].set_yticks(y2, [i[0] for i in items], fontsize=6.5)
    ax[1].set_xlabel("|6K+lambda+2 pi mu - W(E_tri)|")
    ax[1].set_title("(b) independent re-implementation", fontsize=7.5)
    fig.tight_layout()
    fig.savefig(GEN / "fig_calibration.pdf")
    plt.close(fig)

    # ---- LeanFlow runs
    lf = json.loads((DATA / "lean_data_certificates/summary.json").read_text())
    mac("SSALFPosAcc", str(lf["positive_run"]["n_accepted"]))
    mac("SSALFPosN", str(lf["positive_run"]["n_assertions"]))
    mac("SSALFNegAcc", str(lf["negctl_run"]["n_accepted"]))
    mac("SSALFNegN", str(lf["negctl_run"]["n_assertions"]))
    resn = json.loads((DATA / "lean_data_certificates/result_negctl_run.json").read_text())
    failed_labels = [a["label"] for a in resn["assertions"] if not a["lean_accepted"]]
    assert len(failed_labels) == len(lf["negctl_run"]["failed"]), failed_labels
    (GEN / "lf_failed.txt").write_text("\n".join(failed_labels) + "\n")
    mac("SSALFFailedList", "; ".join(f"\\texttt{{{l.replace('_', chr(92) + '_')}}}" for l in failed_labels).replace("&", "\\&"))
    mac("SSALFNFailed", str(len(failed_labels)))
    mac("SSALFCommit", LEANFLOW_COMMIT)
    mac("SSALFLean", lf["positive_run"]["lean_version"].split(",")[0].replace("Lean (", "Lean ").replace("version ", ""))
    prov = json.loads((DATA / "leanflow_provenance.json").read_text())
    mac("SSALFBranch", prov["branch"])
    pt = (RERUN / "leanflow_pytest.txt").read_text()
    m = re.search(r"(\d+) passed in ([0-9.]+)s", pt)
    mac("SSALFPassed", m.group(1) if m else "?")
    mac("SSALFPytestTime", m.group(2) if m else "?")
    pl = (DATA / "leanflow_pinned_tests.log").read_text().strip().splitlines()[-1]
    mp = re.match(r"(\d+) passed, (\d+) deselected", pl)
    assert mp, pl
    mac("SSALFPinnedLog", f"{mp.group(1)} passed, {mp.group(2)} deselected")
    mac("SSALFNotPinned", str(int(m.group(1)) - int(mp.group(1))))
    mac("SSALFNNew", "6")
    mac("SSALFOldCommit", LEANFLOW_OLD_COMMIT)
    mac("SSALFFixCommit", LEANFLOW_FIX_COMMIT)
    mac("SSAShaMainOld", sha_file(DATA / "before_revision/SandierSerfatyStatement.lean"))

    # ---- audit tallies (from REDUCTION_AUDIT.md tables)
    audit = (DATA / "REDUCTION_AUDIT.md").read_text()
    rows_all = re.findall(r"^\| ([RGKT]\d+) \|.*\| ([A-Z_]+(?: \([^)]*\))?) \|$", audit, flags=re.M)
    counts = {"R": 0, "G": 0, "K": 0, "T": 0}
    for rid, verdict in rows_all:
        counts[rid[0]] += 1
        assert verdict.startswith("CONFIRMED"), (rid, verdict)
    mac("SSAnR", str(counts["R"]))
    mac("SSAnG", str(counts["G"]))
    mac("SSAnK", str(counts["K"]))
    mac("SSAnT", str(counts["T"]))
    mac("SSAnSteps", str(sum(counts.values())))
    assert counts == {"R": 10, "G": 7, "K": 8, "T": 6}, counts

    # ---- ledger gate (run ledger/build_ledger.py and ledger/run_gate.py first)
    led = json.loads((HERE / "ledger/ledger.json").read_text())["claims"]
    mac("SSALedgerN", str(len(led)))
    for t in "ALCX":
        mac(f"SSALedger{t}", str(sum(1 for c in led if c["tier"] == t)))
    gate = (HERE / "ledger/gate_output.txt").read_text()
    mac("SSAGateExit", re.search(r"exit_code=(\d+)", gate).group(1))
    mac("SSAGateFlag", str(len(re.findall(r"^\s*flag\s", gate, flags=re.M))))
    mac("SSAGateBlock", str(len(re.findall(r"^\s*block\s", gate, flags=re.M))))
    mac("SSAGateOther", str(len([ln for ln in gate.splitlines() if ln.strip() and not ln.lstrip().startswith(("flag", "block", "exit_code"))])))

    # ---- write numbers
    lines =["% generated by gen_inputs.py; do not edit"]
    for k, v in macros.items():
        lines.append(f"\\newcommand{{\\{k}}}{{{v}}}")
    (HERE / "gen_numbers.tex").write_text("\n".join(lines) + "\n")
    (GEN / "gen_log.json").write_text(json.dumps({"macros": macros, "pairs_equal": n_equal, "fit": {
        "er0": er0, "eri": eri, "m_star": m_star, "m_drop": m_drop}}, indent=1))
    print(f"macros {len(macros)}; pairs equal {n_equal}/{len(record_pairs)}; defs lines {n_defs}; lemma lines {n_lem}; controls lines {n_ctl}")
    print(f"fit er0={er0:.3f} eri={eri:.3f} m*={m_star:.2f} A_pred={fa_pred:.1f} obs={fa_obs}; m_drop={m_drop:.3f} B_pred={b_pred} obs={b_obs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
