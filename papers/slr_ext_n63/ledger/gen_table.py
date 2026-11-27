"""Write table_cert.tex (papers/slr_ext_n63) from data/certificates/cert_n063.json; nothing typed by hand.
Run: python3 -I gen_table.py"""
from __future__ import annotations

import json
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent


def main() -> int:
    c = json.loads((PAPER / "data" / "certificates" / "cert_n063.json").read_text())
    v, a, D = c["v"], c["a"], c["D"]
    assert len(v) == 63 and len(set(v)) == 63 and D == 520
    zero = sorted(x for x, s in zip(v, a) if s == 0)
    rest = [(x, s) for x, s in zip(v, a) if s != 0]
    rest.sort()
    out = [r"\begin{center}\scriptsize\begin{tabular}{rr|rr|rr|rr}\toprule",
           r"$v$ & $a$ & $v$ & $a$ & $v$ & $a$ & $v$ & $a$\\\midrule"]
    cells = [f"{x} & {s}" for x, s in rest]
    while len(cells) % 4:
        cells.append(" & ")
    for i in range(0, len(cells), 4):
        out.append(" & ".join(cells[i:i + 4]) + r"\\")
    out.append(r"\bottomrule\end{tabular}\end{center}")
    (PAPER / "table_rephased.tex").write_text("\n".join(out) + "\n")
    z = ", ".join(map(str, zero))
    (PAPER / "table_zero.tex").write_text(z + "\n")
    print(len(zero), "zero-shift velocities;", len(rest), "others")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
