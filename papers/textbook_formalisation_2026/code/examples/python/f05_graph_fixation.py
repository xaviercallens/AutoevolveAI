"""Annexe F, exemple 5 : fixation sur un graphe isotherme et sur l'etoile, par resolution lineaire exacte.

Processus naissance-mort (celui de N4, Lieberman-Hauert-Nowak) : un individu i est choisi avec probabilite
f_i / F (f = r pour un mutant, 1 sinon) ; son descendant remplace j avec probabilite W(i,j).
L'etat est l'ensemble S des mutants (2^n etats). La probabilite de fixation x_S est l'unique solution de
  x_vide = 0, x_tout = 1, sum_S' P(S,S') (x_S' - x_S) = 0 pour S interieur,
resolue en fractions exactes par elimination de Gauss.
Temoins positifs : cycle a 4 sommets (isotherme) -> 8/15 de partout a r = 2 (Moran) ; etoile n = 3 -> 5/12 (centre),
2/3 (feuille), 7/12 (moyenne), valeurs de N4. Temoin negatif : l'etoile n'est pas isotherme et s'ecarte de Moran.
Usage : python -I f05_graph_fixation.py
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import appF_style as st  # noqa: E402

Kernel = list[list[Fraction]]


def cycle(n: int) -> Kernel:
    half = Fraction(1, 2)
    return [[half if (j - i) % n in (1, n - 1) else Fraction(0) for j in range(n)] for i in range(n)]


def star(n: int) -> Kernel:
    """Centre 0 relie aux n - 1 feuilles : W(0,j) = 1/(n-1), W(j,0) = 1."""
    w = [[Fraction(0)] * n for _ in range(n)]
    for j in range(1, n):
        w[0][j], w[j][0] = Fraction(1, n - 1), Fraction(1)
    return w


def transitions(w: Kernel, r: Fraction, s: int) -> dict[int, Fraction]:
    """Probabilites de transition depuis l'ensemble de mutants s (masque de bits)."""
    n = len(w)
    fit = [r if s >> i & 1 else Fraction(1) for i in range(n)]
    total = sum(fit)
    out: dict[int, Fraction] = {}
    for i in range(n):
        for j in range(n):
            if w[i][j] and (s >> i & 1) != (s >> j & 1):
                t = s | 1 << j if s >> i & 1 else s & ~(1 << j)
                out[t] = out.get(t, Fraction(0)) + fit[i] / total * w[i][j]
    return out


def fixation(w: Kernel, r: Fraction) -> list[Fraction]:
    """x_S pour les 2^n ensembles S, par elimination de Gauss exacte."""
    n = len(w)
    full, inner = (1 << n) - 1, list(range(1, (1 << n) - 1))
    idx = {s: k for k, s in enumerate(inner)}
    a = [[Fraction(0)] * (len(inner) + 1) for _ in inner]
    for s in inner:
        row = a[idx[s]]
        for t, p in transitions(w, r, s).items():
            row[idx[s]] -= p
            if t == full:
                row[-1] -= p  # x_tout = 1 passe au second membre
            elif t in idx:
                row[idx[t]] += p
    for c in range(len(inner)):  # pivot de Gauss (la matrice est inversible)
        piv = next(k for k in range(c, len(inner)) if a[k][c] != 0)
        a[c], a[piv] = a[piv], a[c]
        for k in range(len(inner)):
            if k != c and a[k][c] != 0:
                f = a[k][c] / a[c][c]
                a[k] = [x - f * y for x, y in zip(a[k], a[c])]
    x = [Fraction(0)] * (full + 1)
    x[full] = Fraction(1)
    for s in inner:
        x[s] = a[idx[s]][-1] / a[idx[s]][idx[s]]
    return x


def moran(n: int, r: Fraction, i: int) -> Fraction:
    return (1 - r**-i) / (1 - r**-n)


def report(name: str, w: Kernel, r: Fraction) -> tuple[Fraction, Fraction, Fraction]:
    n = len(w)
    x = fixation(w, r)
    singles = [x[1 << v] for v in range(n)]
    mean = sum(singles) / n
    print(f"{name:<9} r={r}: mutant seul en v -> {[str(q) for q in singles]}  moyenne={mean}  Moran={moran(n, r, 1)}")
    return singles[0], singles[-1], mean


def main() -> int:
    r = Fraction(2)
    c4 = report("cycle-4", cycle(4), r)
    s3 = report("etoile-3", star(3), r)
    s4 = report("etoile-4", star(4), r)
    up = {}
    for name, s in (("voisins", 0b0011), ("opposes", 0b0101)):
        tr = transitions(cycle(4), r, s)
        p_up = sum(p for t, p in tr.items() if bin(t).count("1") == 3)
        p_down = sum(p for t, p in tr.items() if bin(t).count("1") == 1)
        up[name] = (p_up, p_up / p_down)
        print(f"cycle-4, 2 mutants {name}: P+ = {p_up}, P- = {p_down}, P+/P- = {p_up / p_down}"
              " (biais par configuration)")
    ok = (all(q == moran(4, r, 1) for q in c4) and s3 == (Fraction(5, 12), Fraction(2, 3), Fraction(7, 12))
          and s4[2] != moran(4, r, 1) and up == {"voisins": (Fraction(1, 3), r), "opposes": (Fraction(2, 3), r)})
    plot()
    print("temoins conformes:", ok)
    return 0 if ok else 1


def plot() -> None:
    import numpy as np

    plt = st.setup()
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.5), gridspec_kw={"width_ratios": [1, 1.6]})
    pos_c = [(np.cos(t), np.sin(t)) for t in np.pi / 2 + np.arange(4) * np.pi / 2]
    pos_s = [(3.2, 0.0)] + [(3.2 + np.cos(t), np.sin(t)) for t in np.pi / 2 + np.arange(3) * 2 * np.pi / 3]
    for pos, edges, col in ((pos_c, [(0, 1), (1, 2), (2, 3), (3, 0)], st.BLUE), (pos_s, [(0, 1), (0, 2), (0, 3)], st.ORANGE)):
        for i, j in edges:
            ax[0].plot([pos[i][0], pos[j][0]], [pos[i][1], pos[j][1]], color=st.GREY, lw=1)
        ax[0].plot([p[0] for p in pos], [p[1] for p in pos], "o", ms=11, color=col)
    ax[0].text(0, -1.6, "cycle (isotherme)", ha="center")
    ax[0].text(3.2, -1.6, "étoile (non isotherme)", ha="center")
    ax[0].set_xlim(-1.5, 4.7)
    ax[0].set_ylim(-1.9, 1.4)
    ax[0].set_aspect("equal")
    ax[0].axis("off")
    ax[0].set_title("(a) les deux graphes à n = 4 sommets")
    rs = [Fraction(k, 10) for k in range(5, 31, 1)]
    curves = {"cycle": [], "centre": [], "feuille": [], "moyenne": []}
    for r in rs:
        xc, xs = fixation(cycle(4), r), fixation(star(4), r)
        curves["cycle"].append(float(xc[1]))
        curves["centre"].append(float(xs[1]))
        curves["feuille"].append(float(xs[2]))
        curves["moyenne"].append(float(sum(xs[1 << v] for v in range(4)) / 4))
    rf = [float(r) for r in rs]
    ax[1].plot(rf, [float(moran(4, r, 1)) if r != 1 else 0.25 for r in rs], color=st.GREY, lw=1, label="Moran (formule)")
    ax[1].plot(rf, curves["cycle"], "o", ms=4, mfc="white", mec=st.BLUE, label="cycle, n'importe quel sommet")
    ax[1].plot(rf, curves["centre"], "s-", ms=3, color=st.ORANGE, label="étoile, mutant au centre")
    ax[1].plot(rf, curves["feuille"], "^-", ms=3, color=st.GREEN, label="étoile, mutant sur une feuille")
    ax[1].plot(rf, curves["moyenne"], "--", color=st.ORANGE, lw=1, label="étoile, départ uniforme")
    ax[1].set_xlabel("valeur sélective relative r")
    ax[1].set_ylabel("probabilité de fixation d'un mutant")
    ax[1].set_title("(b) calcul exact en fractions, n = 4")
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    print("figure:", st.save(fig, "appF_graph_fixation").name)


if __name__ == "__main__":
    sys.exit(main())
