"""Generate table_encl.tex (enclosure boxes) from data/enclosures.json. Standard library only. Run: python3 -I gen_tables.py"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
CHECKED = {1.0, 10.0, 40.0}  # output times at which the auditor's independent MPFI/Lohner boxes exist


def sci(x: float, d: int = 2) -> str:
    m, e = f"{x:.{d}e}".split("e")
    return f"${m}\\!\\times\\!10^{{{int(e)}}}$"


def main() -> int:
    enc = json.loads((PAPER / "data" / "enclosures.json").read_text())
    rows = []
    for e in enc:
        t = e["t"]
        c = {k["name"]: k for k in e["comps"]}
        chk = "yes" if t in CHECKED else "--"
        tt = f"{t:g}"
        rows.append(
            f"{tt} & {c['y1']['mid_dec']:.12f} & {c['y2']['mid_dec']:.9e} & {c['y3']['mid_dec']:.12f} & {chk} \\\\"
        )
    (PAPER / "table_encl_mid.tex").write_text("\n".join(rows).removesuffix(" \\\\") + "\n")
    rows = []
    for e in enc:
        t = e["t"]
        c = {k["name"]: k for k in e["comps"]}
        rows.append(
            f"{t:g} & {sci(c['y1']['rel_width'])} & {sci(c['y2']['rel_width'])} & {sci(c['y3']['rel_width'])} & {e['steps']:,} \\\\".replace(",", "\\,")
        )
    (PAPER / "table_encl_width.tex").write_text("\n".join(rows).removesuffix(" \\\\") + "\n")
    print("tables written:", len(enc), "rows; max rel width",
          max(k["rel_width"] for e in enc for k in e["comps"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
