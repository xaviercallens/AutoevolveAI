"""Harmonic zero-point motion of the 2D triangular Wigner crystal (1/r, neutralising background) and Lindemann estimates.

Reduced units: e = m = hbar = 1 and lengths in units of the Wigner-Seitz radius a_ws (pi a_ws^2 n = 1), so the cell area
is pi and the nearest-neighbour spacing is a = sqrt(2 pi / sqrt 3). Physical frequencies are omega_red * r_s^(-3/2) Hartree.
"""
import sys
import numpy as np
from scipy.special import erfc

A_CELL = np.pi
A_NN = np.sqrt(2 * np.pi / np.sqrt(3))
A1, A2 = np.array([A_NN, 0.0]), np.array([A_NN / 2, A_NN * np.sqrt(3) / 2])
B1 = 2 * np.pi / A_NN * np.array([1.0, -1 / np.sqrt(3)])
B2 = 2 * np.pi / A_NN * np.array([0.0, 2 / np.sqrt(3)])


def lattice(v1: np.ndarray, v2: np.ndarray, cut: float) -> np.ndarray:
    """All nonzero points j v1 + k v2 with norm <= cut."""
    n = int(cut / (min(np.linalg.norm(v1), np.linalg.norm(v2)) * np.sqrt(3) / 2)) + 2
    j, k = np.meshgrid(np.arange(-n, n + 1), np.arange(-n, n + 1))
    p = j.ravel()[:, None] * v1 + k.ravel()[:, None] * v2
    r = np.linalg.norm(p, axis=1)
    return p[(r > 1e-12) & (r <= cut)]


def radial_hessian(p: np.ndarray, d1: np.ndarray, d2: np.ndarray) -> np.ndarray:
    """Hessian of a radial function f(|x|) at points p, given f'(r) and f''(r): f'' xx/r^2 + f'/r (I - xx/r^2)."""
    r = np.linalg.norm(p, axis=1)
    u = p / r[:, None]
    uu = u[:, :, None] * u[:, None, :]
    return d2[:, None, None] * uu + (d1 / r)[:, None, None] * (np.eye(2) - uu)


def psi(k: np.ndarray, alpha: float = 1.0, keep_g0: bool = True) -> np.ndarray:
    """Psi(k) = sum_{R != 0} Phi(R) cos(k.R), Phi = Hessian of 1/r, by Ewald splitting 1/r = erfc(ar)/r + erf(ar)/r.

    keep_g0=False drops the G = 0 term of the reciprocal sum at every k (the NEGATIVE control: the background cancels
    the G = 0 term of the energy, not of the k-dependent dynamical matrix)."""
    R = lattice(A1, A2, 6.5 / alpha)
    r = np.linalg.norm(R, axis=1)
    g = 2 * alpha / np.sqrt(np.pi) * np.exp(-(alpha * r) ** 2)
    d1 = -erfc(alpha * r) / r**2 - g / r
    d2 = 2 * erfc(alpha * r) / r**3 + g * (2 / r**2 + 2 * alpha**2)
    phis = radial_hessian(R, d1, d2)
    short = np.einsum("kr,rab->kab", np.cos(k @ R.T), phis)
    G = np.vstack([np.zeros((1, 2)), lattice(B1, B2, 13.0 * alpha)])
    out = short.copy()
    for i in range(len(k)):
        q = G - k[i]
        qn = np.linalg.norm(q, axis=1)
        m = qn > 1e-12
        if not keep_g0:
            m[0] = False
        vt = 2 * np.pi / qn[m] * erfc(qn[m] / (2 * alpha))
        out[i] -= np.einsum("g,ga,gb->ab", vt, q[m], q[m]) / A_CELL
    out += 4 * alpha**3 / (3 * np.sqrt(np.pi)) * np.eye(2)
    return out


def omega2(k: np.ndarray, alpha: float = 1.0, keep_g0: bool = True) -> np.ndarray:
    """Squared phonon frequencies (ascending) of D(k) = Psi(0) - Psi(k)."""
    d = psi(np.zeros((1, 2)), alpha, keep_g0)[0] - psi(k, alpha, keep_g0)
    return np.linalg.eigvalsh(d)


def mp_grid(m: int) -> np.ndarray:
    """Monkhorst-Pack (half-shifted) m x m grid on the reciprocal cell; never contains Gamma."""
    t = (np.arange(m) + 0.5) / m
    i, j = np.meshgrid(t, t)
    return i.ravel()[:, None] * B1 + j.ravel()[:, None] * B2


def bz_averages(m: int) -> tuple[float, float, float]:
    """BZ averages of sum_lambda omega, sum 1/omega, sum 1/omega^2 on an m x m grid (chunked)."""
    k = mp_grid(m)
    w = np.vstack([omega2(k[s:s + 4096]) for s in range(0, len(k), 4096)])
    om = np.sqrt(w)
    return float(om.sum(1).mean()), float((1 / om).sum(1).mean()), float((1 / w).sum(1).mean())


def main() -> None:
    rng = np.random.default_rng(7)
    kr = rng.uniform(-1, 1, (5, 2))
    print("== P1 Ewald alpha-invariance of D(k) at 5 random k (max |D_a - D_1|)")
    d_ref = psi(np.zeros((1, 2)), 1.0)[0] - psi(kr, 1.0)
    for al in (0.6, 1.6):
        d = psi(np.zeros((1, 2)), al)[0] - psi(kr, al)
        print(f"   alpha={al}: {np.abs(d - d_ref).max():.2e}")
    print("== P2 trace sum rule: tr D(k) vs direct sum_{R!=0} (1-cos k.R)/R^3 (R<=400, tail 2pi/(A_c Rmax))")
    Rb = lattice(A1, A2, 400.0)
    rb = np.linalg.norm(Rb, axis=1)
    for kk in kr[:3]:
        direct = np.sum((1 - np.cos(Rb @ kk)) / rb**3) + 2 * np.pi / (A_CELL * 400.0)
        print(f"   k=({kk[0]:+.3f},{kk[1]:+.3f}): Ewald {omega2(kk[None])[0].sum():.6f}  direct {direct:.6f}")
    print("== P3 long-wavelength limits along Gamma-M (expect omega_L^2/k -> 2 pi n = 2)")
    for kn in (1e-2, 1e-3, 1e-4):
        w = omega2(np.array([[0.0, kn]]))[0]
        print(f"   k={kn:.0e}: omega_L^2/k = {w[1] / kn:.6f}   omega_T/k = {np.sqrt(w[0]) / kn:.6f}")
    print("== zero-point quantities on m x m Monkhorst-Pack grids (reduced units)")
    print("    m   <sum w>        <sum 1/w>      <sum 1/w^2>")
    rows = []
    for m in (12, 24, 48, 96, 192, 384):
        s1, s2, s3 = bz_averages(m)
        rows.append((m, s1, s2, s3))
        print(f"  {m:4d}  {s1:.10f}  {s2:.10f}  {s3:.8f}")
    (m4, a4, b4, c4), (m5, a5, b5, c5) = rows[-2], rows[-1]
    p_w = np.log2(abs(rows[-3][1] - a4) / abs(a4 - a5))
    p_i = np.log2(abs(rows[-3][2] - b4) / abs(b4 - b5))
    s1 = a5 + (a5 - a4) / (2**p_w - 1)
    s2 = b5 + (b5 - b4) / (2**p_i - 1)
    print(f"   observed orders: <sum w> p={p_w:.2f}, <sum 1/w> p={p_i:.2f}; Richardson: {s1:.8f}, {s2:.8f}")
    czp = s1 / 2
    print(f"RESULT c_zp = {czp:.6f} Ha = {2 * czp:.6f} Ry   (E_zp = c_zp r_s^-3/2); literature 0.814 Ha [BM via DN]:"
          f" rel diff {(czp - 0.814) / 0.814:+.2e}")
    cu_ws, c_a = s2 / 2, s2 / 2 / A_NN**2
    print(f"RESULT <|u|^2> = {cu_ws:.6f} a_ws^2 r_s^-1/2 ;  <|u|^2>/a^2 = C r_s^-1/2 with C = {c_a:.6f}  (a/a_ws = {A_NN:.6f})")
    print("== N1 classical <|u|^2> at T>0 is proportional to <sum 1/w^2>: grows like log m (Mermin-Wagner)")
    ct = np.sqrt(omega2(np.array([[0.0, 1e-4]]))[0][0]) / 1e-4
    slope = (rows[-1][3] - rows[-2][3]) / np.log(2)
    print(f"   slope d<sum 1/w^2>/d ln m (m {rows[-2][0]}->{rows[-1][0]}) = {slope:.5f}; predicted 1/(2 c_T^2) = {1 / (2 * ct**2):.5f}")
    print("== N2 dropping the G = 0 reciprocal term at k != 0 (wrong background handling), 48 x 48 grid")
    k = mp_grid(48)
    w = omega2(k, keep_g0=False)
    print(f"   fraction of k with an imaginary branch (omega^2<0): {np.mean(w.min(1) < 0):.3f};  min omega^2 {w.min():.4f}")
    wl = omega2(np.array([[0.0, 1e-3]]), keep_g0=False)[0]
    print(f"   at k=1e-3 along Gamma-M: omega^2 = {wl[0]:.3e}, {wl[1]:.3e} (no sqrt(k) plasmon)")
    print("== Lindemann: gamma^2 = <|u|^2>/a^2 = C r_s^-1/2  =>  r_s* = (C/gamma_c^2)^2")
    for gc in (0.20, 0.22, 0.24, 0.26, 0.28, 0.30, 0.33, 0.36, 0.40):
        print(f"   gamma_c={gc:.2f}: r_s* = {(c_a / gc**2) ** 2:8.1f}")
    for rs in (31.0, 37.0):
        print(f"   harmonic gamma at r_s={rs}: {np.sqrt(c_a) * rs**-0.25:.4f}")
    print("== Relative (nearest-neighbour) displacement, delta = a1: finite at T > 0, unlike <|u|^2>")
    print("    m   classical <sum (1-cos k.delta)/w^2>   quantum <sum (1-cos k.delta)/w>")
    for m in (48, 96, 192, 384):
        k = mp_grid(m)
        w = np.vstack([omega2(k[s:s + 4096]) for s in range(0, len(k), 4096)])
        f = (1 - np.cos(k @ A1))[:, None]
        rc, rq = float((f / w).sum(1).mean()), float((f / np.sqrt(w)).sum(1).mean())
        print(f"  {m:4d}  {rc:.8f}                        {rq:.8f}")
    print(f"   classical gamma_rel^2 = <|u_i-u_j|^2>/a^2 = (2/Gamma) * {rc:.6f} / (a/a_ws)^2 = {2 * rc / A_NN**2:.6f}/Gamma;"
          f" at Gamma = 137: gamma_rel = {np.sqrt(2 * rc / A_NN**2 / 137):.4f}")
    print(f"   quantum (T=0) gamma_rel^2 = {rq / A_NN**2:.6f} r_s^-1/2; at r_s = 31: gamma_rel = {np.sqrt(rq / A_NN**2) * 31**-0.25:.4f}")
    print("== Exciton potential h(t) = 2/sqrt(t) - 2/sqrt(t + d^2), t = r^2: signs of (-1)^r h^(r), r = 0..10")
    cm_check()
    if len(sys.argv) > 1:
        figure(sys.argv[1], c_a)


def cm_check() -> None:
    """Symbolic derivatives (sympy), evaluated to 40 digits: sign check of (-1)^r g^(r) on a grid; Lennard-Jones 4(t^-6 - t^-3) as negative control."""
    import mpmath
    import sympy as sp
    mpmath.mp.dps = 40
    t = sp.symbols("t", positive=True)
    grid = [sp.Rational(1, 1000) * sp.Integer(10) ** sp.Rational(k, 4) for k in range(25)]
    cases = [(f"exciton d^2={d2}", 2 / sp.sqrt(t) - 2 / sp.sqrt(t + d2)) for d2 in (sp.Rational(1, 10), 1, 10)]
    cases.append(("control Lennard-Jones", 4 * (t**-6 - t**-3)))
    for name, g in cases:
        bad, worst = 0, None
        for r in range(11):
            f = (-1) ** r * sp.diff(g, t, r)
            for x in grid:
                v = f.subs(t, x).evalf(40)
                if v < 0:
                    bad += 1
                    worst = worst or (r, float(x))
        print(f"   {name:22s}: {bad:3d} negative values out of {11 * len(grid)}; first failure (r, t) = {worst}")


def figure(path: str, c_a: float) -> None:
    """Two panels: dispersion along Gamma-M-K-Gamma (correct and negative control); harmonic gamma against r_s."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    M, K = B2 / 2, (2 * B1 + B2) / 3
    legs = [(np.zeros(2), M), (M, K), (K, np.zeros(2))]
    path_k, x, x0 = [], [], 0.0
    for p0, p1 in legs:
        t = np.linspace(0, 1, 200)[:, None]
        seg = p0 + t * (p1 - p0)
        seg[np.linalg.norm(seg, axis=1) < 1e-9] += 1e-6
        path_k.append(seg)
        x.append(x0 + t[:, 0] * np.linalg.norm(p1 - p0))
        x0 += np.linalg.norm(p1 - p0)
    kp, xp = np.vstack(path_k), np.concatenate(x)
    good, bad = omega2(kp), omega2(kp, keep_g0=False)
    fig, ax = plt.subplots(1, 2, figsize=(9.0, 3.4))
    for b in range(2):
        ax[0].plot(xp, np.sqrt(good[:, b]), color="#2166ac", lw=1.8, label="Ewald, $G=0$ kept" if b == 0 else None)
        ax[0].plot(xp, np.sign(bad[:, b]) * np.sqrt(np.abs(bad[:, b])), color="#b35806", lw=1.2, ls="--",
                   label="control: $G=0$ dropped" if b == 0 else None)
    ticks = [0, np.linalg.norm(M), np.linalg.norm(M) + np.linalg.norm(K - M), x0]
    ax[0].set_xticks(ticks, [r"$\Gamma$", "M", "K", r"$\Gamma$"])
    for t in ticks:
        ax[0].axvline(t, color="0.85", lw=0.6)
    ax[0].axhline(0, color="0.6", lw=0.6)
    ax[0].set_xlim(0, x0)
    ax[0].set_ylabel(r"$\omega$  [$(e^2/m a_{ws}^3)^{1/2}$]  (negative: $-\sqrt{|\omega^2|}$)")
    ax[0].legend(frameon=False, fontsize=8, loc="upper center", ncol=2)
    ax[0].set_ylim(-0.05, 1.55)
    ax[0].set_title("(a) phonons of the triangular Wigner crystal", fontsize=9)
    rs = np.geomspace(1, 300, 200)
    ax[1].plot(rs, np.sqrt(c_a) * rs**-0.25, color="#2166ac", lw=1.8)
    ax[1].text(1.3, np.sqrt(c_a) * 1.3**-0.25 + 0.015, r"harmonic $\gamma=\sqrt{C}\,r_s^{-1/4}$", fontsize=8)
    for r0, lab in ((31, "DN 31(1)"), (37, "TC 37(5)")):
        ax[1].axvline(r0, color="#b35806", lw=1.0, ls=":")
        ax[1].text(r0 * (0.95 if r0 == 31 else 1.08), 0.62, lab, fontsize=8, color="0.25", ha="right" if r0 == 31 else "left")
    ax[1].set_xscale("log")
    ax[1].set_xlabel(r"$r_s$")
    ax[1].set_ylabel(r"$\gamma=\sqrt{\langle|u|^2\rangle}/a$")
    ax[1].set_ylim(0.1, 0.75)
    ax[1].set_title("(b) Lindemann ratio at $T=0$ (harmonic)", fontsize=9)
    for a in ax:
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path)
    print(f"figure written: {path}")


if __name__ == "__main__":
    main()
