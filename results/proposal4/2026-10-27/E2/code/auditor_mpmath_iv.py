"""Independent auditor enclosure of t* using mpmath.iv: interval-Newton roots,
integral tail bound, interval-Newton solve for tau. Not derived from spm_cert.py."""
import json
import sys
from fractions import Fraction

from mpmath import iv, mp, mpf

iv.dps = 60
mp.dps = 60
PI = iv.pi


def g(a):
    return iv.sin(a) - a * iv.cos(a)


def gp(a):
    return a * iv.sin(a)


roots = {}


def root(n: int):
    if n in roots:
        return roots[n]
    x = mp.mpf(n) * mp.pi + mp.pi / 2 - 1 / (mp.mpf(n) * mp.pi + mp.pi / 2)
    for _ in range(60):
        x = x - (mp.sin(x) - x * mp.cos(x)) / (x * mp.sin(x))
    d = mpf(10) ** (-50)
    X = iv.mpf([x - d, x + d])
    # X inside (n pi, n pi + pi/2): g' = a sin a has fixed sign there, root index is n
    assert X.a > (n * PI).b and X.b < (n * PI + PI / 2).a, n
    for _ in range(4):
        m = iv.mpf(X.mid)
        NX = m - g(m) / gp(X)
        assert NX.a >= X.a and NX.b <= X.b, ("Newton not contracting", n)
        X = NX
    roots[n] = X
    return X


def tail(tau, N: int):
    """sum_{n>N} exp(-a_n^2 tau)/a_n^2 <= int_N^inf exp(-pi^2 tau x^2)/(pi^2 x^2) dx (a_n >= n pi,
    summand decreasing) <= erfc(N pi sqrt tau) / (2 sqrt(pi tau) pi^2 N^2), erfc(z) <= exp(-z^2)/(z sqrt pi)."""
    ta = iv.mpf(tau.a)
    zi = N * PI * iv.sqrt(ta)
    erfc_ub = iv.exp(-zi * zi) / (zi * iv.sqrt(PI))
    ub = erfc_ub / (2 * iv.sqrt(PI * ta)) / (PI ** 2 * N * N)
    return iv.mpf([0, ub.b])


def F(tau, N: int):
    s = iv.mpf(0)
    for n in range(1, N + 1):
        a = root(n)
        s += iv.exp(-a * a * tau) / (a * a)
    return 3 * tau + iv.mpf(1) / 5 - 2 * (s + tail(tau, N))


def Fp(tau, N: int):
    s = iv.mpf(0)
    for n in range(1, N + 1):
        a = root(n)
        s += iv.exp(-a * a * tau)
    # tail sum_{n>40} exp(-(n pi)^2 tau) for tau > 0.3 is < exp(-4900): enclosed by [0, 1e-30]
    return 3 + 2 * s + iv.mpf([0, mpf("1e-30")])


N = 40
P = {"D": "3.3e-14", "R": "5.86e-06", "cmax": "33133.0", "L": "8.52e-05", "eps": "0.75",
     "h": "0.065", "w": "1.58", "I1": "5.0", "F": "96485.33212331001"}
q = {k: iv.mpf(v) for k, v in P.items()}
beta1 = q["I1"] * q["R"] ** 2 / (3 * q["eps"] * q["L"] * q["h"] * q["w"] * q["F"] * q["D"] * q["cmax"])
print("beta per 1C", beta1)
scale = q["R"] ** 2 / q["D"]
prod = json.load(open(sys.argv[1]))
out = []
for rec in prod:
    C = rec["C"]
    x0 = iv.mpf(rec["x0"])
    xs = iv.mpf(1) if rec["x_star"] == "1.0" else iv.mpf(29866) / iv.mpf(33133)
    T = (xs - x0) / (C * beta1)
    X = iv.mpf([((T - iv.mpf(1) / 5) / 3).a, (T / 3).b])
    assert X.a > 0.3
    # sanity: F(X.a) < T < F(X.b) so root bracketed (F increasing)
    assert F(iv.mpf(X.a), N).b < T.a and F(iv.mpf(X.b), N).a > T.b
    for it in range(12):
        m = iv.mpf(X.mid)
        NX = m - (F(m, N) - T) / Fp(X, N)
        lo = max(NX.a, X.a)
        hi = min(NX.b, X.b)
        assert lo <= hi
        X = iv.mpf([lo, hi])
    t = X * scale
    tlo, thi = t.a, t.b
    plo, phi = mpf(rec["t_lo_s"]), mpf(rec["t_hi_s"])
    tl = Fraction(*map(int, rec["tau_lo"].split("/")))
    th = Fraction(*map(int, rec["tau_hi"].split("/")))
    inside_tau = bool(mpf(tl.numerator) / tl.denominator <= X.a and X.b <= mpf(th.numerator) / th.denominator)
    inside_f = bool(plo <= tlo and thi <= phi)
    out.append(dict(C=C, x0=rec["x0"], xs=rec["x_star"], my_t=[mp.nstr(tlo, 25), mp.nstr(thi, 25)],
                    my_tau=[mp.nstr(X.a, 25), mp.nstr(X.b, 25)], prod_t=[rec["t_lo_s"], rec["t_hi_s"]],
                    my_tau_inside_prod_tau=inside_tau, my_t_inside_prod_float=inside_f))
    print(C, rec["x0"], rec["x_star"], mp.nstr(t.mid, 16), "w=%.1e" % float(t.delta),
          "inside_tau", inside_tau, "inside_float", inside_f)
json.dump(dict(beta1=str(beta1), N=N, cases=out), open("/tmp/e2audit/my_cert.json", "w"), indent=1)
