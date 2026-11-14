"""Figure du chapitre 13 : reproduction du certificat Sandier--Serfaty (aucune preuve revendiquée).

Valeurs lues dans papers/prog_sandier_serfaty_audit/gen_numbers.tex (macros générées par gen_inputs.py
à partir des journaux d'exécution ; doi:10.5281/zenodo.23653827). Panneau (a) : durée des six étapes du
programme lors de la reproduction. Panneau (b) : l'identité de calibration et ses contrôles négatifs.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
REC = ROOT / "papers" / "prog_sandier_serfaty_audit"
OUT = ROOT / "papers" / "discovery_journal_2026" / "figures"
OKABE = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73",
         "blue": "#0072B2", "vermillion": "#D55E00", "purple": "#CC79A7"}
IVORY = "#FFFFF0"


def macros(path: Path) -> dict[str, str]:
    pat = re.compile(r"\\newcommand\{\\(SSA\w+)\}\{(.*)\}\s*$")
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = pat.match(line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def num(s: str) -> float:
    return float(s.replace("{,}", "").replace(",", ""))


def sci(s: str) -> float:
    """Lit une macro de la forme « -1.034\\times10^{-25} » (accolade finale absorbée par la regex)."""
    m = re.match(r"^(-?[\d.]+)\\times10\^\{(-?\d+)\}?$", s.strip())
    assert m is not None, s
    return float(m.group(1)) * 10.0 ** int(m.group(2))


def fr(x: float, _pos: int | None = None) -> str:
    return f"{x:g}".replace("-", "\u2212").replace(".", ",")


def main() -> None:
    mc = macros(REC / "gen_numbers.tex")
    stages = [("préparation", "SSATInitCore"), ("λ et μ", "SSATCalcLam"), ("K", "SSATCalcK"),
              ("bornes des dérivées", "SSATBdsup"), ("grille globale", "SSATGlobalGrid"), ("hessienne", "SSATInsideHess")]
    secs = [num(mc[k]) for _, k in stages]
    child = num(mc["SSAPosChild"])
    assert abs(sum(secs) - child) < 0.5, (sum(secs), child)
    assert mc["SSAPairsEqual"] == mc["SSAPairsTotal"] == "22"

    lam, mu, kk = num(mc["SSAReLam"]), num(mc["SSAReMu"]), num(mc["SSAReK"])
    w_tri = num(mc["SSAWtri"])
    lo, hi = num(mc["SSACalLo"]), num(mc["SSACalHi"])
    ident = 6 * kk + lam + 2 * math.pi * mu
    assert lo <= w_tri <= hi and abs(ident - w_tri) < 1e-9, (ident, w_tri)
    negs = [("réseau carré", num(mc["SSANegSquare"])), ("décalage oublié", num(mc["SSANegShift"])),
            ("facteur 2π oublié", num(mc["SSANegNoTwoPi"]))]
    assert all(not (lo <= v <= hi) for _, v in negs)

    plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 8.5})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.3, 2.8), dpi=300, gridspec_kw={"width_ratios": [1.05, 1]})
    fig.patch.set_facecolor(IVORY)
    for ax in (ax1, ax2):
        ax.set_facecolor(IVORY)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)

    names = [s[0].replace("_", " ") for s in stages]
    ys = list(range(len(stages)))[::-1]
    ax1.barh(ys, secs, color=OKABE["blue"], height=0.6)
    for y, v in zip(ys, secs):
        ax1.text(v + 4, y, fr(v) + " s", va="center", fontsize=7)
    ax1.set_yticks(ys)
    ax1.set_yticklabels(names, fontsize=7.5)
    ax1.set_xlim(0, 290)
    ax1.xaxis.set_major_formatter(FuncFormatter(fr))
    ax1.set_xlabel("secondes (reproduction du 25 octobre)")
    ax1.set_title(f"(a) six étapes, {fr(round(child))} s au total", fontsize=8.5)

    half = (hi - lo) / 2
    resid = abs(sci(mc["SSAReId"]))
    dist = [("recalcul depuis\nles formules", resid, OKABE["green"])] + [
        (n.replace(" ", "\n", 1), abs(v - w_tri), OKABE["vermillion"]) for n, v in negs]
    xs = list(range(len(dist)))
    ax2.axhline(half, color=OKABE["blue"], lw=1.2, ls="--")
    ax2.text(len(dist) - 0.6, half * 3, "demi-largeur de la bande certifiée", fontsize=6.5, color=OKABE["blue"], ha="right")
    for x, (n, v, col) in zip(xs, dist):
        ax2.plot([x], [v], marker="o", ms=5, color=col)
    ax2.set_yscale("log")
    ax2.set_ylim(1e-27, 1e2)
    ax2.set_xticks(xs)
    ax2.set_xticklabels([d[0] for d in dist], fontsize=7)
    ax2.set_xlim(-0.5, len(dist) - 0.5)
    ax2.set_ylabel("écart à la valeur exacte")
    ax2.set_title("(b) contrôle 6K + λ + 2πμ = W", fontsize=8.5)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"c13_reproduction.{ext}", dpi=300, facecolor=IVORY)
    print("stages:", dict(zip(names, secs)), "sum", round(sum(secs), 1), "child", child)
    print("identity:", ident, "W_tri", w_tri, "band", lo, hi, "width", hi - lo)
    print("negatives:", negs)
    print("distances:", [(d[0].replace(chr(10), " "), d[1]) for d in dist], "half-width", half)


if __name__ == "__main__":
    main()
