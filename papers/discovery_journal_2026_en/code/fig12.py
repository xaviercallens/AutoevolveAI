"""Figure du chapitre 12 : courbure de l'énergie de point zéro au réseau triangulaire,
en fonction du paramètre a de la cloche exp(-pi a r^2) (a grand = cloche étroite).

Toutes les valeurs sont lues dans le dossier du papier doi:10.5281/zenodo.23653833
(papers/prog_zero_point_optimality/data/mechanism.json, champ « scan » et « c_sign_changes »),
puis comparées aux nombres imprimés dans le papier (gen_numbers.tex). Rien n'est retapé à la main.
Le papier n'affirme le signe de c que pour 0,15 <= a <= 4 ; les points hors de cette fenêtre sont
dessinés en gris (a = 0,1 : réseau à peine stable ; a = 6 et 8 : précision signalée, a = 8 instable).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
REC = ROOT / "papers" / "prog_zero_point_optimality"
OUT = ROOT / "papers" / "discovery_journal_2026_en" / "figures"

OKABE = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73",
         "yellow": "#F0E442", "blue": "#0072B2", "vermillion": "#D55E00", "purple": "#CC79A7"}
GREY = "#999999"
IVORY = "#FFFFF0"

A_MIN, A_MAX = 0.15, 4.0          # fenêtre où le papier affirme le signe de c
TESTED_REFUTED = (0.5, 1.0)       # gaussiennes du test G1 réfutées
TESTED_SURVIVED = (0.25, 2.0, 4.0)  # gaussiennes du test G1 non réfutées


def macros(text: str) -> dict[str, str]:
    return dict(re.findall(r"\\newcommand\{\\(ZP\w+)\}\{([^}]*)\}", text))


def fr(x: float, _pos: int | None = None) -> str:
    s = f"{x:g}"
    return s.replace("-", "−").replace(".", ",")


def main() -> None:
    mech = json.loads((REC / "data" / "mechanism.json").read_text(encoding="utf-8"))
    mac = macros((REC / "gen_numbers.tex").read_text(encoding="utf-8"))
    scan = [(float(r["a"]), float(r["c_ezp"]), bool(r["tri_stable"])) for r in mech["scan"]]
    assert len(scan) == 23, len(scan)
    c_of = {a: c for a, c, _ in scan}

    # Cohérence avec le texte du papier (macros générées).
    for a, key in ((0.25, "ZPcQuarter"), (0.5, "ZPcHalf"), (1.0, "ZPcOne"), (2.0, "ZPcTwo"), (4.0, "ZPcFour")):
        assert abs(c_of[a] - float(mac[key])) < 5e-4, (a, c_of[a], mac[key])
    roots = sorted(float(r["root"]) for r in mech["c_sign_changes"])
    inside = [r for r in roots if A_MIN <= r <= A_MAX]
    assert len(inside) == 2, roots
    assert abs(inside[0] - float(mac["ZPRootOne"])) < 1e-5 and abs(inside[1] - float(mac["ZPRootTwo"])) < 1e-5, inside
    # Le signe de c doit être négatif exactement entre les deux racines, sur les points de la fenêtre.
    for a, c, _ in scan:
        if A_MIN <= a <= A_MAX:
            assert (c < 0) == (inside[0] < a < inside[1]), (a, c)
    # Relation c = (laplacien de E_zp)/4 aux gaussiennes du test, quand elle est enregistrée.
    for row in mech["at_G1_potentials"]:
        assert abs(row["c_ezp"] - row["ezp_lap"] / 4) < 1e-9, row["a"]

    in_win = [(a, c) for a, c, _ in scan if A_MIN <= a <= A_MAX]
    out_win = [(a, c) for a, c, _ in scan if not (A_MIN <= a <= A_MAX)]

    plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 9})
    fig, ax = plt.subplots(figsize=(6.3, 3.4), dpi=300)
    fig.patch.set_facecolor(IVORY)
    ax.set_facecolor(IVORY)
    ax.set_xscale("log")
    ax.axvspan(inside[0], inside[1], color=OKABE["vermillion"], alpha=0.10, lw=0)
    ax.axhline(0.0, color=OKABE["black"], lw=0.8)
    ax.plot([a for a, _ in in_win], [c for _, c in in_win], color=OKABE["blue"], lw=1.4, marker="o", ms=2.6, zorder=3)
    ax.plot([a for a, _ in out_win], [c for _, c in out_win], ls="none", marker="o", ms=3.2,
            mfc="none", mec=GREY, mew=0.9, zorder=3)
    for a in TESTED_REFUTED:
        ax.plot([a], [c_of[a]], marker="o", ms=7, color=OKABE["vermillion"], zorder=4)
    for a in TESTED_SURVIVED:
        ax.plot([a], [c_of[a]], marker="s", ms=6, color=OKABE["green"], zorder=4)
    for r in inside:
        ax.annotate(fr(round(r, 3)), (r, 0.0), xytext=(-4, 6), textcoords="offset points", ha="right",
                    fontsize=7.5, color=OKABE["vermillion"])
    ax.text(0.77, -1.28, r"$c<0$ : le triangle est un sommet local," "\npas un fond", ha="center", va="bottom",
            fontsize=7.5, color=OKABE["vermillion"])
    ax.text(0.09, 0.86, "← cloche plus large", fontsize=7.5, color=OKABE["black"])
    ax.text(9.3, 0.86, "cloche plus étroite →", fontsize=7.5, color=OKABE["black"], ha="right")
    ax.plot([], [], marker="o", ls="none", color=OKABE["vermillion"], label="testée, contre-exemple trouvé")
    ax.plot([], [], marker="s", ls="none", color=OKABE["green"], label="testée, pas de contre-exemple")
    ax.plot([], [], marker="o", ls="none", mfc="none", mec=GREY, label="hors fenêtre (non affirmé)")
    ax.legend(loc="lower right", fontsize=7, frameon=False)
    ax.set_xlim(0.085, 9.5)
    ax.set_ylim(-1.35, 0.95)
    ax.xaxis.set_major_locator(FixedLocator([0.1, 0.25, 0.5, 1, 2, 4, 8]))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.xaxis.set_major_formatter(FuncFormatter(fr))
    ax.yaxis.set_major_formatter(FuncFormatter(fr))
    ax.set_xlabel(r"paramètre $a$ de la répulsion en cloche $e^{-\pi a r^2}$")
    ax.set_ylabel(r"courbure $c$ au réseau triangulaire")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"c12_courbure_largeur.{ext}", dpi=300, facecolor=IVORY)
    print("roots in window:", [round(r, 5) for r in inside], "all roots:", [round(r, 5) for r in roots])
    print("scan:", [(a, round(c, 4)) for a, c, _ in scan])


if __name__ == "__main__":
    main()
