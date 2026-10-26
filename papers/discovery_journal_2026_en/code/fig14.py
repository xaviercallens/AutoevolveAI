"""Figure du chapitre 14 : les douze étapes du certificat revendiqué, et la part refaite dans le noyau Lean.

Lit le tableau des étapes de papers/p2_sandier_serfaty_lean/main.tex (doi:10.5281/zenodo.23656804) et
vérifie les totaux contre les macros de gen_numbers.tex (1 685 129 sur 1 238 829 689 opérations).
"""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
REC = ROOT / "papers" / "p2_sandier_serfaty_lean"
OUT = ROOT / "papers" / "discovery_journal_2026_en" / "figures"
OKABE = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73",
         "blue": "#0072B2", "vermillion": "#D55E00", "grey": "#999999"}
IVORY = "#FFFFF0"

FR_NAMES: dict[str, str] = {"1": "constantes", "2": "coefficients", "3": "grande table", "4": "test du cœur",
                            "5": "valeur au bord", "6": "λ et μ", "7": "K", "8": "assertions",
                            "9": "bornes des dérivées", "10": "grille globale", "11": "partie négative",
                            "12": "hessienne"}


def macro_int(text: str, name: str) -> int:
    m = re.search(r"\\newcommand\{\\" + name + r"\}\{([\d{},]+)\}", text)
    assert m is not None, name
    return int(m.group(1).replace("{,}", "").replace(",", ""))


def parse_stages(tex: str) -> list[tuple[str, int, bool]]:
    body = tex[tex.index("label{tab:stages}"):]
    body = body[:body.index("\\end{tabular}")]
    rows: list[tuple[str, int, bool]] = []
    for line in body.splitlines():
        m = re.match(r"^(\d+) & (.*)\\\\(\\bottomrule)?$", line.strip())
        if not m:
            continue
        cols = [c.strip() for c in m.group(2).split(" & ")]
        ops_field, status = cols[2], cols[3]
        n = re.match(r"^([\d{},]+)", ops_field)
        ops = int(n.group(1).replace("{,}", "")) if n else 0
        ported = "L1" in status and "complete" in status
        rows.append((m.group(1), ops, ported))
    return rows


def main() -> None:
    tex = (REC / "main.tex").read_text(encoding="utf-8")
    nums = (REC / "gen_numbers.tex").read_text(encoding="utf-8")
    rows = parse_stages(tex)
    assert [r[0] for r in rows] == [str(i) for i in range(1, 13)], rows
    total, done = sum(r[1] for r in rows), sum(r[1] for r in rows if r[2])
    assert total == macro_int(nums, "PTTotalOps"), total
    assert done == macro_int(nums, "PTDoneOps"), done
    assert sum(1 for r in rows if r[2]) == 4
    share = 100.0 * done / total

    plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 8.5})
    fig, ax = plt.subplots(figsize=(6.3, 3.3), dpi=300)
    fig.patch.set_facecolor(IVORY)
    ax.set_facecolor(IVORY)
    ys = list(range(len(rows)))[::-1]
    for y, (num, ops, ported) in zip(ys, rows):
        label = f"{num}. {FR_NAMES[num]}"
        if ops == 0:
            note = "(comptée avec 10)" if num == "11" else "(assertions seules, vérifiées sur les nombres exacts)"
            ax.text(1.3, y, note, va="center", fontsize=6.8, color=OKABE["grey"])
        else:
            ax.barh([y], [ops], left=1, color=OKABE["green"] if ported else OKABE["grey"], height=0.62)
            ax.text(ops * 1.3, y, f"{ops:,}".replace(",", "\u202f"), va="center", fontsize=6.8)
        ax.text(0.8, y, label, va="center", ha="right", fontsize=7.5)
    ax.set_xscale("log")
    ax.set_xlim(1, 8e10)
    ax.set_yticks([])
    ax.set_xlabel("opérations d'intervalles (multiplications et inversions), échelle logarithmique")
    ax.set_title(f"4 étapes sur 12 refaites dans le noyau : {share:.3f} % du calcul".replace(".", ","), fontsize=8.5)
    ax.legend(handles=[Patch(color=OKABE["green"], label="refaite dans le noyau Lean"),
                       Patch(color=OKABE["grey"], label="pas encore portée")],
              loc="upper right", fontsize=7, frameon=False)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    fig.subplots_adjust(left=0.24, right=0.98, top=0.9, bottom=0.16)
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"c14_etapes.{ext}", dpi=300, facecolor=IVORY)
    print("rows:", rows)
    print("done", done, "total", total, "share %", round(share, 4))


if __name__ == "__main__":
    main()
