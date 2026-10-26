"""Style commun des figures de l'annexe F (meme palette que les figures du chapitre 5).

Les couleurs bleu / orange / vert portent l'identite des series ; le gris est reserve aux references
(formule exacte, valeur certifiee). Chaque serie a aussi un marqueur ou un style de trait propre, pour que
la lecture ne repose jamais sur la couleur seule.
"""
from __future__ import annotations

import os

# Au plus deux fils de calcul (machine partagee) : a fixer avant d'importer numpy.
for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "2")

from pathlib import Path  # noqa: E402

BLUE, ORANGE, GREEN, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#52514e"
BOOK = Path(__file__).resolve().parents[3]
FIGURES = BOOK / "figures"


def setup() -> object:
    """Configure matplotlib (sortie PDF, polices lisibles a 1/1 sur une page A4) et renvoie pyplot."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.size": 9, "axes.titlesize": 9, "axes.labelsize": 9, "legend.fontsize": 8,
        "xtick.labelsize": 8, "ytick.labelsize": 8, "lines.linewidth": 1.5, "lines.markersize": 5,
        "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
        "pdf.fonttype": 42, "savefig.bbox": "tight", "savefig.pad_inches": 0.04,
    })
    return plt


def save(fig: object, name: str) -> Path:
    """Ecrit figures/<name>.pdf et renvoie son chemin."""
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / f"{name}.pdf"
    fig.savefig(path)  # type: ignore[attr-defined]
    return path
