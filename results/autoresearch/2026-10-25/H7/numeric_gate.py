"""H7 numeric falsification gate: sigma = 3 regulated shell model, 2 D Omega <= H3 + (2E)^{3/2}.

(a) exact-symbolic conservation of H_sigma and mass for sigma = 3 (copy of the owner's
    exploration/second_invariant/symbolic_check.py with k^2 -> k^sigma), with the perturbed-weight control;
(b) the inequality on random + adversarially optimised states, recording sup (2DOmega - H3)/S^{3/2};
(c) negative controls: drop the S^{3/2} term; sigma = 2 regulator vs enstrophy;
(d) short dynamics run (exact linear rotation + RK4 on the nonlinearity), drift of H3, S and the Omega bound.
Run: taskset -c 7 python3 -I numeric_gate.py  -> writes numeric_gate.json next to this file.
"""
import json
import os
import sys

import numpy as np
import sympy as sp

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "numeric_gate.json")


def symbolic_check(N: int, seam: str, sigma: int, perturb: bool = False) -> tuple[bool, bool]:
    x = sp.symbols(f"x0:{N+1}", real=True)
    y = sp.symbols(f"y0:{N+1}", real=True)
    k = sp.symbols(f"k0:{N+1}", real=True)
    D, mu = sp.symbols("D mu", real=True)
    v = [x[n] + sp.I * y[n] for n in range(N + 1)]
    top = sp.I * mu * v[N] ** 2 if seam == "gpe" else 0
    ve = v + [top]
    dv = [(k[n-1] * v[n-1] ** 2 if n else 0) - k[n] * sp.conjugate(v[n]) * ve[n+1]
          - sp.I * D * k[n] ** sigma * v[n] for n in range(N + 1)]
    w = [sp.Rational(1, 2 ** n) for n in range(N + 1)]
    if perturb:
        w[2] = sp.Rational(1, 3)
    H = sum(w[n] * (D * k[n] ** sigma * (x[n] ** 2 + y[n] ** 2)) for n in range(N + 1)) \
        + sum(w[n] * k[n] * sp.im(sp.expand(sp.conjugate(v[n]) ** 2 * v[n+1])) for n in range(N)) \
        + (sp.Rational(1, 2) * mu * k[N] * w[N] * (x[N] ** 2 + y[N] ** 2) ** 2 if seam == "gpe" else 0)
    mass = sum(x[n] ** 2 + y[n] ** 2 for n in range(N + 1))

    def rate(F: sp.Expr) -> sp.Expr:
        return sp.expand(sum(sp.diff(F, x[n]) * sp.re(sp.expand(dv[n])) + sp.diff(F, y[n]) * sp.im(sp.expand(dv[n]))
                             for n in range(N + 1)))
    return rate(H) == 0, rate(mass) == 0


def quantities(v: np.ndarray, D: float, sigma: int = 3) -> dict:
    """v has M = N+2 shells (indices 0..N+1)."""
    M = len(v)
    k = 2.0 ** np.arange(M)
    a = np.abs(v) ** 2
    S = a.sum()
    Omega = 0.5 * (k ** 2 * a).sum()
    cub = sum((2.0 ** -n) * k[n] * (np.conj(v[n]) ** 2 * v[n + 1]).imag for n in range(M - 1))
    Hs = (2.0 ** -np.arange(M) * D * k ** sigma * a).sum() + cub
    return {"S": S, "E": S / 2, "Omega": Omega, "H": Hs, "cub": cub}


def main() -> None:
    rep: dict = {}
    # (a)
    sym = {}
    for N in (3, 5):
        for seam in ("trunc", "gpe"):
            sym[f"N={N},{seam}"] = list(symbolic_check(N, seam, 3))
    sym["neg_control_perturbed_weight_N=4_dH0"] = symbolic_check(4, "trunc", 3, perturb=True)[0]
    sym["sigma2_reproduce_N=3_trunc"] = list(symbolic_check(3, "trunc", 2))
    rep["a_symbolic_sigma3"] = sym
    print("(a)", sym, flush=True)

    # (b)
    rng = np.random.default_rng(20261025)
    viol, worst, ntest = 0, -np.inf, 0
    for _ in range(200000):
        M = int(rng.integers(2, 14))
        D = float(rng.choice([1e-3, 0.1, 1.0, 10.0])) * (1 if rng.random() < 0.8 else -1)
        scale = 10 ** rng.uniform(-3, 3)
        v = scale * (rng.normal(size=M) + 1j * rng.normal(size=M)) * (2.0 ** (-rng.uniform(0, 1.5) * np.arange(M)))
        q = quantities(v, D)
        lhs, rhs = 2 * D * q["Omega"], q["H"] + q["S"] ** 1.5
        ntest += 1
        ratio = (lhs - q["H"]) / q["S"] ** 1.5
        worst = max(worst, ratio)
        if lhs > rhs * (1 + 1e-12) + 1e-300 and lhs - rhs > 1e-9 * max(abs(lhs), abs(rhs), 1):
            viol += 1
    # adversarial: maximise -cub / S^{3/2} (exactly (2DOmega - H3)/S^{3/2}, D-independent) by projected ascent
    best = -np.inf
    for M in range(2, 13):
        for _ in range(8):
            z = rng.normal(size=2 * M)
            for _ in range(300):
                def f(zz: np.ndarray) -> float:
                    vv = zz[:M] + 1j * zz[M:]
                    q = quantities(vv, 1.0)
                    return -q["cub"] / q["S"] ** 1.5
                g = np.zeros_like(z)
                f0 = f(z)
                for i in range(2 * M):
                    e = np.zeros_like(z); e[i] = 1e-6
                    g[i] = (f(z + e) - f0) / 1e-6
                z = z + 0.05 * g
                z /= np.linalg.norm(z)
            best = max(best, f(z))
    rep["b_inequality"] = {"random_tests": ntest, "violations": viol, "max_random_ratio_(2DOmega-H3)/S^1.5": worst,
                           "adversarial_sup_ratio": best, "two_shell_analytic_sup": 2 / 3 ** 1.5}
    print("(b)", rep["b_inequality"], flush=True)

    # (c) negative controls
    v = np.array([1.0 + 0j, -1j])  # N = 0: shells 0,1
    D = 1.0
    q = quantities(v, D)
    rep["c1_drop_S32_term"] = {"v": "[1, -i]", "D": D, "2DOmega": 2 * D * q["Omega"], "H3": q["H"],
                               "violates_2DOmega<=H3": bool(2 * D * q["Omega"] > q["H"])}
    growth = []
    for N in range(0, 12):
        vv = np.zeros(N + 2, dtype=complex); vv[-1] = 1.0
        q2 = quantities(vv, 1.0, sigma=2)
        growth.append({"N": N, "ratio_2DOmega/(H2+S^1.5)": 2 * q2["Omega"] / (q2["H"] + q2["S"] ** 1.5)})
    rep["c2_sigma2_vs_enstrophy"] = growth
    print("(c)", rep["c1_drop_S32_term"], growth[-1], flush=True)

    # (d) dynamics: Strang split, exact rotation for -i omega v, RK4 for the nonlinearity
    N, D, dt, steps = 4, 0.05, 2e-4, 50000
    M = N + 2
    k = 2.0 ** np.arange(M)
    om = D * k ** 3
    v = 0.3 * (rng.normal(size=M) + 1j * rng.normal(size=M))

    def B(u: np.ndarray) -> np.ndarray:
        ue = np.append(u, 0)
        out = -k * np.conj(u) * ue[1:]
        out[1:] += k[:-1] * u[:-1] ** 2
        return out
    q0 = quantities(v, D)
    bound = (q0["H"] + q0["S"] ** 1.5) / (2 * D)
    maxO, maxdH, maxdS = 0.0, 0.0, 0.0
    rot = np.exp(-1j * om * dt / 2)
    for _ in range(steps):
        v = v * rot
        a1 = B(v); a2 = B(v + dt / 2 * a1); a3 = B(v + dt / 2 * a2); a4 = B(v + dt * a3)
        v = v + dt / 6 * (a1 + 2 * a2 + 2 * a3 + a4)
        v = v * rot
        q = quantities(v, D)
        maxO = max(maxO, q["Omega"]); maxdH = max(maxdH, abs(q["H"] - q0["H"])); maxdS = max(maxdS, abs(q["S"] - q0["S"]))
    rep["d_dynamics"] = {"N": N, "D": D, "dt": dt, "T": dt * steps, "H0": q0["H"], "S0": q0["S"],
                         "max_|dH|": maxdH, "max_|dS|": maxdS, "max_Omega": maxO, "Omega_bound_from_t0": bound,
                         "within_bound": bool(maxO <= bound)}
    print("(d)", rep["d_dynamics"], flush=True)

    ok = (all(all(vv) for kk, vv in sym.items() if kk.startswith("N=")) and sym["neg_control_perturbed_weight_N=4_dH0"] is False
          and viol == 0 and best < 1 and rep["c1_drop_S32_term"]["violates_2DOmega<=H3"])
    rep["gate_pass"] = bool(ok)
    json.dump(rep, open(OUT, "w"), indent=1, default=float)
    print("gate_pass", ok)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
