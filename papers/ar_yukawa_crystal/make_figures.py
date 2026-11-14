"""Figure fig_signs (Tier X illustration, never evidence): signed derivatives (-1)^n g^(n)(t) of the planar Yukawa
potential g(t) = exp(-kappa sqrt t)/sqrt t (kappa = 1) for n = 0..6, and the negative-control signed mixture
g_1 - 2 g_2, which changes sign. Derivatives by mpmath numerical differentiation at 40 digits.

Usage: python -I make_figures.py   (writes figures/fig_signs.{pdf,png} and figures/fig_signs.json)
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import mpmath as mp  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "figures"
mp.mp.dps = 40


def g(k: mp.mpf, t: mp.mpf) -> mp.mpf:
    return mp.e ** (-k * mp.sqrt(t)) / mp.sqrt(t)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    ts = [mp.mpf(i) / 40 for i in range(2, 161)]
    orders = list(range(7))
    signed = {n: [float((-1) ** n * mp.diff(lambda x: g(mp.mpf(1), x), t, n)) for t in ts] for n in orders}
    mix = [float(g(mp.mpf(1), t) - 2 * g(mp.mpf(2), t)) for t in ts]
    minval = {n: min(v) for n, v in signed.items()}
    mix_quarter = float(g(mp.mpf(1), mp.mpf(1) / 4) - 2 * g(mp.mpf(2), mp.mpf(1) / 4))
    closed = float(2 * mp.e ** -1 * (mp.e ** mp.mpf(0.5) - 2))
    fig, ax = plt.subplots(1, 2, figsize=(9.0, 3.4))
    tf = [float(t) for t in ts]
    cmap = plt.get_cmap("viridis")
    for n in orders:
        ax[0].semilogy(tf, signed[n], color=cmap(n / 6), lw=1.4, label=f"n={n}")
    ax[0].set_xlabel("t = r^2")
    ax[0].set_ylabel("(-1)^n g^(n)(t)")
    ax[0].set_title("planar Yukawa, kappa = 1: all positive")
    ax[0].legend(fontsize=7, ncol=2)
    ax[1].plot(tf, mix, color="#b2182b", lw=1.6, label="g_1 - 2 g_2 (negative control)")
    ax[1].plot(tf, [float(g(mp.mpf(1), t) + 0.5 * g(mp.mpf(3), t)) for t in ts], color="#2166ac", lw=1.4,
               label="g_1 + 0.5 g_3 (admissible mixture)")
    ax[1].axhline(0, color="k", lw=0.7)
    ax[1].plot([0.25], [mix_quarter], "o", color="#b2182b")
    ax[1].set_ylim(-1.0, 3.0)
    ax[1].set_xlabel("t = r^2")
    ax[1].set_title("mixtures: sign of the weights matters")
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "fig_signs.pdf")
    fig.savefig(OUT / "fig_signs.png", dpi=150)
    (OUT / "fig_signs.json").write_text(json.dumps({
        "t_grid": [tf[0], tf[-1], len(tf)], "min_signed_derivative_by_order": minval,
        "signed_mix_at_quarter": mix_quarter, "closed_form_2e^-1(e^0.5-2)": closed}, indent=1))
    print(json.dumps({"min_signed": minval, "mix_quarter": mix_quarter, "closed": closed}))


if __name__ == "__main__":
    main()
