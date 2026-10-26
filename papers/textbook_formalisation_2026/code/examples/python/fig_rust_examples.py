"""Annexe F, figures des exemples Rust 7 a 9, tracees a partir des CSV ecrits par les binaires de
qf-textbook-examples (rusty-SUNDIALS) : tb_moran_forward, tb_yukawa_relax, tb_shell_sigma3.

Aucun nombre n'est recalcule ici : le script lit les fichiers du dossier donne (par defaut logs/rust_out).
Usage : python -I fig_rust_examples.py [DOSSIER_CSV]
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import appF_style as st  # noqa: E402

DEFAULT = Path(__file__).resolve().parents[1] / "logs" / "rust_out"


def rows(path: Path) -> list[dict[str, float]]:
    with path.open() as f:
        return [{k: float(v) for k, v in r.items()} for r in csv.DictReader(f)]


def moran(d: Path, plt: object) -> None:
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.4))  # type: ignore[attr-defined]
    tab = rows(d / "moran_N10.csv")
    for r, col, mk in ((0.8, st.ORANGE, "s"), (1.0, st.GREY, "^"), (1.5, st.BLUE, "o")):
        sub = [x for x in tab if x["r"] == r]
        ax[0].plot([x["i"] / 10 for x in sub], [x["p_exact"] for x in sub], color=col, lw=1)
        ax[0].plot([x["i"] / 10 for x in sub], [x["p_cvode"] for x in sub], mk, mfc="white", mec=col,
                   label=f"r = {r:g}")
    ax[0].set_xlabel("fréquence initiale i/N (N = 10)")
    ax[0].set_ylabel("probabilité de fixation")
    ax[0].set_title("(a) CVODE (marqueurs) et formule exacte (traits)")
    ax[0].legend()
    tr = rows(d / "moran_trace_N3.csv")
    t = [x["t"] for x in tr]
    ax[1].semilogx(t, [x["p_absorbed_N"] for x in tr], "o-", color=st.BLUE, label="masse en N (fixation)")
    ax[1].semilogx(t, [x["interior"] for x in tr], "s-", color=st.ORANGE, label="masse intérieure")
    ax[1].axhline(4 / 7, color=st.GREY, lw=1, ls="--")
    ax[1].text(t[0], 4 / 7 + 0.03, "4/7", color=st.GREY, fontsize=8)
    ax[1].set_xlabel("temps t (pas de Moran)")
    ax[1].set_title(r"(b) $\dot\pi=\pi(P-I)$, N = 3, r = 2, i = 1")
    ax[1].legend()
    fig.tight_layout()
    print("figure:", st.save(fig, "appF_rust_moran").name)


def yukawa(d: Path, plt: object) -> None:
    fig, ax = plt.subplots(1, 3, figsize=(11.5, 3.5), gridspec_kw={"width_ratios": [1.3, 1, 1]})  # type: ignore[attr-defined]
    e_tri = 0.393542848871227  # imprime par tb_yukawa_relax (log f08), somme exacte R = 12
    for name, col, mk, lab in (("tri_perturbed", st.BLUE, "o", "triangulaire perturbé"),
                               ("random", st.GREEN, "^", "départ aléatoire"),
                               ("square_perturbed", st.ORANGE, "s", "carré perturbé (boîte carrée)")):
        tr = rows(d / f"yukawa_{name}_trace.csv")
        tt = [max(x["t"], 1e-3) for x in tr]
        gap = [max(x["energy_per_particle"] - e_tri, 1e-16) for x in tr]
        ax[0].loglog(tt, gap, marker=mk, ms=3, color=col, label=lab)
    ax[0].set_xlabel("temps de relaxation t (t = 0 placé à 1e-3)")
    ax[0].set_ylabel(r"$E/N - E_{\mathrm{tri}}$")
    ax[0].set_title(r"(a) énergie au-dessus du réseau triangulaire")
    ax[0].legend(fontsize=7)
    a = math.sqrt(2 / math.sqrt(3))
    for axk, name, box, title in ((ax[1], "random", (8 * a, 4 * math.sqrt(3) * a), "(b) aléatoire, état final"),
                                  (ax[2], "square_perturbed", (8.0, 8.0), "(c) boîte carrée, état final")):
        pts = rows(d / f"yukawa_{name}_final.csv")
        axk.plot([p["x"] for p in pts], [p["y"] for p in pts], "o", ms=4, color=st.BLUE)
        axk.plot([0, box[0], box[0], 0, 0], [0, 0, box[1], box[1], 0], color=st.GREY, lw=0.8)
        axk.set_aspect("equal")
        axk.set_xticks([])
        axk.set_yticks([])
        axk.set_title(title)
    fig.tight_layout()
    print("figure:", st.save(fig, "appF_rust_yukawa").name)


def shell(d: Path, plt: object) -> None:
    tr = rows(d / "shell_sigma3_trace.csv")
    s0, h0 = tr[0]["S"], tr[0]["H"]
    bound = h0 + s0**1.5
    t = [x["t"] for x in tr]
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.3))  # type: ignore[attr-defined]
    ax[0].semilogy(t, [max(abs(x["S"] - s0) / s0, 1e-17) for x in tr], color=st.BLUE, label=r"$|S(t)-S(0)|/S(0)$")
    ax[0].semilogy(t, [max(abs(x["H"] - h0) / abs(h0), 1e-17) for x in tr], "--", color=st.ORANGE,
                   label=r"$|H_3(t)-H_3(0)|/|H_3(0)|$")
    ax[0].set_xlabel("t")
    ax[0].set_title("(a) dérive des deux invariants (CVODE, rtol 1e-10)")
    ax[0].legend()
    ax[1].plot(t, [2 * 0.05 * x["Omega"] / bound for x in tr], color=st.BLUE, label=r"$2D\,\Omega(t)/(H_3(0)+S(0)^{3/2})$")
    ax[1].axhline(1, color=st.GREY, lw=1, ls="--")
    ax[1].text(0.02, 0.93, "borne de Lean (Niveau A)", color=st.GREY, fontsize=8)
    ax[1].set_ylim(0, 1.1)
    ax[1].set_xlabel("t")
    ax[1].set_title(r"(b) l'enstrophie reste sous la borne, $\sigma = 3$, D = 0,05")
    ax[1].legend(loc="center right")
    fig.tight_layout()
    print("figure:", st.save(fig, "appF_rust_shell").name)


def main() -> int:
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    plt = st.setup()
    moran(d, plt)
    yukawa(d, plt)
    shell(d, plt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
