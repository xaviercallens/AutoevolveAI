"""Generate gen_numbers.tex (LaTeX macros) and table_*.tex from the H7 numerics and Lean compile records.

Usage: python -I gen_numbers.py
Inputs (read only): data/summary.json, data/sigma2_probes.jsonl, data/well_spectrum.json, data/download_record.json,
results/autoresearch/2026-10-25/H7/contribution/{compile_flow_final,compile_flow_controls,recheck_prior,
recompile_paper_stage_flow,recompile_paper_stage_controls}.json.
Every number in the paper that comes from a run is produced here; none is typed by hand.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = HERE.parents[1]
DATA = HERE / "data"
C = W / "results/autoresearch/2026-10-25/H7/contribution"


def e(x: float, d: int = 1) -> str:
    """Scientific notation for LaTeX math mode, e.g. 2.1\\times10^{-9}."""
    if x == 0:
        return "0"
    m, ex = f"{x:.{d}e}".split("e")
    return f"{m}\\times10^{{{int(ex)}}}"


def f(x: float, d: int = 3) -> str:
    return f"{x:.{d}f}"


def axiom_lines(path: Path) -> list[str]:
    out = json.loads(path.read_text())["stdout"].replace("\n ", " ")
    return [l.strip() for l in out.split("\n") if "depends on axioms" in l]


def main() -> int:
    s = json.loads((DATA / "summary.json").read_text())
    probes = [json.loads(l) for l in (DATA / "sigma2_probes.jsonl").read_text().splitlines() if l.strip()]
    ws = json.loads((DATA / "well_spectrum.json").read_text())
    dl = json.loads((DATA / "download_record.json").read_text())
    m: dict[str, str] = {}
    conv = s["convergence"]
    p4, p6 = conv["P1_positive_convergence_n4"], conv["P1_positive_convergence_n6"]
    n4, n6 = conv["N1_negative_perturbed_n4"], conv["N1_negative_perturbed_n6"]
    m["PosSfourLo"], m["PosSfourHi"] = e(p4[0]["max_rel_dS"]), e(p4[-1]["max_rel_dS"])
    m["PosSsixLo"], m["PosSsixHi"] = e(p6[0]["max_rel_dS"]), e(p6[-1]["max_rel_dS"])
    m["PosHfourLo"], m["PosHfourHi"] = e(p4[0]["max_rel_dH"]), e(p4[-1]["max_rel_dH"])
    m["PosHsixLo"], m["PosHsixHi"] = e(p6[0]["max_rel_dH"]), e(p6[-1]["max_rel_dH"])
    m["NegSfour"], m["NegSsix"] = e(n4[-1]["max_rel_dS"]), e(n6[-1]["max_rel_dS"])
    m["NegHfour"], m["NegHsix"] = e(n4[-1]["max_rel_dH"]), e(n6[-1]["max_rel_dH"])
    r = s["neg_over_pos_at_rtol_1e-10"]
    m["RatioSfour"], m["RatioSsix"] = e(r["n4"]["dS_ratio_neg_over_pos"]), e(r["n6"]["dS_ratio_neg_over_pos"])
    m["RatioHfour"], m["RatioHsix"] = e(r["n4"]["dH_ratio_neg_over_pos"]), e(r["n6"]["dH_ratio_neg_over_pos"])
    m["SthreeMaxRatio"] = f(s["S3_max_sup_ratio"])
    m["SthreeMaxdS"], m["SthreeMaxdH"] = e(s["S3_max_rel_dS"]), e(s["S3_max_rel_dH"])
    s3 = s["S3"]
    m["SthreeNruns"] = str(len(s3))
    m["SthreeAboveTzero"] = str(sum(1 for x in s3 if x["sup_ratio"] > x["ratio_t0"]))
    m["SthreeMinRatio"] = f(min(x["sup_ratio"] for x in s3))
    m["SthreeMaxSteps"] = f"{max(x['steps'] for x in s3):,}".replace(",", "{,}")
    m["WMaxRatio"] = f(s["W_max_sup_ratio"])
    m["WNruns"], m["WAbove"] = str(s["W_n_runs"]), str(s["W_runs_with_sup_above_t0"])
    m["WMaxdS"] = e(max(x["max_rel_dS"] for x in s["W"]))
    m["WMaxdH"] = e(max(x["max_rel_dH"] for x in s["W"]))
    m["TotalWall"] = f(s["total_wall_s"], 1)
    m["Dval"] = f"{s['D']}"
    m["AllGates"] = "all pass" if s["all_gates_pass"] else "NOT all pass"
    m["NGates"] = str(len(s["gates"]))
    c2 = {int(row["sigma"]): row["rows"] for row in s["C2"]}
    sup2 = {x["n_max"]: x["sup_ratio"] for x in c2[2]}
    for p in probes:
        if p["sigma"] == 2 and "top_shell" in p["label"] and p["n_max"] > 6 and p["t_end"] == 0.5:
            sup2[p["n_max"]] = p["sup_ratio"]
    sup3 = {x["n_max"]: x["sup_ratio"] for x in c2[3]}
    rows = []
    for n in sorted(sup2):
        t3 = f(sup3[n]) if n in sup3 else "not run"
        src = "C2" if n <= 6 else "supp."
        rows.append(f"{n} & {n - 1} & {sup2[n]:.4g} & {t3} & {src}\\\\")
    (HERE / "table_c2.tex").write_text("\n".join(rows) + "\n")
    steps = [math.log2(sup2[n + 1] / sup2[n]) for n in range(6, 10)]
    m["CtwoLogSteps"] = ", ".join(f"{x:.2f}" for x in steps)
    m["CtwoTen"] = f"{sup2[10]:.1f}"
    m["CthreeMax"] = f(max(sup3.values()))
    # top-shell rows: sup over steps vs the t = 0 ratio (revision after AUDIT.md item 5)
    gap3 = max(x["sup_ratio"] - x["ratio_t0"] for x in c2[3])
    rel2 = [(x["sup_ratio"] - x["ratio_t0"]) / x["ratio_t0"] for x in c2[2]]
    for p in probes:
        if p["sigma"] == 2 and "top_shell" in p["label"] and p["n_max"] > 6 and p["t_end"] == 0.5:
            r0 = 2 * p["D"] * p["trace_t_S_H_Omega"][0][3] / p["bound_rhs"]
            rel2.append((p["sup_ratio"] - r0) / r0)
    m["CthreeGapAbs"] = e(gap3)
    m["CtwoGapRel"] = e(max(rel2))
    # negative control ranges across rtol (revision after AUDIT.md item 4)
    neg = [x[k] for x in n4 + n6 for k in ("max_rel_dS", "max_rel_dH")]
    m["NegAllMin"], m["NegAllMax"] = e(min(neg)), e(max(neg))
    m["NegHsixMin"] = e(min(x["max_rel_dH"] for x in n6))
    m["NegHsixMax"] = e(max(x["max_rel_dH"] for x in n6))
    dec = {p["n_max"]: p for p in probes if p["sigma"] == 2 and "decaying" in p["label"] and p["t_end"] == 2}
    m["DecHtwoFour"], m["DecHtwoSix"] = e(dec[4]["max_rel_dH"]), e(dec[6]["max_rel_dH"])
    m["DecRatioFour"], m["DecRatioSix"] = f(dec[4]["sup_ratio"], 2), f(dec[6]["sup_ratio"], 2)
    m["DecOmegaFour"], m["DecOmegaSix"] = f(dec[4]["sup_Omega"], 1), f(dec[6]["sup_Omega"], 1)
    # positive-control table
    prow = []
    for lab, pos, neg, n in (("4", p4, n4, 4), ("6", p6, n6, 6)):
        for a, b in zip(pos, neg):
            prow.append(f"{n} & {n - 1} & $10^{{{int(round(math.log10(a['rtol'])))}}}$ & ${e(a['max_rel_dS'])}$ & ${e(a['max_rel_dH'])}$ & "
                        f"${e(b['max_rel_dS'])}$ & ${e(b['max_rel_dH'])}$ & {a['steps']:,}\\\\".replace(",", "{,}"))
    (HERE / "table_controls.tex").write_text("\n".join(prow) + "\n")
    # Well spectrum
    snaps = ws["snapshots"]
    m["WellParseval"] = e(max(x["parseval_rel_err"] for x in snaps))
    m["WellSlopes"] = ", ".join(f"{x:.2f}" for x in ws["log2_slope_E_n_data"])
    m["WellNoiseSlope"] = f"{ws['log2_slope_E_n_white_noise']:.2f}"
    m["WellNsnap"] = str(len(snaps))
    m["WellRev"] = dl["revision"]
    h5 = [x for x in dl["files"] if x["path"].endswith(".hdf5")][0]
    m["WellHfiveSha"] = h5["sha256"]
    m["WellControls"] = "pass" if ws["controls_pass"] else "FAIL"
    # Lean compile records
    final = json.loads((C / "compile_flow_final.json").read_text())
    ctl = json.loads((C / "compile_flow_controls.json").read_text())
    prior = json.loads((C / "recheck_prior.json").read_text())
    rs = json.loads((C / "recompile_paper_stage_flow.json").read_text())
    rc = json.loads((C / "recompile_paper_stage_controls.json").read_text())
    fl, rl = axiom_lines(C / "compile_flow_final.json"), axiom_lines(C / "recompile_paper_stage_flow.json")
    allow = "[propext, Classical.choice, Quot.sound]"
    m["FlowNaxiom"] = str(len(fl))
    m["FlowAllAllow"] = "yes" if all(l.endswith(allow) for l in fl) else "NO"
    m["FlowSha"], m["FlowSeconds"], m["FlowRc"] = final["sha256"], f(final["seconds"], 1), str(final["rc"])
    m["CtlSha"], m["CtlRc"] = ctl["sha256"], str(ctl["rc"])
    m["PriorSha"], m["PriorRc"], m["PriorSeconds"] = prior["sha256"], str(prior["rc"]), f(prior["seconds"], 1)
    m["RerunRc"], m["RerunSeconds"] = str(rs["rc"]), f(rs["seconds"], 1)
    m["RerunCtlRc"], m["RerunCtlSeconds"] = str(rc["rc"]), f(rc["seconds"], 1)
    m["RerunSame"] = "identical" if (rl == fl and rs["sha256"] == final["sha256"]) else "DIFFERENT"
    m["RerunCtlSame"] = "identical" if axiom_lines(C / "recompile_paper_stage_controls.json") == axiom_lines(C / "compile_flow_controls.json") else "DIFFERENT"
    (HERE / "axioms_flow.txt").write_text("\n".join(fl) + "\n")
    (HERE / "axioms_controls.txt").write_text("\n".join(axiom_lines(C / "compile_flow_controls.json")) + "\n")
    (HERE / "axioms_prior.txt").write_text("\n".join(axiom_lines(C / "recheck_prior.json")) + "\n")
    lines = [f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in sorted(m.items())]
    (HERE / "gen_numbers.tex").write_text("% generated by gen_numbers.py; do not edit\n" + "\n".join(lines) + "\n")
    print(f"{len(m)} macros; flow axioms {len(fl)}; rerun {m['RerunSame']}; controls rerun {m['RerunCtlSame']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
