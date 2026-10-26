"""Figure du chapitre 12 : ancienne et nouvelle méthode, potentiels de Yukawa (N2).

Valeurs lues dans papers/p3_zero_point_physical/data/result.json (doi:10.5281/zenodo.23663551) :
encadrement certifié de U_lin''(0) (majorante fixe de l'article précédent) et de M (majorante mobile),
plus la valeur approchée (niveau X) de E''(0). Rien n'est retapé à la main.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
REC = ROOT / "papers" / "p3_zero_point_physical"
OUT = ROOT / "papers" / "discovery_journal_2026" / "figures"
OKABE = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73",
         "blue": "#0072B2", "vermillion": "#D55E00", "purple": "#CC79A7"}
IVORY = "#FFFFF0"

ROWS: list[tuple[str, str, str]] = [
    ("yukawa1_main", "yukawa:1.0", "Yukawa, écran 1"),
    ("yukawa2_main", "yukawa:2.0", "Yukawa, écran 2"),
    ("gauss1_positive_control", "gauss:1.0", "cloche a = 1\n(contrôle positif)"),
    ("gauss2_negative_control", "gauss:2.0", "cloche a = 2\n(contrôle négatif)"),
]


def fr(x: float, _pos: int | None = None) -> str:
    return f"{x:g}".replace("-", "−").replace(".", ",")


def main() -> None:
    with open(REC / "data" / "result.json", encoding="utf-8") as fh:
        res = json.load(fh)
    runs = res["runs"]
    scan = res["tierx_scan_rc40"]
    # Contrôles : signes annoncés dans le papier.
    assert runs["yukawa1_main"]["certified_not_local_min"] and runs["yukawa2_main"]["certified_not_local_min"]
    assert not runs["gauss2_negative_control"]["certified_not_local_min"]
    assert abs(runs["yukawa1_main"]["M_window_curvature_bound"]["hi_float"] - (-2.03704)) < 1e-5
    assert abs(runs["yukawa2_main"]["M_window_curvature_bound"]["hi_float"] - (-1.86854)) < 1e-5
    cells = runs["yukawa1_main"]["stats"]["cells"] + runs["yukawa2_main"]["stats"]["cells"]
    assert cells == 86581, cells

    plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 9})
    fig, ax = plt.subplots(figsize=(6.3, 3.2), dpi=300)
    fig.patch.set_facecolor(IVORY)
    ax.set_facecolor(IVORY)
    ax.axvline(0.0, color=OKABE["black"], lw=0.9)
    n = len(ROWS)
    for k, (key, skey, label) in enumerate(ROWS):
        y = n - 1 - k
        r = runs[key]
        ul = r["U_lin_pp0_B2_majorant"]
        m = r["M_window_curvature_bound"]
        ax.plot([ul["lo_float"], ul["hi_float"]], [y + 0.17] * 2, color=OKABE["orange"], lw=6, solid_capstyle="butt",
                marker="|", ms=10, mew=2, label="ancienne majorante (fixe)" if k == 0 else None)
        ax.plot([m["lo_float"], m["hi_float"]], [y - 0.17] * 2, color=OKABE["blue"], lw=6, solid_capstyle="butt",
                label="nouvelle majorante (mobile)" if k == 0 else None)
        ax.plot([scan[skey]["E_pp0"]], [y - 0.17], marker="o", ms=4, color=OKABE["black"],
                label="valeur approchée de la courbure (niveau X)" if k == 0 else None)
    ax.set_yticks(list(range(n))[::-1])
    ax.set_yticklabels([r[2] for r in ROWS], fontsize=8)
    ax.set_xlim(-9.0, 14.0)
    ax.set_ylim(-0.6, n - 0.4)
    ax.xaxis.set_major_formatter(FuncFormatter(fr))
    ax.set_xlabel("courbure certifiée de la majorante ; entièrement à gauche de 0 : « pas un minimum »")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=6.5, frameon=False)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"spare_c12_majorantes.{ext}", dpi=300, facecolor=IVORY)
    for key, skey, label in ROWS:
        r = runs[key]
        print(label.replace("\n", " "), "U_lin", round(r["U_lin_pp0_B2_majorant"]["lo_float"], 5),
              round(r["U_lin_pp0_B2_majorant"]["hi_float"], 5), "M", round(r["M_window_curvature_bound"]["lo_float"], 5),
              round(r["M_window_curvature_bound"]["hi_float"], 5), "E''(X)", scan[skey]["E_pp0"])
    print("cells Yukawa:", cells)


if __name__ == "__main__":
    main()
