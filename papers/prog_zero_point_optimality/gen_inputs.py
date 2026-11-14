"""Generate every number, Lean listing, axiom transcript and table that main.tex prints (programme P2, zero-point energy).

Inputs (read-only): data/*.json|csv (copied from results/programmes/2026-10-25/P2/ and its g2/ folder), the Lean sources in
formal_cert/Programmes/ZeroPoint/, the ledger gate output in ledger/. Outputs (this directory): gen_numbers.tex (macros),
gen/*.lst (verbatim Lean statements, non-ASCII escaped for listings), gen/axioms_*.txt, gen/table_*.tex.
Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I gen_inputs.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = HERE.parents[1]
DATA = HERE / "data"
GEN = HERE / "gen"
LEAN_DIR = W / "formal_cert/Programmes/ZeroPoint"
BASIC = LEAN_DIR / "Basic.lean"
CTL = LEAN_DIR / "Controls.lean"
# sha256 values recorded in results/programmes/2026-10-25/P2/PROOF.md when the files were compiled
RECORDED_SHA = {
    "Basic.lean": "7d59f1817767ae64cc37d017348e1eb5f5b9ed83ed068086fae839baff0d64f0",
    "Controls.lean": "c725bdcba93362681c58f65eaf00d717eea37254c10f364bab4e039d645acd90",
}
RUSTY = {
    "gate": "a961a714dd040ad1e1a542db1efc54e0401cd55b",
    "edge": "5f2f73b8c636c4ae45a43ad67c99621acc609660",
    "spectral": "6ad3cf7e5e171479d1481e5fd17e7d432aae21d1",
    "harden": "609338e6485fc96002e4c60c0c3e34f9130c0108",  # audit N7: ezp_gauss_duffy_stable / DuffyResult::is_stable
}

UMAP = {
    "ℝ": r"$\mathbb{R}$", "ℂ": r"$\mathbb{C}$", "→": r"$\to$", "∀": r"$\forall$", "≤": r"$\le$", "≥": r"$\ge$",
    "∈": r"$\in$", "²": r"$^2$", "³": r"$^3$", "⁴": r"$^4$", "⁻": r"$^{-}$", "¹": r"$^{1}$", "√": r"$\surd$",
    "ρ": r"$\rho$", "τ": r"$\tau$", "γ": r"$\gamma$", "α": r"$\alpha$", "ξ": r"$\xi$", "π": r"$\pi$", "Δ": r"$\Delta$",
    "∇": r"$\nabla$", "∘": r"$\circ$", "¬": r"$\neg$", "∧": r"$\wedge$", "∞": r"$\infty$", "≠": r"$\ne$", "·": r"$\cdot$",
    "⟨": r"$\langle$", "⟩": r"$\rangle$", "₁": r"$_1$", "₂": r"$_2$", "ₓ": r"$_x$", "ᵧ": r"$_y$", "ᶠ": r"$^f$",
    "×": r"$\times$", "∃": r"$\exists$", "↦": r"$\mapsto$", "–": "--", "—": "---", "′": r"$'$", "≈": r"$\approx$",
    "∑": r"$\sum$", "∂": r"$\partial$", "⁻¹": r"$^{-1}$", "°": r"$^\circ$", "θ": r"$\theta$", "λ": r"$\lambda$",
    "‖": r"$\Vert$", "⊤": r"$\top$", "∃": r"$\exists$", "↔": r"$\leftrightarrow$", "←": r"$\leftarrow$", "⁼": "=", "∣": r"$\mid$",
}

N: dict[str, str] = {}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tex_sci(x: float, d: int = 2, plus: bool = False) -> str:
    """Scientific notation as LaTeX math (no $)."""
    if x == 0:
        return "0"
    m, ex = f"{x:.{d}e}".split("e")
    s = f"{m}\\times10^{{{int(ex)}}}"
    if plus and x > 0:
        s = "+" + s
    return s


def tex_fix(x: float, d: int, plus: bool = False) -> str:
    s = f"{x:+.{d}f}" if plus else f"{x:.{d}f}"
    return s.replace("-", "$-$") if False else s


def put(k: str, v: str) -> None:
    N[k] = v


def load(name: str) -> object:
    return json.loads((DATA / name).read_text())


def read_csv(name: str) -> list[dict[str, float | str]]:
    out = []
    with (DATA / name).open() as fh:
        for r in csv.DictReader(fh):
            out.append({k: (v if k == "pot" else float(v)) for k, v in r.items()})
    return out


# ---------------------------------------------------------------- Lean listings
def statement(src: list[str], name: str, full: bool = False) -> list[str]:
    pat = re.compile(rf"^(theorem|lemma|noncomputable def|def|axiom) {re.escape(name)}(?![\w'])")
    for i, line in enumerate(src):
        if not pat.match(line):
            continue
        out: list[str] = []
        j = i
        if line.startswith(("noncomputable def", "def", "axiom")) or full:
            while j < len(src) and src[j].strip():
                out.append(src[j])
                j += 1
            return out
        while j < len(src):
            l = src[j]
            if ":=" in l:
                out.append(l[: l.index(":=") + 2] + " ... -- proof elided")
                return out
            out.append(l)
            j += 1
    raise SystemExit(f"declaration {name} not found")


def block(src: list[str], names: list[str | tuple[str, bool]]) -> str:
    lines: list[str] = []
    for n in names:
        nm, full = (n, False) if isinstance(n, str) else n
        lines += statement(src, nm, full) + [""]
    return "\n".join(lines).rstrip() + "\n"


def lean_listings() -> None:
    basic = BASIC.read_text().splitlines()
    ctl = CTL.read_text().splitlines()
    texts = {
        "s1": block(basic, ["Q", "hasDerivAt_Q_x", "hasDerivAt_Q_y", "hasDerivAt_Qx_x", "hasDerivAt_Qy_y"]),
        "s2": block(basic, ["lap_Q", "grad_Q"]),
        "s3": block(basic, ["lap_comp"]),
        "s4": block(basic, ["gauss_f'", "gauss_h", "m2f", "m2f'", "m2_f'", "m2_h"]),
        "s5": block(basic, ["rho", "rho_sq", "sqrt3_half_sq", ("gamma_fixes_rho", True), "rho_sq_mul_rot", "hasDerivAt_gamma"]),
        "s6": block(basic, ["rot120_comm_symm", ("rot120_fixed_vec", True)]),
        "s7": block(basic, ["deriv_at_one_of_inversion"]),
        "controls": "\n".join(l for l in ctl if l.startswith(("theorem", "axiom", "    ", "  intro", "  have", "  norm_num")) and not l.startswith("/")) + "\n",
    }
    # the controls file is short: print its declarations whole
    cl: list[str] = []
    for nm in ("ctl_sorry", "ctl_cheat", "ctl_axiom", "lap_wrong_false"):
        kind_full = True
        cl += statement(ctl, nm, kind_full) + [""]
    texts["controls"] = "\n".join(cl).rstrip() + "\n"
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


def strip_paths(s: str) -> str:
    return s.replace(str(W) + "/", "")


def axiom_lines(out: str) -> list[str]:
    return [l for l in strip_paths(out).splitlines() if "depends on axioms" in l]


def lean_status() -> None:
    lb = load("lean_basic.json")
    lc = load("lean_controls.json")
    rb = load("rerun_basic.json")
    rc = load("rerun_controls.json")
    for nm, j in (("axioms_basic", lb), ("axioms_controls", lc), ("axioms_rerun_basic", rb), ("axioms_rerun_controls", rc)):
        (GEN / f"{nm}.txt").write_text(f"rc = {j['rc']}, {j.get('seconds')} s\n" + strip_paths(j["output"]))
    allow = {"propext", "Classical.choice", "Quot.sound"}
    lines = axiom_lines(lb["output"])
    ok = 0
    for l in lines:
        ax = set(re.findall(r"\[(.*)\]", l)[0].split(", "))
        ok += int(ax <= allow)
    put("LeanNThm", str(len(lines)))
    put("LeanNInAllow", str(ok))
    put("LeanRc", str(lb["rc"]))
    put("LeanSecs", f"{lb['seconds']}")
    put("LeanRerunRc", str(rb["rc"]))
    put("LeanRerunSecs", f"{rb['seconds']}")
    put("LeanRerunCtlRc", str(rc["rc"]))
    same_b = axiom_lines(lb["output"]) == axiom_lines(rb["output"])
    same_c = axiom_lines(lc["output"]) == axiom_lines(rc["output"])
    put("LeanRerunSameBasic", "identical to" if same_b else "DIFFERENT from")
    put("LeanRerunSameCtl", "identical to" if same_c else "DIFFERENT from")
    if not (same_b and same_c):
        raise SystemExit("rerun axiom output differs from the recorded one")
    sb, sc = sha(BASIC), sha(CTL)
    put("ShaBasic", sb)
    put("ShaCtl", sc)
    put("ShaMatch", "match" if (sb == RECORDED_SHA["Basic.lean"] and sc == RECORDED_SHA["Controls.lean"]) else "DO NOT MATCH")
    put("LeanSorryCount", str(BASIC.read_text().count("sorry")))
    ctl_l = axiom_lines(lc["output"])
    put("LeanCtlSorryAx", "yes" if any("ctl_sorry" in l and "sorryAx" in l for l in ctl_l) else "NO")
    put("LeanCtlAxiom", "yes" if any("ctl_axiom" in l and "ctl_cheat" in l for l in ctl_l) else "NO")
    put("LeanCtlWrongOk", "yes" if any("lap_wrong_false" in l and set(re.findall(r"\[(.*)\]", l)[0].split(", ")) <= allow for l in ctl_l) else "NO")
    el = load("elenchus_check.json")
    put("ElenchusSeedRc", str(el["rc"]))
    ctest = (DATA / "rerun_cargo_test.txt").read_text()
    m = re.search(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored", ctest)
    put("CargoPassed", m.group(1))
    put("CargoFailed", m.group(2))
    put("CargoIgnored", m.group(3))
    rtest = (DATA / "revise_cargo_test.txt").read_text()
    m2 = re.search(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored", rtest)
    put("ReviseCargoPassed", m2.group(1))
    put("ReviseCargoFailed", m2.group(2))
    put("ReviseCargoIgnored", m2.group(3))
    assert "fmt_exit=0" in (DATA / "revise_cargo_fmt.txt").read_text() and "clippy_exit=0" in (DATA / "revise_cargo_clippy.txt").read_text()


# ---------------------------------------------------------------- numerics
def numerics() -> None:
    mech = load("mechanism.json")
    pc = load("poisson_check.json")
    scan = load("scan_summary_cm.json")
    edge = load("edge_check.json")
    ctrl = load("controls.json")
    el = load("elastic_check.json")
    sumr = load("sumrule_identity.json")

    # headline (Duffy)
    summ = {(s["pot"], round(s["x"], 4), round(s["y"], 4)): s for s in pc["summary"]}
    tri = summ[("gauss:1", 0.5, 0.866)]
    head = summ[("gauss:1", 0.5, 0.966)]
    marg = summ[("gauss:1", 0.295, 0.9555)]
    c3 = summ[("gauss:1", 0.3, 0.9539)]
    put("EzpTri", f"{tri['ezp_duffy128']:.10f}")
    put("EzpHead", f"{head['ezp_duffy128']:.10f}")
    put("dEHead", tex_sci(head["dEzp_vs_tri"], 4))
    put("dEHeadShort", tex_sci(head["dEzp_vs_tri"], 2))
    put("QuadErr", tex_sci(max(tri["duffy_conv_96_128"], head["duffy_conv_96_128"]), 1))
    put("RatioTri", f"{tri['min_ratio']:.5f}")
    put("RatioHead", f"{head['min_ratio']:.5f}")
    case_head = next(c for c in pc["cases"] if c["pot"] == "gauss:1" and abs(c["y"] - 0.966025403784) < 1e-9)
    case_tri = next(c for c in pc["cases"] if c["pot"] == "gauss:1" and abs(c["y"] - 0.8660254037844386) < 1e-9)
    put("LWHead", f"{case_head['stability']['longwave_min_ratio']['0.003']:.4f}")
    put("LWTri", f"{case_tri['stability']['longwave_min_ratio']['0.003']:.4f}")
    el_lookup = {(e["pot"], round(e["x"], 3), round(e["y"], 3)): e for e in el}
    put("LWHeadExact", f"{el_lookup[('gauss:1', 0.5, 0.966)]['rc400']['min_lam']:.4f}")
    put("LWTriExact", f"{el_lookup[('gauss:1', 0.5, 0.866)]['rc400']['min_lam']:.4f}")
    put("LWSqGaussOne", f"{el_lookup[('gauss:1', 0.0, 1.0)]['rc400']['min_lam']:.4f}")
    put("dEMarg", tex_sci(marg["dEzp_vs_tri"], 3))
    put("RatioMarg", tex_sci(marg["min_ratio"], 3))
    lw_m = next(e for k, e in el_lookup.items() if k[0] == "gauss:1" and abs(k[1] - 0.295) < 1e-3)
    put("MargLW", tex_sci(lw_m["rc400"]["min_lam"], 3))
    put("MargFrac", f"{100 * lw_m['rc400']['min_lam'] / el_lookup[('gauss:1', 0.5, 0.866)]['rc400']['min_lam']:.2f}")
    put("MargConv", tex_sci(marg["duffy_conv_96_128"], 1))
    put("dEthree", tex_sci(c3["dEzp_vs_tri"], 3))
    # Rust n=768
    rt = read_csv("rust_curv/rust_fine_tri.csv")
    rh = read_csv("rust_curv/rust_fine_c1.csv")
    rt768 = next(r for r in rt if int(r["n"]) == 768)["e_zp"]
    rh768 = next(r for r in rh if int(r["n"]) == 768)["e_zp"]
    put("RustTri", f"{rt768:.9f}")
    put("RustHead", f"{rh768:.9f}")
    put("RustDiffTri", tex_sci(abs(rt768 - tri["ezp_duffy128"]), 1))
    put("RustDiffHead", tex_sci(abs(rh768 - head["ezp_duffy128"]), 1))
    # k-grid error at n=96 (G1)
    g1 = scan["gauss:1"]
    put("KgridErrOne", tex_sci(abs(g1["kgrid_err_n96_tri"]), 1))
    put("MarginRatio", f"{abs(head['dEzp_vs_tri']) / abs(g1['kgrid_err_n96_tri']):.0f}")
    kexp = [v["kgrid_exponent_tri"] for k, v in scan.items() if k in {p for p in scan}]
    put("KgridExpMin", f"{min(kexp):.2f}")
    put("KgridExpMax", f"{max(kexp):.2f}")
    put("KgridErrMin", tex_sci(min(abs(v["kgrid_err_n96_tri"]) for v in scan.values()), 1))
    put("KgridErrMax", tex_sci(max(abs(v["kgrid_err_n96_tri"]) for v in scan.values()), 1))
    # rerun of the Rust headline at paper stage
    rr = json.loads((DATA / "rerun_duffy_headline.txt").read_text().strip().splitlines()[-1])
    rr_tri = json.loads((DATA / "rerun_duffy_tri.txt").read_text().strip().splitlines()[-1])
    rc_ = json.loads((DATA / "rerun_curv.txt").read_text().strip().splitlines()[-1])
    put("RerunEzpHead", f"{rr['e_zp']:.12f}")
    put("RerunEzpTri", f"{rr_tri['e_zp']:.12f}")
    put("RerundE", tex_sci(rr["e_zp"] - rr_tri["e_zp"], 4))
    put("RerunC", f"{rc_['c']:.6f}")
    # largest-margin and 12-potential table (robust values)
    pots = ["dipolar:0.1", "dipolar:0.5", "gauss:0.25", "gauss:0.5", "gauss:1", "gauss:2", "gauss:4", "riesz:3", "riesz:4",
            "riesz:6", "yukawa:1", "yukawa:2"]
    rows: list[str] = []
    robust: list[float] = []
    two_comp: list[str] = []
    refuted: list[str] = []
    survive: list[str] = []
    for p in pots:
        e = edge[p]
        best: tuple[float, float, float, str] | None = None
        by_pt: dict[tuple[float, float], dict[int, dict]] = {}
        for c in e["candidates"]:
            if c["rc"] == 400:
                by_pt.setdefault((c["x"], c["y"]), {})[c["n"]] = c
        for (x, y), d in by_pt.items():
            if all(n in d and d[n]["stable"] for n in (96, 192, 384)):
                v = d[384]["dEzp"]
                if best is None or v < best[0]:
                    best = (v, x, y, "candidate")
        for pn, path in e["paths"].items():
            ref = {r["n"]: r for r in path["refined"]}
            if path["argmin"] is not None and all(n in ref and ref[n]["stable"] for n in (192, 384)):
                v = ref[384]["dEzp"]
                if best is None or v < best[0]:
                    best = (v, path["argmin"][0], path["argmin"][1], "dense " + pn)
        assert best is not None, p
        s = scan[p]
        ring = s["rho_rings"]["0.01"]
        verdict = "REFUTED" if best[0] < 0 else "survives"
        (refuted if best[0] < 0 else survive).append(p)
        cmin, cmax = ring["min"], ring["max"]
        loc = "max" if cmax < 0 else ("min" if cmin > 0 else "mixed")
        name = p.replace("_", r"\_")
        vtxt = "\\textbf{REFUTED}" if best[0] < 0 else "survives"
        lwc = next((e_ for k_, e_ in el_lookup.items() if k_[0] == p and abs(k_[1] - best[1]) < 2e-3 and abs(k_[2] - best[2]) < 2e-3), None)
        lwt = el_lookup[(p, 0.5, 0.866)]
        lwtxt = "--" if lwc is None else f"{100 * lwc['rc400']['min_lam'] / lwt['rc400']['min_lam']:.2f}"
        if best[0] < 0:
            robust.append(best[0])
        sgn = lambda v: ("$-$" if v < 0 else "$+$") + f"{abs(v):.2f}"
        c2 = {c_["n"]: c_ for c_ in e["candidates"] if c_["rc"] == 400 and abs(c_["x"] - 0.5) < 1e-9 and abs(c_["y"] - 0.966025403784) < 1e-9}
        c2ok = all(n in c2 and c2[n]["stable"] for n in (96, 192, 384))
        c2txt = f"${tex_sci(c2[384]['dEzp'], 2)}$" if c2ok else "unstable"
        if c2ok and c2[384]["dEzp"] < 0:
            two_comp.append(p)
        # audit C5: the gauss:1 robust minimum is the marginally stable point demoted in the text; mark it
        dag = r"$^{\dagger}$" if (p == "gauss:1" and lwc is not None and float(lwtxt) < 0.5) else ""
        rows.append(
            f"\\texttt{{{name}}} & ${tex_sci(best[0], 3)}$ & "
            f"$({best[1]:.3f},{best[2]:.4f})${dag} & {lwtxt} & {c2txt} & {vtxt} & "
            f"{sgn(cmin)}\\,\\ldots\\,{sgn(cmax)} ({loc}) \\\\")
    (GEN / "table_potentials.tex").write_text("\n".join(rows) + "\n")
    put("NRefuted", str(len(refuted)))
    put("NTested", str(len(pots)))
    put("NSurvive", str(len(survive)))
    put("NTwoComp", str(len(two_comp)))
    put("NoTwoComp", ", ".join("\\texttt{" + q + "}" for q in refuted if q not in two_comp))
    put("ListRefuted", ", ".join(r"\texttt{" + p + "}" for p in refuted))
    put("ListSurvive", ", ".join(r"\texttt{" + p + "}" for p in survive))
    gm = scan["gauss:1"]
    put("NScanPoints", str(gm["n_points"]))
    put("NStableGaussOne", str(gm["n_stable"]))
    # largest margin overall (robust)
    big = min(robust)
    put("LargestRobust", tex_sci(big, 2))
    # map statistics
    pts: dict[tuple[float, float], float] = {}
    for f in ("gauss_1__coarse.csv", "gauss_1__random.csv", "gauss_1__patch_rho.csv"):
        for r in read_csv(f):
            if int(r["n"]) == 96:
                pts[(round(float(r["x"]), 6), round(float(r["y"]), 6))] = float(r["e_zp"])
    etri = pts[(0.5, round(math.sqrt(3) / 2, 6))]
    stab = {k: v for k, v in pts.items() if not math.isnan(v)}
    comp = {k: v - etri for k, v in stab.items() if k != (0.5, round(math.sqrt(3) / 2, 6))}
    put("MapNShapes", str(len(pts)))
    put("MapNStable", str(len(stab)))
    put("MapNComp", str(len(comp)))
    put("MapNLower", str(sum(1 for v in comp.values() if v < 0)))
    put("MapMaxdE", tex_sci(max(comp.values()), 1))
    # curvature table
    sc = mech["scan"]
    cells = []
    for s in [s for s in sc if round(s["a"], 2) not in (0.45, 0.7)]:
        flag = ""
        if s["a"] <= 0.1:
            flag = "$^{\\dagger}$"
        if s["a"] >= 6:
            flag = "$^{\\ddagger}$"
        cells.append(f"{s['a']:g}{flag} & ${s['c_ezp']:+.4f}$ & ${tex_sci(s['lap_m2_exact'], 1, True)}$ & ${tex_sci(s['tri_min_ratio'], 1)}$")
    half = (len(cells) + 1) // 2
    crow = []
    for i in range(half):
        right = cells[i + half] if i + half < len(cells) else "& & &"
        crow.append(cells[i] + " & " + right + " \\\\")
    (GEN / "table_curv.tex").write_text("\n".join(crow) + "\n")
    put("CurvNA", str(len(cells)))
    roots = {round(r["bracket"][0], 2): r["root"] for r in mech["c_sign_changes"]}
    put("RootA", f"{roots[0.1]:.3f}")
    put("RootOne", f"{roots[0.35]:.5f}")
    put("RootTwo", f"{roots[1.4]:.5f}")
    put("RootLapm", f"{mech['lap_m2_sign_changes'][0]['root']:.5f}")
    # isotropy at rho (audit N3): a >= 0.5 and the a = 0.25 exception, all from mechanism.json
    iso = {p_["a"]: p_ for p_ in mech["at_G1_potentials"]}
    wide = [p_ for a_, p_ in iso.items() if a_ >= 0.5]
    rel = lambda p_: abs(p_["ezp_fxx_fyy_fxy"][0] - p_["ezp_fxx_fyy_fxy"][1]) / abs(p_["ezp_fxx_fyy_fxy"][0])
    put("IsoRelMax", tex_sci(max(rel(p_) for p_ in wide), 1))
    put("IsoXYMax", tex_sci(max(abs(p_["ezp_fxx_fyy_fxy"][2]) for p_ in wide), 1))
    put("IsoGradMax", tex_sci(max(abs(g_) for p_ in wide for g_ in p_["ezp_grad"]), 1))
    put("IsoRelQuarter", tex_sci(rel(iso[0.25]), 1))
    put("IsoGradQuarter", tex_sci(max(abs(g_) for g_ in iso[0.25]["ezp_grad"]), 1))
    cmap = {s["a"]: s["c_ezp"] for s in sc}
    put("cOne", f"{cmap[1.0]:+.3f}")
    put("cHalf", f"{cmap[0.5]:+.3f}")
    put("cQuarter", f"{cmap[0.25]:+.3f}")
    put("cTwo", f"{cmap[2.0]:+.3f}")
    put("cFour", f"{cmap[4.0]:+.3f}")
    # decomposition table
    drow = []
    for p in mech["at_G1_potentials"]:
        d = p["decomposition"]
        drow.append(f"{p['a']:g} & ${p['ezp_lap']:+.3f}$ & ${d['lin']:+.3f}$ & ${d['conc']:+.3f}$ "
                    f"& ${d['conc_diag']:+.3f}$ & ${d['conc_cross']:+.3f}$ & ${p['einstein_lap']:+.3f}$ \\\\")
    (GEN / "table_decomp.tex").write_text("\n".join(drow) + "\n")
    p1 = next(p for p in mech["at_G1_potentials"] if p["a"] == 1.0)
    put("LapOne", f"{p1['ezp_lap']:.3f}")
    put("LinOne", f"{p1['decomposition']['lin']:.3f}")
    put("ConcOne", f"{p1['decomposition']['conc']:.3f}")
    put("DecompResid", tex_sci(max(abs(p["decomposition"]["lin_plus_conc"] - p["ezp_lap_h2e-3"]) for p in mech["at_G1_potentials"]), 1))
    put("ShellFracOne", f"{100 * (p1['decomposition']['lin_by_shell'][2] + p1['decomposition']['conc_diag_by_shell'][2] + p1['decomposition']['conc_cross_by_shell'][2]) / p1['ezp_lap']:.0f}")
    # branch/shell split
    sp1 = mech["split_gauss1_c1"]
    sp2 = mech["split_gauss2_c1"]
    put("SplitLower", tex_sci(sp1["lower_branch"], 3))
    put("SplitUpper", tex_sci(sp1["upper_branch"], 3))
    put("SplitLowerZB", tex_sci(sp1["lower_branch_by_shell"][2], 3))
    put("SplitLowerLW", tex_sci(sp1["lower_branch_by_shell"][0], 2))
    put("SplitLowerMid", tex_sci(sp1["lower_branch_by_shell"][1], 3))
    put("SplitDtrD", tex_sci(sp1["d_trD_avg"], 3))
    put("SplitEinstein", tex_sci(sp1["einstein_diff"], 3))
    share = sp1["einstein_diff"] / sp1["total"]
    put("SplitEinsteinPct", f"{100 * share:.0f}")
    put("SplitJensenPct", f"{100 * (1 - share):.0f}")
    put("SplitJensen", tex_sci(sp1["total"] - sp1["einstein_diff"], 3))
    put("SplitTwoTotal", tex_sci(sp2["total"], 3))
    put("SplitTwoDtrD", tex_sci(sp2["d_trD_avg"], 3))
    put("SplitTwoUpper", tex_sci(sp2["upper_branch"], 3))
    # headline table: gauss:1 lattices (Duffy values + exact long-wave limit), and the human-check numbers
    def elk(pot: str, x: float, y: float) -> dict:
        return next(e_ for e_ in el if e_["pot"] == pot and abs(e_["x"] - x) < 2e-3 and abs(e_["y"] - y) < 2e-3)

    hrows = []
    for label, (x, y) in (("triangular $\\rho$", (0.5, 0.866)), ("$0.5+0.966025\\,i$ (headline)", (0.5, 0.966)),
                          ("$0.3+0.953939\\,i$", (0.3, 0.9539)), ("$0.295+0.9555\\,i$ ($\\dagger$)", (0.295, 0.9555))):
        sm = next(s_ for s_ in pc["summary"] if s_["pot"] == "gauss:1" and abs(s_["x"] - x) < 2e-3 and abs(s_["y"] - y) < 2e-3)
        lw = elk("gauss:1", x, y)["rc400"]["min_lam"]
        dtxt = "0" if sm["dEzp_vs_tri"] == 0 else f"${tex_sci(sm['dEzp_vs_tri'], 4)}$"
        hrows.append(f"{label} & {sm['ezp_duffy128']:.10f} & {dtxt} & {sm['min_ratio']:.5f} & {lw:.5f} \\\\")
    sq = next(s_ for s_ in pc["summary"] if s_["pot"] == "gauss:1" and s_["x"] == 0.0)
    hrows.append(f"$i$ (square, negative control) & -- & -- & ${sq['min_ratio']:+.4f}$ (unstable) & ${elk('gauss:1', 0.0, 1.0)['rc400']['min_lam']:+.4f}$ \\\\")
    (GEN / "table_head.tex").write_text("\n".join(hrows) + "\n")
    hc = load("human_check.json")
    put("HumanTri", f"{hc['triangular']['E_richardson']:.9f}")
    put("HumanHead", f"{hc['rhombic 0.5+0.966025i']['E_richardson']:.9f}")
    put("HumandE", tex_sci(hc["dE_head_vs_tri"], 4))
    put("HumanSq", f"{hc['square (negative control)']['min_lambda_over_k2_on_grid']:+.4f}")
    put("HumanRatioTri", f"{hc['triangular']['min_lambda_over_k2_on_grid']:.3f}")
    put("HumanRatioHead", f"{hc['rhombic 0.5+0.966025i']['min_lambda_over_k2_on_grid']:.3f}")
    put("HumanDiffDuffy", tex_sci(abs(hc["dE_head_vs_tri"] - head["dEzp_vs_tri"]), 1))
    # sum rule identity at a=1
    put("SumRuleNPts", str(len(sumr)))
    put("SumRuleMaxErr", tex_sci(max(abs(s["S_1"] - s["theta_1_over_2pi"]) / abs(s["S_1"]) for s in sumr), 1))
    put("SumRuleThetaHex", f"{sumr[0]['theta_1']:.10f}")
    put("SumRuleMtwoErr", tex_sci(max(abs(s["m2_pair_sum"] - s["m2_from_theta"]) / abs(s["m2_pair_sum"]) for s in sumr), 1))
    # elastic table
    erows = []
    # audit C5: same competitor as Table pot (its robust minimum), except gauss:1 where that point is the demoted marginal one
    comp_tau = {"gauss:0.5": (0.5, 1.016), "gauss:1": (0.5, 0.966)}
    for p in ["dipolar:0.1", "dipolar:0.5", "gauss:0.5", "gauss:1", "riesz:3", "riesz:4", "yukawa:1", "yukawa:2"]:
        cx, cy = comp_tau.get(p, (0.3, 0.954))
        ec = el_lookup[(p, cx, cy)]
        et = el_lookup[(p, 0.5, 0.866)]
        es = el_lookup[(p, 0.0, 1.0)]
        erows.append(f"\\texttt{{{p}}} & ${cx:g}+{cy:.3f}\\,i$ & ${tex_sci(ec['rc400']['min_lam'], 3)}$ & ${et['rc400']['min_lam']:.4f}$ & ${es['rc400']['min_lam']:+.4f}$ \\\\")
    (GEN / "table_elastic.tex").write_text("\n".join(erows) + "\n")
    put("ElasticRcDiff", tex_sci(max(abs(e["rc200"]["min_lam"] - e["rc400"]["min_lam"]) for e in el), 1))
    dropped = [(0.3, 0.954, "gauss:0.5"), (0.295, 0.956, "yukawa:1")]
    put("DroppedGaussHalf", tex_sci(el_lookup[("gauss:0.5", 0.3, 0.954)]["rc400"]["min_lam"], 2))
    put("DroppedYuk", tex_sci(el_lookup[("yukawa:1", 0.295, 0.956)]["rc400"]["min_lam"], 2))
    # controls
    put("FrozenN", str(len(ctrl["frozen_phonon"])))
    put("FrozenMax", tex_sci(ctrl["frozen_phonon_max_rel_diff"], 2))
    put("EpsteinMax", tex_sci(max(abs(e["diff"]) for e in ctrl["epstein"]), 2))
    put("EpsteinMaxHi", tex_sci(max(abs(e["diff"]) for e in ctrl["epstein"] if e["s"] >= 4), 1))
    put("DipEwaldMax", tex_sci(max(abs(e["diff"]) for e in ctrl["dipolar_static_vs_ewald"]), 2))
    cc = ctrl["cutoff_convergence"]
    rel = []
    for a in cc:
        if a["rc"] == 400:
            b = next(x for x in cc if x["rc"] == 800 and x["pot"] == a["pot"] and x["x"] == a["x"] and x["y"] == a["y"])
            rel.append(abs(a["ez"] - b["ez"]) / abs(b["ez"]))
    put("CutoffMax", tex_sci(max(rel), 1))
    mi = ctrl["modular_invariance"]
    put("ModularMax", tex_sci(max(abs(v - m[k][0]) / abs(m[k][0]) for m in mi for k in ("ez96", "ez192", "es") for v in m[k][1:]), 1))
    ic = load("independent_check.json")
    # independent numpy vs Rust: compare centred n=128 to Rust extrapolated at the triangular gauss:1 point
    put("IndepGaussTri", f"{ic[0]['n254_s0.5']['ezp']:.7f}")
    put("PoissonRealMax", tex_sci(max(c["ctl_poisson_vs_realspace_maxrel"] for c in pc["cases"]), 1))
    put("SumRuleDuffyMax", tex_sci(max(abs(c["duffy"]["128"]["trD_avg"] - c["sum_rule_exact_poisson"]) for c in pc["cases"]), 1))
    put("SumRulePRMax", tex_sci(max(abs(c["sum_rule_exact_poisson"] - c["sum_rule_exact_realspace"]) for c in pc["cases"]), 1))
    bug = [c["ctl_planted_bug_drop_c0_maxrel"] for c in pc["cases"]]
    put("BugDropMin", f"{min(bug):.3f}")
    put("BugDropMax", f"{max(bug):.1f}")
    swap_a1 = [c["ctl_planted_bug_swap_maxrel"] for c in pc["cases"] if c["pot"] == "gauss:1"]
    swap_other = [c["ctl_planted_bug_swap_maxrel"] for c in pc["cases"] if c["pot"] != "gauss:1"]
    put("BugSwapOneMax", tex_sci(max(swap_a1), 1))
    put("BugSwapOtherMin", f"{min(swap_other):.3f}")
    put("BugSwapOtherMax", f"{max(swap_other):.1f}")
    put("SqUnstable", f"{pc['summary'][4]['min_ratio']:.4f}" if pc["summary"][4]["pot"] == "gauss:1" and pc["summary"][4]["x"] == 0.0 else "n/a")
    g2c = summ[("gauss:2", 0.5, 0.966)]
    put("GaussTwoCtl", tex_sci(g2c["dEzp_vs_tri"], 3, True))
    put("GaussTwoUnstableA", "unstable" if not summ[("gauss:2", 0.295, 0.9555)]["stable"] else "STABLE")
    put("GaussTwoUnstableB", "unstable" if not summ[("gauss:2", 0.3, 0.9539)]["stable"] else "STABLE")
    allstat = all(s["static_min"]["d_es"] == 0.0 and s["static_min"]["x"] == 0.5 for s in scan.values())
    put("StaticTriAll", "all %d" % len(scan) if allstat else "NOT ALL")
    msd = load("max_stable_dist.json")  # written by max_stable_dist.py from the rusty G1 scan CSVs (audit N6)
    put("MaxStableDist", f"{msd['max_dist']:.2f}")
    # negative control
    neg = load("scan_summary_neg.json")
    nrows = []
    for k, v in neg.items():
        zp = v.get("min_d_ez_stable_competitor")
        zps = "none stable" if (zp is None or zp.get("d_ez") is None) else f"${tex_sci(zp['d_ez'], 2, True)}$ at $({zp['x']:.3f},{zp['y']:.3f})$"
        sm = v["static_min"]
        kk = k.replace("1.414213562373", "1.414").replace("_", r"\_")
        nrows.append(f"\\texttt{{{kk}}} & {'yes' if v['tri_stable'] else 'no'} & {v['n_stable']}/{v['n_points']} & ${tex_sci(sm['d_es'], 2)}$ at $({sm['x']:.3f},{sm['y']:.3f})$ & {zps} \\\\")
    (GEN / "table_neg.tex").write_text("\n".join(nrows) + "\n")
    w1 = neg["wells:1.0;1.414213562373;0.12;0.5"]
    w2 = neg["wells:1.0;1.414213562373;0.2;0.0"]
    put("WellsStatic", f"{w1['static_min']['d_es']:.3f}")
    put("WellsZp", f"{w1['min_d_ez_stable_competitor']['d_ez']:.2f}")
    put("WellsTwoZp", f"{w2['min_d_ez_stable_competitor']['d_ez']:.2f}")
    put("WellsSqStable", "stable" if w1["square_point"]["stable"] else "unstable")
    # E_static + Lambda E_zp (functional statement)
    lam = {p: scan[p]["total_min_stable"] for p in pots}
    first_loss = {}
    for p in refuted:
        for L in ("0.1", "0.3", "1.0", "3.0", "10.0"):
            if lam[p][L]["d_total"] < 0:
                first_loss[p] = L
                break
    put("LambdaFirstMin", min(first_loss.values(), key=float))
    put("LambdaFirstMax", max(first_loss.values(), key=float))
    put("LambdaSurviveAll", "all five" if all(all(lam[p][L]["d_total"] == 0 for L in lam[p]) for p in survive if p != "riesz:4") else "NOT ALL")
    # rho rings
    # stability extent
    # rust n=768 curvature brackets
    br = {}
    for a, f in ((0.35, "gauss_0.35.csv"), (0.40, "gauss_0.40.csv"), (1.50, "gauss_1.50.csv"), (1.65, "gauss_1.65.csv")):
        rows_ = [r for r in read_csv("rust_curv/" + f) if int(r["n"]) == 768]
        e0 = next(r["e_zp"] for r in rows_ if abs(r["x"] - 0.5) < 1e-9)
        e1 = next(r["e_zp"] for r in rows_ if abs(r["x"] - 0.5) > 1e-9)
        br[a] = e1 - e0
    put("BrOne", tex_sci(br[0.35], 3, True))
    put("BrTwo", tex_sci(br[0.40], 3, True))
    put("BrThree", tex_sci(br[1.50], 3, True))
    put("BrFour", tex_sci(br[1.65], 3, True))
    # small-a robustness
    sm = load("smalla_check.json")
    put("SmallaTriLam", tex_sci(next(s for s in sm if s["a"] == 0.1)["tri_elastic_min_lam"], 1))
    put("SmallaAFifteenRatio", tex_sci(next(s for s in mech["scan"] if s["a"] == 0.15)["tri_min_ratio"], 1))
    put("SmallaAHundred", f"{next(s for s in mech['scan'] if s['a'] == 0.1)['c_ezp']:.4f}")
    # first-run artefact
    v1 = load("poisson_check_v1_unbounded_optimizer.json")
    v1s = next(s for s in v1["summary"] if s["pot"] == "gauss:1" and abs(s["x"] - 0.295) < 1e-6)
    put("VoneRatio", tex_sci(v1s["min_ratio"], 2))
    # citations
    cit = load("citation_check.json")
    put("CitationAccepted", str(sum(1 for v in cit.values() if '"ACCEPTED"' in v["stdout"])))
    put("CitationN", str(len(cit)))
    put("RustyGate", RUSTY["gate"])
    put("RustyEdge", RUSTY["edge"])
    put("RustySpectral", RUSTY["spectral"])
    put("RustyGateShort", RUSTY["gate"][:7])
    put("RustyEdgeShort", RUSTY["edge"][:7])
    put("RustySpectralShort", RUSTY["spectral"][:7])
    put("RustyHarden", RUSTY["harden"])
    put("RustyHardenShort", RUSTY["harden"][:7])


def ledger_status() -> None:
    lg = HERE / "ledger/ledger.json"
    gate = HERE / "ledger/gate_output.txt"
    if not lg.exists() or not gate.exists():
        for k in ("LedgerN", "LedgerA", "LedgerL", "LedgerC", "LedgerX"):
            put(k, "?")
        put("GateExit", "?")
        put("GateBlock", "?")
        put("GateFlag", "?")
        return
    cl = json.loads(lg.read_text())["claims"]
    put("LedgerN", str(len(cl)))
    for t in "ALCX":
        put(f"Ledger{t}", str(sum(1 for c in cl if c["tier"] == t)))
    txt = gate.read_text()
    put("GateExit", re.search(r"exit_code=(\d+)", txt).group(1))
    put("GateBlock", str(len(re.findall(r"^\s*block\s", txt, re.M))))
    put("GateFlag", str(len(re.findall(r"^\s*flag\s", txt, re.M))))
    put("GateFlagKinds", ", ".join(sorted(set(re.findall(r"^\s*flag\s+(\w+)", txt, re.M)))).replace("_", r"\_"))


def main() -> int:
    GEN.mkdir(exist_ok=True)
    lean_listings()
    lean_status()
    numerics()
    ledger_status()
    lines = ["% generated by gen_inputs.py; do not edit"]
    for k, v in sorted(N.items()):
        key = re.sub(r"[^A-Za-z]", "", k)
        assert key == k, k
        lines.append(f"\\newcommand{{\\ZP{k}}}{{{v}}}")
    (HERE / "gen_numbers.tex").write_text("\n".join(lines) + "\n")
    print(f"{len(N)} macros")
    return 0


if __name__ == "__main__":
    sys.exit(main())
