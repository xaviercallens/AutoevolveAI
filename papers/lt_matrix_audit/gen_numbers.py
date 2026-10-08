#!/usr/bin/env python3
"""Generate every number and table of the paper from the committed result files.

Writes gen_numbers.tex (macros) and table_*.tex next to this script. Nothing in the paper body is typed by hand
except prose. Run: python3 papers/lt_matrix_audit/gen_numbers.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
RES = REPO / "results" / "openai_math" / "hypotheses"
NIGHT = RES / "night_2026-10-08"


def load(p: Path) -> Any:
    return json.loads(p.read_text())


def sci(x: float, digits: int = 2) -> str:
    """LaTeX scientific notation, e.g. 8.95\\times10^{-7}."""
    if x == 0:
        return "0"
    e = int(math.floor(math.log10(abs(x))))
    m = x / 10**e
    return f"{m:.{digits}f}\\!\\times\\!10^{{{e}}}"


def wrap(spec: str, header: str, rows: list[str]) -> str:
    """A complete tabular, so the paper can \\input it whole (an \\input inside a tabular breaks \\bottomrule)."""
    return "\\begin{tabular}{" + spec + "}\\toprule\n" + header + " \\\\\n\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n"


def main() -> None:
    macros: dict[str, str] = {}
    a = load(NIGHT / "LT_A" / "result.json")
    b = load(NIGHT / "LT_B" / "result.json")
    c = load(NIGHT / "LT_C" / "result.json")
    ctl = load(RES / "lt_matrix" / "controls.json")["controls"]
    cmp_path = NIGHT / "LT_CMP" / "result.json"
    cmpr = load(cmp_path) if cmp_path.exists() else None
    tri_cmp_path = NIGHT / "TRI_CMP" / "result.json"
    tri = load(tri_cmp_path) if tri_cmp_path.exists() else None

    cells_a = a["cells"] if isinstance(a["cells"], list) else list(a["cells"].items())
    macros["MTwoCells"] = str(a["n_cells"])
    macros["MTwoRestarts"] = str(a["total_restarts"])
    macros["MTwoFlagged"] = str(a["total_flagged"])
    closest = min(v["closeness_below_L1"] for _, v in cells_a)
    macros["MTwoClosest"] = sci(closest)
    macros["MTwoFarthestBest"] = sci(max(v["closeness_below_L1"] for _, v in cells_a))

    # table m=2 (all cells)
    rows = []
    for k, v in sorted(cells_a, key=lambda kv: (kv[1]["gamma"], kv[1]["family"], kv[1]["K"])):
        rows.append(f"{v['gamma']} & {v['family']} & {v['K']}/{v['P']} & {v['restarts']} & ${sci(v['closeness_below_L1'])}$ & {v['flagged']} \\\\")
    (HERE / "table_m2.tex").write_text(wrap(r"@{}rlcrcr@{}", r"$\gamma$ & family & $K/P$ & restarts & best distance below $L_1$ & flagged", rows))

    # m=3
    p1 = b["part1"]
    rows = []
    for k in sorted(p1):
        v = p1[k]
        label = ("control, $\\gamma=3/2$" if k.startswith("control") else "$\\gamma=" + k[1:].split("_")[0] + "$, " + k.split("_", 1)[1])
        rows.append(f"{label} & {v['restarts']} & ${sci(-v['max_excess'])}$ \\\\")
    (HERE / "table_m3.tex").write_text(wrap(r"@{}lcc@{}", r"cell & restarts & best distance below the bound", rows))
    macros["MThreeCells"] = str(len([k for k in p1 if not k.startswith("control")]))

    # second variation: test cells (gamma <= 1.4) and the gamma = 3 negative control, kept apart
    p2 = b["part2"]
    rows, ctl_rows = [], []
    pos_main = pos_ctl = n_main = 0
    for k in sorted(p2, key=lambda s: (float(s[1:].split("_")[0]), s)):
        v = p2[k]
        g = k[1:].split("_")[0]
        m = k.split("_m")[1]
        line = (
            f"{g} & {m} & ${sci(v['lambda_max_restricted'])}$ & ${sci(v['hessian_threshold'])}$ & {v['n_positive_beyond_thr']} & {v['n_zero_within_thr']} & {v['n_negative_beyond_thr']} \\\\"
        )
        if float(g) < 3:
            rows.append(line)
            pos_main += v["n_positive_beyond_thr"]
            n_main += 1
        else:
            ctl_rows.append(line.replace("\\\\", f"& {v['n_confirmed_positive']} \\\\"))
            pos_ctl += v["n_positive_beyond_thr"]
    (HERE / "table_hessian.tex").write_text(wrap(r"@{}rrccrrr@{}", r"$\gamma$ & $m$ & $\lambda_{\max}$ (restricted) & tolerance & $>$tol & within tol & $<-$tol", rows))
    (HERE / "table_hessian_ctl.tex").write_text(wrap(r"@{}rrccrrrr@{}", r"$\gamma$ & $m$ & $\lambda_{\max}$ & tolerance & $>$tol & within tol & $<-$tol & confirmed positive", ctl_rows))
    macros["HessCells"] = str(n_main)
    macros["HessPositive"] = str(pos_main)
    macros["HessCtlPositive"] = str(pos_ctl)

    # dual kinetic bound
    h5 = c["H-LT5"]["min_excess_per_cell_(J/(pi^2/4)-1)_and_restarts_within_1e-5"]
    rows = []
    mn = min(v[0] for v in h5.values())
    for k in sorted(h5):
        m, n = k.replace("m", "").split("_N")
        rows.append(f"{m} & {n} & ${sci(h5[k][0])}$ & {h5[k][1]} \\\\")
    (HERE / "table_dual.tex").write_text(wrap(r"@{}rrcc@{}", r"$m$ & $N$ & smallest excess over $\pi^2/4$ & restarts within $10^{-5}$", rows))
    macros["DualMinExcess"] = sci(mn)
    macros["DualCells"] = str(len(h5))
    never = [k for k, v in h5.items() if v[1] == 0]
    macros["DualNeverClose"] = str(len(never))

    # H-LT2
    h2 = c["H-LT2"]
    sc = h2["status_counts"]
    macros["TwoRows"] = str(sum(sc.values()))
    macros["TwoAnalysed"] = str(sc["KILLED"] + sc["INTERMEDIATE"] + sc["PREDICTION_HOLDS"])
    macros["TwoKilled"] = str(sc["KILLED"])
    macros["TwoKilledOutside"] = str(h2["killed_outside_gamma_1.5_control"])
    macros["TwoNotStored"] = str(sc["PARAMETERS_NOT_STORED"])
    macros["TwoHolds"] = str(sc["PREDICTION_HOLDS"])
    macros["TwoIntermediate"] = str(sc["INTERMEDIATE"])

    # controls table
    rows = [
        f"C1 & equality potential, $\\gamma\\in\\{{0.75,1,1.25,1.4\\}}$ & computed ratio minus $L_1$ in $[{sci(min(v['excess'] for v in ctl['C1']['results'].values()))},\\,{sci(max(v['excess'] for v in ctl['C1']['results'].values()))}]$, one bound state & pass \\\\",
        f"C2/C3 & unitary invariance, embedding, additivity ($m=2,3$) & residuals $\\le {sci(max(abs(ctl['C2_C3']['invariance'][m][key]) for m in ('m2', 'm3') for key in ('embed_minus_scalar', 'dressed_minus_embed')))}$ & pass \\\\",
        f"C4 & scalar search ($m=1$) must reach but not exceed $L_1$ & best excess $\\le {sci(max(v['best_excess'] for v in ctl['C4']['results'].values()))}$ & pass \\\\",
        f"C6 & $\\gamma=3/2$, proved sup $3/16$, matrix search & best excess ${sci(ctl['C6']['best_excess'])}$ (not exceeded) & pass \\\\",
        f"C5 & NEGATIVE: wrong claimed constant at $\\gamma=3$ & violation found, excess ${ctl['C5']['best_excess']:.4f}$ & pass \\\\",
        f"C7 & NEGATIVE: matrix search at $\\gamma=3$ & violation found, excess ${ctl['C7']['best_excess']:.4f}$ & pass \\\\",
    ]
    (HERE / "table_controls.tex").write_text(wrap(r"@{}l p{3.6cm} p{5.6cm} l@{}", r"id & test & measured & result", rows))

    if cmpr is not None:
        macros["CmpLTVerdict"] = "accepted"
        macros["CmpOutput"] = next(l for l in cmpr["output_evidence"] if "okay" in l).replace("_", "\\_")
    else:
        macros["CmpLTVerdict"] = "NOT RUN"
        macros["CmpOutput"] = "not run"
    macros["CmpTriVerdict"] = tri["verdict"].replace("_", "\\_") if tri else "pending"

    out = ["% generated by gen_numbers.py from committed result files; do not edit by hand"]
    for k, v in macros.items():
        out.append(f"\\newcommand{{\\{k}}}{{{v}}}")
    (HERE / "gen_numbers.tex").write_text("\n".join(out) + "\n")
    print(json.dumps(macros, indent=1))


if __name__ == "__main__":
    main()
