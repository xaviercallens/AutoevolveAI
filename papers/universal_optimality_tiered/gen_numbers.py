"""Generate gen_numbers.tex (LaTeX macros) and table_numerics.tex from the result files; no number is typed by hand.

Sources: rusty-SUNDIALS crates/qf-yukawa-crystal/results/{references,controls}.jsonl and summary.json;
AutoevolveAI results/discovery/ledger/ledger.json (+ the Elenchus gate output, re-run here).
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = HERE.parents[1]
YUK = Path("/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-yukawa/crates/qf-yukawa-crystal/results")
ELENCHUS = Path("/mnt/disks/disk-socrateai-local-1/SocrateAI-Scientific-Elenchus/tools/ledger.py")


def jl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def sci(x: float, d: int = 2) -> str:
    m, e = f"{x:.{d}e}".split("e")
    return f"{m}\\times10^{{{int(e)}}}"


def main() -> None:
    refs = {r["kappa"]: r for r in jl(YUK / "references.jsonl")}
    ctl = jl(YUK / "controls.jsonl")
    s = json.loads((YUK / "summary.json").read_text())
    m: dict[str, str] = {}
    for k, tag in ((2, "Two"), (1, "One")):
        r = refs[k]
        m[f"ETri{tag}"] = f"{r['e_tri_sum']:.10f}"
        m[f"ESq{tag}"] = f"{r['e_square_sum']:.10f}"
        m[f"DSq{tag}"] = sci(r["square_minus_tri"])
        m[f"Trunc{tag}"] = sci(r["truncation_v_rc"], 1)
        m[f"BoxVsSum{tag}"] = sci(abs(r["e_tri_periodic_box"] - r["e_tri_sum"]), 1)
    pos = [c for c in ctl if c["label"] == "ctl_pos_perfect" and c["kappa"] == 2][0]["quench"]
    noisy = [c for c in ctl if c["label"] == "ctl_pos_noisy" and c["kappa"] == 2][0]["quench"]
    sq = [c for c in ctl if c["label"] == "ctl_neg_square_saddle" and c["kappa"] == 2][0]
    m["PosGap"] = sci(abs(pos["rel_gap"]), 1)
    m["NoisyGap"] = sci(abs(noisy["rel_gap"]), 1)
    m["HessMin"] = f"{pos['hess_lowest'][2]:.4f}"
    m["SqNeg"] = str(sq["hess_negative"])
    m["SqAfterGap"] = sci(sq["e_after_minus_e_tri"])
    rows = []
    for key, tag in (("main_kappa2", "Two"), ("main_kappa1", "One")):
        if key not in s:
            continue
        k = s[key]
        m[f"POne{tag}"] = "pass" if k["P1_no_undercut"]["pass"] else "FAIL"
        m[f"PTwo{tag}"] = "pass" if k["P2_annealed_reaches_lattice"]["pass"] else "FAIL"
        m[f"Incomm{tag}"] = "pass" if k["neg_control_incommensurate"]["pass"] else "FAIL"
        for fam, v in sorted(k["families"].items()):
            fname, stage = fam.split("/")
            short = {"hf_oc20": "OC20-derived", "uniform": "uniform", "ctl_neg_incommensurate_box": "incomm.\\ box (ctl)"}[fname]
            label = f"{short}, {'anneal + quench' if stage == 'anneal_quench' else '$T=0$ quench'}"
            rows.append(f"$\\kappa={2 if tag == 'Two' else 1}$ & {label} & {v['runs']} & {v['perfect_lattice']} & {v['defected']} & "
                        f"${sci(v['min_rel_gap'])}$ & ${sci(v['max_rel_gap'])}$ & {v['not_converged']} & {v['hess_negative_runs']} \\\\")
        m[f"Undercuts{tag}"] = str(len(k["P1_no_undercut"]["undercuts"]))
        fam = k["families"]
        m[f"Relax{tag}"] = str(sum(v["runs"] for v in fam.values()))
        for f, ftag in (("hf_oc20", "HF"), ("uniform", "Uni")):
            a = fam[f"{f}/anneal_quench"]
            q = fam[f"{f}/quench"]
            m[f"Perf{tag}{ftag}"] = str(a["perfect_lattice"])
            m[f"Runs{tag}{ftag}"] = str(a["runs"])
            m[f"QDef{tag}{ftag}"] = str(q["defected"])
            m[f"MinGap{tag}{ftag}"] = sci(a["min_rel_gap"], 1)
        m[f"IncommMin{tag}"] = sci(k["neg_control_incommensurate"]["min_rel_gap"], 1)
    if "disk" in s:
        for g, tag in (("open_bowl", "Open"), ("closed_wall", "Closed")):
            v = s["disk"][g]
            m[f"Disk{tag}Int"] = f"{v['interior_defect_fraction_mean']:.3f}"
            m[f"Disk{tag}Edge"] = f"{v['edge_defect_fraction_mean']:.3f}"
            m[f"Disk{tag}Psi"] = f"{v['interior_psi6_local_mean']:.3f}"
            m[f"Disk{tag}R"] = f"{v['cluster_radius_mean']:.2f}"
    g = subprocess.run(["python3", "-I", str(ELENCHUS), str(W / "results/discovery/ledger/ledger.json"), "--evidence-dir",
                        str(W / "results/discovery/ledger/evidence"), "--json"], capture_output=True, text=True)
    gate = json.loads(g.stdout)
    sev = [f.get("severity") for f in gate["findings"]]
    m["LedgerClaims"] = str(gate["claims"])
    m["LedgerBlocks"] = str(sev.count("block"))
    m["LedgerFlags"] = str(sev.count("flag"))
    m["LedgerExit"] = str(g.returncode)
    tex = "\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in m.items()) + "\n"
    (HERE / "gen_numbers.tex").write_text(tex)
    (HERE / "table_numerics.tex").write_text("\n".join(rows) + "\n\\bottomrule\n")
    print(f"{len(m)} macros, {len(rows)} table rows; ledger exit {g.returncode} blocks {sev.count('block')} flags {sev.count('flag')}")


if __name__ == "__main__":
    main()
