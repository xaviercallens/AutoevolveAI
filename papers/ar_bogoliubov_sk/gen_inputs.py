"""Generate every number, Lean listing and axiom transcript that main.tex prints (lane H8, bogoliubov_sk).

Inputs (read-only): data/*.json (Stage 2 numerics, copied from the rusty-SUNDIALS worktree), the claimed Lean module and
its controls in results/autoresearch/2026-10-25/H8/contribution/, the compile transcripts there (producer run and the
paper-stage recompile), and the owner's QuantumFluids lean_src/DualLength.lean.
Outputs (this directory): gen_numbers.tex, gen/*.lean (verbatim excerpts, proofs elided), gen/*.lst (same text with
non-ASCII escaped for listings), gen/axioms_*.txt (verbatim #print axioms output).
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
C8 = W / "results/autoresearch/2026-10-25/H8/contribution"
LEAN = C8 / "Autoresearch_SkBoundShape.lean"
CTL = C8 / "Autoresearch_SkBoundShapeControls.lean"
OWNER = Path("/mnt/disks/disk-socrateai-local-1/leanmaster/SocrateAI-Scientific-QuantumFluids/lean_src/DualLength.lean")

UMAP = {
    "ℝ": r"$\mathbb{R}$", "→": r"$\to$", "≤": r"$\le$", "≥": r"$\ge$", "≠": r"$\ne$", "↔": r"$\leftrightarrow$",
    "¬": r"$\neg$", "√": r"$\surd$", "ε": r"$\varepsilon$", "₀": r"$_0$", "²": r"$^2$", "·": r"$\cdot$",
    "ħ": r"$\hbar$", "∀": r"$\forall$", "ℓ": r"$\ell$", "∘": r"$\circ$", "≡": r"$\equiv$", "ᵢ": r"$_i$",
    "∞": r"$\infty$", "−": "-", "–": "--", "…": "...", "′": "'", "⇔": r"$\Leftrightarrow$", "₂": r"$_2$",
    "³": r"$^3$", "α": r"$\alpha$", "ξ": r"$\xi$", "⟨": r"$\langle$", "⟩": r"$\rangle$",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def e(x: float, d: int = 1) -> str:
    if x == 0:
        return "0"
    m, ex = f"{x:.{d}e}".split("e")
    return rf"{m}\times10^{{{int(ex)}}}"


def extract(src: list[str], name: str, kind: str) -> list[str]:
    pat = re.compile(rf"^(theorem|lemma|noncomputable def|def) {re.escape(name)}(\s|$)")
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


def axiom_lines(stdout: str) -> list[str]:
    return [l.strip() for l in stdout.replace("\n ", " ").split("\n") if "depends on axioms" in l]


def main() -> int:
    GEN.mkdir(exist_ok=True)
    src = LEAN.read_text().splitlines()
    own = OWNER.read_text().splitlines()
    blocks = {
        "defs": [("epsFree", "def"), ("epsBog", "def"), ("sBog", "def")],
        "round1": [("bogoliubovSq_pos", "t"), ("epsBog_sq", "t"), ("sBog_pos", "t"), ("sBog_sq", "t"),
                   ("sBog_sq_le", "t"), ("sBog_le_sqrt", "t"), ("sBog_sq_eq_iff", "t"), ("feynman_sBog_exact", "t"),
                   ("sBog_sq_le_via_project", "t"), ("free_S_one_violates", "t")],
        "shape": [("sBog_eq_closed", "t"), ("sBog_sq_lt_sq", "t"), ("sBog_strictMonoOn", "t"), ("sBog_lt_phonon", "t"),
                  ("phonon_lower_lt_sBog", "t"), ("sBog_lt_one", "t"), ("one_sub_sBog_le", "t"),
                  ("sBog_tendsto_one", "t"), ("epsBog_eq_epsFree_div_sBog", "t")],
        "test": [("diffraction_test_model", "t"), ("diffraction_test_dispersion", "t"), ("peak_sqrt_iff_sq", "t"),
                 ("diffraction_fires_free_at_selfdual", "t"), ("diffraction_silent_on_sBog", "t"),
                 ("free_S_one_violates_phonon", "t"), ("nonvacuous_selfdual", "t")],
    }
    used: set[str] = set()
    ndecl = 0
    for key, decls in blocks.items():
        lines: list[str] = []
        for name, kind in decls:
            lines += extract(src, name, kind) + [""]
            ndecl += kind == "t"
        txt = "\n".join(lines).rstrip() + "\n"
        used |= {c for c in txt if ord(c) > 127}
        (GEN / f"{key}.lean").write_text(txt)
    own_lines: list[str] = []
    for name, kind in [("bogoliubovSq", "def"), ("ell", "def"), ("dualLength", "def"), ("ell_ge", "t"),
                       ("feynman_ge_iff", "t"), ("not_bogoliubov_of_structure_factor", "t")]:
        own_lines += extract(own, name, kind) + [""]
    t = "\n".join(own_lines).rstrip() + "\n"
    used |= {c for c in t if ord(c) > 127}
    (GEN / "owner.lean").write_text(t)
    ctl = CTL.read_text()
    used |= {c for c in ctl if ord(c) > 127}
    (GEN / "controls.lean").write_text(ctl)
    missing = sorted(c for c in used if c not in UMAP)
    if missing:
        raise SystemExit(f"unmapped codepoints: {[hex(ord(c)) + ' ' + c for c in missing]}")
    for f in sorted(GEN.glob("*.lean")):
        s = f.read_text()
        for c in used:
            s = s.replace(c, "(*@" + UMAP[c] + "@*)")
        f.with_suffix(".lst").write_text(s)

    comp = {k: json.loads((C8 / f).read_text()) for k, f in [
        ("prod", "compile_main.json"), ("prodctl", "compile_controls.json"),
        ("re", "paper_recompile_main.json"), ("rectl", "paper_recompile_controls.json")]}
    allow = {"propext", "Classical.choice", "Quot.sound"}
    stats = {}
    for k, j in comp.items():
        lines = axiom_lines(j["stdout"])
        (GEN / f"axioms_{k}.txt").write_text("\n".join(lines) + "\n" + (j["stderr"] or ""))
        outside = []
        for l in lines:
            ax = l.split("depends on axioms:")[1].strip().strip("[]")
            outside += [a.strip() for a in ax.split(",") if a.strip() not in allow]
        stats[k] = {"rc": j["rc"], "n": len(lines), "outside": outside, "sha": j["sha256"], "sec": j["seconds"],
                    "warn": j["stdout"].count("warning") + (j["stderr"] or "").count("warning")}
    assert stats["prod"]["sha"] == stats["re"]["sha"] == sha(LEAN), "claimed file changed since compile"
    assert stats["prodctl"]["sha"] == stats["rectl"]["sha"] == sha(CTL)
    assert stats["re"]["rc"] == 0 and stats["re"]["n"] == 26 and not stats["re"]["outside"]
    assert stats["prod"]["n"] == 26 and not stats["prod"]["outside"]
    assert "sorryAx" in stats["rectl"]["outside"] and any("ctl_cheat" in a for a in stats["rectl"]["outside"])
    assert ndecl == 26
    grep_bad = [l for l in src if re.search(r"\b(sorry|admit|native_decide)\b", l) or re.match(r"^\s*axiom\b", l)]
    assert not grep_bad, grep_bad

    s = json.loads((DATA / "linear_response_summary.json").read_text())
    g = s["gates"]
    he = json.loads((DATA / "helium_tier_l.json").read_text())
    cx = json.loads((DATA / "crosscheck_rust_numpy.json").read_text())
    hfs = json.loads((DATA / "hf_search.json").read_text())
    card = json.loads((DATA / "hf_neutron_card.json").read_text())
    lr = json.loads((DATA / "linear_response.json").read_text())
    assert s["all_pass"] is True
    big = max(f["size"] for f in card["files"])
    dtc = {round(r["x"], 2): r for r in s["dt_convergence"]}
    ref = s["dt_convergence_reference"][0]
    nm = {
        "LeanSha": sha(LEAN), "LeanShaShort": sha(LEAN)[:12], "CtlSha": sha(CTL), "CtlShaShort": sha(CTL)[:12],
        "OwnerSha": sha(OWNER), "OwnerShaShort": sha(OWNER)[:12],
        "NDecl": str(stats["re"]["n"]), "ProdSec": f"{stats['prod']['sec']:.1f}", "ReSec": f"{stats['re']['sec']:.1f}",
        "ReCtlSec": f"{stats['rectl']['sec']:.1f}",
        "GPhase": e(g["pos_phase_g1_max_rel_err_vs_epsB"]["value"], 2),
        "GDensity": e(g["pos_density_g1_max_rel_err_vs_epsB"]["value"], 2),
        "GAmp": e(g["pos_S_amp_vs_S_freq_max_rel"]["value"], 2),
        "GZero": e(g["neg_g0_max_rel_err_vs_eps0"]["value"], 2),
        "GZeroDist": f"{g['neg_g0_min_rel_distance_from_epsB_for_x_lt_1']['value']:.4f}",
        "GBound": e(g["bound_g1_max_S_over_bound_minus_1"]["value"], 3),
        "GNearOne": e(g["bound_g1_ratio_at_x_near_1_minus_1_abs"]["value"], 3),
        "GNearOneExact": e(abs(s["informational"]["exact_SB_over_bound_minus_1_at_sweep_x_nearest_1"]), 4),
        "GNearOneDiff": e(abs(abs(s["informational"]["exact_SB_over_bound_minus_1_at_sweep_x_nearest_1"])
                              - g["bound_g1_ratio_at_x_near_1_minus_1_abs"]["value"]), 1),
        "GRefAmp": f"{g['neg_reference_splitting_S_amp_vs_S_freq_max_rel']['value']:.4f}",
        "GRefOrder": f"{g['neg_reference_amp_order_max']['value']:.3f}",
        "GOrder": f"{g['pos_dt_observed_order_min_first3']['value']:.3f}",
        "GIso": e(g["pos_isotropy_max_rel_err"]["value"], 2),
        "GGs": e(g["gs_residual_max"]["value"], 2),
        "NGates": str(len(g)), "NGatesPass": str(sum(v["pass"] for v in g.values())),
        "RefEpsB": e(s["informational"]["reference_max_rel_err_vs_epsB"], 2),
        "TangFine": e(s["informational"]["S_freq_over_bound_minus_1_at_exactly_x1_finest_dt"], 2),
        "RefAmpFirst": e(ref["S_amp_rel_err"][0], 2), "RefAmpLast": e(ref["S_amp_rel_err"][-1], 2),
        "StrOneFirst": e(dtc[1.0]["rel_err"][0], 2), "StrOneLast": e(dtc[1.0]["rel_err"][-1], 2),
        "NSweep": str(len(lr["sweep_phase_g1"])) if isinstance(lr["sweep_phase_g1"], list) else "?",
        "Grid": str(lr["grid_n"]), "Periods": str(lr["periods"]), "SPP": str(lr["steps_per_period"]),
        "Eps": e(lr["eps"], 0),
        "CxOmegaMax": e(max(r["rel_diff_omega"] for r in cx), 1), "CxOmegaMin": e(min(r["rel_diff_omega"] for r in cx), 1),
        "CxAmpMax": e(max(r["rel_diff_amp"] for r in cx), 1),
        "HeKs": f"{he['k_s_inv_A']:.4f}", "HeHbarTwoM": f"{he['hbar2_over_2m_meV_A2']:.5f}",
        "HeThrQR": f"{he['threshold_at_Q_R_1.9260']:.4f}",
        "HeThrLo": f"{min(he['threshold_at_Q_R_c_minus_plus_err']):.5f}",
        "HeThrHi": f"{max(he['threshold_at_Q_R_c_minus_plus_err']):.5f}",
        "HeSilentHi": f"{he['silent_k_range_inv_A'][1]:.2f}", "HeFirstUnd": f"{he['first_undecided_k']:.2f}",
        "HeNSilent": str(he["n_silent"]), "HeNUnd": str(he["n_undecided"]), "HeNRows": str(len(he["rows"])),
        "HeSupRoton": f"{he['threshold_at_roton']['S_up_feynman']:.2f}",
        "HeThrRotonTab": f"{he['threshold_at_roton']['sqrt_k_over_2ks']:.4f}",
        "HeRotonK": f"{he['threshold_at_roton']['k']:.2f}",
        "HeNoErrK": ", ".join(f"{r['k']:.2f}" for r in he["rows"] if r["err"] == 0.0 and r["silent"]),
        "HeNoErrMargins": "; ".join(f"{r['S_up']:.4f} vs {r['threshold']:.4f}" for r in he["rows"]
                                    if r["err"] == 0.0 and r["silent"]),
        "HeEpsRatio": f"{he['threshold_at_roton']['eps_over_epsB']:.3f}",
        "HeEpsRatioMin": f"{min(r['eps_over_epsB'] for r in he['rows']):.3f}",
        "HeMarginS": f"{he['margin_at_k_0.5']['S_up_strict']:.4f}", "HeMarginT": f"{he['margin_at_k_0.5']['threshold']:.4f}",
        "HePhonRel": f"{100 * he['phonon_check']['rel_diff']:.2f}",
        "HFQueries": str(len(hfs)), "HFId": card["repo"].replace("_", r"\_").replace("/", r"/\allowbreak{}").replace("-", r"-\allowbreak{}"), "HFSha": card["sha"],
        "HFBig": f"{big / 1e9:.2f}",
    }
    for k, v in nm.items():
        if not re.fullmatch(r"[A-Za-z]+", k):
            raise SystemExit(f"bad macro name {k}")
    (HERE / "gen_numbers.tex").write_text("% generated by gen_inputs.py; do not edit\n" + "".join(
        rf"\newcommand{{\{k}}}{{{v}}}" + "\n" for k, v in nm.items()))
    print(json.dumps({"stats": stats, "n_macros": len(nm)}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
