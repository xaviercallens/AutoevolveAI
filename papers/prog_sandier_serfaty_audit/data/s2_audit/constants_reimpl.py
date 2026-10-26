"""S2 check 4: independent float re-implementation (mpmath, tier X) of lambda, mu, K from the
manuscript's formulas (cal:f0-e), (cal:primitive), (cal:constants), written from the TeX, not
from the C++.

Only radii t in [p, R0] are needed for lambda, mu, K (t(s)=sqrt(p^2+s^2), 0<=s<=x0=R0/2,
t(x0)=R0).  On (0, R0] the construction gives u_0=gamma, u_m=(-1)^m c_m r^{6m} (tau=0 and the
U_m cutoff is off), hence B(r)=gamma(r)+sum_m a_m r^{k_m} with a_m=(-1)^m c_m, and the exact
monomial integrals (comp:initial-integrals) hold up to R0.  On [p,R0]: b_m=V_m (edge
polynomial) = c_m t^k cos(k phi), cos phi = p/t; D_0=0; D_m = V_m - a_m t^k.
Retained modes m=1..38 (modes >=39 change f0, e by <1e-11, Section 5).

Positive control: the exact calibration identity 6K+lambda+2pi*mu = W(E_tri) =
-4.15041280767896... (BS2018 closed form) must hold to quadrature accuracy.
Negative controls: (i) drop the angular energy e (set e=0) and (ii) treat the two exponent-6
modes as one (drop the auxiliary index entirely is a no-op on [p,R0] since D_0=0, so instead
we drop mode m=1); both must move lambda or K outside the certificate's printed intervals.
"""
import json
import sys

import mpmath as mp

mp.mp.dps = 25


def lattice_coeffs(a: mp.mpf, M: int = 38) -> list[mp.mpf]:
    import numpy as np
    out = []
    w0 = complex(0.5, float(mp.sqrt(3)) / 2)
    for m in range(1, M + 1):
        D = 256 if m == 1 else 48
        n = np.arange(0, D + 1)
        q = np.arange(-D, D + 1)
        N, Qq = np.meshgrid(n, q, indexing="ij")
        mask = ~((N == 0) & (Qq <= 0))
        w = (N + Qq * w0)[mask]
        k = 6 * m
        s = 2.0 * np.sum(np.real(w ** (-k)))
        out.append(mp.mpf(s) / (k * a ** k))
    return out


class Model:
    def __init__(self, drop_m1: bool = False, no_e: bool = False) -> None:
        self.a = mp.sqrt(2 / mp.sqrt(3))
        self.p = self.a / 2
        self.R0 = 2 * self.p / mp.sqrt(3)
        self.x0 = self.R0 / 2
        self.c = lattice_coeffs(self.a)
        if drop_m1:
            self.c[0] = mp.mpf(0)
        self.no_e = no_e
        self.ks = [6] + [6 * m for m in range(1, 39)]          # index 0 = auxiliary mode
        self.am = [(-1) ** m * self.c[m - 1] for m in range(1, 39)]
        # monomial list for B1: (e_i, v_i)
        self.mon = [(2, mp.pi)] + [(6 * m, 6 * m * self.am[m - 1]) for m in range(1, 39)]

    def S1(self, t: mp.mpf) -> mp.mpf:
        s = t ** 2 / 2 * (mp.mpf(1) / 2 - mp.log(t)) + mp.pi / 8 * t ** 4
        for m in range(1, 39):
            k = 6 * m
            s += self.am[m - 1] * t ** (k + 2) / (k + 2)
        return s

    def S2(self, t: mp.mpf) -> mp.mpf:
        s = mp.mpf(0)
        for e, v in self.mon:
            s += -2 * v * t ** e / e
        for e1, v1 in self.mon:
            for e2, v2 in self.mon:
                s += v1 * v2 * t ** (e1 + e2) / (e1 + e2)
        return s

    def Hk(self, t: mp.mpf, k: int) -> mp.mpf:
        return sum(v * t ** e / (e + k) for e, v in self.mon)

    def D_and_Dp(self, t: mp.mpf) -> tuple[list[mp.mpf], list[mp.mpf]]:
        p = self.p
        phi = mp.acos(p / t) if t > p else mp.mpf(0)
        D = [mp.mpf(0)]
        Dp = [mp.mpf(0)]
        for m in range(1, 39):
            k = 6 * m
            cm = self.c[m - 1]
            V = cm * t ** k * mp.cos(k * phi)
            # d/dt [t^k cos(k phi)] = k t^(k-1) [cos(k phi) - sin(k phi) cot(phi)]
            if phi == 0:
                ratio = mp.mpf(k)
            else:
                ratio = mp.sin(k * phi) * mp.cos(phi) / mp.sin(phi)
            Vp = cm * k * t ** (k - 1) * (mp.cos(k * phi) - ratio)
            D.append(V - self.am[m - 1] * t ** k)
            Dp.append(Vp - k * self.am[m - 1] * t ** (k - 1))
        return D, Dp

    def f0_e(self, t: mp.mpf) -> tuple[mp.mpf, mp.mpf]:
        D, Dp = self.D_and_Dp(t)
        ks = self.ks
        H = {k: self.Hk(t, k) for k in set(ks)}
        src = self.S1(t) + t ** 2 * sum(D[i] / (ks[i] + 2) for i in range(39))
        lin = sum(-2 * D[i] + 2 * ks[i] * D[i] * H[ks[i]] for i in range(39))
        quad = mp.mpf(0)
        e = mp.mpf(0)
        Q = [t * Dp[i] - ks[i] * D[i] for i in range(39)]
        for i in range(39):
            for j in range(39):
                quad += ks[i] * ks[j] * D[i] * D[j] / (ks[i] + ks[j])
                e += Q[i] * Q[j] / (ks[i] + ks[j])
        f0 = -2 * mp.pi * src - (mp.log(t) + self.S2(t) + lin + quad) / 2
        e = e / 2
        if self.no_e:
            e = mp.mpf(0)
        return f0, e

    def constants(self) -> dict[str, mp.mpf]:
        p, R0, x0 = self.p, self.R0, self.x0
        f0p, _ = self.f0_e(p)
        f0R, eR = self.f0_e(R0)

        def t_of(s: mp.mpf) -> mp.mpf:
            return mp.sqrt(p ** 2 + s ** 2)

        # (f0(t(s))-f0(p))/s^2 cancels catastrophically as s->0 (t-p ~ s^2/2p).  A first run
        # with tanh-sinh at 25 digits sampled s ~ 1e-12 and returned garbage (lambda ~ 5e5).
        # Use Gauss-Legendre (nodes not clustered at 0) and 45 working digits for this integral.
        with mp.workdps(45):
            f0p_hi = self.f0_e(p)[0]
            I1 = mp.quad(lambda s: (self.f0_e(t_of(s))[0] - f0p_hi) / s ** 2,
                         [0, mp.mpf("0.05"), x0], method="gauss-legendre")
        I2 = mp.quad(lambda s: self.f0_e(t_of(s))[1], [0, mp.mpf("0.05"), x0])
        bracket = (p / x0) * (f0R - f0p) - (x0 / p) * eR + p * I1 + I2 / p
        lam = bracket / (p * x0)
        mu = f0R - eR / 3 - lam * R0 ** 2 / 2

        def G(s: mp.mpf) -> mp.mpf:
            t = t_of(s)
            f0, e = self.f0_e(t)
            f = f0 - lam * t ** 2 / 2 - mu
            return p / t ** 2 * f - s ** 2 / (p * t ** 2) * e

        K = 2 * mp.quad(G, [0, mp.mpf("0.15"), x0])
        return {"lambda": lam, "mu": mu, "K": K, "G_at_x0": G(x0)}


def main() -> int:
    printed = {"lambda": (mp.mpf(-67300312) / 10**7, mp.mpf(-67300275) / 10**7),
               "mu": (mp.mpf(4138830) / 10**7, mp.mpf(4138838) / 10**7),
               "K": (mp.mpf(-34823) / 10**7, mp.mpf(-34809) / 10**7)}
    w_tri = (mp.pi * mp.log(mp.pi) - mp.pi / 2 * mp.log(3) - 3 * mp.pi * mp.log(mp.gamma(mp.mpf(1) / 3))
             + mp.mpf(3) / 2 * mp.pi * mp.log(2))
    out: dict[str, object] = {}
    ok = True
    for label, kw in [("main", {}), ("NEG_no_angular_e", {"no_e": True}), ("NEG_drop_mode_m1", {"drop_m1": True})]:
        cst = Model(**kw).constants()
        inside = {k: bool(printed[k][0] <= cst[k] <= printed[k][1]) for k in printed}
        ident = 6 * cst["K"] + cst["lambda"] + 2 * mp.pi * cst["mu"]
        out[label] = {k: mp.nstr(v, 15) for k, v in cst.items()}
        out[label]["inside_printed"] = inside
        out[label]["6K+lambda+2pi*mu"] = mp.nstr(ident, 15)
        out[label]["identity_minus_W_tri"] = mp.nstr(ident - w_tri, 5)
        if label == "main":
            ok = ok and all(inside.values()) and abs(ident - w_tri) < mp.mpf(10) ** -10 and abs(cst["G_at_x0"]) < mp.mpf(10) ** -15
        else:
            ok = ok and not all(inside.values())
    out["W_tri_closed_form"] = mp.nstr(w_tri, 15)
    out["all_checks_pass"] = bool(ok)
    print(json.dumps(out, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
