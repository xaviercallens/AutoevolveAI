"""Jellium bookkeeping on triangular-lattice disks (textbook v2, section jel:). Tier X.

For a disk patch of the density-one triangular lattice A (FACTS section 1) and a uniform neutralising disk background
of density n = 1 and radius R_b = sqrt(N / pi) (exactly neutral), compute, with each pair counted ONCE
(the convention of the rusty-SUNDIALS Ewald code, FACTS section 4):

    U_pp = 1/2 sum_{i != j} g(|x_i - x_j|)        (exact, lattice autocorrelation by FFT)
    U_pb = - n sum_i int_D g(|x_i - y|) dy        (closed-form disk potentials)
    U_bb = 1/2 n^2 int_D int_D g(|x - y|) dx dy   (closed form)

for g = 1/r (s = 1) and g = -log r (s = 0). Prints every number quoted in the book.

Usage: python -I jellium_cancel.py [--fig PATH] [--json PATH]
numpy + scipy (+ matplotlib for --fig). Pass tolerances are fixed below, before any run.
"""
from __future__ import annotations

import argparse
import json
import math
import time

import numpy as np
from scipy import integrate, special
from scipy.spatial.distance import pdist

B = math.sqrt(3.0) / 2.0
SC = 1.0 / math.sqrt(B)
E_TRI_CRATE = -1.960515789320  # FACTS section 4 (crate Ewald, pairs once, density 1)
E_TRI_LIT = -1.960515789825  # FACTS section 4 (Alves et al. eta * sqrt(pi))

# ---- pass tolerances (fixed before the first run) ----
TOL_DISKPOT = 1e-9  # closed-form disk potentials vs ray quadrature (relative)
TOL_CONST = 1e-10  # 16 pi / 3 constant vs quadrature (relative)
TOL_FFT = 1e-12  # FFT pair sum vs brute-force pdist (relative)
TOL_EWALD_CRATE = 1e-9  # Python Ewald vs crate value (absolute)
TOL_ALPHA = 1e-11  # alpha-invariance of the one-cell Ewald sums (absolute)
POS_MAX_DE = 0.02  # positive control: |e(R_max) - e_tri| below this
POS_SHRINK = 3.0  # and |de| shrinks by at least this factor from R_min to R_max
NEG_REL = 0.10  # negative controls: measured/predicted divergent part within 10 percent at R_max


def disk_lattice(radius: float, centre: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
    """Indicator grid (j,k in [-M,M]) of lattice points within radius of centre, their positions, and M."""
    m = int(math.ceil(1.5 * radius)) + 3
    j, k = np.meshgrid(np.arange(-m, m + 1), np.arange(-m, m + 1), indexing="ij")
    x = SC * (j + k / 2.0)
    y = SC * (k * B)
    mask = (x - centre[0]) ** 2 + (y - centre[1]) ** 2 <= radius * radius
    pts = np.stack([x[mask], y[mask]], axis=1)
    if mask[0, :].any() or mask[-1, :].any() or mask[:, 0].any() or mask[:, -1].any():
        raise RuntimeError("index grid too small")
    return mask.astype(np.float64), pts, m


def pair_sums(mask: np.ndarray) -> tuple[float, float]:
    """(sum_{i<j} 1/r_ij, sum_{i<j} -log r_ij) from the exact integer autocorrelation of the indicator."""
    g = mask.shape[0]
    p = 2 * g
    f = np.fft.rfft2(mask, s=(p, p))
    corr = np.rint(np.fft.irfft2(f * np.conj(f), s=(p, p)))
    d = np.arange(p)
    d = np.where(d < g, d, d - p).astype(np.float64)
    dj, dk = np.meshgrid(d, d, indexing="ij")
    r2 = (dj * dj + dj * dk + dk * dk) / B
    r2[0, 0] = 1.0
    w = corr.copy()
    w[0, 0] = 0.0
    s1 = 0.5 * float(np.sum(w / np.sqrt(r2)))
    s0 = 0.5 * float(np.sum(w * (-0.5 * np.log(r2))))
    return s1, s0


def phi1(r: np.ndarray, rb: float) -> np.ndarray:
    """int_D dy/|x-y| for a unit-density disk of radius rb, |x| = r (scipy ellipe/ellipk take m = k^2)."""
    r = np.asarray(r, dtype=np.float64)
    out = np.empty_like(r)
    ins = r <= rb
    out[ins] = 4.0 * rb * special.ellipe((r[ins] / rb) ** 2)
    ro = r[~ins]
    mo = (rb / ro) ** 2
    out[~ins] = 4.0 * ro * (special.ellipe(mo) - (1.0 - mo) * special.ellipk(mo))
    return out


def lphi0(r: np.ndarray, rb: float) -> np.ndarray:
    """int_D log|x-y| dy for a unit-density disk of radius rb, |x| = r."""
    r = np.asarray(r, dtype=np.float64)
    inside = math.pi * (r * r / 2.0 + rb * rb * math.log(rb) - rb * rb / 2.0)
    outside = math.pi * rb * rb * np.log(np.maximum(r, 1e-300))
    return np.where(r <= rb, inside, outside)


def ray_phi1(r: float, rb: float) -> float:
    """Independent check: int_D dy/|x-y| as a 1D integral of chord lengths seen from x."""
    if r < rb:
        val, _ = integrate.quad(lambda t: -r * math.cos(t) + math.sqrt(rb * rb - (r * math.sin(t)) ** 2),
                                0.0, 2.0 * math.pi, epsabs=1e-13, epsrel=1e-13, limit=200)
        return val
    t0 = math.asin(rb / r)
    val, _ = integrate.quad(lambda t: 2.0 * math.sqrt(max(rb * rb - (r * math.sin(t)) ** 2, 0.0)),
                            -t0, t0, epsabs=1e-13, epsrel=1e-13, limit=200)
    return val


def reciprocal_and_direct(cut: int) -> tuple[np.ndarray, np.ndarray]:
    """|v| for v in A \\ 0 and |k| for k in 2 pi A* \\ 0, index range [-cut, cut]^2."""
    a1 = SC * np.array([1.0, 0.0])
    a2 = SC * np.array([0.5, B])
    amat = np.stack([a1, a2])
    kmat = 2.0 * np.pi * np.linalg.inv(amat).T  # rows k1,k2 with a_i . k_j = 2 pi delta_ij
    i, j = np.meshgrid(np.arange(-cut, cut + 1), np.arange(-cut, cut + 1), indexing="ij")
    ij = np.stack([i.ravel(), j.ravel()], axis=1).astype(np.float64)
    ij = ij[np.any(ij != 0, axis=1)]
    v = np.linalg.norm(ij @ amat, axis=1)
    k = np.linalg.norm(ij @ kmat, axis=1)
    return v, k


def ewald_s1(alpha: float, cut: int = 30) -> float:
    """Ewald energy per particle (pairs once) of A + background, g = 1/r, one particle per cell of area 1."""
    v, k = reciprocal_and_direct(cut)
    real = 0.5 * float(np.sum(special.erfc(alpha * v) / v))
    recip = math.pi * float(np.sum(special.erfc(k / (2.0 * alpha)) / k))
    return real + recip - alpha / math.sqrt(math.pi) - math.sqrt(math.pi) / alpha


def ewald_s0(alpha: float, cut: int = 30) -> float:
    """Same for g = -log r: split -log r = E1(a^2 r^2)/2 + smooth part with FT 2 pi exp(-k^2/4a^2)/k^2."""
    v, k = reciprocal_and_direct(cut)
    real = 0.5 * float(np.sum(0.5 * special.exp1(alpha * alpha * v * v)))
    recip = 0.5 * float(np.sum(2.0 * math.pi * np.exp(-k * k / (4.0 * alpha * alpha)) / (k * k)))
    self_term = -0.5 * (0.5 * np.euler_gamma + math.log(alpha))
    bg_term = -0.5 * math.pi / (2.0 * alpha * alpha)
    return real + recip + self_term + bg_term


def bookkeeping(radius: float, centre: np.ndarray) -> dict[str, float]:
    """The three terms for s = 1 and s = 0, background exactly neutral (R_b = sqrt(N/pi), n = 1)."""
    mask, pts, _ = disk_lattice(radius, centre)
    n_pts = pts.shape[0]
    rb = math.sqrt(n_pts / math.pi)
    rr = np.linalg.norm(pts - centre, axis=1)
    pp1, pp0 = pair_sums(mask)
    pb1 = -float(np.sum(phi1(rr, rb)))
    bb1 = 8.0 * math.pi * rb ** 3 / 3.0
    pb0 = float(np.sum(lphi0(rr, rb)))
    bb0 = -0.5 * n_pts * n_pts * (math.log(rb) - 0.25)
    return {"R": radius, "N": n_pts, "Rb": rb, "pp1": pp1, "pb1": pb1, "bb1": bb1,
            "pp0": pp0, "pb0": pb0, "bb0": bb0, "n_outside_Rb": int(np.sum(rr > rb))}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fig", default="")
    ap.add_argument("--json", default="")
    args = ap.parse_args()
    t_start = time.time()
    report: dict[str, object] = {}

    # ---- checks of the ingredients ----
    rb = 3.0
    errs = [abs(phi1(np.array([r]), rb)[0] - ray_phi1(r, rb)) / ray_phi1(r, rb) for r in (0.0, 0.7, 2.2, 2.999, 3.0, 3.4, 7.5)]
    print(f"[check] disk potential 1/r: closed form vs ray quadrature, max rel err = {max(errs):.2e}  (tol {TOL_DISKPOT:g})")
    print(f"[check] rim potential / (4 n R) = {phi1(np.array([rb]), rb)[0] / (4 * rb):.15f}")
    const, _ = integrate.quad(lambda r: 2.0 * math.pi * r * 4.0 * special.ellipe(r * r), 0.0, 1.0, epsabs=1e-13, epsrel=1e-13)
    print(f"[check] int_D int_D 1/|x-y| (unit disk) = {const:.15f}; 16 pi/3 = {16 * math.pi / 3:.15f}; rel {abs(const / (16 * math.pi / 3) - 1):.2e}")
    l0, _ = integrate.quad(lambda r: 2.0 * math.pi * r * float(lphi0(np.array([r]), 2.0)[0]), 0.0, 2.0, epsabs=1e-13, epsrel=1e-13)
    l0_exact = math.pi ** 2 * 2.0 ** 4 * (math.log(2.0) - 0.25)
    print(f"[check] int_D int_D log|x-y| (R=2) = {l0:.12f}; pi^2 R^4 (log R - 1/4) = {l0_exact:.12f}")
    mask, pts, _ = disk_lattice(9.0, np.array([0.31, 0.17]))
    f1, f0 = pair_sums(mask)
    dd = pdist(pts)
    b1, b0 = float(np.sum(1.0 / dd)), float(np.sum(-np.log(dd)))
    print(f"[check] FFT pair sums vs pdist (N={pts.shape[0]}): rel err 1/r {abs(f1 / b1 - 1):.2e}, -log r {abs(f0 / b0 - 1):.2e}")
    e1 = [ewald_s1(a) for a in (1.0, 2.0, 4.0)]
    e0 = [ewald_s0(a) for a in (1.0, 2.0, 4.0)]
    print(f"[check] Ewald s=1 per particle, alpha=1,2,4: {e1[0]:.12f} {e1[1]:.12f} {e1[2]:.12f}")
    print(f"[check]   vs crate {E_TRI_CRATE}: diff {e1[0] - E_TRI_CRATE:.2e}; vs literature {E_TRI_LIT}: diff {e1[0] - E_TRI_LIT:.2e}")
    print(f"[check] Ewald s=0 (-log r) per particle, alpha=1,2,4: {e0[0]:.12f} {e0[1]:.12f} {e0[2]:.12f}")
    ok_checks = (max(errs) < TOL_DISKPOT and abs(const / (16 * math.pi / 3) - 1) < TOL_CONST
                 and abs(f1 / b1 - 1) < TOL_FFT and abs(f0 / b0 - 1) < TOL_FFT
                 and abs(e1[0] - E_TRI_CRATE) < TOL_EWALD_CRATE
                 and max(e1) - min(e1) < TOL_ALPHA and max(e0) - min(e0) < TOL_ALPHA
                 and abs(l0 / l0_exact - 1) < TOL_CONST)
    print(f"[check] all ingredient checks: {'PASS' if ok_checks else 'FAIL'}")
    e_tri1, e_tri0 = e1[1], e0[1]
    report.update({"ewald_s1": e1, "ewald_s0": e0, "const_16pi3": const, "checks": ok_checks})

    # ---- disk patches ----
    rng = np.random.default_rng(20261011)
    radii = np.geomspace(6.0, 200.0, 14)
    n_off = 6
    a1 = SC * np.array([1.0, 0.0])
    a2 = SC * np.array([0.5, B])
    rows: list[dict[str, float]] = []
    for radius in radii:
        for _ in range(n_off):
            u = rng.random(2)
            rows.append(bookkeeping(float(radius), u[0] * a1 + u[1] * a2))
    print(f"\n[disk s=1] neutral background, n=1, pairs once; mean over {n_off} random centre offsets (std in brackets)")
    print("    R      N_mean   pp/N      pb/N       bb/N     (8/3)Rb   e=E/N        e-e_tri      sqrt(N)(e-e_tri)")
    summary = []
    for radius in radii:
        sel = [r for r in rows if r["R"] == float(radius)]
        nn = np.array([r["N"] for r in sel], dtype=float)
        pp = np.array([r["pp1"] for r in sel]) / nn
        pb = np.array([r["pb1"] for r in sel]) / nn
        bb = np.array([r["bb1"] for r in sel]) / nn
        e = pp + pb + bb
        de = e - e_tri1
        rbm = float(np.mean([r["Rb"] for r in sel]))
        e_nob = pp  # negative control (i): no background
        e_09 = pp + 0.9 * pb + 0.81 * bb  # negative control (ii): background density 0.9n on the same disk
        pp0 = np.array([r["pp0"] for r in sel]) / nn
        pb0 = np.array([r["pb0"] for r in sel]) / nn
        bb0 = np.array([r["bb0"] for r in sel]) / nn
        e0d = pp0 + pb0 + bb0
        summary.append({"R": float(radius), "N": float(nn.mean()), "Rb": rbm, "pp": float(pp.mean()), "pb": float(pb.mean()),
                        "bb": float(bb.mean()), "e": float(e.mean()), "e_std": float(e.std()), "de": float(de.mean()),
                        "de_std": float(de.std()), "sqrtN_de": float(np.mean(np.sqrt(nn) * de)),
                        "sqrtN_de_std": float(np.std(np.sqrt(nn) * de)), "e_nobg": float(e_nob.mean()),
                        "e_bg09": float(e_09.mean()), "pp0": float(pp0.mean()), "pb0": float(pb0.mean()),
                        "bb0": float(bb0.mean()), "e0": float(e0d.mean()), "e0_std": float(e0d.std()),
                        "de0": float((e0d - e_tri0).mean()), "logRb": math.log(rbm),
                        "n_outside_Rb": float(np.mean([r["n_outside_Rb"] for r in sel]))})
        s = summary[-1]
        print(f"{radius:7.2f} {s['N']:9.1f} {s['pp']:9.3f} {s['pb']:10.3f} {s['bb']:9.3f} {8 * rbm / 3:9.3f} "
              f"{s['e']:.6f}({s['e_std']:.1e}) {s['de']:+.3e}({s['de_std']:.1e}) {s['sqrtN_de']:+.4f}({s['sqrtN_de_std']:.3f})")
    report["s1"] = summary
    print("[split s=1] (pb + 2 bb)/N: " + " ".join(f"{s['pb'] + 2 * s['bb']:+.2e}" for s in summary))
    print("[split s=1] (pp - bb)/N:   " + " ".join(f"{s['pp'] - s['bb']:.4f}" for s in summary))

    big = [s for s in summary if s["R"] >= 40.0]
    lx = np.log([s["N"] for s in big])
    ly = np.log([abs(s["de"]) for s in big])
    slope = float(np.polyfit(lx, ly, 1)[0])
    nn_all = np.array([s["N"] for s in summary])
    de_all = np.array([s["de"] for s in summary])
    # Fit de = a N^{-1/2} + c N^{-1} with e_tri FIXED (not a fit parameter), R >= 20
    selm = np.array([s["R"] >= 20.0 for s in summary])
    xa = np.stack([nn_all[selm] ** -0.5, nn_all[selm] ** -1.0], axis=1)
    coef, *_ = np.linalg.lstsq(xa, de_all[selm], rcond=None)
    # Alternative with a log: de = a N^{-1/2} + b N^{-1/2} log N
    xb = np.stack([nn_all[selm] ** -0.5, nn_all[selm] ** -0.5 * np.log(nn_all[selm])], axis=1)
    coefb, *_ = np.linalg.lstsq(xb, de_all[selm], rcond=None)
    rms_a = float(np.sqrt(np.mean((xa @ coef - de_all[selm]) ** 2)))
    rms_b = float(np.sqrt(np.mean((xb @ coefb - de_all[selm]) ** 2)))
    # free-intercept fit, information only
    xc = np.stack([np.ones(selm.sum()), nn_all[selm] ** -0.5, nn_all[selm] ** -1.0], axis=1)
    coefc, *_ = np.linalg.lstsq(xc, np.array([s["e"] for s in summary])[selm], rcond=None)
    print(f"\n[edge s=1] log-log slope of |e - e_tri| vs N for R >= 40: {slope:.3f}")
    print(f"[edge s=1] fit (e_tri fixed, R>=20): e - e_tri = {coef[0]:.4f} N^-1/2 + {coef[1]:.4f} N^-1   rms {rms_a:.2e}")
    print(f"[edge s=1] alt fit: e - e_tri = {coefb[0]:.4f} N^-1/2 + {coefb[1]:.4f} N^-1/2 log N   rms {rms_b:.2e}")
    print(f"[edge s=1] info only, free intercept: e_inf = {coefc[0]:.6f} (e_tri {e_tri1:.6f}), {coefc[1]:.4f} N^-1/2 + {coefc[2]:.4f} N^-1")
    report["edge"] = {"slope": slope, "fixed_fit": coef.tolist(), "rms_fixed": rms_a, "log_fit": coefb.tolist(),
                      "rms_log": rms_b, "free_fit": coefc.tolist()}

    first, last = summary[0], summary[-1]
    pos_ok = abs(last["de"]) < POS_MAX_DE and abs(first["de"]) / abs(last["de"]) > POS_SHRINK
    print(f"\n[POSITIVE s=1] |e - e_tri| at R={first['R']:.0f}: {abs(first['de']):.3e}; at R={last['R']:.0f}: "
          f"{abs(last['de']):.3e}; shrink x{abs(first['de']) / abs(last['de']):.1f}  -> {'PASS' if pos_ok else 'FAIL'}")
    pred_nob = 8.0 * last["Rb"] / 3.0
    pred_09 = 0.01 * 8.0 * last["Rb"] / 3.0
    r_nob = last["e_nobg"] / pred_nob
    r_09 = (last["e_bg09"] - e_tri1) / pred_09
    neg1_ok = abs(r_nob - 1) < NEG_REL and last["e_nobg"] > 10 * first["e_nobg"] / 2
    neg2_ok = abs(r_09 - 1) < NEG_REL and last["e_bg09"] > first["e_bg09"]
    print(f"[NEGATIVE i  ] no background: e at R=6: {first['e_nobg']:.3f}, at R=200: {last['e_nobg']:.3f}; predicted (8/3)R_b = "
          f"{pred_nob:.3f}; ratio {r_nob:.4f} -> {'FIRES (diverges as predicted)' if neg1_ok else 'DOES NOT FIRE'}")
    print(f"[NEGATIVE ii ] background 0.9n: e at R=6: {first['e_bg09']:.4f}, at R=200: {last['e_bg09']:.4f}; (e-e_tri)/[(0.1)^2 (8/3)R_b] = "
          f"{r_09:.4f} -> {'FIRES (diverges as predicted)' if neg2_ok else 'DOES NOT FIRE'}")
    report["controls"] = {"pos": pos_ok, "neg_nobg": neg1_ok, "neg_09": neg2_ok, "ratio_nobg": r_nob, "ratio_09": r_09}

    print(f"\n[disk s=0] g = -log r, neutral background; e_Ewald(-log) = {e_tri0:.10f}")
    print("    R      N_mean      pp/N          pb/N          bb/N      -(N/2)(log Rb - 1/4)   e=E/N      e - e_Ewald")
    for s in summary:
        print(f"{s['R']:7.2f} {s['N']:9.1f} {s['pp0']:13.2f} {s['pb0']:13.2f} {s['bb0']:13.2f} {-0.5 * s['N'] * (s['logRb'] - 0.25):13.2f}"
              f"        {s['e0']:.6f}  {s['e0'] - e_tri0:+.3e}")
    pos0_ok = abs(summary[-1]["e0"] - e_tri0) < POS_MAX_DE and abs(summary[0]["e0"] - e_tri0) / abs(summary[-1]["e0"] - e_tri0) > POS_SHRINK
    print(f"[POSITIVE s=0] |e - e_Ewald| R=6: {abs(summary[0]['e0'] - e_tri0):.3e}, R=200: {abs(summary[-1]['e0'] - e_tri0):.3e} -> {'PASS' if pos0_ok else 'FAIL'}")
    report["controls"]["pos_s0"] = pos0_ok
    n0 = np.array([s["N"] for s in big])
    d0 = np.array([s["e0"] - e_tri0 for s in big])
    slope0 = float(np.polyfit(np.log(n0), np.log(np.abs(d0)), 1)[0])
    print(f"[edge s=0] log-log slope of |e - e_Ewald| vs N for R >= 40: {slope0:.3f}")
    print("[edge s=0] sqrt(N)(e - e_Ewald): " + " ".join(f"{math.sqrt(s['N']) * (s['e0'] - e_tri0):.3f}" for s in summary))
    report["edge_s0_slope"] = slope0
    print("[disk s=0] std of e over the 6 centres: " + " ".join(f"{s['e0_std']:.1e}" for s in summary))
    # s = 0 negative controls (added after the first run): no background, and background 0.9n on the same disk
    nob0 = last["pp0"]
    pred_nob0 = last["bb0"]
    e09_0 = last["pp0"] + 0.9 * last["pb0"] + 0.81 * last["bb0"]
    pred_09_0 = 0.01 * last["bb0"]
    print(f"[NEGATIVE s=0 i ] no background, R=200: e = {nob0:.2f}; predicted bb/N = -(N/2)(log R_b - 1/4) = {pred_nob0:.2f}; "
          f"ratio {nob0 / pred_nob0:.6f}")
    print(f"[NEGATIVE s=0 ii] background 0.9n, R=200: e - e_Ewald = {e09_0 - e_tri0:.2f}; predicted 0.01 bb/N = {pred_09_0:.2f}; "
          f"ratio {(e09_0 - e_tri0) / pred_09_0:.4f}")

    # Extension (added after the first run, NOT part of the preregistered 14-radius set): larger disks
    print("\n[extension] R = 300, 450, 6 centres each (same seed stream continued); s=1 and s=0 per particle")
    for radius in (300.0, 450.0):
        ext = []
        for _ in range(n_off):
            u = rng.random(2)
            ext.append(bookkeeping(radius, u[0] * a1 + u[1] * a2))
        nn = np.array([r["N"] for r in ext], dtype=float)
        e_s1 = (np.array([r["pp1"] for r in ext]) + np.array([r["pb1"] for r in ext]) + np.array([r["bb1"] for r in ext])) / nn
        e_s0 = (np.array([r["pp0"] for r in ext]) + np.array([r["pb0"] for r in ext]) + np.array([r["bb0"] for r in ext])) / nn
        print(f"[extension] R={radius:.0f} N={nn.mean():.1f}: s=1 e-e_tri = {np.mean(e_s1 - e_tri1):+.3e} (std {np.std(e_s1):.1e}), "
              f"sqrt(N)(e-e_tri) = {np.mean(np.sqrt(nn) * (e_s1 - e_tri1)):.4f}; "
              f"s=0 e-e_Ewald = {np.mean(e_s0 - e_tri0):+.3e} (std {np.std(e_s0):.1e}), sqrt(N)(e-e_Ewald) = "
              f"{np.mean(np.sqrt(nn) * (e_s0 - e_tri0)):.4f}")
    print(f"\nlattice points outside R_b (mean, largest R): {summary[-1]['n_outside_Rb']:.1f}")
    print(f"runtime {time.time() - t_start:.1f} s")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump(report, fh, indent=1)
    if args.fig:
        make_figure(summary, e_tri1, args.fig)


def make_figure(summary: list[dict[str, float]], e_tri: float, path: str) -> None:
    """Three panels: the three terms per particle, convergence of the total, negative controls."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    c1, c2, c3, c4 = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6"
    ink = "#52514e"
    rb = np.array([s["Rb"] for s in summary])
    nn = np.array([s["N"] for s in summary])
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": ink, "axes.labelcolor": "#0b0b0b",
                         "xtick.color": ink, "ytick.color": ink, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.5), constrained_layout=True)
    a = ax[0]
    a.plot(rb, [s["pp"] for s in summary], "-o", color=c1, lw=2, ms=3, label="particle-particle")
    a.plot(rb, [s["pb"] for s in summary], "-o", color=c2, lw=2, ms=3, label="particle-background")
    a.plot(rb, [s["bb"] for s in summary], "--", color=c3, lw=2, label="background-background")
    a.plot(rb, [s["e"] for s in summary], "-", color="#0b0b0b", lw=1.2, label="sum")
    a.set_xlabel("$R_b$")
    a.set_ylabel("energy per particle")
    a.set_title("(a) three terms, $s=1$", fontsize=8)
    a.legend(frameon=False, fontsize=6.5, loc="lower left")
    a.grid(alpha=0.25, lw=0.5)
    b = ax[1]
    de = np.array([s["de"] for s in summary])
    b.loglog(nn, np.abs(de), "o", color=c1, ms=4, label=r"$|e(N)-e_{\rm tri}|$")
    b.errorbar(nn, np.abs(de), yerr=[s["de_std"] for s in summary], fmt="none", ecolor=c1, elinewidth=0.8)
    ref = np.abs(de[-1]) * np.sqrt(nn[-1] / nn)
    b.loglog(nn, ref, "--", color=ink, lw=1, label=r"$\propto N^{-1/2}$")
    b.set_xlabel("$N$")
    b.set_title("(b) total minus Madelung", fontsize=8)
    b.legend(frameon=False, fontsize=6.5)
    b.grid(alpha=0.25, lw=0.5, which="both")
    c = ax[2]
    et = np.array([s["e"] for s in summary])
    c.loglog(rb, np.array([s["e_nobg"] for s in summary]) - e_tri, "-o", color=c2, lw=2, ms=3, label="no background")
    c.loglog(rb, 8 * rb / 3, ":", color=ink, lw=1, label=r"$\frac{8}{3}R_b$ and $0.01\cdot\frac{8}{3}R_b$")
    c.loglog(rb, np.array([s["e_bg09"] for s in summary]) - e_tri, "-o", color=c4, lw=2, ms=3, label=r"background $0.9n$")
    c.loglog(rb, 0.08 * rb / 3, ":", color=ink, lw=1)
    c.loglog(rb, et - e_tri, "-o", color=c1, lw=2, ms=3, label="neutral (correct)")
    c.set_xlabel("$R_b$")
    c.set_ylabel(r"$e-e_{\rm tri}$")
    c.set_title("(c) negative controls", fontsize=8)
    c.set_ylim(1e-3, 3e5)
    c.legend(frameon=False, fontsize=6.5, loc="upper left")
    c.grid(alpha=0.25, lw=0.5, which="both")
    fig.savefig(path)
    print(f"figure written: {path}")


if __name__ == "__main__":
    main()
