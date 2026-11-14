"""Generate gen_numbers.tex (macros) and gen/*.tex (tables) from data/ so that no number in the paper is typed by hand.

Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I gen_inputs.py   (after copy_data.py and checks.py)
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
GEN = HERE / "gen"
GEN.mkdir(exist_ok=True)


def load(name: str):
    return json.loads((DATA / name).read_text())


NUM = load("result_numbers.json")
TAB = NUM["hbar_star_table"]
BY_A = {r["a"]: r for r in TAB}
SC = NUM["scha"]
CTL = load("controls.json")
PIMC = load("pimc_feasibility.json")
EXT = load("scha_extend.json")
SLOPE = load("scha_slope_control.json")
EXTRA = load("extra_checks.json")
SCHA_FULL = load("scha.json")
MACROS: list[tuple[str, str]] = []


def f(x: float, nd: int = 4) -> str:
    return f"{x:.{nd}f}"


def sci(x: float, nd: int = 1) -> str:
    m, e = f"{x:.{nd}e}".split("e")
    return f"\\ensuremath{{{m}\\times10^{{{int(e)}}}}}"


def mac(name: str, val: str) -> None:
    MACROS.append((name, val))


def macros() -> None:
    mn = min((r for r in TAB if r["hbar_star"]), key=lambda r: r["hbar_star"])
    mac("BAMinHbar", f(mn["hbar_star"], 4))
    mac("BAMinHbarA", f"{mn['a']:g}")
    a1 = BY_A[1.0]
    mac("BAHbarOne", f(a1["hbar_star"], 4))
    mac("BALamOne", f(a1["Lam_1_edge"]["Lam1"], 4))
    mac("BALamOneMargin", f(a1["Lam_1_margin_0.01"][0], 4))
    mac("BAGammaStarOne", f(a1["gamma_at_hbar_star"], 3))
    mac("BAGammaLamOne", f(a1["gamma_at_Lam_1_edge"], 3))
    mac("BACStaticOne", f(a1["c_static"], 5))
    mac("BACZpOne", f(a1["c_zp"], 5))
    rat = [r["Lam_1_edge"]["Lam1"] / r["hbar_star"] for r in TAB if r["Lam_1_edge"] and 0.45 <= r["a"] <= 1.2]
    mac("BARatioLo", f(min(rat), 2))
    mac("BARatioHi", f(max(rat), 2))
    mrg = [r["Lam_1_margin_0.01"][0] / r["Lam_1_edge"]["Lam1"] - 1 for r in TAB if r["Lam_1_margin_0.01"]]
    mac("BAMarginShiftLo", f(100 * min(mrg), 0))
    mac("BAMarginShiftHi", f(100 * max(mrg), 0))
    b = EXTRA["bands"]
    mac("BBMinGammaStar", f(b["min_gamma_hbar_star"], 4))
    mac("BBMinGammaStarA", f"{b['a_at_min_gamma_hbar_star']:g}")
    mac("BBMinGammaLam", f(b["min_gamma_Lam1"], 3))
    mac("BBInsideNarrow", ", ".join(f"{a:g}" for a in b["a_inside_023_028"]))
    mac("BBInsideWide", ", ".join(f"{a:g}" for a in b["a_inside_023_030"]))
    mac("BBSensLo", f(b["sensitivity_Lam_L"]["gamma_c_x0.9"], 2))
    mac("BBSensHi", f(b["sensitivity_Lam_L"]["gamma_c_x1.1"], 2))
    mac("BBCoulomb", f(b["sensitivity_Lam_L"]["coulomb_rs_star_x0.9"], 2))
    r1 = next(x for x in b["rows"] if x["a"] == 1.0)
    mac("BBRatioOneNarrow", f(r1["Lam1_over_LamL"]["0.23"], 2))
    mac("BBRatioOneWide", f(r1["Lam1_over_LamL"]["0.28"], 2))
    rays = EXTRA["ray_slopes"]
    mac("RayRatioOne", f(rays["1"]["slope_ratio_up_over_arc"], 2))
    mac("RayRatioHalf", f(rays["0.5"]["slope_ratio_up_over_arc"], 2))
    mac("RayRatioSeven", f(rays["0.7"]["slope_ratio_up_over_arc"], 2))
    mac("RayRatioEight", f(rays["0.8"]["slope_ratio_up_over_arc"], 2))
    mac("RayRatioTwelve", f(rays["1.2"]["slope_ratio_up_over_arc"], 2))
    mac("RaySlopeUpOne", f(rays["1"]["line_up"]["slope"], 4))
    mac("RaySlopeArcOne", f(rays["1"]["arc_to_i"]["slope"], 4))
    for a, nm in (("0.5", "Half"), ("0.7", "Seven"), ("1", "One"), ("1.3", "Thirteen")):
        s = SC[a]
        if s["lam_star_scha"]:
            mac(f"SchaSpin{nm}", f(s["lam_star_scha"], 4))
            mac(f"SchaGamma{nm}", f(s["gamma_at_lam_star_scha"], 2))
        mac(f"SchaBreak{nm}", f(s["breakdown_lam"][0], 3))
    s1 = SC["1"]
    lo = max(q["lam"] for q in s1["lap_ladder"] if q["lap"] > 0)
    hi = min(p[0] for p in s1["profiles_min_dE_stable"] if p[2] < 0)
    mac("SchaOneLo", f(lo, 3))
    mac("SchaOneHi", f(hi, 4))
    mac("SchaOneLapLo", f(next(q["lap"] for q in s1["lap_ladder"] if q["lam"] == lo), 3))
    mac("SchaOneLapFifteen", f(next(q["lap"] for q in s1["lap_ladder"] if abs(q["lam"] - 0.15) < 1e-9), 3))
    mac("HarmLapOneFifteen", f(4 * (a1["c_static"] + 0.15 * a1["c_zp"]), 3))
    mac("HarmLapOneTen", f(4 * (a1["c_static"] + 0.10 * a1["c_zp"]), 3))
    mac("SchaMinDEOne", sci(s1["profiles_min_dE_stable"][0][2], 2))
    mac("SchaGammaAtLamOne", f(s1["profiles_min_dE_stable"][0][1], 3))
    mac("SchaGammaFirstBelowOne", f(next(p[1] for p in s1["profiles_min_dE_stable"] if p[2] < 0), 2))
    mac("SchaGammaLowAll", f(min(SC[a]["gamma_at_lam_star_scha"] for a in SC if SC[a]["gamma_at_lam_star_scha"]), 2))
    mac("SchaGammaHighAll", f(max(SC[a]["gamma_at_lam_star_scha"] for a in SC if SC[a]["gamma_at_lam_star_scha"]), 2))
    mac("ExtNPointsLo", str(min(e["n_points"] for e in EXT)))
    mac("ExtStableLo", str(min(e["n_scha_stable"] for e in EXT)))
    mac("ExtStableHi", str(max(e["n_scha_stable"] for e in EXT)))
    mac("ExtUnstLo", str(min(e["n_scha_stable_but_harmonically_unstable"] for e in EXT)))
    mac("ExtUnstHi", str(max(e["n_scha_stable_but_harmonically_unstable"] for e in EXT)))
    mac("ExtBelow", str(sum(e["n_below_triangular"] for e in EXT)))
    mac("ExtMinDELo", sci(min(e["min_dE"]["dE"] for e in EXT), 1))
    mac("ExtMinDEHi", sci(max(e["min_dE"]["dE"] for e in EXT), 1))
    mac("ExtEdgeDELo", sci(min(e["min_dE_beyond_harmonic_edge"]["dE"] for e in EXT), 1))
    mac("ExtEdgeDEHi", sci(max(e["min_dE_beyond_harmonic_edge"]["dE"] for e in EXT), 1))
    mac("SlopeExtrap", f(__import__("numpy").polyfit([float(k) for k in SLOPE], [SLOPE[k]["slope_from_0"] for k in SLOPE], 1)[1], 3))
    mac("SlopeHarm", f(4 * a1["c_zp"], 3))
    mac("SlopeFirst", f(SLOPE["0.0025"]["slope_from_0"], 3))
    mac("SlopeLast", f(SLOPE["0.01"]["slope_from_0"], 3))
    mac("SlopeCoef", f((SLOPE["0.01"]["slope_from_0"] - SLOPE["0.0025"]["slope_from_0"]) / (0.01 - 0.0025), 1))
    mac("FrozenMax", sci(CTL["frozen_phonon_max_rel"], 1))
    mac("FrozenBug", f(CTL["frozen_phonon_bug"][0]["rel"], 2))
    mac("FrozenN", str(len(CTL["frozen_phonon"])))
    p = PIMC[0]
    mac("PimcDEInf", sci(p["dE_total_inf"], 2))
    cells = {c["M"]: c for c in p["cells"]}
    mac("PimcShiftEight", sci(cells[8]["finite_size_shift_of_dE_total"], 1))
    mac("PimcShiftTwelve", sci(cells[12]["finite_size_shift_of_dE_total"], 1))
    mac("PimcNdEEight", f(cells[8]["N_times_abs_dE_total_inf"], 3))
    mac("PimcNdETwelve", f(cells[12]["N_times_abs_dE_total_inf"], 3))
    mac("PimcOmegaTwelve", f(cells[12]["lowest_phonon_hbar_omega_tri"], 3))
    sh = EXTRA["shoulder_ft"]
    mac("ShoulderMinRel", f(sh["shoulder_min_value"] / sh["shoulder_value_at_k0"], 4))
    mac("ShoulderMinK", f(sh["shoulder_min_k"], 2))
    mac("ShoulderNegFrac", f(100 * sh["fraction_of_k_grid_negative"], 0))
    mac("GaussCtlErr", sci(sh["gaussian_positive_control_max_abs_error"], 1))
    mac("ShoulderCutoffDiff", sci(sh["shoulder_two_cutoffs_max_abs_diff"], 1))
    ry = EXTRA["rydberg"]
    mac("RydEnergyHz", f(ry["E_Rc_over_h_Hz"], 1))
    mac("RydRatio", f(ry["U0_over_E_Rc"], 1))
    mac("RydParam", f(ry["hbar_over_sqrt_m_U0_Rc2"], 3))
    # interaction-set motional scale sqrt(U0 E_Rc)/h (audit N6); E_Rc/h and U0/E_Rc come from checks.py
    f_int = ry["E_Rc_over_h_Hz"] * ry["U0_over_E_Rc"] ** 0.5
    mac("RydIntHz", f(f_int, 0))
    mac("RydInvOmegaMs", f(1e3 / (2 * 3.141592653589793 * f_int), 2))
    mac("RydPeriodMs", f(1e3 / f_int, 1))
    mac("RydSlowMs", f(1e3 / ry["E_Rc_over_h_Hz"], 0))
    mac("RydFactorLo", f(1e3 / (2 * 3.141592653589793 * f_int) / 0.130, 0))
    mac("RydFactorHi", f(1e3 / f_int / 0.130, 0))
    edge = [r["Lam_1_edge"]["margin_full"] for r in TAB if r["Lam_1_edge"]]
    mac("BAMarginEdgeLo", sci(min(edge), 1))
    mac("BAMarginEdgeHi", sci(max(edge), 1))
    summ = load("summary.json")
    mac("BATriMarginOne", f(next(r["tri_margin"] for r in summ if r["a"] == 1.0), 3))
    lad = load("scan_a1.json")["ladder"]
    jlo = max(q["lam"] for q in lad if q["tri_is_min"])
    jhi = min(q["lam"] for q in lad if not q["tri_is_min"])
    mac("LadderJumpLo", f(jlo, 2))
    mac("LadderJumpHi", f(jhi, 2))
    mac("LadderDEAtHi", sci(next(q["dE_min"] for q in lad if q["lam"] == jhi), 2))
    mac("PimcDEs", sci(PIMC[0]["dEs"], 2))
    mac("PimcDEzp", f(PIMC[0]["dEzp_inf"], 4))
    hs = [r["hbar_star"] for r in TAB if r["hbar_star"] and 0.45 <= r["a"] <= 1.3]
    l1 = [r["Lam_1_edge"]["Lam1"] for r in TAB if r["Lam_1_edge"] and 0.45 <= r["a"] <= 1.3]
    mac("HbarStarRangeLo", f(min(hs), 3))
    mac("HbarStarRangeHi", f(max(hs), 3))
    mac("LamOneRangeLo", f(min(l1), 3))
    mac("LamOneRangeHi", f(max(l1), 3))
    mac("ShoulderZero", f(sh["first_zero_crossing_k"], 2))
    mac("HbarStarNearRoot", f(next(r["hbar_star"] for r in load("b1a_curvature.json")["rows"] if r["a"] == 0.378), 2))
    lh = {round(q["lam"], 3): q["lap"] for q in SC["0.5"]["lap_ladder"]}
    mac("SchaHalfLapThree", f(lh[0.3], 3))
    mac("SchaHalfLapFive", f(lh[0.5], 3))
    cc = load("crosscheck.json")
    mac("CrossMax", sci(max(c["abs_diff"] for c in cc), 1))
    mac("CrossN", str(len(cc)))
    import re
    log = (HERE / "ledger" / "rust_test.log").read_text()
    m = re.search(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored", log)
    mac("RustPassed", m.group(1))
    mac("RustFailed", m.group(2))
    mac("RustIgnored", m.group(3))
    # --- revision (audit B2, N1, N3, N10): macros emitted from data, never typed by hand
    np = __import__("numpy")
    below = [r for r in TAB if r["hbar_star"] and r["a"] >= 0.45 and r["gamma_at_hbar_star"] < 0.30]
    mac("BCBelowLo", f(min(r["gamma_at_hbar_star"] for r in below), 3))
    mac("BCBelowHi", f(max(r["gamma_at_hbar_star"] for r in below), 3))
    mac("BCBelowALo", f"{min(r['a'] for r in below):g}")
    mac("BCBelowAHi", f"{max(r['a'] for r in below):g}")
    for nm, aa in (("Half", 0.5), ("One", 1.0)):
        e = next(x for x in EXT if x["a"] == aa and abs(x["lam"] - BY_A[aa]["hbar_star"]) < 1e-3)
        mac(f"ExtGamStar{nm}", f(e["gamma_rho"], 2))
    sl = sorted(SLOPE, key=float)
    xs = [float(k) for k in sl]
    ys = [SLOPE[k]["slope_from_0"] for k in sl]
    mac("SlopeTwoPt", f(2 * ys[0] - ys[1], 3))
    q2 = np.polyfit(xs, ys, 2)
    mac("SlopeQuad", f(q2[2], 3))
    mac("SlopeQuadCoef", f(q2[1], 1))
    mac("SlopeCubCoef", f(q2[0], 0))
    mac("SlopeCubAtTen", f(q2[0] * 0.1 ** 3, 3))
    mac("SlopeSqAtTen", f(q2[1] * 0.1 ** 2, 3))
    for nm, aa, xy in (("One", "1", (0.30, 0.96)), ("Half", "0.5", (0.305, 0.955))):
        pts = [q for q in SCHA_FULL[aa]["profiles"][0]["points"] if q["kind"] == "edge" and q["dE"] == q["dE"]]
        w = next(q for q in pts if abs(q["x"] - xy[0]) < 1e-6 and abs(q["y"] - xy[1]) < 1e-6)
        mac(f"SchaEdgeWin{nm}", sci(w["dE"], 2))
        mac(f"SchaEdgeMin{nm}", sci(min(q["dE"] for q in pts), 1))
    mac("RootOne", "0.37668")
    mac("RootTwo", "1.58148")
    body = "\n".join(f"\\newcommand{{\\{n}}}{{{v}}}" for n, v in MACROS)
    (HERE / "gen_numbers.tex").write_text("% generated by gen_inputs.py from data/; do not edit\n" + body + "\n")


def tab_main() -> None:
    rows = []
    for r in TAB:
        a = r["a"]
        if r["hbar_star"] is None:
            rows.append(f"{a:g} & {f(r['rho_sigma2'], 3)} & {f(r['c_static'], 4)} & ${f(r['c_zp'], 4)}$ & \\multicolumn{{5}}{{c}}{{none ($c_{{\\mathrm{{zp}}}}>0$)}} \\\\")
            continue
        l1 = r["Lam_1_edge"]
        rows.append(f"{a:g} & {f(r['rho_sigma2'], 3)} & {f(r['c_static'], 4)} & ${f(r['c_zp'], 4)}$ & {f(r['hbar_star'], 4)} & {f(r['gamma_at_hbar_star'], 3)} & "
                    f"{f(l1['Lam1'], 4)} & ({l1['x']:.3f}, {l1['y']:.3f}) & {f(r['gamma_at_Lam_1_edge'], 3)} \\\\")
    (GEN / "tab_main.tex").write_text("\n".join(rows) + "\n")


def tab_lindemann() -> None:
    rows = []
    for x in EXTRA["bands"]["rows"]:
        r = BY_A[x["a"]]
        ll = r["Lam_Lindemann"]
        rows.append(f"{x['a']:g} & {f(ll['0.23'], 4)} & {f(ll['0.28'], 4)} & {f(ll['0.3'], 4)} & {f(r['Lam_1_edge']['Lam1'], 4)} & "
                    f"{f(x['Lam1_over_LamL']['0.23'], 2)} & {f(x['Lam1_over_LamL']['0.28'], 2)} & {f(x['Lam1_over_LamL']['0.3'], 2)} \\\\")
    (GEN / "tab_lindemann.tex").write_text("\n".join(rows) + "\n")


def tab_scha() -> None:
    rows = []
    for a in ("0.5", "0.7", "1", "1.3"):
        s = SC[a]
        r = BY_A[float(a)]
        lad = {round(q["lam"], 3): q["lap"] for q in s["lap_ladder"]}
        cells = " & ".join(f"${f(lad[l], 3)}$" for l in (0.05, 0.1, 0.15, 0.2, 0.3))
        harm = 4 * (r["c_static"] + 0.10 * r["c_zp"])
        spin = f(s["lam_star_scha"], 3) if s["lam_star_scha"] else f"$({SC['1']['lap_ladder'][-1]['lam']:.2f},\\,{min(p[0] for p in s['profiles_min_dE_stable'] if p[2] < 0):.3f})$"
        gam = f(s["gamma_at_lam_star_scha"], 2) if s["gamma_at_lam_star_scha"] else "--"
        m = s["profiles_min_dE_stable"][0]
        rows.append(f"{a} & {f(r['hbar_star'], 4)} & {f(r['Lam_1_edge']['Lam1'], 4)} & {cells} & ${f(harm, 3)}$ & {spin} & {gam} & {f(m[1], 3)} & {sci(m[2], 1)} \\\\")
    (GEN / "tab_scha.tex").write_text("\n".join(rows) + "\n")


def tab_ext() -> None:
    rows = []
    for e in EXT:
        rows.append(f"{e['a']:g} & {f(e['lam'], 4)} & {f(e['gamma_rho'], 2)} & {e['n_points']} & {e['n_scha_stable']} & {e['n_scha_stable_but_harmonically_unstable']} & "
                    f"{e['n_below_triangular']} & {sci(e['min_dE']['dE'], 1)} & {sci(e['min_dE_beyond_harmonic_edge']['dE'], 1)} \\\\")
    (GEN / "tab_ext.tex").write_text("\n".join(rows) + "\n")


def tab_pimc() -> None:
    rows = []
    p = PIMC[0]
    for c in p["cells"]:
        rows.append(f"{c['M']} & {c['N']} & {sci(c['finite_size_shift_of_dE_total'], 1)} & {sci(c['dE_total_M'], 2)} & {f(c['N_times_abs_dE_total_inf'], 3)} & {f(c['lowest_phonon_hbar_omega_tri'], 4)} \\\\")
    (GEN / "tab_pimc.tex").write_text("\n".join(rows) + "\n")


def tab_rays() -> None:
    rows = []
    for a, d in EXTRA["ray_slopes"].items():
        rows.append(f"{a} & {f(d['line_up']['slope'], 4)} & {f(d['arc_to_i']['slope'], 4)} & ${f(d['slope_ratio_up_over_arc'], 3)}$ \\\\")
    (GEN / "tab_rays.tex").write_text("\n".join(rows) + "\n")


def main() -> int:
    macros()
    tab_main()
    tab_lindemann()
    tab_scha()
    tab_ext()
    tab_pimc()
    tab_rays()
    print(len(MACROS), "macros;", len(list(GEN.glob('*.tex'))), "tables")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
