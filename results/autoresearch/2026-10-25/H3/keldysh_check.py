"""H3 Tier X numerics: Rytova-Keldysh potential as a positive Gaussian mixture in t = r^2.

Checks
  (1) mixture  int_0^inf w(a) e^{-r^2/(4a)}/(2a) da,  w(a) = (1/r0) erfcx(sqrt(a)/r0)
      vs closed form (pi/(2 r0)) [H0(r/r0) - Y0(r/r0)]   (mpmath and scipy), 50 radii in [0.01, 50] r0;
  (1b) Laplace identity  int_0^inf e^{-s a} w(a) da = 1/(sqrt(s)(1 + r0 sqrt(s)));
  (1d) independent cross-route (DLMF 11.5.2): H0(x) - Y0(x) = (2/pi) int_0^inf e^{-xu} (1+u^2)^{-1/2} du,
       i.e. V is a positive Laplace transform in r (CM in r, hence CM in t = r^2);
  (1c) Hankel identity   int_0^inf J0(k r)/(1 + r0 k) dk = closed form (inverse 2D FT of 2 pi/(k(1+r0 k)));
  (3) (-1)^n d^n/dt^n V(sqrt t), n = 0..8: computed independently by high-precision numerical
      differentiation of the CLOSED FORM (mpmath.diff), compared with the mixture's exact
      derivative int w(a) (4a)^{-n} e^{-t/(4a)}/(2a) da; signs required >= 0 (strictly > 0);
  (2) negative controls: (a) signed weight w(a)(1 - 2 e^{-a}); (b) Gaussian-core-minus-Gaussian
      e^{-t} - 0.5 e^{-2t}; (c) Morse-type e^{-2(sqrt t - 1)} - 2 e^{-(sqrt t - 1)}. Each must show a
      negative (-1)^n g^{(n)} for some n <= 6 on the grid (pipeline must be able to fire).
  Positive control: Coulomb 1/sqrt(t) through the same mpmath.diff pipeline (all signs >= 0).
Writes result_numerics.json next to this file.
"""
from __future__ import annotations

import json
import math
import pathlib
from typing import Callable

import mpmath as mp
import numpy as np
from scipy import special

mp.mp.dps = 40
R0 = mp.mpf(1)  # r0 = 1 sets the length unit; V scales as (1/r0) f(r/r0)


def weight(a: mp.mpf, r0: mp.mpf = R0) -> mp.mpf:
    """w(a) = (1/r0) e^{a/r0^2} erfc(sqrt(a)/r0), computed stably."""
    x = mp.sqrt(a) / r0
    return mp.exp(x * x) * mp.erfc(x) / r0


def mixture_deriv(t: mp.mpf, n: int, w: Callable[[mp.mpf], mp.mpf] = weight) -> mp.mpf:
    """(-1)^n d^n/dt^n of int w(a) e^{-t/(4a)}/(2a) da (exact differentiation under the integral)."""
    f = lambda a: w(a) * (4 * a) ** (-n) * mp.exp(-t / (4 * a)) / (2 * a)
    peak = t / (4 * (n + 1)) if t > 0 else mp.mpf(1)
    pts = [0, peak / 10, peak, 10 * peak, 100 * peak, 1e4 * peak + 1, mp.inf]
    pts = sorted(set(pts))
    return mp.quad(f, pts, maxdegree=10)


def keldysh_closed(r: mp.mpf, r0: mp.mpf = R0) -> mp.mpf:
    x = r / r0
    return mp.pi / (2 * r0) * (mp.struveh(0, x) - mp.bessely(0, x))


def keldysh_scipy(r: float, r0: float = 1.0) -> float:
    x = r / r0
    return math.pi / (2 * r0) * (special.struve(0, x) - special.y0(x))


def signs_via_diff(g: Callable[[mp.mpf], mp.mpf], ts: list[mp.mpf], nmax: int) -> dict[int, float]:
    """min over t of (-1)^n g^{(n)}(t) / |scale|, by mpmath.diff on the closed form."""
    out: dict[int, float] = {}
    for n in range(nmax + 1):
        vals = [(-1) ** n * mp.diff(g, t, n) for t in ts]
        out[n] = float(min(vals))
    return out


def main() -> None:
    res: dict[str, object] = {}

    # (1) mixture vs closed form
    radii = np.geomspace(0.01, 50.0, 50)
    errs_mp, errs_sp, errs_sp_cf, rows = [], [], [], []
    for r in radii:
        rm = mp.mpf(r)
        mix = mixture_deriv(rm * rm, 0)
        cf = keldysh_closed(rm)
        sp = keldysh_scipy(float(r))
        e1 = float(abs(mix - cf) / abs(cf))
        e2 = float(abs(mix - sp) / abs(mix))
        errs_mp.append(e1)
        errs_sp.append(e2)
        errs_sp_cf.append(float(abs(cf - sp) / abs(cf)))
        rows.append([float(r), float(mix), float(cf), sp, e1, e2])
    res["check1_max_rel_err_vs_mpmath_closed_form"] = max(errs_mp)
    res["check1_max_rel_err_vs_scipy_closed_form"] = max(errs_sp)
    res["check1_diag_scipy_vs_mpmath_closed_form"] = max(errs_sp_cf)
    print("check1 done", max(errs_mp), max(errs_sp), flush=True)
    dl = []
    for x in [mp.mpf(v) for v in ("0.01", "0.3", "1", "7", "50")]:
        lhs = mp.struveh(0, x) - mp.bessely(0, x)
        rhs = 2 / mp.pi * mp.quad(lambda u: mp.exp(-x * u) / mp.sqrt(1 + u * u), [0, 1 / x, 1, mp.inf])
        dl.append(float(abs(lhs - rhs) / lhs))
    res["check1d_dlmf_laplace_in_r_max_rel_err"] = max(dl)
    res["check1_rows_r_mix_mpmath_scipy_err_mp_err_sp"] = rows

    # (1b) Laplace identity
    lap_err = []
    for s in [mp.mpf(x) for x in (1e-3, 0.1, 1, 10, 1e3)]:
        lhs = mp.quad(lambda a: mp.exp(-s * a) * weight(a), [0, 1 / s, 1, mp.inf])
        rhs = 1 / (mp.sqrt(s) * (1 + R0 * mp.sqrt(s)))
        lap_err.append(float(abs(lhs - rhs) / rhs))
    res["check1b_laplace_max_rel_err"] = max(lap_err)

    # (1c) Hankel identity (oscillatory; mpmath quadosc)
    hk_err = []
    for r in [mp.mpf(x) for x in (0.1, 1, 5)]:
        lhs = mp.quadosc(lambda k: mp.besselj(0, k * r) / (1 + R0 * k), [0, mp.inf], omega=r)
        hk_err.append(float(abs(lhs - keldysh_closed(r)) / keldysh_closed(r)))
    res["check1c_hankel_max_rel_err"] = max(hk_err)
    print("check1b/c done", flush=True)

    # (3) derivative signs n = 0..8, independent (closed-form diff) vs mixture
    ts = [mp.mpf(x) for x in np.geomspace(1e-3, 1e3, 13)]
    gK = lambda t: keldysh_closed(mp.sqrt(t))
    nmax = 8
    sign_rows = []
    all_pos = True
    max_dev = 0.0
    for t in ts:
        for n in range(nmax + 1):
            d_cf = (-1) ** n * mp.diff(gK, t, n)
            d_mix = mixture_deriv(t, n)
            dev = float(abs(d_cf - d_mix) / abs(d_mix))
            max_dev = max(max_dev, dev)
            all_pos = all_pos and d_cf > 0 and d_mix > 0
            sign_rows.append([float(t), n, float(d_cf), float(d_mix), dev])
    res["check3_all_signs_strictly_positive"] = bool(all_pos)
    res["check3_max_rel_dev_closedform_diff_vs_mixture"] = max_dev
    print("check3 done", all_pos, max_dev, flush=True)
    res["check3_rows_t_n_closedform_mixture_dev"] = sign_rows

    # positive control: Coulomb through same diff pipeline
    res["posctl_coulomb_min_signed_deriv"] = signs_via_diff(lambda t: 1 / mp.sqrt(t), ts, 6)

    # (2) negative controls
    ctl: dict[str, object] = {}
    wpert = lambda a: weight(a) * (1 - 2 * mp.exp(-a))
    ctl_a = {n: float(min(mixture_deriv(t, n, wpert) for t in ts)) for n in range(7)}
    ctl["a_signed_weight_min_signed_deriv"] = ctl_a
    ctl["b_gauss_minus_gauss"] = signs_via_diff(lambda t: mp.exp(-t) - mp.mpf("0.5") * mp.exp(-2 * t), ts, 6)
    ctl["c_morse"] = signs_via_diff(
        lambda t: mp.exp(-2 * (mp.sqrt(t) - 1)) - 2 * mp.exp(-(mp.sqrt(t) - 1)), ts, 6)
    fired = {k: any(v < 0 for v in d.values()) for k, d in ctl.items()}  # type: ignore[union-attr]
    ctl["fired"] = fired
    res["negative_controls"] = ctl
    res["positive_control_ok"] = all(v > 0 for v in res["posctl_coulomb_min_signed_deriv"].values())  # type: ignore[union-attr]

    # asymptotics
    small = mp.mpf("1e-6")
    res["asym_r_to_0_V_minus_(ln(2/r)-gamma)"] = float(keldysh_closed(small) - (mp.log(2 / small) - mp.euler))
    big = mp.mpf(1000)
    res["asym_r_to_inf_r_times_V"] = float(big * keldysh_closed(big))

    out = pathlib.Path(__file__).with_name("result_numerics.json")
    out.write_text(json.dumps(res, indent=1))
    summary = {k: v for k, v in res.items() if "rows" not in k}
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
