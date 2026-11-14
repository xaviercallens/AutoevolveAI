"""B2: rigorous ball-arithmetic (arb) enclosure of the linear-response curvature U'' of the harmonic zero-point energy at
the triangular lattice, Gaussian V(r) = exp(-pi a r^2), plus certified tails, stability margin and positive controls.

usage: python -I b2_certify.py A PATH N T0 QMAX OUT.json
  A     Gaussian width parameter (rational string, e.g. 1, 2, 1/2)
  PATH  shear | diag          strain path P_t (det P_t = 1 exactly)
          shear: P_t = [[1, t], [t, 1 + t^2]]    (mirror image of P_{-t}, so E(t) = E(-t))
          diag : P_t = diag(1 + t, 1/(1 + t))
  N     initial Duffy grid N x N per triangle (power of 2); cells are bisected adaptively (see REFINE)
  T0    half-width of the t window (rational string, e.g. 1/1000)
  QMAX  lattice truncation: all n = (m, l) != 0 with m^2 + m l + l^2 <= QMAX are summed exactly; the rest is a tail bound

Setting (all conventions fixed here; see CERTIFIED_CURVATURE.md):
  L_rho = c Z(1,0) + c Z(1/2, sqrt3/2), c^2 = 2/sqrt3 (unit covolume, lattice vector on the x axis).
  R_n(t) = P_t R_n(0).  H(R) = Hess exp(-pi a |R|^2) = e^{-pi a |R|^2} (4 pi^2 a^2 R R^T - 2 pi a I).
  D_t(kappa) = sum_{n != 0} (1 - cos 2 pi kappa.n) H(R_n(t)),  kappa in [-1/2,1/2]^2 (reduced, fixed integer labels n).
  E(t) = (1/2) int tr D_t^{1/2} dkappa  (harmonic zero-point energy per particle, hbar = m = 1).
  U(t) = (1/4) int [tr X + tr X^{-1} D_t] dkappa,  X = D_0^{1/2}.   2 tr D^{1/2} <= tr X + tr X^{-1} D  =>  E <= U, U(0) = E(0).
  U(t) + U(-t) - 2 U(0) = (1/4) int tr(X^{-1} sum_n (1 - cos) [H_n(t) + H_n(-t) - 2 H_n(0)])
                        = t^2 [ Upp0 + pert(t) ],  Upp0 = (1/4) int tr(X^{-1} G),  G = sum_n (1 - cos) H_n''(0),
  |pert(t)| <= (int tr X^{-1}) * sum_n e_n,  e_n = sum_entries sup_{|xi| <= T0} |H_n''(xi) - H_n''(0)| (sum over the three entries, not the max).
  So for 0 < t <= T0:  (U(t) + U(-t) - 2U(0)) / t^2 <= B := Upp0.hi + trW.hi * sum e_n.hi.

Duffy coordinates on the four triangles of the reduced square (apex Gamma): kappa = s v(t'), v = (1/2, t'-1/2) (right)
or (t'-1/2, 1/2) (top), Jacobian s/2; left/bottom are the images under kappa -> -kappa (integrand even).
D_0 = s^2 B, B = sum_n theta_n^2 f(s theta_n) H_n, theta_n = 2 pi v.n, f(x) = (1 - cos x)/x^2 = sinc(x/2)^2 / 2,
so every integrand times the Jacobian is a bounded function of (s, t') and boxes at the apex s = 0 are fine.
  X^{-1} = B^{-1/2}/s,  B^{-1/2} = ((tr B + d) I - B)/(d tau), d = sqrt det B, tau = sqrt(tr B + 2 d).
  Upp0 integrand: (s^2/8) tr(B^{-1/2} G~),  G = s^2 G~.      trW integrand: tau/(2 d).
  E(0) integrand: s^2 tau / 4.                               <tr D> integrand: s^3 tr B / 2.

Every number is an arb ball (python-flint 0.6.0, Arb ball arithmetic, prec 96 bits): the enclosures are rigorous
(outward rounded, transcendental functions with certified error bounds) but they are NOT kernel-checked.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time
from fractions import Fraction

sys.path.insert(0, "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/.scratchpad/b2_pylib")
import flint  # noqa: E402
from flint import arb, ctx  # noqa: E402

ctx.prec = 96
PI = arb.pi()
SQ3 = arb(3).sqrt()
C2 = 2 / SQ3  # c^2
C = C2.sqrt()
HALF = arb(1) / 2


def q_arb(s: str) -> arb:
    f = Fraction(s)
    return arb(f.numerator) / arb(f.denominator)


# ---------------------------------------------------------------- lattice and the Gaussian Hessian along the path

def lattice_half(qmax: int) -> list[tuple[int, int]]:
    """Representatives of {n != 0 : m^2 + m l + l^2 <= qmax} modulo n -> -n."""
    out = []
    lim = int(math.isqrt(4 * qmax)) + 2
    for m in range(-lim, lim + 1):
        for l in range(-lim, lim + 1):
            if (m, l) == (0, 0) or m * m + m * l + l * l > qmax:
                continue
            if m > 0 or (m == 0 and l > 0):
                out.append((m, l))
    return out


def path_R(path: str, X0: arb, Y0: arb, t: arb) -> tuple[arb, ...]:
    """R(t), R'(t), R''(t) for R(t) = P_t R0."""
    if path == "shear":
        return (X0 + t * Y0, t * X0 + (1 + t * t) * Y0, Y0, X0 + 2 * t * Y0, arb(0), 2 * Y0)
    if path == "diag":
        u = 1 + t
        return (u * X0, Y0 / u, X0, -Y0 / (u * u), arb(0), 2 * Y0 / (u * u * u))
    raise ValueError(path)


def path_norms(path: str, t0: arb) -> tuple[arb, arb, arb, arb]:
    """(sigma_min, sigma_max, sup ||P'||, sup ||P''||) over |t| <= t0 (operator norms, crude but valid)."""
    if path == "shear":
        # P_t - I = [[0, t], [t, t^2]]: ||.|| <= |t| + t^2;  P' = [[0,1],[1,2t]]: ||.|| <= 1 + 2|t|;  P'' = diag(0,2).
        e = t0 + t0 * t0
        return (1 - e, 1 + e, 1 + 2 * t0, arb(2))
    if path == "diag":
        lo = 1 / (1 + t0)
        return (lo - t0 if lo - t0 < 1 - t0 else 1 - t0, 1 / (1 - t0), 1 / ((1 - t0) * (1 - t0)), 2 / ((1 - t0) ** 3))
    raise ValueError(path)


def hess_and_dd(a: arb, R: tuple[arb, ...]) -> tuple[tuple[arb, arb, arb], tuple[arb, arb, arb]]:
    """H(R(t)) and d^2/dt^2 H(R(t)) (closed form; Lean: ZeroPointCert.Basic.hasDerivAt_* for the scalar pieces)."""
    Rx, Ry, dx, dy, ddx, ddy = R
    pa = PI * a
    k = 4 * pa * pa
    q1 = 2 * (Rx * dx + Ry * dy)
    q2 = 2 * (dx * dx + dy * dy + Rx * ddx + Ry * ddy)
    e = (-pa * (Rx * Rx + Ry * Ry)).exp()
    H, H2 = [], []
    for (Ri, Rj, di, dj, ddi, ddj, dl) in ((Rx, Rx, dx, dx, ddx, ddx, 1), (Rx, Ry, dx, dy, ddx, ddy, 0),
                                          (Ry, Ry, dy, dy, ddy, ddy, 1)):
        M = k * Ri * Rj - 2 * pa * dl
        M1 = k * (di * Rj + Ri * dj)
        M2 = k * (ddi * Rj + 2 * di * dj + Ri * ddj)
        H.append(e * M)
        H2.append(e * ((pa * pa * q1 * q1 - pa * q2) * M - 2 * pa * q1 * M1 + M2))
    return (H[0], H[1], H[2]), (H2[0], H2[1], H2[2])


# ---------------------------------------------------------------- tails (uniform in kappa and |t| <= t0)

def tail_bounds(a: arb, qmax: int, path: str, t0: arb) -> dict:
    """Entrywise bounds of the truncated parts, summed over all n with m^2 + m l + l^2 >= qmax + 1.

    |R0| >= r_tail = c sqrt(qmax + 1). Lattice-point count: #{n : |R0_n| <= r} <= pi (r + 1)^2 (disjoint Voronoi
    hexagons of area 1 and circumradius c/sqrt3 < 1 inside the disc of radius r + 1). Shells [r_k, r_k + Delta),
    r_k = r_tail + k Delta, each term bounded by its value at the inner radius (all bounds are decreasing for r >= 2).
    theta_n^2 <= 4 pi^2 |v|^2 |n|^2 <= 4 pi^2 (1/2)(2 |R0|^2 / c^2) = 4 pi^2 |R0|^2 / c^2, f <= 1/2.
    """
    smin, smax, d1, d2 = path_norms(path, t0)
    pa = PI * a
    k = 4 * pa * pa
    r_tail = C * arb(qmax + 1).sqrt()
    delta = arb(1) / 4

    def BH(r: arb) -> arb:
        return (-pa * smin * smin * r * r).exp() * (k * smax * smax * r * r + 2 * pa)

    def BH2(r: arb) -> arb:
        R, dR, ddR = smax * r, d1 * r, d2 * r
        q1 = 2 * R * dR
        q2 = 2 * dR * dR + 2 * R * ddR
        M = k * R * R + 2 * pa
        M1 = 2 * k * R * dR
        M2 = k * (2 * ddR * R + 2 * dR * dR)
        return (-pa * smin * smin * r * r).exp() * ((pa * pa * q1 * q1 + pa * q2) * M + 2 * pa * q1 * M1 + M2)

    # sup_x |f'(x)|: |f'(x)| <= (|x| + 4)/|x|^3 <= 1/8 for |x| >= 4; on [0, 4] by ball evaluation on 256 subintervals
    F1 = arb(1) / 8
    for i in range(256):
        F1 = F1.max(fprime_enc(arb((i + 0.5) / 64, 0.5 / 64)).abs_upper())
    sq2 = arb(2).sqrt()
    acc = {key: arb(0) for key in ("D", "G", "E", "Tr", "Ds", "Dt", "Gs", "Gt")}
    K = 200
    last = None
    for kk in range(K):
        r = r_tail + kk * delta
        cnt = PI * (r + delta + 1) ** 2
        th = 2 * PI * r / C  # |theta_n| <= th
        be = sq2 * th  # |beta| = 2 pi |l| or 2 pi |m| <= 2 pi |n| <= 2 pi sqrt2 |R0| / c
        w = th * th / 2  # per point theta^2 f <= theta^2 / 2
        ws = th * th * th * F1  # |d/ds (theta^2 f(s theta))| = |theta^3 f'|
        wt = th * be + th * th * F1 * be  # |d/dt'| <= 2 |theta beta| f + theta^2 |f'| s |beta|, f <= 1/2, s <= 1
        bh, bh2 = BH(r), BH2(r)
        acc["D"] += cnt * w * bh
        acc["G"] += cnt * w * bh2
        acc["Ds"] += cnt * ws * bh
        acc["Dt"] += cnt * wt * bh
        acc["Gs"] += cnt * ws * bh2
        acc["Gt"] += cnt * wt * bh2
        acc["E"] += cnt * 6 * bh2  # |H''(xi) - H''(0)| <= 2 bh2 per entry, 3 entries (audit NB-1: was 3 * bh2)
        acc["Tr"] += cnt * (2 * k * smax * smax * r * r + 4 * pa) * (-pa * smin * smin * r * r).exp()
        last = cnt * (ws + wt + 3) * (bh + bh2) * (1 + th * th)
    # remainder beyond r_K = r_tail + 50: ASSERTED, not computed here. The term ratio is below exp(-pi a smin^2 2 r delta) < e^-40
    # at r ~ 55 (delta = 1/4, a >= 1/2; independent audit NB-6), hence < 1/2, so the tail is bounded by 2 * last.
    rem = 2 * last
    return {"r_tail": r_tail, "F1_sup_fprime": F1, "D_entry": acc["D"] + rem, "G_entry": acc["G"] + rem,
            "Ds_entry": acc["Ds"] + rem, "Dt_entry": acc["Dt"] + rem, "Gs_entry": acc["Gs"] + rem,
            "Gt_entry": acc["Gt"] + rem, "pert": acc["E"] + rem, "trH": acc["Tr"] + rem, "last_term": last}


# ---------------------------------------------------------------- cell evaluation

def f_enc(x: arb) -> arb:
    """f(x) = (1 - cos x)/x^2 = sinc(x/2)^2 / 2 over a ball (valid when the ball contains 0)."""
    sc = (x / 2).sinc()
    return sc * sc / 2


FACT = [arb(math.factorial(k)) for k in range(40)]


def fprime_enc(x: arb) -> arb:
    """f'(x) for f(x) = (1 - cos x)/x^2.  |x| >= 1 on the ball: closed form (x sin x - 2(1 - cos x))/x^3.
    Otherwise the alternating series f'(x) = sum_{k>=1} (-1)^k 2k x^{2k-1}/(2k+2)!, truncated after k = 7 with the
    remainder bounded by the first omitted term (terms decrease in modulus for |x| < 1)."""
    if bool(x.abs_lower() >= 1):
        sn, cs = x.sin(), x.cos()
        return (x * sn - 2 * (1 - cs)) / (x * x * x)
    if not bool(x.abs_upper() < 1):
        # ball straddles |x| = 1: split is not needed for validity; use the series with the remainder valid for
        # |x| <= 2 (ratio of consecutive terms x^2 (2k+2) / (2k (2k+3)(2k+4)) < 1 for k >= 1, |x| <= 2)
        if not bool(x.abs_upper() <= 2):
            raise ValueError("fprime_enc: ball too wide")
    tot = arb(0)
    for k in range(1, 8):
        tot += (-1) ** k * (2 * k) * x ** (2 * k - 1) / FACT[2 * k + 2]
    K = 8
    rem = (2 * K) * x.abs_upper() ** (2 * K - 1) / FACT[2 * K + 2]
    return tot + arb(0, 1) * rem


class Model:
    def __init__(self, a: arb, path: str, t0: arb, qmax: int) -> None:
        self.a, self.path, self.t0, self.qmax = a, path, t0, qmax
        self.ns = lattice_half(qmax)
        zero = arb(0)
        tball = arb(0, 1) * t0  # [-t0, t0]
        self.H0, self.G0, self.dH, self.e = [], [], [], []
        for (m, l) in self.ns:
            X0 = C * (m + HALF * l)
            Y0 = C * l * SQ3 / 2
            H0, G0 = hess_and_dd(a, path_R(path, X0, Y0, zero))
            Ht, Gt = hess_and_dd(a, path_R(path, X0, Y0, tball))
            self.H0.append(H0)
            self.G0.append(G0)
            # sup over |t| <= t0 of the entry sum |H_n(t) - H_n(0)| (for the stability margin)
            self.dH.append(sum(((h1 - h0).abs_upper() for h1, h0 in zip(Ht, H0)), arb(0)))
            # sup over |xi| <= t0 of the entry sum |H_n''(xi) - H_n''(0)| (>= operator norm of the difference)
            self.e.append(sum(((g1 - g0).abs_upper() for g1, g0 in zip(Gt, G0)), arb(0)))
        # theta_n(t') = alpha + beta t' per triangle: right v = (1/2, t'-1/2), top v = (t'-1/2, 1/2)
        self.th = {0: [(PI * (m - l), 2 * PI * l) for (m, l) in self.ns], 1: [(PI * (l - m), 2 * PI * m) for (m, l) in self.ns]}
        self.tails = tail_bounds(a, qmax, path, t0)
        self.tD = arb(0, 1) * self.tails["D_entry"]
        self.tG = arb(0, 1) * self.tails["G_entry"]
        # x2 for n and -n; plus the tail (entry sums over all far n)
        self.e_sum = 2 * sum(self.e, arb(0)) + self.tails["pert"]
        # ||B_t - B_0||_op <= sum_n w_n ||H_n(t) - H_n(0)||, w_n = 2 theta_n^2 f <= theta_n^2 <= 4 pi^2 |n|^2 |v|^2,
        # |v|^2 <= 1/2, |n|^2 = m^2 + l^2  (stability margin of the strained lattices, |t| <= t0)
        self.dB = sum((2 * PI * PI * (m * m + l * l) * dh for (m, l), dh in zip(self.ns, self.dH)), arb(0)) \
            + 6 * self.tails["D_entry"]

    def _sums(self, tri: int, s: arb, tt: arb, deriv: bool) -> tuple[list[arb], ...]:
        """B, G~ entries (with tails) and, if deriv, their s- and t'-partials, all as enclosures over (s, tt)."""
        B = [arb(0), arb(0), arb(0)]
        G = [arb(0), arb(0), arb(0)]
        Bs = [arb(0), arb(0), arb(0)]
        Bt = [arb(0), arb(0), arb(0)]
        Gs = [arb(0), arb(0), arb(0)]
        Gt = [arb(0), arb(0), arb(0)]
        for (al, be), H0, G0 in zip(self.th[tri], self.H0, self.G0):
            th = al + be * tt
            x = s * th
            fx = f_enc(x)
            w = 2 * th * th * fx  # n and -n
            if deriv:
                fp = fprime_enc(x)
                ws = 2 * th * th * th * fp
                wt = 4 * th * be * fx + 2 * th * th * fp * s * be
            for i in range(3):
                B[i] += w * H0[i]
                G[i] += w * G0[i]
                if deriv:
                    Bs[i] += ws * H0[i]
                    Bt[i] += wt * H0[i]
                    Gs[i] += ws * G0[i]
                    Gt[i] += wt * G0[i]
        B = [b + self.tD for b in B]
        G = [g + self.tG for g in G]
        if deriv:
            Bs = [b + arb(0, 1) * self.tails["Ds_entry"] for b in Bs]
            Bt = [b + arb(0, 1) * self.tails["Dt_entry"] for b in Bt]
            Gs = [g + arb(0, 1) * self.tails["Gs_entry"] for g in Gs]
            Gt = [g + arb(0, 1) * self.tails["Gt_entry"] for g in Gt]
        return B, G, Bs, Bt, Gs, Gt

    @staticmethod
    def _phi(B: list[arb], G: list[arb], d: arb, tau: arb) -> arb:
        trB, trG = B[0] + B[2], G[0] + G[2]
        trBG = B[0] * G[0] + 2 * B[1] * G[1] + B[2] * G[2]
        return ((trB + d) * trG - trBG) / (d * tau)

    def cell(self, tri: int, s0: Fraction, t0_: Fraction, h: Fraction) -> dict:
        """Mean-value enclosures of the cell integrals of the four integrands over [s0, s0+h] x [t0_, t0_+h]."""
        hs = arb(float(h / 2))
        sc, tc = arb(float(s0 + h / 2)), arb(float(t0_ + h / 2))
        sb, tb = arb(float(s0 + h / 2), float(h / 2)), arb(float(t0_ + h / 2), float(h / 2))
        dS, dT = arb(0, 1) * hs, arb(0, 1) * hs
        # centre values (thin balls)
        Bc, Gc, _, _, _, _ = self._sums(tri, sc, tc, False)
        detc = Bc[0] * Bc[2] - Bc[1] * Bc[1]
        if not bool(detc > 0):
            return {"ok": False}
        dc = detc.sqrt()
        tauc = (Bc[0] + Bc[2] + 2 * dc).sqrt()
        phic = self._phi(Bc, Gc, dc, tauc)
        # cell enclosures: naive values and partials
        Bn, Gn, Bs, Bt, Gs, Gt = self._sums(tri, sb, tb, True)
        Bm = [(bc + bs * dS + bt * dT).intersection(bn) for bc, bs, bt, bn in zip(Bc, Bs, Bt, Bn)]
        Gm = [(gc + gs * dS + gt * dT).intersection(gn) for gc, gs, gt, gn in zip(Gc, Gs, Gt, Gn)]
        dets = Bm[2] * Bs[0] + Bm[0] * Bs[2] - 2 * Bm[1] * Bs[1]
        dett = Bm[2] * Bt[0] + Bm[0] * Bt[2] - 2 * Bm[1] * Bt[1]
        det = (detc + dets * dS + dett * dT).intersection(Bm[0] * Bm[2] - Bm[1] * Bm[1])
        trB = Bm[0] + Bm[2]
        if not (bool(det > 0) and bool(trB > 0)):
            return {"ok": False}
        d = det.sqrt()
        tau = (trB + 2 * d).sqrt()
        out = {"ok": True, "lmin": det / trB}
        # partials of d, tau, phi on the cell
        res = {}
        for name, Bx, Gx, detx in (("s", Bs, Gs, dets), ("t", Bt, Gt, dett)):
            dx = detx / (2 * d)
            taux = (Bx[0] + Bx[2] + 2 * dx) / (2 * tau)
            trBx, trGx = Bx[0] + Bx[2], Gx[0] + Gx[2]
            trG = Gm[0] + Gm[2]
            Nn = (trB + d) * trG - (Bm[0] * Gm[0] + 2 * Bm[1] * Gm[1] + Bm[2] * Gm[2])
            Nx = (trBx + dx) * trG + (trB + d) * trGx \
                - (Bx[0] * Gm[0] + Bm[0] * Gx[0] + 2 * (Bx[1] * Gm[1] + Bm[1] * Gx[1]) + Bx[2] * Gm[2] + Bm[2] * Gx[2])
            phix = Nx / (d * tau) - Nn * (dx * tau + d * taux) / ((d * tau) ** 2)
            res[name] = (dx, taux, trBx, phix, Nn / (d * tau))
        phi = res["s"][4]
        A = arb(float(h * h))
        q = hs / 2  # int |s - s_c| ds / h = h/4 = hs/2
        # integrand g = s^2 phi / 8
        g_s = sb * phi / 4 + sb * sb * res["s"][3] / 8
        g_t = sb * sb * res["t"][3] / 8
        out["upp"] = A * (sc * sc * phic / 8 + arb(0, 1) * q * (g_s.abs_upper() + g_t.abs_upper()))
        # tr W integrand tau / (2 d)
        w_s = res["s"][1] / (2 * d) - tau * res["s"][0] / (2 * d * d)
        w_t = res["t"][1] / (2 * d) - tau * res["t"][0] / (2 * d * d)
        out["trw"] = A * (tauc / (2 * dc) + arb(0, 1) * q * (w_s.abs_upper() + w_t.abs_upper()))
        # E integrand s^2 tau / 4
        e_s = sb * tau / 2 + sb * sb * res["s"][1] / 4
        e_t = sb * sb * res["t"][1] / 4
        out["ezp"] = A * (sc * sc * tauc / 4 + arb(0, 1) * q * (e_s.abs_upper() + e_t.abs_upper()))
        # <tr D> integrand s^3 tr B / 2
        r_s = 3 * sb * sb * trB / 2 + sb ** 3 * res["s"][2] / 2
        r_t = sb ** 3 * res["t"][2] / 2
        out["trd"] = A * (sc ** 3 * (Bc[0] + Bc[2]) / 2 + arb(0, 1) * q * (r_s.abs_upper() + r_t.abs_upper()))
        out["width_upp"] = out["upp"].rad()
        return out


def integrate(model: Model, N: int, refine_tol: float, max_depth: int, tris: tuple[int, ...] = (0, 1)) -> dict:
    """Adaptive mean-value box sums over the independent triangles (x2 for the kappa -> -kappa images)."""
    tot = {"upp": arb(0), "trw": arb(0), "ezp": arb(0), "trd": arb(0)}
    stats = {"cells": 0, "refined": 0, "lmin_lo": math.inf, "failed": 0}
    h0 = Fraction(1, N)
    stack = []
    for tri in tris:
        for i in range(N):
            for j in range(N):
                stack.append((tri, Fraction(i, N), Fraction(j, N), h0, 0))
    while stack:
        tri, s0, t0_, h, depth = stack.pop()
        r = model.cell(tri, s0, t0_, h)
        wide = (not r["ok"]) or bool(r["width_upp"] > refine_tol * float(h * h))
        if wide and depth < max_depth:
            h2 = h / 2
            for ds in (0, 1):
                for dt in (0, 1):
                    stack.append((tri, s0 + ds * h2, t0_ + dt * h2, h2, depth + 1))
            stats["refined"] += 1
            continue
        stats["cells"] += 1
        if not r["ok"]:
            stats["failed"] += 1
            continue
        for key in tot:
            tot[key] += 2 * r[key]
        stats["lmin_lo"] = min(stats["lmin_lo"], float(lower_frac(r["lmin"])) * (1 - 1e-12))
    return {"tot": tot, "stats": stats}


def ball(x: arb) -> dict:
    return {"lo": str(to_q_lower(x, 10**15)), "hi": str(to_q_upper(x, 10**15)), "lo_float": float(lower_frac(x)),
            "hi_float": float(upper_frac(x)), "mid": float(x.mid()), "rad": float(exact_frac(x.rad()))}


def exact_frac(x: arb) -> Fraction:
    """Exact value of an exact (radius 0) arb."""
    m, e = x.man_exp()
    m, e = int(m), int(e)
    return Fraction(m) * (Fraction(2) ** e)


def upper_frac(x: arb) -> Fraction:
    return exact_frac(x.mid()) + exact_frac(x.rad())


def lower_frac(x: arb) -> Fraction:
    return exact_frac(x.mid()) - exact_frac(x.rad())


def to_q_upper(x: arb, den: int = 10**12) -> Fraction:
    """Smallest p/den >= every point of the ball x (rational certificate endpoint, rounded outward)."""
    return Fraction(math.ceil(upper_frac(x) * den), den)


def to_q_lower(x: arb, den: int = 10**12) -> Fraction:
    return Fraction(math.floor(lower_frac(x) * den), den)


def theta_direct(a: arb, qmax: int) -> tuple[arb, arb]:
    """sum_{n != 0} tr H_n = sum e^{-pi a r^2}(4 pi^2 a^2 r^2 - 4 pi a) (= <tr D>, exact since int (1-cos) = 1) and
    theta_L(a) = sum_n e^{-pi a |R|^2}, with tails (|R0|^2 >= c^2 (qmax+1))."""
    pa = PI * a
    tr = arb(0)
    th = arb(1)
    for (m, l) in lattice_half(qmax):
        r2 = C2 * (m * m + m * l + l * l)
        e = (-pa * r2).exp()
        tr += 2 * e * (4 * pa * pa * r2 - 4 * pa)
        th += 2 * e
    return tr, th


def main() -> None:
    a_s, path, N, t0_s, qmax, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5]), sys.argv[6]
    refine_tol = float(os.environ.get("B2_REFINE_TOL", "0.02"))
    max_depth = int(os.environ.get("B2_MAX_DEPTH", "3"))
    a, t0 = q_arb(a_s), q_arb(t0_s)
    t_start = time.time()
    model = Model(a, path, t0, qmax)
    res = integrate(model, N, refine_tol, max_depth)
    tot, st = res["tot"], res["stats"]
    upp0 = tot["upp"]
    trw = tot["trw"]
    B = upp0 + trw * model.e_sum
    trd_direct, theta = theta_direct(a, qmax)
    trd_direct = trd_direct + arb(0, 1) * model.tails["trH"]
    theta = theta + arb(0, 1) * model.tails["trH"]
    stab_margin = st["lmin_lo"] - float(upper_frac(model.dB)) * (1 + 1e-9)
    certified_neg = bool(B < 0) and st["failed"] == 0 and stab_margin > 0
    # rational certificate data (outward rounded)
    rec = {
        "a": a_s, "path": path, "N": N, "t0": t0_s, "qmax": qmax, "refine_tol": refine_tol, "max_depth": max_depth,
        "n_lattice_half": len(model.ns), "python_flint": flint.__version__, "arb_prec_bits": ctx.prec,
        "seconds": round(time.time() - t_start, 1),
        "Upp0": ball(upp0), "int_trW": ball(trw), "sum_e": ball(model.e_sum), "B": ball(B),
        "E0": ball(tot["ezp"]), "trD_cells": ball(tot["trd"]), "trD_direct": ball(trd_direct), "theta_L_a": ball(theta),
        "tails": {k: (float(v.upper()) if isinstance(v, arb) else v) for k, v in model.tails.items()},
        "stats": st, "stability": {"lambda_min_B0_lower": st["lmin_lo"], "dB_upper": float(upper_frac(model.dB)), "margin": stab_margin},
        "certified_B_negative": certified_neg,
        "cert_rationals": {
            "Upp0_hi": str(to_q_upper(upp0)), "Upp0_lo": str(to_q_lower(upp0)),
            "trW_hi": str(to_q_upper(trw)), "esum_hi": str(to_q_upper(model.e_sum)),
            "lmin_lo": str(Fraction(math.floor(st["lmin_lo"] * 10**12), 10**12)) if math.isfinite(st["lmin_lo"]) else None,
            "dB_hi": str(to_q_upper(model.dB)),
        },
        "controls": {
            "E0_contains_P2_value_1.50335235220736": bool(tot["ezp"].contains(arb("1.50335235220736"))) if a_s == "1" else None,
            "trD_cells_overlaps_direct_lattice_sum": bool(tot["trd"].overlaps(trd_direct)),
            "trD_direct_overlaps_4pi_minus_2pi_theta1": bool(trd_direct.overlaps(4 * PI - 2 * PI * theta)) if a_s == "1" else None,
        },
    }
    with open(__file__, "rb") as fh:
        rec["script_sha256"] = hashlib.sha256(fh.read()).hexdigest()
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=1)
    print(json.dumps({k: rec[k] for k in ("a", "path", "N", "Upp0", "int_trW", "sum_e", "B", "E0", "certified_B_negative", "seconds", "controls")}, indent=1))
    print("stats", st)


if __name__ == "__main__":
    main()
