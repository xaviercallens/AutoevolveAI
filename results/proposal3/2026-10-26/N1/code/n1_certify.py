"""N1: rigorous ball-arithmetic (Arb) two-sided enclosure of the EXACT second variation E''(xi) of the harmonic
zero-point energy along a unimodular strain path through the triangular lattice, Gaussian V(r) = exp(-pi a r^2),
uniformly for a in an a-ball and xi in the window [-t0, t0].

usage: python -I n1_certify.py OUT.json PATH N T0 QMAX TOL DEPTH A_LO:A_HI [A_LO:A_HI ...]
  OUT.json  output (one record per a-interval, written after each interval)
  PATH      shear | diag  (shear: P_t = [[1, t], [t, 1 + t^2]]; diag: P_t = diag(1 + t, 1/(1 + t)))
  N         initial Duffy grid N x N per triangle
  T0        window half-width (rational string), xi ranges over the ball [-T0, T0]
  QMAX      lattice truncation: n = (m, l) with m^2 + m l + l^2 <= QMAX summed exactly, the rest a rigorous tail;
            QMAX = 0 picks max(6, ceil(40/(pi a_lo c^2))) per a-interval
  TOL       a cell is bisected while the radius of its E'' enclosure exceeds TOL * cell area (up to DEPTH levels)
  A_LO:A_HI a-interval (rationals, e.g. 2/5:41/100); A_LO = A_HI gives a point

Setting (as B2, CERTIFIED_CURVATURE.md): L_rho = c Z(1,0) + c Z(1/2, sqrt3/2), c^2 = 2/sqrt3; R_n(t) = P_t R_n(0);
H_n(t) = Hess exp(-pi a |R_n(t)|^2); D_t(kappa) = sum_{n != 0} (1 - cos 2 pi kappa.n) H_n(t), reduced kappa;
E(t) = (1/2) int tr D_t^{1/2} dkappa.
For a 2x2 positive definite matrix tr sqrt(D) = sqrt(tr D + 2 sqrt det D). In Duffy coordinates (kappa = s v(t'),
Jacobian s/2, D_t = s^2 B_t, B_t = sum_n theta_n^2 f(s theta_n) H_n(t), f(x) = (1 - cos x)/x^2) the E integrand is
s^2 tau/4 with tau = sqrt(T + 2 delta), T = tr B_t, delta = sqrt det B_t, so
    E''(t) = int g,   g = s^2 tau''/4,
    delta' = det'/(2 delta),  delta'' = det''/(2 delta) - det'^2/(4 delta^3),
    tau''  = (T'' + 2 delta'')/(2 tau) - (T' + 2 delta')^2/(4 tau^3),
with B', B'' built from H_n', H_n'' (closed form; Lean B2 hasDerivAt_* for the scalar pieces).
Cells: int_cell g in |cell| g(centre) + |cell| (h/4)(sup|g_s| + sup|g_t'|)[-1,1]; the partials come from a
first-order forward-mode jet in (s, t') evaluated over the cell ball (and the a-ball and xi-ball). A cell counts
only if det B > 0 on the whole cell ball (this also certifies the dynamical stability of every L_xi, |xi| <= T0,
for every a in the a-ball: D = s^2 B > 0 for kappa != 0).
Controls computed from the same cells: E(0) (integrand s^2 tau/4) and B2's U''(0) (integrand
(s^2/8) tr(B^{-1/2} B'')).
Every number is an arb ball (python-flint 0.6.0, prec 96): rigorous, not kernel-checked (Tier C-ball).
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from fractions import Fraction

sys.path.insert(0, "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/.scratchpad/b2_pylib")
import flint  # noqa: E402
from flint import arb, ctx  # noqa: E402

ctx.prec = 96
PI = arb.pi()
SQ3 = arb(3).sqrt()
C2 = 2 / SQ3
C = C2.sqrt()
HALF = arb(1) / 2
FACT = [arb(math.factorial(k)) for k in range(60)]


def q_arb(s: str) -> arb:
    f = Fraction(s)
    return arb(f.numerator) / arb(f.denominator)


def frac_ball(lo: Fraction, hi: Fraction) -> arb:
    """An arb ball containing [lo, hi] (exact rational endpoints, outward)."""
    a_lo = arb(lo.numerator) / lo.denominator
    a_hi = arb(hi.numerator) / hi.denominator
    return a_lo.union(a_hi)


# ---------------------------------------------------------------- first-order jets in (s, t', a)

class J:
    """Value and first partials in (s, t', a), all arb balls."""
    __slots__ = ("v", "s", "t", "a")

    def __init__(self, v: arb, s: arb, t: arb, a: arb) -> None:
        self.v, self.s, self.t, self.a = v, s, t, a

    def __add__(self, o: object) -> "J":
        if isinstance(o, J):
            return J(self.v + o.v, self.s + o.s, self.t + o.t, self.a + o.a)
        return J(self.v + o, self.s, self.t, self.a)

    __radd__ = __add__

    def __sub__(self, o: object) -> "J":
        if isinstance(o, J):
            return J(self.v - o.v, self.s - o.s, self.t - o.t, self.a - o.a)
        return J(self.v - o, self.s, self.t, self.a)

    def __rsub__(self, o: object) -> "J":
        return J(o - self.v, -self.s, -self.t, -self.a)

    def __neg__(self) -> "J":
        return J(-self.v, -self.s, -self.t, -self.a)

    def __mul__(self, o: object) -> "J":
        if isinstance(o, J):
            return J(self.v * o.v, self.s * o.v + self.v * o.s, self.t * o.v + self.v * o.t,
                     self.a * o.v + self.v * o.a)
        return J(self.v * o, self.s * o, self.t * o, self.a * o)

    __rmul__ = __mul__

    def __truediv__(self, o: object) -> "J":
        if isinstance(o, J):
            q = self.v / o.v
            return J(q, (self.s - q * o.s) / o.v, (self.t - q * o.t) / o.v, (self.a - q * o.a) / o.v)
        return J(self.v / o, self.s / o, self.t / o, self.a / o)

    def __rtruediv__(self, o: object) -> "J":
        q = o / self.v
        return J(q, -q * self.s / self.v, -q * self.t / self.v, -q * self.a / self.v)

    def exp(self) -> "J":
        e = self.v.exp()
        return J(e, e * self.s, e * self.t, e * self.a)


def sqrt_(x: object) -> object:
    if isinstance(x, J):
        r = x.v.sqrt()
        return J(r, x.s / (2 * r), x.t / (2 * r), x.a / (2 * r))
    return x.sqrt()


def val(x: object) -> arb:
    return x.v if isinstance(x, J) else x


# ---------------------------------------------------------------- f(x) = (1 - cos x)/x^2 and f'

def f_thin(x: arb) -> tuple[arb, arb, arb]:
    """f, f', f'' at a (nearly) thin x. |x| < 1/2: Taylor series to order x^24 (k <= 12) with remainder bounded by
    twice the first omitted coefficient bound (2K+2)^2 2^{-2K}/(2K+4)! (term ratios < 1/2 for |x| <= 1/2).
    Otherwise the closed forms f = (1 - cos x)/x^2, f' = (x sin x - 2(1 - cos x))/x^3,
    f'' = (x^2 cos x - 4 x sin x + 6(1 - cos x))/x^4."""
    if bool(x.abs_upper() < HALF):
        f, f1, f2 = arb(0), arb(0), arb(0)
        for k in range(0, 13):
            sg = 1 if k % 2 == 0 else -1
            f += sg * x ** (2 * k) / FACT[2 * k + 2] if k > 0 else 1 / FACT[2]
            if k >= 1:
                f1 += sg * (2 * k) * x ** (2 * k - 1) / FACT[2 * k + 2]
                f2 += sg * (2 * k) * (2 * k - 1) * x ** (2 * k - 2) / FACT[2 * k + 2]
        K = 13
        rem = 2 * arb((2 * K) ** 2) / arb(2) ** (2 * K - 2) / FACT[2 * K + 2]
        e = arb(0, 1) * rem
        return f + e, f1 + e, f2 + e
    if not bool(x.abs_lower() > 0):
        raise ValueError("f_thin: ball contains 0 and is not small")
    sn, cs = x.sin(), x.cos()
    omc = 1 - cs
    x2 = x * x
    return omc / x2, (x * sn - 2 * omc) / (x2 * x), (x2 * cs - 4 * x * sn + 6 * omc) / (x2 * x2)


def f_ball(X: arb) -> tuple[arb, arb]:
    """Enclosures of f and f' over the ball X by centred Taylor forms. From f(x) = int_0^1 (1 - u) cos(u x) du,
    |f^{(k)}| <= int_0^1 (1 - u) u^k du = 1/((k+1)(k+2)) everywhere: 0 <= f <= 1/2, |f'| <= 1/6, |f''| <= 1/12,
    |f'''| <= 1/20. So with xc the midpoint and |x - xc| <= r:
    f(x) in f(xc) + |f'(xc)| r [-1,1] + (r^2/24)[-1,1],  f'(x) in f'(xc) + |f''(xc)| r [-1,1] + (r^2/40)[-1,1]."""
    xc = arb(X.mid())
    r = arb(X.rad())
    f, f1, f2 = f_thin(xc)
    F = f + arb(0, 1) * (f1.abs_upper() * r + r * r / 24)
    F1 = f1 + arb(0, 1) * (f2.abs_upper() * r + r * r / 40)
    F = F.intersection(arb(1, 1) / 4)
    F1 = F1.intersection(arb(0, 1) / 6)
    return F, F1


# ---------------------------------------------------------------- lattice, path, Gaussian Hessian and t-derivatives

def lattice_half(qmax: int) -> list[tuple[int, int]]:
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
        e = t0 + t0 * t0
        return (1 - e, 1 + e, 1 + 2 * t0, arb(2))
    if path == "diag":
        return (1 - t0, 1 / (1 - t0), 1 / ((1 - t0) * (1 - t0)), 2 / ((1 - t0) ** 3))
    raise ValueError(path)


def hess_derivs(a: arb, R: tuple[arb, ...]) -> tuple[list[arb], list[arb], list[arb]]:
    """H, dH/dt, d^2H/dt^2 of Hess exp(-pi a |R(t)|^2), entries (11, 12, 22).
    H = e M, e = exp(-pi a q), q = |R|^2: e' = -pi a q' e, e'' = (pi^2 a^2 q'^2 - pi a q'') e."""
    Rx, Ry, dx, dy, ddx, ddy = R
    pa = PI * a
    k = 4 * pa * pa
    q1 = 2 * (Rx * dx + Ry * dy)
    q2 = 2 * (dx * dx + dy * dy + Rx * ddx + Ry * ddy)
    e = (-pa * (Rx * Rx + Ry * Ry)).exp()
    H, H1, H2 = [], [], []
    for (Ri, Rj, di, dj, ddi, ddj, dl) in ((Rx, Rx, dx, dx, ddx, ddx, 1), (Rx, Ry, dx, dy, ddx, ddy, 0),
                                          (Ry, Ry, dy, dy, ddy, ddy, 1)):
        M = k * Ri * Rj - 2 * pa * dl
        M1 = k * (di * Rj + Ri * dj)
        M2 = k * (ddi * Rj + 2 * di * dj + Ri * ddj)
        H.append(e * M)
        H1.append(e * (-pa * q1 * M + M1))
        H2.append(e * ((pa * pa * q1 * q1 - pa * q2) * M - 2 * pa * q1 * M1 + M2))
    return H, H1, H2


# ---------------------------------------------------------------- tails (uniform in kappa, |t| <= t0, a in the ball)

DEG = 10  # bound on the polynomial degree in r of a tail term besides the count (weights <= r^3, Hessian bounds <= r^6, d/da factor r^2: <= 10)


def tail_bounds(a: arb, qmax: int, path: str, t0: arb) -> dict:
    """Bounds, valid for every entry of B, B', B'' (value and both Duffy partials), of the part of the lattice sum
    over n with m^2 + m l + l^2 >= qmax + 1, i.e. |R0_n| >= r_tail = c sqrt(qmax + 1).

    Shells [r_k, r_k + Delta), r_k = r_tail + k Delta, Delta = 1/4. The number of lattice points with |R0| < r_k +
    Delta is <= pi (r_k + Delta + 1)^2 (disjoint Voronoi hexagons of area 1, circumradius c/sqrt3 < 1). In a shell,
    every polynomial factor is evaluated at the OUTER radius and every Gaussian factor exp(-pi a sigma_min^2 r^2) at
    the INNER radius, so no monotonicity is assumed. Per lattice point: |theta_n| <= th = 2 pi r/c, |beta| <=
    sqrt2 th, f <= 1/2, |f'| <= F1 = 1/6; weight theta^2 f <= th^2/2, |d/ds| <= th^3 F1, |d/dt'| <= th be + th^2 F1 be.
    Beyond K shells the remainder is bounded by a geometric series whose ratio rho_K (computed, must be < 1) bounds
    term_{k+1}/term_k for all k >= K:
    rho(r) = ((r_out + Delta + 1)/(r_out + 1))^2 ((r_out + Delta)/r_out)^DEG exp(-cg (2 r_in Delta + Delta^2)),
    decreasing in r (each factor is), cg = pi a_lo sigma_min^2.
    """
    smin, smax, d1, d2 = path_norms(path, t0)
    a_lo = arb(a.lower())
    a_hi = arb(a.upper())
    pa_hi = PI * a_hi
    k_hi = 4 * pa_hi * pa_hi
    cg = PI * a_lo * smin * smin
    r_tail = C * arb(qmax + 1).sqrt()
    delta = arb(1) / 4

    def hbounds(rin: arb, rout: arb) -> arb:
        g = (-cg * rin * rin).exp()
        R, dR, ddR = smax * rout, d1 * rout, d2 * rout
        q1 = 2 * R * dR
        q2 = 2 * dR * dR + 2 * R * ddR
        M = k_hi * R * R + 2 * pa_hi
        M1 = 2 * k_hi * R * dR
        M2 = k_hi * (2 * ddR * R + 2 * dR * dR)
        bh = M
        bh1 = pa_hi * q1 * M + M1
        bh2 = (pa_hi * pa_hi * q1 * q1 + pa_hi * q2) * M + 2 * pa_hi * q1 * M1 + M2
        return g * (bh + bh1 + bh2)

    F1 = arb(1) / 6  # |f'| <= 1/6 everywhere (integral representation, see f_ball)
    sq2 = arb(2).sqrt()
    acc = {"v": arb(0), "s": arb(0), "t": arb(0), "a": arb(0)}
    K = 400
    last = None
    for kk in range(K + 1):
        rin = r_tail + kk * delta
        rout = rin + delta
        cnt = PI * (rout + 1) ** 2
        th = 2 * PI * rout / C
        be = sq2 * th
        hb = hbounds(rin, rout)
        tv = cnt * (th * th / 2) * hb
        ts = cnt * (th * th * th * F1) * hb
        tt = cnt * (th * be + th * th * F1 * be) * hb
        # |d/da (e^{-pi a q} P(a))| <= e^{-pi a q} P(a) (pi q + 4/a), P of degree <= 4 in a with
        # nonnegative coefficients, q <= (sigma_max r_out)^2
        ta = tv * (PI * smax * smax * rout * rout + 4 / a_lo)
        if kk < K:
            acc["v"] += tv
            acc["s"] += ts
            acc["t"] += tt
            acc["a"] += ta
        else:
            last = (tv, ts, tt, ta)
            rho = ((rout + delta + 1) / (rout + 1)) ** 2 * ((rout + delta) / rout) ** DEG \
                * (-cg * (2 * rin * delta + delta * delta)).exp()
    if not bool(rho < 1):
        raise ValueError("tail ratio not < 1")
    fac = 1 / (1 - rho)
    return {"r_tail": r_tail, "F1": F1, "rho_K": rho, "v": acc["v"] + last[0] * fac, "s": acc["s"] + last[1] * fac,
            "t": acc["t"] + last[2] * fac, "a": acc["a"] + last[3] * fac}


# ---------------------------------------------------------------- the integrands

def integrands(B: list, B1: list, B2: list, s: object) -> tuple[object, object, object] | None:
    """(g = s^2 tau''/4, e0 = s^2 tau/4, upp = (s^2/8) tr(B^{-1/2} B'')), or None if det B > 0 is not certified."""
    det = B[0] * B[2] - B[1] * B[1]
    T = B[0] + B[2]
    if not (bool(val(det) > 0) and bool(val(T) > 0)):
        return None
    T1 = B1[0] + B1[2]
    T2 = B2[0] + B2[2]
    det1 = B1[0] * B[2] + B[0] * B1[2] - 2 * B[1] * B1[1]
    det2 = B2[0] * B[2] + 2 * B1[0] * B1[2] + B[0] * B2[2] - 2 * (B1[1] * B1[1] + B[1] * B2[1])
    dl = sqrt_(det)
    dl1 = det1 / (2 * dl)
    dl2 = det2 / (2 * dl) - det1 * det1 / (4 * dl * dl * dl)
    tau = sqrt_(T + 2 * dl)
    u = T1 + 2 * dl1
    tau2 = (T2 + 2 * dl2) / (2 * tau) - u * u / (4 * tau * tau * tau)
    s2 = s * s
    g = s2 * tau2 / 4
    e0 = s2 * tau / 4
    upp = s2 * ((T + dl) * T2 - (B[0] * B2[0] + 2 * B[1] * B2[1] + B[2] * B2[2])) / (8 * dl * tau)
    return g, e0, upp


class Model:
    def __init__(self, a_lo: Fraction, a_hi: Fraction, path: str, t0: arb, qmax: int) -> None:
        """a ranges over [a_lo, a_hi]; centre values use the exact midpoint a_c, the cell partials (including
        d/da) are enclosed over the whole a-interval, radius delta = (a_hi - a_lo)/2."""
        a = frac_ball(a_lo, a_hi)
        ac = (a_lo + a_hi) / 2
        self.a, self.path, self.t0, self.qmax = a, path, t0, qmax
        self.a_c = arb(ac.numerator) / ac.denominator
        dl = (a_hi - a_lo) / 2
        self.delta = arb(dl.numerator) / dl.denominator
        self.dA = arb(0, 1) * self.delta
        self.ns = lattice_half(qmax)
        tball = arb(0, 1) * t0
        aJ = J(a, arb(0), arb(0), arb(1))
        self.H = []
        self.HJ = []
        for (m, l) in self.ns:
            X0 = C * (m + HALF * l)
            Y0 = C * l * SQ3 / 2
            R = path_R(path, X0, Y0, tball)
            self.H.append(hess_derivs(self.a_c, R))
            self.HJ.append([[(h.v, h.a) for h in Hm] for Hm in hess_derivs(aJ, R)])
        self.th = {0: [(PI * (m - l), 2 * PI * l) for (m, l) in self.ns],
                   1: [(PI * (l - m), 2 * PI * m) for (m, l) in self.ns]}
        self.tails = tail_bounds(a, qmax, path, t0)
        self.tv = arb(0, 1) * self.tails["v"]
        self.ts = arb(0, 1) * self.tails["s"]
        self.tt = arb(0, 1) * self.tails["t"]
        self.ta = arb(0, 1) * self.tails["a"]

    def centre(self, tri: int, s: arb, tt: arb) -> tuple | None:
        Bs = [[arb(0), arb(0), arb(0)] for _ in range(3)]
        for (al, be), Hs in zip(self.th[tri], self.H):
            th = al + be * tt
            w = 2 * th * th * f_thin(s * th)[0]
            for M, Hm in zip(Bs, Hs):
                M[0] += w * Hm[0]
                M[1] += w * Hm[1]
                M[2] += w * Hm[2]
        Bs = [[x + self.tv for x in M] for M in Bs]
        self._last_centre = Bs
        return integrands(Bs[0], Bs[1], Bs[2], s)

    def ball(self, tri: int, s: arb, tt: arb, Bc: list) -> tuple | None:
        """Jets over the cell ball. The values of B, B', B'' are tightened by their own mean-value forms
        B(c) + B_s [-r_s, r_s] + B_t [-r_t, r_t] (intersected with the naive enclosure)."""
        dS = arb(0, 1) * arb(s.rad())
        dT = arb(0, 1) * arb(tt.rad())
        acc = [[[arb(0), arb(0), arb(0), arb(0)] for _ in range(3)] for _ in range(3)]  # [matrix][entry][v,s,t,a]
        for (al, be), Hs in zip(self.th[tri], self.HJ):
            th = al + be * tt
            x = s * th
            fx, fp = f_ball(x)
            th2 = th * th
            wv = 2 * th2 * fx
            ws = 2 * th2 * th * fp
            wt = 4 * th * be * fx + 2 * th2 * fp * s * be
            for M, Hm in zip(acc, Hs):
                for i in range(3):
                    h, ha = Hm[i]
                    e = M[i]
                    e[0] += wv * h
                    e[1] += ws * h
                    e[2] += wt * h
                    e[3] += wv * ha
        mats = []
        for M, Mc in zip(acc, Bc):
            row = []
            for e, ec in zip(M, Mc):
                vs, vt, va = e[1] + self.ts, e[2] + self.tt, e[3] + self.ta
                v = (ec + vs * dS + vt * dT + va * self.dA).intersection(e[0] + self.tv)
                row.append(J(v, vs, vt, va))
            mats.append(row)
        return integrands(mats[0], mats[1], mats[2], J(s, arb(1), arb(0), arb(0)))

    def cell(self, tri: int, s0: Fraction, t0_: Fraction, h: Fraction) -> dict:
        sc, tc = s0 + h / 2, t0_ + h / 2
        sca, tca = arb(sc.numerator) / sc.denominator, arb(tc.numerator) / tc.denominator
        ha = arb(h.numerator) / h.denominator
        sb, tb = sca + arb(0, 1) * ha / 2, tca + arb(0, 1) * ha / 2
        try:
            c = self.centre(tri, sca, tca)
            b = self.ball(tri, sb, tb, self._last_centre) if c is not None else None
        except ValueError:
            return {"ok": False}
        if c is None or b is None:
            return {"ok": False}
        A = ha * ha
        q = ha / 4
        out = {"ok": True}
        for key, cv, bj in zip(("epp", "e0", "upp"), c, b):
            out[key] = A * (cv + arb(0, 1) * (q * (bj.s.abs_upper() + bj.t.abs_upper())
                                               + self.delta * bj.a.abs_upper()))
            if not out[key].is_finite():
                return {"ok": False, "nonfinite": True}
        return out


def integrate(model: Model, N: int, tol: float, max_depth: int) -> dict:
    tot = {"epp": arb(0), "e0": arb(0), "upp": arb(0)}
    st = {"cells": 0, "refined": 0, "failed": 0}
    h0 = Fraction(1, N)
    stack = [(tri, Fraction(i, N), Fraction(j, N), h0, 0) for tri in (0, 1) for i in range(N) for j in range(N)]
    while stack:
        tri, s0, t0_, h, depth = stack.pop()
        r = model.cell(tri, s0, t0_, h)
        wide = (not r["ok"]) or bool(r["epp"].rad() > tol * float(h * h))
        if wide and depth < max_depth:
            h2 = h / 2
            for ds in (0, 1):
                for dt in (0, 1):
                    stack.append((tri, s0 + ds * h2, t0_ + dt * h2, h2, depth + 1))
            st["refined"] += 1
            continue
        st["cells"] += 1
        if not r["ok"]:
            st["failed"] += 1
            st.setdefault("failed_cells", []).append([tri, str(s0), str(t0_), str(h), bool(r.get("nonfinite"))])
            continue
        for key in tot:
            tot[key] += 2 * r[key]
    return {"tot": tot, "stats": st}


def exact_frac(x: arb) -> Fraction:
    m, e = x.man_exp()
    return Fraction(int(m)) * (Fraction(2) ** int(e))


def lo_frac(x: arb) -> Fraction:
    return exact_frac(x.mid()) - exact_frac(x.rad())


def hi_frac(x: arb) -> Fraction:
    return exact_frac(x.mid()) + exact_frac(x.rad())


def q_down(x: arb, den: int = 10**9) -> Fraction:
    return Fraction(math.floor(lo_frac(x) * den), den)


def q_up(x: arb, den: int = 10**9) -> Fraction:
    return Fraction(math.ceil(hi_frac(x) * den), den)


def ballrec(x: arb) -> dict:
    return {"lo": str(q_down(x)), "hi": str(q_up(x)), "lo_float": float(lo_frac(x)), "hi_float": float(hi_frac(x))}


def main() -> None:
    out, path, N, t0_s, qmax, tol, depth = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5]), \
        float(sys.argv[6]), int(sys.argv[7])
    t0 = q_arb(t0_s)
    with open(__file__, "rb") as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()
    recs = []
    for spec in sys.argv[8:]:
        lo_s, hi_s = spec.split(":")
        lo, hi = Fraction(lo_s), Fraction(hi_s)
        tstart = time.time()
        qm = qmax if qmax > 0 else max(6, math.ceil(40 / (math.pi * float(lo) * 2 / math.sqrt(3))))
        model = Model(lo, hi, path, t0, qm)
        res = integrate(model, N, tol, depth)
        tot, st = res["tot"], res["stats"]
        epp = tot["epp"]
        ok = st["failed"] == 0
        if not ok:
            for key in tot:
                tot[key] = arb(0)
        sign = "pos" if (ok and bool(epp > 0)) else ("neg" if (ok and bool(epp < 0)) else "none")
        rec = {"a_lo": str(lo), "a_hi": str(hi), "path": path, "N": N, "t0": t0_s, "qmax": qm, "tol": tol,
               "depth": depth, "n_lattice_half": len(model.ns), "Epp_window": ballrec(epp), "sign": sign,
               "E0": ballrec(tot["e0"]), "Upp0_majorant": ballrec(tot["upp"]), "stats": st,
               "tails": {"v": float(model.tails["v"].upper()), "s": float(model.tails["s"].upper()),
                         "t": float(model.tails["t"].upper()), "a": float(model.tails["a"].upper()), "rho_K": float(model.tails["rho_K"].upper())},
               "seconds": round(time.time() - tstart, 1), "python_flint": flint.__version__, "prec": ctx.prec,
               "script_sha256": sha}
        recs.append(rec)
        print(json.dumps({k: rec[k] for k in ("a_lo", "a_hi", "Epp_window", "sign", "E0", "Upp0_majorant", "stats",
                                               "seconds")}), flush=True)
        with open(out, "w") as fh:
            json.dump(recs, fh, indent=1)


if __name__ == "__main__":
    main()
