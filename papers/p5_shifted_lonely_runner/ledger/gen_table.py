"""Write table_certs.tex (papers/p5_shifted_lonely_runner) from data/certificates and data/logs/auditor_checker_rerun.jsonl.

The gamma column is the exact value gamma(v;s) printed by the auditor's checker (method B), re-run by us; nothing is typed by hand.
Run:  python3 -I gen_table.py
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent
DATA = PAPER / "data"


def main() -> int:
    rows = {}
    for line in (DATA / "logs" / "auditor_checker_rerun.jsonl").read_text().splitlines():
        d = json.loads(line)
        rows[d["n"]] = d
    out = [r"\begin{center}\scriptsize\begin{tabular}{rlrrrr}\toprule",
           r"$n$ & velocities & $\max v$ & $D$ & $\gamma(v;s)$ (exact) & $1/\gamma-(n+1)$\\\midrule"]
    margins = []
    for n in range(18, 39):
        cert = json.loads((DATA / "certificates" / f"cert_n{n:03d}.json").read_text())
        v = cert["v"]
        is_n = sorted(v) == list(range(1, n + 1))
        g = Fraction(rows[n]["gamma"])
        assert rows[n]["valid"] and rows[n]["coverA"] and rows[n]["coverB"] and g < Fraction(1, n + 1)
        m = float(1 / g - (n + 1))
        margins.append(m)
        label = r"$\{1,\dots,%d\}$" % n if is_n else "swapped set"
        out.append(f"{n} & {label} & {max(v)} & {cert['D']} & ${g.numerator}/{g.denominator}$ & {m:.4f}\\\\")
    out.append(r"\bottomrule\end{tabular}\end{center}")
    (PAPER / "table_certs.tex").write_text("\n".join(out) + "\n")
    lean_dir = PAPER.parent.parent / "formal_cert" / "Programmes" / "SLR18"
    hrows = [r"\begin{center}\scriptsize\begin{tabular}{ll}\toprule", r"file & sha256\\\midrule"]
    for stem in [f"SLRN{n:02d}" for n in range(5, 39)] + ["SLRP1", "SLRP1neg"]:
        h = hashlib.sha256((lean_dir / f"{stem}.lean").read_bytes()).hexdigest()
        hrows.append(f"\\texttt{{{stem}.lean}} & \\texttt{{{h}}}\\\\")
    hrows.append(r"\bottomrule\end{tabular}\end{center}")
    (PAPER / "table_lean_hashes.tex").write_text("\n".join(hrows) + "\n")
    print(f"min margin {min(margins):.4f}, max margin {max(margins):.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
