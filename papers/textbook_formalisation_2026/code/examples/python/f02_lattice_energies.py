"""Annexe F, exemple 2 : energie par particule du reseau triangulaire et du reseau carre (Niveau X).

E(L) = 1/2 sum_{v in L, v != 0} V(|v|), densite 1, pour trois potentiels completement monotones en r^2 :
  gaussien  V = exp(-pi a r^2)           (E = (Theta_L(a) - 1)/2, une somme theta) ;
  Yukawa    V = exp(-kappa r)/r ;
  dipolaire U = V/d^2 = 2/(r s (r+s)), s = sqrt(r^2+d^2), plus la queue continue exacte 2 pi/(sqrt(R^2+d^2)+R).
On suit aussi l'arc tau = exp(i theta), theta de pi/3 (triangulaire) a pi/2 (carre).
Temoin positif : les valeurs enregistrees par rusty-SUNDIALS (qf-yukawa-crystal, exact_refs.jsonl et
lattice_gaps.jsonl) sont retrouvees. Temoin negatif : a pas egal (densites differentes), la comparaison
s'inverse ; c'est pourquoi tous les theoremes fixent la densite.
Usage : python -I f02_lattice_energies.py [--refs DOSSIER_RESULTS_QF_YUKAWA]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import appF_style as st  # noqa: E402

import numpy as np  # noqa: E402
from scipy.integrate import quad  # noqa: E402
from scipy.special import erfc  # noqa: E402

REFS = Path("/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-tb2-examples/crates/qf-yukawa-crystal/results")


def basis(theta: float) -> np.ndarray:
    """Base du reseau de forme tau = exp(i theta), mise a l'echelle pour la covolume 1."""
    s = 1.0 / math.sqrt(math.sin(theta))
    return np.array([[s, 0.0], [s * math.cos(theta), s * math.sin(theta)]])


def distances(b: np.ndarray, rmax: float) -> np.ndarray:
    """Normes des vecteurs non nuls du reseau de base b, de norme < rmax."""
    m = int(rmax / min(abs(b[1, 1]), abs(b[0, 0]) * abs(b[1, 1]))) + 3
    i, j = np.meshgrid(np.arange(-m, m + 1), np.arange(-m, m + 1))
    x, y = i * b[0, 0] + j * b[1, 0], i * b[0, 1] + j * b[1, 1]
    r = np.hypot(x, y).ravel()
    return np.sort(r[(r > 0) & (r < rmax)])[::-1]  # petits termes d'abord


def energy(pot: str, b: np.ndarray, rmax: float = 60.0) -> float:
    r = distances(b, rmax)
    if pot == "gauss":  # a = 1
        return 0.5 * float(np.exp(-math.pi * r * r).sum())
    if pot.startswith("yukawa"):
        kappa = float(pot.split(":")[1])
        return 0.5 * float((np.exp(-kappa * r) / r).sum())
    return dipolar(float(pot.split(":")[1]), b)


def dipolar(d: float, b: np.ndarray, big_r: float = 30.0, sig: float = 6.0) -> float:
    """U = V/d^2, queue en 1/r^3 : coupure douce w = erfc((r-R)/sig)/2 sur le reseau, et le reste
    (1-w) U integre comme un continuum de densite 1. Une coupure brutale laisserait une erreur ~1e-5."""
    u = lambda x: 2.0 / (x * math.sqrt(x * x + d * d) * (x + math.sqrt(x * x + d * d)))  # noqa: E731
    r = distances(b, big_r + 12 * sig)
    lattice = 0.5 * float(sum(u(x) * 0.5 * erfc((x - big_r) / sig) for x in r))
    rest = quad(lambda x: u(x) * (1 - 0.5 * erfc((x - big_r) / sig)) * math.pi * x, 1e-9, np.inf,
                limit=200, epsabs=1e-15, epsrel=1e-13)[0]
    return lattice + rest


def recorded(refs: Path) -> dict[str, tuple[float, float]]:
    out: dict[str, tuple[float, float]] = {}
    for line in (refs / "exact" / "exact_refs.jsonl").read_text().splitlines():
        row = json.loads(line)
        if row.get("kind") == "lattice":
            out[f"yukawa:{row['kappa']}"] = (row["tri"]["exact_partial"], row["square"]["exact_partial"])
    for line in (refs / "dipolar" / "lattice_gaps.jsonl").read_text().splitlines():
        row = json.loads(line)
        if row["d"] == 3.0:
            out["dipolar:3"] = (row["e_tri"], row["e_square"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refs", type=Path, default=REFS)
    args = ap.parse_args()
    ref = recorded(args.refs) if args.refs.is_dir() else {}
    tri, sq = basis(math.pi / 3), basis(math.pi / 2)
    ok = True
    print(f"{'potentiel':<11} {'E_tri':>19} {'E_carre':>19} {'carre-tri':>11}  ecart a la valeur enregistree")
    for pot in ("gauss", "yukawa:1", "yukawa:2", "dipolar:3"):
        et, es = energy(pot, tri), energy(pot, sq)
        note = "-"
        if pot in ref:
            dev = max(abs(et - ref[pot][0]), abs(es - ref[pot][1]))
            ok = ok and dev < 1e-10
            note = f"{dev:.1e}"
        ok = ok and es > et
        print(f"{pot:<11} {et:19.16f} {es:19.16f} {es - et:11.4e}  {note}")
    e_sharp = 0.5 * sum(2 / (x * math.hypot(x, 3) * (x + math.hypot(x, 3))) for x in distances(tri, 60.0))
    e_sharp += 2 * math.pi / (math.hypot(60.0, 3.0) + 60.0)
    print(f"dipolaire, coupure brutale R=60 + queue continue: ecart {abs(e_sharp - energy('dipolar:3', tri)):.1e}")
    print("== temoin negatif : pas egal a 1 (densites 2/sqrt(3) et 1) ==")
    tri_unit = tri / tri[0, 0]  # pas 1 : densite 2/sqrt(3) > 1
    et, es = energy("yukawa:1", tri_unit), energy("yukawa:1", sq)
    ok = ok and et > es
    print(f"yukawa:1   E_tri(pas 1)={et:.10f} > E_carre(pas 1)={es:.10f} : comparaison inversee")
    plot()
    print("temoins conformes:", ok)
    return 0 if ok else 1


def plot() -> None:
    plt = st.setup()
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.5))
    th = np.linspace(math.pi / 3, math.pi / 2, 41)
    for pot, col, mk, lab in (("gauss", st.BLUE, "o", "gaussien, a = 1"),
                              ("yukawa:1", st.ORANGE, "s", r"Yukawa, $\kappa = 1$"),
                              ("dipolar:3", st.GREEN, "^", "dipolaire, d = 3")):
        e = np.array([energy(pot, basis(t), 40.0) for t in th])
        ax[0].plot(np.degrees(th), (e - e[0]) / (e[-1] - e[0]), marker=mk, markevery=8, color=col, label=lab)
    ax[0].set_xlabel(r"angle $\theta$ du réseau (degrés) : 60 = triangulaire, 90 = carré")
    ax[0].set_ylabel(r"$(E(\theta)-E_{\mathrm{tri}})/(E_{\mathrm{carré}}-E_{\mathrm{tri}})$")
    ax[0].set_title("(a) énergie le long de l'arc triangulaire - carré")
    ax[0].legend()
    for b, col, lab in ((basis(math.pi / 3), st.BLUE, "triangulaire"), (basis(math.pi / 2), st.ORANGE, "carré")):
        i, j = np.meshgrid(np.arange(-4, 5), np.arange(-4, 5))
        x, y = i * b[0, 0] + j * b[1, 0], i * b[0, 1] + j * b[1, 1]
        keep = np.hypot(x, y) < 2.6
        ax[1].plot(x[keep], y[keep], "o" if lab == "triangulaire" else "s", ms=5 if lab == "triangulaire" else 4,
                   mfc="white" if lab == "carré" else col, mec=col, ls="none", label=lab)
    ax[1].add_patch(plt.Circle((0, 0), 2.5, fill=False, color=st.GREY, lw=0.8, ls="--"))
    ax[1].set_aspect("equal")
    ax[1].set_title("(b) les deux réseaux à densité 1 (disque de rayon 2,5)")
    ax[1].legend(loc="upper right", fontsize=7)
    fig.tight_layout()
    print("figure:", st.save(fig, "appF_lattice_energies").name)


if __name__ == "__main__":
    sys.exit(main())
