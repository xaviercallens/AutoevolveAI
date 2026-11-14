"""Annexe F, exemple 12 : controle croise CVODE (rusty-SUNDIALS) contre SciPy (Niveau X).

On relit les sorties des binaires Rust (logs/f07a_tb_stiff.txt et logs/rust_out/moran_trace_N3.csv) et on
recalcule les memes quantites avec deux methodes independantes de SciPy :
  1. probleme raide y' = lambda (y - cos t) - sin t : solve_ivp(method="Radau"), rtol 1e-12 ;
  2. equation de Kolmogorov progressive de Moran (N = 3, r = 2, i = 1) : exponentielle de matrice
     pi(t) = e_i expm(t (P - I)), sans aucun pas de temps.
Temoin positif : accord a la tolerance des solveurs. Temoin negatif : un decalage d'un temps de sortie
(comparer y(1) de CVODE a y(1,001) de SciPy) produit un desaccord bien visible.
Usage : python -I f12_scipy_crosscheck.py [DOSSIER_LOGS]
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import appF_style as st  # noqa: E402,F401  (fixe le nombre de fils avant numpy)

import numpy as np  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402
from scipy.linalg import expm  # noqa: E402

LOGS = Path(__file__).resolve().parents[1] / "logs"
LAM = -1e4


def cvode_stiff(log: Path) -> list[tuple[float, float]]:
    """Couples (t, y_cvode) lus dans la table imprimee par tb_stiff."""
    out = []
    for line in log.read_text().splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[0][0].isdigit():
            out.append((float(parts[0]), float(parts[1])))
    return out


def moran_kernel(n: int, r: float) -> np.ndarray:
    p = np.zeros((n + 1, n + 1))
    for i in range(n + 1):
        up = r * i / (r * i + n - i) * (n - i) / n
        down = (n - i) / (r * i + n - i) * i / n
        if i > 0:
            p[i, i - 1] = down
        if i < n:
            p[i, i + 1] = up
        p[i, i] = 1 - up - down
    return p


def main() -> int:
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else LOGS
    ok = True
    pts = cvode_stiff(d / "f07a_tb_stiff.txt")
    ts = [t for t, _ in pts]
    sol = solve_ivp(lambda t, y: LAM * (y - math.cos(t)) - math.sin(t), (0, ts[-1]), [2.0], method="Radau",
                    t_eval=ts, rtol=1e-12, atol=1e-14, jac=lambda t, y: [[LAM]])
    print(f"Radau: {sol.nfev} evaluations, statut {sol.status}")
    for (t, yc), ys in zip(pts, sol.y[0]):
        print(f"t={t:<8} CVODE={yc:+.15f}  SciPy Radau={ys:+.15f}  ecart={abs(yc - ys):.1e}")
        ok = ok and abs(yc - ys) < 1e-7
    y_shift = solve_ivp(lambda t, y: LAM * (y - math.cos(t)) - math.sin(t), (0, 1.001), [2.0], method="Radau",
                        rtol=1e-12, atol=1e-14).y[0][-1]
    yc1 = dict(pts)[1.0]
    ok = ok and abs(yc1 - y_shift) > 1e-4
    print(f"temoin negatif (t decale de 1e-3): ecart={abs(yc1 - y_shift):.2e}")
    with (d / "rust_out" / "moran_trace_N3.csv").open() as f:
        trace = [(float(r["t"]), float(r["p_absorbed_N"])) for r in csv.DictReader(f)]
    q = moran_kernel(3, 2.0) - np.eye(4)
    worst = 0.0
    for t, pc in trace:
        pe = expm(t * q)[1, 3]
        worst = max(worst, abs(pc - pe))
    print(f"Moran N=3 r=2 i=1: {len(trace)} temps de sortie, max |CVODE - expm| = {worst:.1e},"
          f" a t={trace[-1][0]:g}: CVODE={trace[-1][1]:.15f} expm={expm(trace[-1][0] * q)[1, 3]:.15f}")
    ok = ok and worst < 1e-8
    print("temoins conformes:", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
