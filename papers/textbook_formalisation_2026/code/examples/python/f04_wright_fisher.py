"""Annexe F, exemple 4 : puissances exactes de la matrice de Wright-Fisher (fractions), P^n(i,N) -> i/N.

P(i,j) = C(N,j) (i/N)^j (1-i/N)^(N-j). Tout est calcule en fractions exactes (module fractions) :
  - la matrice est stochastique et h(i) = i/N est harmonique (P h = h), exactement ;
  - P^n(i,N) tend vers i/N, et l'ecart decroit comme (1 - 1/N)^n (deuxieme valeur propre de Wright-Fisher) ;
  - temoin negatif : avec selection (poids r = 2 sur le type mutant), h(i) = i/N n'est plus harmonique.
C'est l'enonce de KAL (limite d'absorption de Kolmogorov) dans le cas neutre. Usage : python -I f04_wright_fisher.py
"""
from __future__ import annotations

import math
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import appF_style as st  # noqa: E402

Matrix = list[list[Fraction]]


def wright_fisher(n_pop: int, r: Fraction = Fraction(1)) -> Matrix:
    """Noyau de Wright-Fisher ; r != 1 : tirage avec probabilite r i / (r i + N - i) (selection)."""
    rows = []
    for i in range(n_pop + 1):
        p = r * i / (r * i + n_pop - i)
        rows.append([math.comb(n_pop, j) * p**j * (1 - p) ** (n_pop - j) for j in range(n_pop + 1)])
    return rows


def matmul(a: Matrix, b: Matrix) -> Matrix:
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def main() -> int:
    n_pop = 6
    p = wright_fisher(n_pop)
    h = [Fraction(i, n_pop) for i in range(n_pop + 1)]
    stochastic = all(sum(row) == 1 for row in p)
    harmonic = all(sum(pij * hj for pij, hj in zip(row, h)) == hi for row, hi in zip(p, h))
    ps = wright_fisher(n_pop, Fraction(2))
    harmonic_sel = all(sum(pij * hj for pij, hj in zip(row, h)) == hi for row, hi in zip(ps, h))
    print(f"N={n_pop}: stochastique={stochastic}  P h = h exactement={harmonic}"
          f"  | temoin r=2: P h = h ? {harmonic_sel}")
    pn, gaps = p, []
    for n in range(1, 61):
        if n > 1:
            pn = matmul(pn, p)
        gaps.append(max(abs(pn[i][n_pop] - h[i]) for i in range(n_pop + 1)))
        if n in (1, 2, 5, 10, 30, 60):
            print(f"n={n:<3} P^n(2,N) = {float(pn[2][n_pop]):.15f}   max_i |P^n(i,N) - i/N| = {float(gaps[-1]):.3e}"
                  f"   (taille du denominateur: {len(str(pn[2][n_pop].denominator))} chiffres)")
    rate = float(gaps[59] / gaps[58])
    print(f"rapport des ecarts n=60/n=59 : {rate:.12f}   1 - 1/N = {1 - 1 / n_pop:.12f}")
    ok = stochastic and harmonic and not harmonic_sel and abs(rate - (1 - 1 / n_pop)) < 1e-6
    plot([float(g) for g in gaps], n_pop)
    print("temoins conformes:", ok)
    return 0 if ok else 1


def plot(gaps: list[float], n_pop: int) -> None:
    plt = st.setup()
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.4))
    p = wright_fisher(n_pop)
    pn = p
    for n in range(1, 21):
        if n > 1:
            pn = matmul(pn, p)
        if n in (1, 3, 20):
            mk = {1: "o", 3: "s", 20: "^"}[n]
            col = {1: st.BLUE, 3: st.ORANGE, 20: st.GREEN}[n]
            ax[0].plot(range(n_pop + 1), [float(pn[i][n_pop]) for i in range(n_pop + 1)], marker=mk, color=col,
                       label=f"$P^{{{n}}}(i,N)$")
    ax[0].plot(range(n_pop + 1), [i / n_pop for i in range(n_pop + 1)], "--", color=st.GREY, lw=1, label="i/N")
    ax[0].set_xlabel("nombre initial de mutants i")
    ax[0].set_ylabel("probabilité d'être fixé au temps n")
    ax[0].set_title(f"(a) Wright-Fisher neutre, N = {n_pop}")
    ax[0].legend()
    ns = range(1, len(gaps) + 1)
    ax[1].semilogy(ns, gaps, "o", ms=3, mfc="white", mec=st.BLUE, label=r"$\max_i |P^n(i,N)-i/N|$ (exact)")
    ax[1].semilogy(ns, [gaps[-1] * (1 - 1 / n_pop) ** (n - len(gaps)) for n in ns], color=st.GREY, lw=1,
                   label=r"pente $(1-1/N)^n$")
    ax[1].set_xlabel("génération n")
    ax[1].set_title("(b) convergence géométrique")
    ax[1].legend()
    fig.tight_layout()
    print("figure:", st.save(fig, "appF_wright_fisher").name)


if __name__ == "__main__":
    sys.exit(main())
