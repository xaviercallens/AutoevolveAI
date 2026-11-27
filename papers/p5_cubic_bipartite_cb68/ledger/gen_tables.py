"""Generate the counter tables of the EG-CB68 paper from the recorded JSON files (no hand transcription) and cross-check the hashes.

Inputs: data/main/{R_cap*_A,R_cap*_B,T_cap*_o*_A,T_cap*_o*_B}.json (producer), data/audit/out/mine_*.json (auditor search),
data/audit/out/prod_*.json (producer binary rebuilt by the auditor). Outputs: table_route1.tex, table_route2.tex, tables_check.json.
Run:  python3 -I gen_tables.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
MAIN = PAPER / "data" / "main"
AUD = PAPER / "data" / "audit" / "out"
KEYS = ("states", "attempted", "structural", "c8", "c16", "completions")


def load(p: Path) -> dict | None:
    return json.loads(p.read_text()) if p.exists() else None


def h(d: dict) -> str:
    return d.get("transcript_hash") or d["hash"]


def counters(d: dict) -> tuple:
    return tuple(d[k] for k in KEYS)


def fmt(n: int) -> str:
    return f"{n:,}".replace(",", r"\,")


def row(label: str, a: dict, b: dict | None, mine: dict | None, rebuilt: dict | None, cpu_key: str) -> tuple[str, dict]:
    ha = h(a)
    chk = {"A_hash": ha, "B_equal": None if b is None else (h(b) == ha and counters(b) == counters(a)),
           "auditor_search_equal": None if mine is None else (h(mine) == ha and counters(mine) == counters(a)),
           "rebuilt_producer_equal": None if rebuilt is None else (h(rebuilt) == ha and counters(rebuilt) == counters(a))}
    flags = "".join("Y" if v else ("-" if v is None else "N") for v in (chk["B_equal"], chk["auditor_search_equal"], chk["rebuilt_producer_equal"]))
    cells = " & ".join(fmt(x) for x in counters(a)[:5]) + r" & \textbf{0}"
    tex = rf"{label} & {cells} & \texttt{{{ha}}} & \texttt{{{flags}}} \\"
    return tex, chk


def main() -> int:
    check: dict = {}
    head = (r"\begin{tabular}{@{}lrrrrrrll@{}}" "\n" r"\toprule" "\n"
            r"cap (order) & states & attempted & structural & C8 & C16 & compl. & transcript hash & B/aud/reb \\ \midrule")
    # route 1
    lines = [head]
    for cap in range(30, 36):
        for o in (1, 2):
            a = load(MAIN / f"T_cap{cap}_o{o}_A.json")
            b = load(MAIN / f"T_cap{cap}_o{o}_B.json")
            m = load(AUD / f"mine_T_cap{cap}_o{o}.json")
            r = load(AUD / f"prod_T_cap{cap}_o{o}_A.json")
            assert a is not None
            tex, chk = row(rf"{cap} ({2 * cap}), orbit {o}", a, b, m, r, "cpu_seconds")
            lines.append(tex)
            check[f"T_cap{cap}_o{o}"] = chk
    lines += [r"\bottomrule", r"\end{tabular}"]
    (PAPER / "table_route1.tex").write_text("\n".join(lines) + "\n")
    # route 2
    lines = [head]
    for cap in range(29, 35):
        a = load(MAIN / f"R_cap{cap}_A.json")
        b = load(MAIN / f"R_cap{cap}_B.json")
        m = load(AUD / f"mine_R_cap{cap}.json")
        r = load(AUD / f"prod_R_cap{cap}_A.json")
        assert a is not None
        tex, chk = row(rf"{cap} ({2 * cap}), arbitrary root", a, b, m, r, "cpu_seconds")
        lines.append(tex)
        check[f"R_cap{cap}"] = chk
    lines += [r"\bottomrule", r"\end{tabular}"]
    (PAPER / "table_route2.tex").write_text("\n".join(lines) + "\n")
    bad = [k for k, v in check.items() if any(x is False for x in v.values())]
    (HERE / "tables_check.json").write_text(json.dumps({"rows": check, "disagreements": bad}, indent=1))
    print(f"rows {len(check)}; disagreements {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
