"""K3 part (c) + controls P1-P5, N1-N3. Interval arithmetic (mpmath iv) for the certified claims; floats are Tier X."""
from __future__ import annotations

import json
import random
import sys
from fractions import Fraction as F
from pathlib import Path

import mpmath
import numpy as np
from mpmath import iv, mp

sys.path.insert(0, str(Path(__file__).parent))
from k3lib import IRF, Path as EPath, from_nodes, _iv  # noqa: E402

OUT = Path(__file__).resolve().parents[1]
res: dict = {"controls": {}, "certified": {}, "exploratory_X": {}}
irf = IRF.joos()
mp.dps = 40


def mpf(q: F) -> mpmath.mpf:
    return mpmath.mpf(q.numerator) / q.denominator


# ---- P1: coefficient sums (exact) and Seshadri printed
joos_sum = irf.a0 + sum(irf.a)
sesh_sum = F("0.276") + F("0.282") + F("0.224") + F("0.217")
res["controls"]["P1"] = {"joos_sum": str(joos_sum), "seshadri_eq1_printed_sum": str(sesh_sum),
                         "pass": joos_sum == 1 and sesh_sum == F("0.999")}
# ---- P4: CARBON-1 arithmetic (Ciais et al.), exact rational
imb = F("10.38") - F("2.04") - F("3.15") - F("2.06") * F("2.124")
res["controls"]["P4"] = {"value_exact": str(imb), "value": float(imb), "pass": round(float(imb), 2) == 0.81}


def u_quad(path: EPath, irfx: IRF, t: F) -> mpmath.mpf:
    """Independent implementation: numerical quadrature of int_0^t m(z) h(t-z) dz on the breakpoints."""
    a0 = mpf(irfx.a0)
    a = [mpf(x) for x in irfx.a]
    tau = [mpf(x) for x in irfx.tau]
    tt = mpf(t)

    def h(x: mpmath.mpf) -> mpmath.mpf:
        return a0 + sum(ai * mpmath.exp(-x / ti) for ai, ti in zip(a, tau))

    def m(zm: mpmath.mpf) -> mpmath.mpf:
        r = mpmath.mpf(0)
        for zj, c in path.steps:
            if zm >= mpf(zj):
                r += mpf(c)
        for zj, s in path.kinks:
            if zm > mpf(zj):
                r += mpf(s) * (zm - mpf(zj))
        return r

    pts = sorted({mpf(z) for z, _ in path.steps if z < t} | {mpf(z) for z, _ in path.kinks if z < t})
    knots = sorted(set([mpmath.mpf(0)] + pts + [tt]))
    total = mpmath.mpf(0)
    for lo, hi in zip(knots, knots[1:]):
        # integrand is smooth on (lo,hi); evaluate m just inside the piece to resolve jumps
        total += mpmath.quad(lambda z: m((lo + hi) / 2 + (z - (lo + hi) / 2) * (1 - mpmath.mpf("1e-30"))) * h(tt - z), [lo, hi])
    return total


I1_nodes = [(F(0), F(0)), (F(10), F(1)), (F(22), F(1, 10)), (F(300), F(1, 10)), (F(310), F(0))]
I2_nodes = [(F(0), F(0)), (F(10), F(1)), (F(22), F(1, 10)), (F(300), F(1, 20)), (F(310), F(0))]
S1 = EPath(steps=[(F(0), F(1)), (F(5), F(-9, 10)), (F(200), F(-1, 10))])
paths = {"I1_pl": from_nodes(I1_nodes), "I2_pl_strictly_decreasing": from_nodes(I2_nodes), "S1_staircase": S1}


def inside(ui, uq: mpmath.mpf, tol: str = "1e-20") -> bool:
    lo, hi = mpmath.mpf(ui.a.mid), mpmath.mpf(ui.b.mid)
    return lo - mpmath.mpf(tol) <= uq <= hi + mpmath.mpf(tol)


# ---- P3 + N2
rng = random.Random(20261031)
fails = 0
for k in range(50):
    name = rng.choice(list(paths))
    t = F(rng.randint(1, 8000), 10)
    if not inside(paths[name].u(irf, t), u_quad(paths[name], irf, t)):
        fails += 1
res["controls"]["P3"] = {"points": 50, "outside_interval": fails, "pass": fails == 0}


class WrongIRF(IRF):
    """Deliberate sign error: H uses (1 + exp) instead of (1 - exp)."""

    def H(self, x):  # type: ignore[override]
        if x <= 0:
            return iv.mpf(0)
        r = _iv(self.a0) * _iv(x)
        for ai, ti in zip(self.a, self.tau):
            r += _iv(ai) * _iv(ti) * (1 + iv.exp(-_iv(x) / _iv(ti)))
        return r


wr = WrongIRF(irf.a0, irf.a, irf.tau)
bad = 0
for k in range(50):
    t = F(rng.randint(10, 8000), 10)
    if not inside(S1.u(wr, t), u_quad(S1, irf, t)):
        bad += 1
res["controls"]["N2"] = {"wrong_sign_rejected_at_of_50": bad, "pass": bad >= 48}

single = IRF(F(0), [F(1)], [F(30)])


def nmax(path: EPath, irfx: IRF, tmax: float, N: int = 3000) -> tuple[int, int]:
    ts = np.linspace(1e-3, tmax, N)
    u = np.array([path.u_float(irfx, t) for t in ts])
    d = np.diff(u)
    scale = max(1.0, float(np.max(np.abs(u))))
    s = np.where(d > 1e-10 * scale, 1, np.where(d < -1e-10 * scale, -1, 0))
    s = s[s != 0]
    maxima = sum(1 for p, q in zip(s, s[1:]) if p > 0 > q)
    minima = sum(1 for p, q in zip(s, s[1:]) if p < 0 < q)
    return int(maxima), int(minima)


def random_unimodal(rg: random.Random) -> EPath:
    k_up, k_dn = rg.randint(1, 3), rg.randint(1, 4)
    z = F(0)
    lvl = F(0) if rg.random() < 0.5 else F(rg.randint(1, 5), 10)
    nodes = [(z, lvl)]
    for _ in range(k_up):
        z += F(rg.randint(1, 40))
        lvl += F(rg.randint(0, 10), 10)
        nodes.append((z, lvl))
    for _ in range(k_dn):
        z += F(rg.randint(1, 120))
        lvl = lvl * F(rg.randint(0, 10), 10)
        nodes.append((z, lvl))
    z += F(rg.randint(1, 20))
    nodes.append((z, F(0)))
    return from_nodes(nodes)


def last_node(p: EPath) -> float:
    return float(max(z for z, _ in p.kinks))


rng2 = random.Random(7)
hist1 = {0: 0, 1: 0, 2: 0}
mx1 = 0
for k in range(1500):
    p = random_unimodal(rng2)
    mxs, _ = nmax(p, single, last_node(p) + 300, 1500)
    mx1 = max(mx1, mxs)
    hist1[min(mxs, 2)] += 1
res["controls"]["P2_single_exp"] = {"paths": 1500, "max_local_maxima_seen": mx1, "histogram_0_1_2plus": hist1, "pass": mx1 <= 1}

rng2 = random.Random(7)
histj = {0: 0, 1: 0, 2: 0, 3: 0}
for k in range(1500):
    p = random_unimodal(rng2)
    mxj, _ = nmax(p, irf, last_node(p) + 1500, 1500)
    histj[min(mxj, 3)] += 1
res["exploratory_X"]["random_unimodal_PL_joos_local_max_histogram_0_1_2_3plus"] = histj
res["exploratory_X"]["note"] = ("float grid counts, 1e-10 relative slope threshold, Tier X; 1500 random continuous unimodal "
                                "piecewise-linear paths (seed 7, same paths as P2)")


def certify(path: EPath, irfx: IRF, s: list[F]) -> dict:
    vals = [path.u(irfx, t) for t in s]
    d = [vals[1] - vals[0], vals[1] - vals[2], vals[3] - vals[2], vals[3] - vals[4]]
    return {"times": [str(t) for t in s],
            "u_intervals": [[mpmath.nstr(mpmath.mpf(v.a.mid), 20), mpmath.nstr(mpmath.mpf(v.b.mid), 20)] for v in vals],
            "difference_lower_bounds_u2-u1,u2-u3,u4-u3,u4-u5": [mpmath.nstr(mpmath.mpf(x.a.mid), 12) for x in d],
            "two_local_maxima_certified": all(x.a > 0 for x in d)}


res["certified"]["I1_pl_joos"] = certify(paths["I1_pl"], irf, [F(10), F(21), F(32), F(303), F(320)])
res["certified"]["I2_pl_joos_strictly_decreasing"] = certify(paths["I2_pl_strictly_decreasing"], irf, [F(10), F(21), F(40), F(305), F(330)])
res["certified"]["S1_staircase_joos"] = certify(S1, irf, [F(1), F(5), F(11), F(200), F(500)])

# a0 = 0 IRF (hypothetical, not Joos): decays only
irf0 = IRF(F(0), [x / (1 - irf.a0) for x in irf.a], irf.tau)
S0 = EPath(steps=[(F(0), F(1)), (F(5), F(-9, 10)), (F(300), F(-1, 10))])
res["exploratory_X"]["a0_zero_IRF_staircase_(maxima,minima)_float"] = nmax(S0, irf0, 900, 6000)

c3 = {"I1_single_exp_tau30_maxima": nmax(paths["I1_pl"], single, 800, 4000)[0],
      "I1_joos_maxima_float": nmax(paths["I1_pl"], irf, 800, 4000)[0],
      "S1_single_exp_maxima": nmax(S1, single, 800, 4000)[0],
      "S1_joos_maxima_float": nmax(S1, irf, 800, 4000)[0]}
c3["pass"] = (c3["I1_single_exp_tau30_maxima"] == 1 and c3["I1_joos_maxima_float"] == 2
              and c3["S1_single_exp_maxima"] == 1 and c3["S1_joos_maxima_float"] == 2)
res["controls"]["N3"] = c3

grid: dict = {}
for L in [F(1, 20), F(1, 10), F(15, 100), F(2, 10), F(25, 100), F(3, 10), F(4, 10), F(1, 2)]:
    row = {}
    for zd in [2, 5, 12, 20, 40]:
        nodes = [(F(0), F(0)), (F(10), F(1)), (F(10 + zd), L), (F(300), L), (F(310), F(0))]
        row[str(zd)] = nmax(from_nodes(nodes), irf, 900, 3000)[0]
    grid[str(L)] = row
res["exploratory_X"]["plateau_family_maxima_count_rows_L_cols_drop_duration_years"] = grid


# ---- P5 / N1: part (a) numerics
def stop_path(rg: random.Random) -> tuple[EPath, int, F]:
    T = rg.randint(20, 300)
    pts = sorted(rg.sample(range(0, T), rg.randint(1, 6)))
    lv = F(0)
    area = F(0)
    st: list[tuple[F, F]] = []
    prev = F(0)
    for z in pts:
        area += lv * (z - prev)
        prev = F(z)
        dlt = F(rg.randint(-5, 15), 10)
        if lv + dlt < 0:
            dlt = -lv
        lv += dlt
        st.append((F(z), dlt))
    area += lv * (T - prev)
    st.append((F(T), -lv))
    return EPath(steps=st), T, area


def check_a(irfx: IRF, seed: int, n: int) -> tuple[int, F]:
    rg = random.Random(seed)
    good = 0
    for _ in range(n):
        p, T, area = stop_path(rg)
        ts = [float(T) + 0.5 + 3.0 * i for i in range(300)]
        u = np.array([p.u_float(irfx, t) for t in ts])
        tol = 1e-9 * max(1.0, float(np.max(np.abs(u))))
        if np.all(np.diff(u) <= tol) and np.all(np.diff(u, 2) >= -tol):
            good += 1
    return good, F(0)


g, _ = check_a(irf, 11, 200)
rg = random.Random(5)
lims = []
for _ in range(5):
    p, T, area = stop_path(rg)
    lims.append({"a0_times_int_m": float(irf.a0 * area), "u(1e6)": p.u_float(irf, 1e6)})
res["controls"]["P5"] = {"antitone_and_convex_after_cessation_of_200": g, "limit_checks": lims, "pass": g == 200}

neg = IRF(F("0.6573"), [F("-0.2240"), F("0.2824"), F("0.2763")], irf.tau)  # sum 1, one negative coefficient
nbad = 0
for _ in range(200):
    p, T, area = stop_path(random.Random(_ + 100))
    ts = [float(T) + 0.5 + 3.0 * i for i in range(300)]
    u = np.array([p.u_float(neg, t) for t in ts])
    tol = 1e-9 * max(1.0, float(np.max(np.abs(u))))
    if not (np.all(np.diff(u) <= tol) and np.all(np.diff(u, 2) >= -tol)):
        nbad += 1
res["controls"]["N1"] = {"IRF": "a0=0.6573, a1=-0.2240, a2=0.2824, a3=0.2763 (sum 1)", "violating_histories_of_200": nbad,
                         "pass": nbad >= 1}

json.dump(res, open(OUT / "data" / "results_c.json", "w"), indent=1, default=str)
print(json.dumps(res["controls"], indent=1, default=str))
print(json.dumps(res["certified"], indent=1))
print(json.dumps(res["exploratory_X"], indent=1))
