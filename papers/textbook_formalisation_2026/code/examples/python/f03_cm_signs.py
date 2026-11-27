"""Annexe F, exemple 3 : signes de (-1)^n g^(n)(t) avec mpmath, et un contre-exemple (Niveau X).

g est completement monotone (CM) si (-1)^n g^(n)(t) >= 0 pour tout n et tout t > 0. Un ordinateur ne teste
qu'un nombre fini de couples (n, t) : ce test peut REFUTER la CM (un seul signe faux suffit), jamais la prouver.
Les preuves sont en Lean (bibliotheque CM/Bernstein, theoreme ALEXIS pour les melanges de Laplace).
Fonctions de t = r^2 :
  gaussienne exp(-pi t), Yukawa exp(-sqrt t)/sqrt t, dipolaire 2(t^-1/2 - (t+1)^-1/2) (d = 1) : CM ;
  temoins negatifs : exp(-t) - exp(-2t)/2 (mesure de Bernstein de signe variable) et Lennard-Jones t^-6 - t^-3.
Usage : python -I f03_cm_signs.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import appF_style as st  # noqa: E402

import mpmath as mp  # noqa: E402

mp.mp.dps = 40
FUNCS = {
    "gauss": lambda t: mp.exp(-mp.pi * t),
    "yukawa": lambda t: mp.exp(-mp.sqrt(t)) / mp.sqrt(t),
    "dipolaire": lambda t: 2 * (1 / mp.sqrt(t) - 1 / mp.sqrt(t + 1)),
    "bernstein_signe_variable": lambda t: mp.exp(-t) - mp.exp(-2 * t) / 2,
    "lennard_jones": lambda t: t**-6 - t**-3,
}
TS = [mp.mpf(x) for x in ("0.05", "0.2", "0.5", "1", "2", "5", "10")]
NMAX = 8


def first_failure(g: object) -> tuple[int, str, str] | None:
    """Premier couple (n, t) ou (-1)^n g^(n)(t) < 0, ou None si tous les signes sont bons."""
    for n in range(NMAX + 1):
        for t in TS:
            val = (-1) ** n * mp.diff(g, t, n)
            if val < 0:
                return n, mp.nstr(t, 3), mp.nstr(val, 6)
    return None


def main() -> int:
    expect_cm = {"gauss": True, "yukawa": True, "dipolaire": True,
                 "bernstein_signe_variable": False, "lennard_jones": False}
    ok = True
    for name, g in FUNCS.items():
        fail = first_failure(g)
        ok = ok and (fail is None) == expect_cm[name]
        verdict = "tous les signes >= 0" if fail is None else f"ECHEC n={fail[0]} t={fail[1]} valeur={fail[2]}"
        print(f"{name:<25} n<={NMAX}, {len(TS)} valeurs de t : {verdict}")
    plot()
    print("temoins conformes:", ok)
    return 0 if ok else 1


def plot() -> None:
    import numpy as np

    plt = st.setup()
    names = list(FUNCS)
    labels = ["gaussienne", "Yukawa", "dipolaire (d = 1)", r"$e^{-t}-e^{-2t}/2$", "Lennard-Jones"]
    fig, ax = plt.subplots(1, len(names), figsize=(11.5, 2.6), sharey=True)
    for a, name, lab in zip(ax, names, labels):
        grid = np.array([[float((-1) ** n * mp.diff(FUNCS[name], t, n)) for t in TS] for n in range(NMAX + 1)])
        sign = np.sign(grid)
        a.imshow(sign, cmap=plt.matplotlib.colors.ListedColormap([st.ORANGE, "#ffffff", st.BLUE]),
                 vmin=-1, vmax=1, aspect="auto", origin="lower")
        for n in range(NMAX + 1):
            for k in range(len(TS)):
                a.text(k, n, "+" if sign[n, k] > 0 else "-", ha="center", va="center", fontsize=7,
                       color="white")
        a.set_xticks(range(len(TS)), [mp.nstr(t, 2) for t in TS], rotation=90)
        a.set_xlabel("t")
        a.set_title(lab)
    ax[0].set_ylabel(r"ordre $n$ de $(-1)^n g^{(n)}(t)$")
    fig.tight_layout()
    print("figure:", st.save(fig, "appF_cm_signs").name)


if __name__ == "__main__":
    sys.exit(main())
