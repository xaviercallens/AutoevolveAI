"""Writer check: recompute from comparison.json and enclosures.json the quantities quoted in the paper.
Standard library only. Usage: python3 -I analyse.py <PH2 lane dir> <out tex>"""
import json
import sys
from pathlib import Path

lane = Path(sys.argv[1])
enc = json.loads((lane / "enclosures.json").read_text())
cmp_ = json.loads((lane / "comparison.json").read_text())
mid = {(e["t"], c["name"]): c["mid_dec"] for e in enc for c in e["comps"]}
rows = {}
for r in cmp_:
    y = mid[(r["t"], r["comp"])]
    rel = r["err_hi"] / (r["rtol"] * y)
    rows[(r["rtol"], r["t"], r["comp"])] = (r["err_hi"], y, rel, r["err_hi"] / r["atol"], r["ratio_hi"], r["exceeds"], r["within"])
print("per rtol, per component: max over t of err/(rtol|y|) (hi end) and max err/atol")
out = {}
for rt in sorted({k[0] for k in rows}):
    for comp in ("y1", "y2", "y3"):
        sel = [(k[1], v) for k, v in rows.items() if k[0] == rt and k[2] == comp]
        tm, v = max(sel, key=lambda x: x[1][2])
        ma = max(x[1][3] for x in sel)
        mt = max(sel, key=lambda x: x[1][4])
        nex = sum(1 for x in sel if x[1][5])
        nwi = sum(1 for x in sel if x[1][6])
        out[(rt, comp)] = (v[2], tm, ma, mt[1][4], nex, nwi, len(sel))
        print(f"rtol={rt:g} {comp}: max err/(rtol|y|)={v[2]:.3g} at t={tm}; max err/atol={ma:.3g}; max ratio_hi={mt[1][4]:.3g}; provably_exceeds {nex}/{len(sel)}; provably_within {nwi}/{len(sel)}")
# first time of a provable violation per comp
print("first provable exceed (ratio vs rtol|y|+atol):")
for rt in sorted({k[0] for k in rows}):
    for comp in ("y1", "y2", "y3"):
        ts = sorted(k[1] for k, v in rows.items() if k[0] == rt and k[2] == comp and v[5])
        print(rt, comp, ts[0] if ts else None)
# LaTeX table: max error / (rtol |y|) and max error/atol
lines = []
atol = {1e-4: "$10^{-7}$", 1e-6: "$10^{-9}$", 1e-8: "$10^{-11}$", 1e-10: "$10^{-10}$"}
for rt in sorted({k[0] for k in rows}, reverse=True):
    exp = {1e-4: "-4", 1e-6: "-6", 1e-8: "-8", 1e-10: "-10"}[rt]
    cells = []
    for comp in ("y1", "y2", "y3"):
        v = out[(rt, comp)]
        cells.append(f"{v[0]:.3g}")
    maxatol = max(out[(rt, c)][2] for c in ("y1", "y2", "y3"))
    y2atol = out[(rt, "y2")][2]
    lines.append(f"$10^{{{exp}}}$ & {atol[rt]} & {cells[0]} & {cells[1]} & {cells[2]} & {y2atol:.2g} \\\\")
Path(sys.argv[2]).write_text(chr(10).join(lines).removesuffix(" \\\\") + chr(10))
# selected true-error rows (relative error |err|/|y|) at selected times, rtol 1e-6 and 1e-10
sel_t = [1.0, 40.0, 1000.0, 4000.0]
lines = []
for rt in (1e-4, 1e-6, 1e-8, 1e-10):
    exp = {1e-4: "-4", 1e-6: "-6", 1e-8: "-8", 1e-10: "-10"}[rt]
    for t in sel_t:
        cells = []
        for comp in ("y1", "y2", "y3"):
            e, y, rel, ea, rr, ex, wi = rows[(rt, t, comp)]
            cells.append(f"{e / y:.2e}")
        lines.append(f"$10^{{{exp}}}$ & {t:g} & " + " & ".join(cells) + " \\\\")
Path(str(sys.argv[2]).replace(".tex", "_sel.tex")).write_text(chr(10).join(lines).removesuffix(" \\\\") + chr(10))
