"""Figure for chapter 11 (English edition): certified curvature bounds (gaussienne exp(-pi a r^2)).

Toutes les valeurs sont lues dans le dossier du papier doi:10.5281/zenodo.23655392
(papers/p2_certified_zero_point/data/run_*.json et le tableau des reruns de AUDIT.md).
Rien n'est retapé à la main : le script lit les fichiers et vérifie la cohérence.
"""
from __future__ import annotations

import json
import re
from fractions import Fraction
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
REC = ROOT / "papers" / "p2_certified_zero_point"
OUT = ROOT / "papers" / "discovery_journal_2026_en" / "figures"

OKABE = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73",
         "yellow": "#F0E442", "blue": "#0072B2", "vermillion": "#D55E00", "purple": "#CC79A7"}
IVORY = "#FFFFF0"


def load_run(name: str) -> dict:
    with open(REC / "data" / name, encoding="utf-8") as fh:
        return json.load(fh)


def interval_B(run: dict) -> tuple[float, float]:
    lo = float(Fraction(run["B"]["lo"]))
    hi = float(Fraction(run["B"]["hi"]))
    return lo, hi


def audit_coarse_bhi(audit_text: str) -> list[tuple[str, float]]:
    """Lit les lignes « auditor a=1 ... » du tableau des reruns grossiers de AUDIT.md."""
    rows: list[tuple[str, float]] = []
    pat = re.compile(r"^\| \*\*auditor a=1, (N=\d+, depth \d+)[^|]*\*\* \| ([\d,]+) \| \[[^\]]+\] \| \*\*(-?[\d.]+)\*\*")
    for line in audit_text.splitlines():
        m = pat.match(line)
        if m:
            rows.append((m.group(1), float(m.group(3))))
    return rows


def fr(x: float, _pos: int | None = None) -> str:
    s = f"{x:g}"
    return s.replace("-", "−")


def main() -> None:
    main_run = load_run("run_a1_shear_main.json")
    diag = load_run("run_a1_diag_ctl.json")
    half = load_run("run_a05_shear_limit.json")
    neg = load_run("run_a2_shear_negctl.json")
    coarse = audit_coarse_bhi((REC / "AUDIT.md").read_text(encoding="utf-8"))
    assert len(coarse) == 2, coarse

    # Contrôles de cohérence avec le texte du papier.
    b_main = interval_B(main_run)
    assert abs(b_main[1] - (-1.84156)) < 1e-5, b_main
    assert main_run["stats"]["cells"] == 206468 and main_run["stats"]["failed"] == 0, main_run["stats"]
    assert main_run["certified_B_negative"] is True and neg["certified_B_negative"] is False
    b_neg = interval_B(neg)
    assert b_neg[0] > 0, "le contrôle a = 2 doit rester positif"
    # La borne du calcul principal recalculée avec les fractions copiées dans Lean.
    upp0_hi = Fraction(-475041875131, 250000000000)
    trw_hi = Fraction(366706720019, 200000000000)
    esum_hi = Fraction(31964165579, 10**12)
    b_lean = upp0_hi + trw_hi * esum_hi
    assert b_lean < 0 and abs(float(b_lean) - b_main[1]) < 1e-6, float(b_lean)

    rows: list[tuple[str, float, float, str]] = [
        ("a = 1, main computation\n(206,468 cells)", b_main[0], b_main[1], OKABE["blue"]),
        ("a = 1, other path\n(control)", *interval_B(diag), OKABE["sky"]),
    ]
    for label, bhi in coarse:
        n = label.split(",")[0].replace("N=", "")
        rows.append((f"a = 1, redone by the auditor\n(coarse grid {n})", bhi, bhi, OKABE["green"]))
    rows.append(("a = 1/2 (not foreseen\nin the preregistration)", *interval_B(half), OKABE["purple"]))
    rows.append(("a = 2: control that\nmust fail", b_neg[0], b_neg[1], OKABE["vermillion"]))

    plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 9})
    fig, ax = plt.subplots(figsize=(6.3, 3.4), dpi=300)
    fig.patch.set_facecolor(IVORY)
    ax.set_facecolor(IVORY)
    ax.axvspan(-2.6, 0.0, color=OKABE["green"], alpha=0.08, lw=0)
    ax.axvline(0.0, color=OKABE["black"], lw=0.9)
    ys = list(range(len(rows)))[::-1]
    for y, (label, lo, hi, col) in zip(ys, rows):
        if hi > lo:
            ax.plot([lo, hi], [y, y], color=col, lw=5, solid_capstyle="butt")
        ax.plot([hi], [y], marker="|", ms=12, mew=2, color=col)
        ax.annotate(fr(round(hi, 3)), (hi, y), xytext=(6, 4), textcoords="offset points", fontsize=7.5, color=col)
    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows], fontsize=7.5)
    ax.set_xlim(-2.6, 14.0)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.xaxis.set_major_formatter(FuncFormatter(fr))
    ax.set_xlabel("certified bound on the curvature of the roof (line: upper bound)")
    ax.text(-2.5, len(rows) - 0.55, "negative: \"not a minimum\"", fontsize=7.5, color=OKABE["green"])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"c11_courbures.{ext}", dpi=300, facecolor=IVORY)
    print("rows:", [(r[0].replace("\n", " "), round(r[1], 5), round(r[2], 5)) for r in rows])
    print("B (fractions Lean) =", float(b_lean))


if __name__ == "__main__":
    main()
