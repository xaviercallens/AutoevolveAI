"""M1: N2's certifier extended with an Ewald (Gaussian-mixture) split, for r^-3 tails (Riesz s = 3, bilayer point dipole).

usage: python -I m1_certify.py POT PARAM N T0 QMAX OUT.json [ALPHA]
  POT  yukawa | gauss      : N2 path, no split (positive / negative controls; must reproduce N2 bit for bit)
       riesz3              : V = r^-3, Ewald split at ALPHA
       dipolar             : V = 2 (1/r - 1/sqrt(r^2 + d^2)) / d^2  (PARAM = d, P2/N2 normalisation; = r^-3 + O(d^2 r^-5))
                             = r^-3 (Ewald split) + W_d (real space, power-law tail)
       riesz3direct        : V = r^-3 in real space only, power-law tail (negative control: the tail lemma must diverge)
  N, T0, QMAX as in n2_certify.py (N2_REFINE_TOL, N2_MAX_DEPTH env).

Mathematics (C-human, written out in RESULT.md):
  r^-3 = (2/sqrt pi) int_0^inf u^(1/2) e^(-u r^2) du.  Split at u = ALPHA:
    short  g_S(q) = (2/sqrt pi) int_ALPHA^inf u^(1/2) e^(-u q) du,  g_S^(j)(q) = (-1)^j (2/sqrt pi) Gamma(j+3/2, ALPHA q) q^-(j+3/2)
           (completely monotone: |g_S^(j)| decreasing in q; Gaussian-type tail, N2's shell lemma applies);
    long   V_L(r) = (2/sqrt pi) int_0^ALPHA u^(1/2) e^(-u r^2) du, 2D Fourier transform
           Vh(x) = 4 sqrt(pi ALPHA) e^(-x^2/(4 ALPHA)) - 2 pi x erfc(x / (2 sqrt ALPHA)),  x = |q|.
  Poisson summation on the unit-covolume strained lattice L_t = P_t L_rho (det P_t = 1, reciprocal P_t^-1 L*_rho):
    D_L,t(k0) = sum_{n} (1 - cos k0.R_n) Hess V_L(P_t R_n) = sum_{G0 in L*} [F(P_t^-1 (G0 + k0)) - F(P_t^-1 G0)],
    F(q) = q q^T Vh(|q|).  G0 = 0 gives B_0 = w w^T Vh(s |w|), w = P_t^-1 e(t') (k0 = s e(t'), Duffy coordinates of N2).
    G0 != 0 paired with -G0: Phi_G0 = [F(g + s eps) + F(g - s eps) - 2 F(g)] / s^2, g = P_t^-1 G0, eps = P_t^-1 e.
      - first shell (|G0| = |b|), cells with s >= 1/4: evaluated exactly (Arb jets, division by s^2 >= 1/16);
      - every other (G0, region): a rigorous ball from Cauchy estimates on a complex polydisc in (s, t', t), with
        Phi = int_0^1 (1 - tau) [D^2F(g + tau s eps) + D^2F(g - tau s eps)][eps, eps] dtau and an explicit bound of
        |D^2 K_u[eps, eps]|, K_u(z) = z z^T e^(-z.z/(4u)), F = int_0^ALPHA 2 sqrt(pi) u^(-1/2) K_u du.
  Dipolar: W_d = V_d - r^-3 = -(2/sqrt pi) int u^(-1/2) [u - (1 - e^(-u d^2))/d^2] e^(-u r^2) du; the bracket lies in
    [0, u^2 d^2 / 2], so -W_d is completely monotone and |W_d^(j)(q)| <= (d^2/sqrt pi) Gamma(j + 5/2) q^-(j+5/2).
  Power-law tails (W_d, riesz3direct): per lattice point with |R0| = r >= r_tail the entry bound is c r^e (homogeneous);
    sum_{|R0| >= R} r^e <= 2 pi int_{R - 2 rho}^inf y^e (y + rho) dy  (Voronoi cells of area 1 in discs of radius rho),
    finite iff e < -2; otherwise the tail ball is +inf and the certifier refuses.
Everything else (cell rule, positivity, integrand, window logic) is N2's code, imported unchanged.
Tier C-ball (Arb, python-flint 0.6.0, outward rounding); NOT kernel-checked.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time
from fractions import Fraction

N2_CODE = "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal3/2026-10-26/N2/code"
sys.path.insert(0, N2_CODE)
import n2_certify as N2  # noqa: E402
from n2_certify import (C, HALF, PI, RHO_V, SQ3, Dl, Dl2, arb, arb_mat, ctx, flint,  # noqa: E402
                        fprime_sup, fsecond_sup, lattice_half, path_norms, path_R, hess_derivs, point_bounds, tail_bounds)

SQPI = PI.sqrt()
A_REC = 2 * PI / C      # max |e(t')| over the Duffy triangles (= |b| sqrt3 / 2)
B_LEN = 2 * PI * C      # |b1| = |b2|, shortest reciprocal vector of L_rho
B1 = (2 * PI / C, -2 * PI / (C * SQ3))
B2 = (arb(0), 4 * PI / (C * SQ3))
MARGIN = arb(1) / 1000  # region overlap absorbing the outward rounding of the cell balls


def poch(a: arb, j: int) -> arb:
    out = arb(1)
    for i in range(j):
        out *= a + i
    return out


def inv_pow(q: arb, p2: int) -> arb:
    """q^(-p2/2) for an odd or even integer p2 >= 0."""
    out = arb(1)
    for _ in range(p2 // 2):
        out = out * q
    if p2 % 2:
        out = out * q.sqrt()
    return 1 / out


class RieszShort:
    """Short-range part g_S of r^-3 after the split at alpha (completely monotone; Gaussian-type majorant)."""
    pot = "riesz3_short"

    def __init__(self, alpha: arb) -> None:
        self.alpha = alpha
        self.Cj = []
        for j in range(5):
            p = arb(j) + HALF
            cp = arb(1) if j == 0 else arb(2) ** (j - HALF)  # (a+b)^p <= c_p (a^p + b^p), c_p = max(1, 2^(p-1))
            self.Cj.append(2 / SQPI * cp * (alpha ** p + (p + 1).gamma()))

    def g(self, j: int, qv: arb) -> arb:
        s = arb(j) + 3 * HALF
        v = 2 / SQPI * (self.alpha * qv).gamma_upper(s) * inv_pow(qv, 2 * j + 3)
        return v if j % 2 == 0 else -v

    def decay(self, r: arb, smin: arb) -> arb:
        return (-self.alpha * smin * smin * r * r).exp()

    def decay_rate(self, rK: arb, smin: arb) -> arb:
        return 2 * self.alpha * smin * smin * rK


class DipolarShort(RieszShort):
    """Short-range part of V_d = (2/sqrt pi) int w_d(u) e^(-u q) du, w_d(u) = u^(-1/2) (1 - e^(-u d^2)) / d^2 <= u^(1/2):
    g^(j)(q) = (-1)^j (2/(d^2 sqrt pi)) [Gamma(j+1/2, alpha q) q^-(j+1/2) - Gamma(j+1/2, alpha (q+d^2)) (q+d^2)^-(j+1/2)].
    Completely monotone; |g^(j)| <= |g_S,Riesz^(j)| (w_d <= w_3), so RieszShort's far majorant C_j e^(-alpha q) applies."""
    pot = "dipolar_short"

    def __init__(self, alpha: arb, d: arb) -> None:
        super().__init__(alpha)
        self.d2 = d * d

    def g(self, j: int, qv: arb) -> arb:
        """On a wide ball use the mean-value form g(q_c) + g^(j+1)(ball) [-r, r]: the difference of the two incomplete
        gammas cancels to O(d^2) and would otherwise inflate the ball by about 1/d^2."""
        if bool(qv.rad() > 0) and bool(qv.rad() > arb(10) ** -20 * qv.mid().abs_upper()):
            mid = arb(qv.mid())
            return self.g_direct(j, mid) + self.g_direct(j + 1, qv) * arb(0, 1) * arb(qv.rad())
        return self.g_direct(j, qv)

    def g_direct(self, j: int, qv: arb) -> arb:
        s = arb(j) + HALF
        q2 = qv + self.d2
        v = 2 / (self.d2 * SQPI) * ((self.alpha * qv).gamma_upper(s) * inv_pow(qv, 2 * j + 1)
                                    - (self.alpha * q2).gamma_upper(s) * inv_pow(q2, 2 * j + 1))
        return v if j % 2 == 0 else -v


class DipolarW:
    """W_d = V_d - r^-3 (minus a completely monotone function; power-law majorant, p0 = 5)."""
    pot = "dipolar_W"

    def __init__(self, d: arb) -> None:
        self.d = d
        self.d2 = d * d
        self.p0 = 5
        self.Cw = [self.d2 / SQPI * (arb(j) + 5 * HALF).gamma() for j in range(5)]

    def g(self, j: int, qv: arb) -> arb:
        sg = 1 if j % 2 == 0 else -1
        gd = 2 / self.d2 * poch(HALF, j) * (inv_pow(qv, 2 * j + 1) - inv_pow(qv + self.d2, 2 * j + 1))
        g3 = poch(3 * HALF, j) * inv_pow(qv, 2 * j + 3)
        return sg * (gd - g3)


class RieszFull:
    """V = r^-3 in real space only (negative control), power-law majorant p0 = 3 (exact: |g^(j)| = (3/2)_j q^-(j+3/2))."""
    pot = "riesz3_full"

    def __init__(self) -> None:
        self.p0 = 3
        self.Cw = [poch(3 * HALF, j) for j in range(5)]

    def g(self, j: int, qv: arb) -> arb:
        v = poch(3 * HALF, j) * inv_pow(qv, 2 * j + 3)
        return v if j % 2 == 0 else -v


class Composite:
    def __init__(self, comps: list) -> None:
        self.comps = comps

    def g(self, j: int, qv: arb) -> arb:
        tot = arb(0)
        for c in self.comps:
            tot += c.g(j, qv)
        return tot


KEYS = [f"{a}{k}" for a in ("v", "s", "t", "ss", "st", "tt") for k in range(3)]


def power_tail(comp, qmax: int, t0: arb, F1: arb, F2: arb) -> dict:
    """Entry bounds of the real-space sums over |R0| >= r_tail for a power-law component (see module docstring)."""
    smin = path_norms(t0)[0]
    r_tail = C * arb(qmax + 1).sqrt()
    gb = [comp.Cw[j] / smin ** (2 * j + comp.p0) for j in range(5)]
    beta = point_bounds(None, arb(1), arb(1), t0, gb)  # bH^(k)(r) = beta_k r^-(p0+2)
    a = A_REC
    sq2 = arb(2).sqrt()
    mono = {"v": [(a ** 2, 2)], "s": [(2 * F1 * a ** 3, 3)], "t": [(2 * sq2 * a ** 2, 2), (2 * sq2 * F1 * a ** 3, 3)],
            "ss": [(2 * F2 * a ** 4, 4)], "st": [(12 * sq2 * F1 * a ** 3, 3), (4 * sq2 * F2 * a ** 4, 4)],
            "tt": [(8 * a ** 2, 2), (32 * F1 * a ** 3, 3), (8 * F2 * a ** 4, 4)]}
    y0 = r_tail - 2 * RHO_V
    assert bool(y0 > 1)

    def psum(e: int) -> arb:
        if e >= -2:
            return arb("inf")
        return 2 * PI * (y0 ** (e + 2) / (-(e + 2)) + RHO_V * y0 ** (e + 1) / (-(e + 1)))

    res = {}
    for key, ms in mono.items():
        for k in range(3):
            tot = arb(0)
            for (cf, deg) in ms:
                tot += cf * beta[k] * psum(deg - comp.p0 - 2)
            res[f"{key}{k}"] = tot
    res["r_tail"] = r_tail
    res["beta"] = beta
    return res


# ---------------------------------------------------------------- reciprocal (long-range) part

class Recip:
    def __init__(self, alpha: arb, t0: arb, rho_s: arb, rho_tp: arb, rho_t: arb, QG: int = 400, d: arb | None = None,
                 series_M: int = 6, force_series: bool = False) -> None:
        self.alpha = alpha
        self.d = d
        self.series = d is not None or force_series
        self.M = series_M if d is not None else 0
        self.d2 = d * d if d is not None else arb(0)
        if self.series:
            ad = alpha * self.d2
            assert bool(ad < 1)
            k = arb(109) / 100  # > Cramer's constant 1.0865 (|He_n(y)| e^(-y^2/4) <= k sqrt(n!))
            self.rem = []
            for n in range(5):
                if d is None:
                    self.rem.append(arb(0))
                    continue
                Mq = self.M
                r = (2 * SQPI * k * arb(math.factorial(n)).sqrt() * arb(2) ** (-HALF * n) * alpha ** (HALF - HALF * n)
                     * ad ** (Mq + 1) / (arb(math.factorial(Mq + 2)) * (Mq + 3 * HALF - HALF * n) * (1 - ad)))
                self.rem.append(r)
        self.sa = alpha.sqrt()
        self.t0 = t0
        self.c0 = 4 * (PI * alpha).sqrt()
        self.c2 = 2 * SQPI / self.sa
        self.c3 = SQPI / (alpha * self.sa)
        self.e0 = {0: ((B1[0] - B2[0]) / 2, (B1[1] - B2[1]) / 2), 1: ((B2[0] - B1[0]) / 2, (B2[1] - B1[1]) / 2)}
        self.e1 = {0: B2, 1: B1}
        self.shell1 = [(1, 0), (0, 1), (1, 1)]
        self.rho = (rho_s, rho_tp, rho_t)
        self.crude = {"near": self.crude_bound("near", QG), "far": self.crude_bound("far", QG)}

    # Vh^(n)(x), n = 0..4, entire in x
    def vh(self, n: int, x: arb) -> arb:
        E = (-x * x / (4 * self.alpha)).exp()
        if n == 0:
            return self.c0 * E - 2 * PI * x * (x / (2 * self.sa)).erfc()
        if n == 1:
            return -2 * PI * (x / (2 * self.sa)).erfc()
        if n == 2:
            return self.c2 * E
        if n == 3:
            return -self.c3 * x * E
        return self.c3 * (x * x / (2 * self.alpha) - 1) * E

    def vh_all(self, x: arb) -> list[arb]:
        """[Vh(x), Vh'(x), ..., Vh''''(x)] enclosed over the ball x.
        Riesz 3 (closed form) or, for the dipole, Vh_d(x) = sum_m (-d^2)^m/(m+1)! 2 sqrt(pi) J_{m-1/2}(x),
        J_a(x) = int_0^alpha u^a e^(-x^2/(4u)) du,  J_{-1/2} = 2 sqrt(alpha) E - sqrt(pi) x erfc(x/(2 sqrt alpha)),
        J_{m-1/2} = (alpha^(m+1/2) E - (x^2/4) J_{m-3/2}) / (m + 1/2), E = e^(-x^2/(4 alpha)) (Taylor series in x via
        arb_series), truncated after m = M with the remainder self.rem[n] on the n-th derivative."""
        if not self.series:
            return [self.vh(n, x) for n in range(5)]
        xs = flint.arb_series([x, 1], prec=5)
        E = (-(xs * xs) / (4 * self.alpha)).exp()
        J = 2 * self.sa * E - SQPI * xs * (xs / (2 * self.sa)).erfc()
        tot = 2 * SQPI * J
        b = xs * xs / 4
        cf = arb(1)
        for m in range(1, self.M + 1):
            J = (self.alpha ** (m + HALF) * E - b * J) / (m + HALF)
            cf = cf * (-self.d2) / (m + 1)
            tot = tot + 2 * SQPI * cf * J
        co = tot.coeffs()
        return [co[n] * math.factorial(n) + arb(0, 1) * self.rem[n] for n in range(5)]

    def vhD3(self, x: Dl2) -> tuple[Dl2, Dl2, Dl2]:
        d = self.vh_all(x.v)
        return x.compose(d[0], d[1], d[2]), x.compose(d[1], d[2], d[3]), x.compose(d[2], d[3], d[4])

    def fjet(self, vx: Dl2, vy: Dl2, t: arb, sfac: Dl2 | None) -> list[list[Dl2]]:
        """F(P_t^-1 v) / sfac^2 written as w w^T Vh(sfac |w|) with w = P_t^-1 v (sfac = s for G0 = 0, None = 1),
        and its first two t-derivatives at fixed v; entries 11, 12, 22."""
        wx = vx * (1 + t * t) + vy * (-t)
        wy = vx * (-t) + vy
        dwx = vx * (2 * t) - vy
        dwy = -vx
        ddwx = vx * 2
        p = wx * wx + wy * wy
        p1 = (wx * dwx + wy * dwy) * 2
        p2 = (dwx * dwx + dwy * dwy + wx * ddwx) * 2
        nu = p.sqrt()
        nu1 = p1 / (nu * 2)
        nu2 = p2 / (nu * 2) - p1 * p1 / (nu * nu * nu * 4)
        x = nu * sfac if sfac is not None else nu
        V0, V1, V2 = self.vhD3(x)
        if sfac is not None:
            h1 = V1 * sfac * nu1
            h2 = V2 * sfac * sfac * nu1 * nu1 + V1 * sfac * nu2
        else:
            h1 = V1 * nu1
            h2 = V2 * nu1 * nu1 + V1 * nu2
        zero = wx * 0
        W, dW, ddW = (wx, wy), (dwx, dwy), (ddwx, zero)
        out = [[], [], []]
        for (i, j) in ((0, 0), (0, 1), (1, 1)):
            P = W[i] * W[j]
            P1 = dW[i] * W[j] + W[i] * dW[j]
            P2 = ddW[i] * W[j] + dW[i] * dW[j] * 2 + W[i] * ddW[j]
            out[0].append(P * V0)
            out[1].append(P1 * V0 + P * h1)
            out[2].append(P2 * V0 + P1 * h1 * 2 + P * h2)
        return out

    def sums2(self, tri: int, s: arb, tt: arb, ub: arb) -> list[Dl2]:
        sD = Dl2(s, 1)
        tD = Dl2(tt, 0, 1)
        ex = tD * self.e1[tri][0] + self.e0[tri][0]
        ey = tD * self.e1[tri][1] + self.e0[tri][1]
        if bool(s.upper() <= arb(1) / 4 + MARGIN):
            region = "near"
        elif bool(s.lower() >= arb(1) / 4 - MARGIN) and bool(s.upper() <= 1 + MARGIN):
            region = "far"
        else:
            raise ValueError("cell straddles s = 1/4")
        out = []
        for tval in (arb(0), ub):
            blk = self.fjet(ex, ey, tval, sD)
            if region == "far":
                is2 = (sD * sD).inv()
                for (m, n) in self.shell1:
                    gx = B1[0] * m + B2[0] * n
                    gy = B1[1] * m + B2[1] * n
                    fp = self.fjet(ex * sD + gx, ey * sD + gy, tval, None)
                    fm = self.fjet(-(ex * sD) + gx, -(ey * sD) + gy, tval, None)
                    f0 = self.fjet(Dl2(gx), Dl2(gy), tval, None)
                    for k in range(3):
                        for e in range(3):
                            blk[k][e] = blk[k][e] + (fp[k][e] + fm[k][e] - f0[k][e] * 2) * is2
            cb = self.crude[region]
            for k in range(3):
                for e in range(3):
                    x = blk[k][e]
                    blk[k][e] = Dl2(x.v + arb(0, 1) * cb[(0, 0, k)], x.s + arb(0, 1) * cb[(1, 0, k)],
                                    x.t + arb(0, 1) * cb[(0, 1, k)], x.ss + arb(0, 1) * cb[(2, 0, k)],
                                    x.st + arb(0, 1) * cb[(1, 1, k)], x.tt + arb(0, 1) * cb[(0, 2, k)])
            out.append(blk)
        # order of N2's 18 sums: B0, B1_0, B2_0 (t = 0), B_u, B1_u, B2_u (window); 3 entries each
        res = []
        for blk in out:
            for k in range(3):
                res += blk[k]
        return res

    # ------------------------------------------------------------ rigorous bound of the omitted reciprocal terms
    @staticmethod
    def qmin_box(m: int, n: int) -> Fraction:
        """min over (x, y) in [m - 1/2, m + 1/2] x [n - 1/2, n + 1/2] of Q(x, y) = x^2 + y^2 - x y (exact)."""
        def q(x: Fraction, y: Fraction) -> Fraction:
            return x * x + y * y - x * y
        lo = (Fraction(m) - Fraction(1, 2), Fraction(m) + Fraction(1, 2))
        lo2 = (Fraction(n) - Fraction(1, 2), Fraction(n) + Fraction(1, 2))
        if lo[0] <= 0 <= lo[1] and lo2[0] <= 0 <= lo2[1]:
            return Fraction(0)
        best = None
        for x in lo:  # edges x fixed: minimise y^2 - x y over the y interval: y* = x/2
            y = min(max(x / 2, lo2[0]), lo2[1])
            v = q(x, y)
            best = v if best is None or v < best else best
        for y in lo2:
            x = min(max(y / 2, lo[0]), lo[1])
            v = q(x, y)
            best = v if v < best else best
        return best

    def crude_bound(self, region: str, QG: int) -> dict:
        """Bound, uniform over the region's real (s, t') and |t| <= t0, of sum over the omitted G0 pairs of
        |d^a_s d^b_t' d^k_t Phi_G0_ij|, for a + b <= 2, k <= 2 (Cauchy estimates; see module docstring)."""
        r1, r2, r3 = self.rho
        t0 = self.t0
        al = self.alpha
        smax = (arb(1) / 4 if region == "near" else arb(1)) + MARGIN  # real s (and tau s) of the region, with margin
        S = smax + r1
        T = t0 + r3
        nP_c = 1 + (t0 ** 4 + 2 * t0 * t0).sqrt()          # ||P_tc^-1|| for real |t_c| <= t0
        smin_c = 1 - (t0 ** 4 + 2 * t0 * t0).sqrt()        # sigma_min(P_tc^-1)
        nP_T = 1 + (T ** 4 + 2 * T * T).sqrt()             # ||P_t^-1|| on the complex disc
        A1 = r3 * ((2 * t0 + r3) ** 2 + 2).sqrt()          # ||P_t^-1 - P_tc^-1||
        eA = A_REC + r2 * B_LEN
        eps2 = (nP_T * eA) ** 2
        omega = 4 * (PI * al).sqrt()                       # int_0^alpha 2 sqrt(pi) u^(-1/2) du
        tot = arb(0)
        lim = int(math.isqrt(4 * QG)) + 2
        npairs = 0
        maxterm = arb(0)
        for m in range(-lim, lim + 1):
            for n in range(-lim, lim + 1):
                if not (m > 0 or (m == 0 and n > 0)):
                    continue
                Q = m * m + n * n - m * n
                if Q > QG:
                    continue
                if region == "far" and Q == 1:
                    continue  # first shell: exact in the far region
                G = B_LEN * arb(Q).sqrt()
                if region == "near":
                    dist = G - smax * A_REC
                else:
                    qm = self.qmin_box(m, n)
                    dist = B_LEN * arb(qm.numerator).sqrt() / arb(qm.denominator).sqrt() - MARGIN * A_REC
                zc = smin_c * dist
                Dlt = A1 * (G + S * eA) + nP_c * (r1 * eA + S * r2 * B_LEN)
                re = (zc - Dlt) ** 2 - 2 * Dlt * Dlt
                assert bool(zc > Dlt) and bool(re > 0), (m, n, region)
                assert bool(zc * zc - Dlt * Dlt > 8 * al)      # monotone in |z_c| beyond zc
                Y = re / (4 * al)
                assert bool(Y > 2)                              # monotone in u, sup at u = alpha
                Z = (zc + Dlt) ** 2 / (4 * al)
                term = eps2 * omega * (2 + 10 * Z + 4 * Z * Z) * (-Y).exp()
                tot += term
                maxterm = maxterm.max(term)
                npairs += 1
        # remainder |G0| > G_c (all Q > QG): exponential majorant + Voronoi integral lemma on L* (cell area 4 pi^2)
        Gc = B_LEN * arb(QG + 1).sqrt()
        rho_s = B_LEN / SQ3
        g0 = Gc - 2 * rho_s
        A0 = A1 * S * eA + nP_c * (r1 * eA + S * r2 * B_LEN)
        mu = smin_c - A1 - (smin_c * smax * A_REC + A0) / g0
        nu = smin_c + A1 + A0 / g0
        gam = (mu * mu - 2 * (A1 + A0 / g0) ** 2) / (4 * al)
        assert bool(mu > 0) and bool(gam > 0)
        X0 = nu * nu * g0 * g0 / (4 * al)
        assert bool(X0 >= 1)
        # term(g) <= eps2 omega 16 (nu^2/(4 al))^2 g^4 e^(-gam g^2) <= K e^(-lam g), g >= g0
        Kc = eps2 * omega * 16 * (nu * nu / (4 * al)) ** 2 * (4 / gam) ** 2 * arb(-2).exp()
        lam = gam * g0 / 2
        y0 = g0
        rem = Kc / (2 * PI) * (-lam * y0).exp() * ((y0 + rho_s) / lam + 1 / (lam * lam))
        tot += rem
        out = {}
        fact = [1, 1, 2]
        for a in range(3):
            for b in range(3 - a):
                for k in range(3):
                    out[(a, b, k)] = tot * fact[a] * fact[b] * fact[k] / (r1 ** a * r2 ** b * r3 ** k)
        out["_meta"] = {"pairs": npairs, "sum_M": float(tot.upper()), "max_term": float(maxterm.upper()),
                        "remainder": float(rem.upper()), "max_bound": float(max(v for kk, v in out.items()
                                                                                    if kk != "_meta").upper())}
        return out


# ---------------------------------------------------------------- model

class M1Model(N2.Model):
    def __init__(self, Vreal, exp_comps: list, pow_comps: list, recip: Recip | None, t0: arb, qmax: int) -> None:
        self.V, self.t0, self.qmax = Vreal, t0, qmax
        self.ns = lattice_half(qmax)
        self.F1 = fprime_sup()
        zero = arb(0)
        self.ub = arb(0, 1) * t0
        cols = []
        for (m, l) in self.ns:
            X0 = C * (m + HALF * l)
            Y0 = C * l * SQ3 / 2
            H0 = hess_derivs(Vreal, path_R(X0, Y0, zero))
            Hu = hess_derivs(Vreal, path_R(X0, Y0, self.ub))
            row = []
            for H in (H0[0], H0[1], H0[2], Hu[0], Hu[1], Hu[2]):
                row += H
            cols.append(row)
        self.Hmat = arb_mat(len(self.ns), 18, [x for row in cols for x in row])
        self.th = {0: [(PI * (m - l), 2 * PI * l) for (m, l) in self.ns], 1: [(PI * (l - m), 2 * PI * m) for (m, l) in self.ns]}
        self.F2 = fsecond_sup()
        tb = {k: arb(0) for k in KEYS}
        self.tail_parts = []
        for comp in exp_comps:
            t = tail_bounds(comp, qmax, t0, self.F1)
            self.tail_parts.append({"comp": comp.pot, "kind": "N2 shell lemma", "r_tail": float(t["r_tail"].mid()),
                                    "ratio": float(t["ratio"].upper()), **{k: float(t[k].upper()) for k in KEYS}})
            for k in KEYS:
                tb[k] += t[k]
        for comp in pow_comps:
            t = power_tail(comp, qmax, t0, self.F1, self.F2)
            self.tail_parts.append({"comp": comp.pot, "kind": "power-law Voronoi lemma", "r_tail": float(t["r_tail"].mid()),
                                    **{k: (float(t[k].upper()) if t[k].is_finite() else "inf") for k in KEYS}})
            for k in KEYS:
                tb[k] += t[k]
        tb["r_tail"] = C * arb(qmax + 1).sqrt()
        self.tails = tb
        self.tvec = {a: [arb(0, 1) * tb[f"{a}{(k // 3) % 3}"] if tb[f"{a}{(k // 3) % 3}"].is_finite() else arb("nan")
                         for k in range(18)] for a in ("v", "s", "t", "ss", "st", "tt")}
        self.recip = recip
        self.order = int(os.environ.get("N2_ORDER", "2"))

    def sums(self, tri: int, s: arb, tt: arb) -> list[Dl]:
        out = N2.Model.sums(self, tri, s, tt)
        if self.recip is None:
            return out
        rc = self.recip.sums2(tri, s, tt, self.ub)
        return [Dl(o.v + r.v, o.s + r.s, o.t + r.t) for o, r in zip(out, rc)]

    def sums2(self, tri: int, s: arb, tt: arb) -> list[Dl2]:
        out = N2.Model.sums2(self, tri, s, tt)
        if self.recip is None:
            return out
        rc = self.recip.sums2(tri, s, tt, self.ub)
        return [o + r for o, r in zip(out, rc)]


TIERX = {"riesz3": {"Epp0": -2.43932, "E0": 4.2449758}, ("dipolar", "1/10"): {"Epp0": -2.61623, "E0": 4.2096272},
         ("dipolar", "1/2"): {"Epp0": -4.76740, "E0": 3.5284909}}


def build(pot: str, par: str, t0: arb, qmax: int, alpha: arb) -> tuple[M1Model, dict]:
    rho = (arb(1) / 20, arb(1) / 20, arb(1) / 100)
    info = {}
    if pot in ("yukawa", "gauss"):
        V = N2.Potential(pot, par)
        return M1Model(V, [V], [], None, t0, qmax), info
    if pot == "riesz3direct":
        V = RieszFull()
        return M1Model(V, [], [V], None, t0, qmax), info
    d = N2.q_arb(par) if pot in ("dipolar", "dipolarW") else None
    rec = Recip(alpha, t0, *rho, d=(d if pot == "dipolar" else None), force_series=(pot == "riesz3series"))
    info["recip_crude"] = {"near": rec.crude["near"]["_meta"], "far": rec.crude["far"]["_meta"],
                           "rho_s_tp_t": [str(x) for x in ("1/20", "1/20", "1/100")]}
    S = RieszShort(alpha)
    if pot in ("riesz3", "riesz3series"):
        return M1Model(S, [S], [], rec, t0, qmax), info
    if pot == "dipolar":  # whole dipole Gaussian-mixture split (production)
        SD = DipolarShort(alpha, d)
        info["series_M"] = rec.M
        info["series_rem"] = [float(r.upper()) for r in rec.rem]
        return M1Model(SD, [SD], [], rec, t0, qmax), info
    if pot == "dipolarW":  # r^-3 split + W_d in real space with a power-law tail (first design; too wide, kept for record)
        W = DipolarW(d)
        return M1Model(Composite([S, W]), [S], [W], rec, t0, qmax), info
    raise ValueError(pot)


def main() -> None:
    pot, par, N, t0_s, qmax, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5]), sys.argv[6]
    alpha_s = sys.argv[7] if len(sys.argv) > 7 else "1/10"
    refine_tol = float(os.environ.get("N2_REFINE_TOL", "0.05"))
    max_depth = int(os.environ.get("N2_MAX_DEPTH", "2"))
    t_start = time.time()
    t0 = N2.q_arb(t0_s)
    model, info = build(pot, par, t0, qmax, N2.q_arb(alpha_s))
    tl = model.tails
    print(f"{pot}:{par} alpha={alpha_s} pairs={len(model.ns)} r_tail={float(tl['r_tail'].mid()):.2f} "
          f"tail v0={tl['v0'].upper()} s0={tl['s0'].upper()} ss2={tl['ss2'].upper()} info={info}", flush=True)
    if not all(tl[k].is_finite() for k in KEYS):
        rec = {"potential": pot, "param": par, "qmax": qmax, "tails": model.tail_parts, "certified_not_local_min": False,
               "refused": "tail lemma: a real-space tail sum diverges (infinite ball)",
               "infinite_keys": [k for k in KEYS if not tl[k].is_finite()]}
        with open(__file__, "rb") as fh:
            rec["script_sha256"] = hashlib.sha256(fh.read()).hexdigest()
        with open(out, "w") as fh:
            json.dump(rec, fh, indent=1)
        print(json.dumps(rec, indent=1))
        return
    res = N2.integrate(model, N, refine_tol, max_depth)
    tot, st = res["tot"], res["stats"]
    M = tot["g"]
    pd_ok = st["failed"] == 0 and st["lmin_lo"] > 0 and st["lminu_lo"] > 0 and st["qpd_lo"] > 0
    certified = bool(M < 0) and pd_ok
    key = pot if pot == "riesz3" else (pot, par)
    tx = TIERX.get(key)
    p2 = N2.P2_EZP.get((pot, par))
    rec = {
        "potential": pot, "param": par, "alpha": alpha_s if model.recip is not None else None, "path": "shear", "N": N,
        "t0": t0_s, "qmax": qmax, "refine_tol": refine_tol, "max_depth": max_depth, "cell_rule_order": model.order,
        "n_lattice_half": len(model.ns), "python_flint": flint.__version__, "arb_prec_bits": ctx.prec,
        "seconds": round(time.time() - t_start, 1),
        "M_window_curvature_bound": N2.ball(M), "U_lin_pp0_B2_majorant": N2.ball(tot["lin"]), "E0": N2.ball(tot["ezp"]),
        "tails": model.tail_parts, "recip": info, "stats": st, "positivity_ok": pd_ok, "certified_not_local_min": certified,
        "cert_rationals": {"M_hi": str(N2.to_q_upper(M)) if M.is_finite() else None,
                           "M_lo": str(N2.to_q_lower(M)) if M.is_finite() else None,
                           "lmin_lo": str(Fraction(math.floor(st["lmin_lo"] * 10**12), 10**12)) if math.isfinite(st["lmin_lo"]) else None,
                           "lminu_lo": str(Fraction(math.floor(st["lminu_lo"] * 10**12), 10**12)) if math.isfinite(st["lminu_lo"]) else None,
                           "qpd_lo": str(Fraction(math.floor(st["qpd_lo"] * 10**12), 10**12)) if math.isfinite(st["qpd_lo"]) else None},
        "controls": {"E0_contains_P2": (bool(tot["ezp"].overlaps(arb(p2, 1e-6))) if p2 else None), "P2_E0": p2,
                     "TierX": tx,
                     "M_contains_TierX_Epp0": (bool(M.overlaps(arb(tx["Epp0"]))) if tx else None),
                     "E0_minus_TierX_E0": (float((tot["ezp"] - arb(tx["E0"])).mid()) if tx else None)},
    }
    with open(__file__, "rb") as fh:
        rec["script_sha256"] = hashlib.sha256(fh.read()).hexdigest()
    with open(N2.__file__, "rb") as fh:
        rec["n2_certify_sha256"] = hashlib.sha256(fh.read()).hexdigest()
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=1)
    print(json.dumps({k: rec[k] for k in ("potential", "param", "M_window_curvature_bound", "U_lin_pp0_B2_majorant", "E0",
                                          "certified_not_local_min", "positivity_ok", "seconds", "controls")}, indent=1))
    print("stats", st)


if __name__ == "__main__":
    main()
