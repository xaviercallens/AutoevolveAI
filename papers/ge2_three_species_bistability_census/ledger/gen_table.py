"""Generate table_two_edge.tex (the 9 two-internal-reaction bistable networks, one exact witness each) from data/census.jsonl and data/witnesses/.

Run: python3 -I gen_table.py   (standard library only)
"""
from __future__ import annotations

import json
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent
DATA = PAPER / "data"


def tex_complex(c: str) -> str:
    return c.replace("->", r"\to ")


def main() -> int:
    rows = [json.loads(line) for line in (DATA / "census.jsonl").read_text().splitlines()]
    sel = [r for r in rows if r["verdict"] == "BISTABLE_CERT" and r["bucket"] == "C" and r["m"] == 2]
    assert len(sel) == 9
    out = [r"\begin{tabular}{llll}\toprule",
           r"id & internal reactions & positive equilibrium $p$ & positive equilibrium $q$\\\midrule"]
    for r in sorted(sel, key=lambda r: r["id"]):
        w = json.loads((DATA / "witnesses" / f"{r['id']}.json").read_text())
        rxn = r",\ ".join("$" + tex_complex(e) + "$" for e in r["edges"])
        p = "$(" + ",".join(w["equilibrium_p"]) + ")$"
        q = "$(" + ",".join(w["equilibrium_q"]) + ")$"
        out.append(f"\\texttt{{{r['id']}}} & {rxn} & {p} & {q}\\\\")
    out.append(r"\bottomrule\end{tabular}")
    (PAPER / "table_two_edge.tex").write_text("\n".join(out) + "\n")
    print("wrote table_two_edge.tex with", len(sel), "rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
