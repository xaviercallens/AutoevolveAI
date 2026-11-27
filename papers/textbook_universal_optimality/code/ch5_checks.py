"""Chapter 5 numerical illustrations (Tier X). Pure numpy, no external data."""
import math

import numpy as np


def tri_s2_partial(R: float) -> float:
    b = math.sqrt(3) / 2
    sc = 1 / math.sqrt(b)
    K = int(R * 1.2 / (sc * b)) + 3
    j, k = np.meshgrid(np.arange(-K, K + 1), np.arange(-K, K + 1), indexing="ij")
    x = sc * (j + k / 2.0)
    y = sc * (k * b)
    r2 = x * x + y * y
    m = (r2 > 0) & (r2 <= R * R)
    return float(np.sum(1.0 / r2[m]))


def theta3(kind: str, alpha: float, K: int = 12) -> float:
    rng = np.arange(-K, K + 1)
    X, Y, Zc = np.meshgrid(rng, rng, rng, indexing="ij")
    pts = np.stack([X.ravel(), Y.ravel(), Zc.ravel()], axis=1).astype(float)
    if kind == "fcc":
        pts = pts[(pts.sum(axis=1) % 2) == 0]  # D3, covolume 2
        pts = pts * 2.0 ** (-1.0 / 3.0)
    else:
        pts = np.vstack([pts, pts + 0.5])  # bcc, covolume 1/2
        pts = pts * 2.0 ** (1.0 / 3.0)
    r2 = (pts ** 2).sum(axis=1)
    r2 = r2[r2 > 0]
    return float(np.sum(np.exp(-math.pi * alpha * r2)))


def main() -> None:
    print("s=2 triangular partial sums S(R) over 0<|a|<=R, and S(R)-2*pi*log R")
    for R in (50.0, 100.0, 200.0, 400.0, 800.0):
        S = tri_s2_partial(R)
        print(f"R={R:6.0f}  S={S:.6f}  S-2pi logR={S - 2 * math.pi * math.log(R):.6f}")
    print("density-one Gaussian lattice sums sum_{x!=0} exp(-pi alpha |x|^2)")
    for a in (0.5, 0.8, 1.0, 1.25, 2.0):
        f = theta3("fcc", a)
        bb = theta3("bcc", a)
        print(f"alpha={a:5.2f}  fcc={f:.10f}  bcc={bb:.10f}  fcc-bcc={f - bb:+.3e}")


if __name__ == "__main__":
    main()
