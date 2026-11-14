"""PH-2 validated integrator for 2-D quadratic polynomial ODEs y' = c + L y + Q(y,y).

A-posteriori method (see PREREG_ITEM.md): piecewise Taylor reference q, rigorous defect bound,
one-sided Lipschitz constant in a per-step eigen-basis P, bootstrap tube argument, jump and
basis-change factors.  All inequalities are evaluated in Arb balls (160 bits).  Floats are used only
to choose h, the basis P and to display.  Run with:  sage --python3 ph2_enclose.py <args>  (see driver).
"""
from __future__ import annotations
import json, os, resource, sys, time
import numpy as np
from sage.all import RealBallField, QQ, RealNumber

PREC = 160
R = RealBallField(PREC)


def B(x):
    """Exact ball from a rational / float / RealNumber (floats convert exactly)."""
    if isinstance(x, float):  # exact: QQ(float) would round to a 'simple' rational in Sage (QQ(0.1)==1/10)
        n, d = x.as_integer_ratio()
        return R(QQ(n) / QQ(d))
    return R(x)


def sq(x):
    y = x * x
    if y.lower() < 0:
        y = R(0).union(R(y.upper()))
    return y


def rsqrt(x):
    """sqrt of a ball known to be >= 0 mathematically (guards the ball's lower end)."""
    if x.lower() <= 0:
        return R(0).union(R(x.upper()).sqrt())
    return x.sqrt()


def dq(x):
    """exact dyadic rational of a float (keeps denominators powers of 2; QQ(float) would not)."""
    n, d = float(x).as_integer_ratio()
    return QQ(n) / QQ(d)


def up(b):
    """Upper bound of ball as an exact zero-radius ball."""
    return R(b.upper())


class Quad:
    """f_i(y) = c_i + sum_j L_ij y_j + sum_{j,l} Q_ijl y_j y_l (Q_ijl as given, not symmetrised)."""

    def __init__(self, c, L, Q):
        self.c = [B(QQ(x)) for x in c]
        self.L = [[B(QQ(x)) for x in r] for r in L]
        self.Qs = [[[B(QQ(x)) for x in r] for r in m] for m in Q]  # Q[i][j][l]
        self.Qq = Q
        self.nz = [[(j, l, self.Qs[i][j][l]) for j in range(2) for l in range(2) if Q[i][j][l] != 0] for i in range(2)]
        self.Lf = np.array([[float(QQ(x)) for x in r] for r in L])
        self.cf = np.array([float(QQ(x)) for x in c])
        self.Qf = np.array([[[float(QQ(x)) for x in r] for r in m] for m in Q])

    def jac_float(self, y):
        J = self.Lf.copy()
        for i in range(2):
            for j in range(2):
                for l in range(2):
                    J[i][j] += (self.Qf[i][j][l] + self.Qf[i][l][j]) * y[l] if False else 0.0
        # J_ij = L_ij + sum_l (Q_ijl + Q_ilj) y_l
        J = self.Lf.copy()
        for i in range(2):
            for j in range(2):
                for l in range(2):
                    J[i][j] += (self.Qf[i][j][l] + self.Qf[i][l][j]) * y[l]
        return J

    def jac_ball(self, U):
        """Interval Jacobian over box U (list of 2 balls): J_ij = L_ij + sum_l (Q_ijl+Q_ilj) U_l."""
        J = [[None, None], [None, None]]
        for i in range(2):
            for j in range(2):
                s = self.L[i][j]
                for l in range(2):
                    qq = self.Qs[i][j][l] + self.Qs[i][l][j]
                    if qq != 0:
                        s = s + qq * U[l]
                J[i][j] = s
        return J


def conv(sa, sb, k):
    s = R(0)
    for m in range(k + 1):
        s = s + sa[m] * sb[k - m]
    return s


def Fk(sys_, s, k):
    """k-th Taylor coefficient of f(s(t)) for series s=[s0,s1] (lists of balls, possibly shorter)."""
    out = []
    for i in range(2):
        v = sys_.c[i] if k == 0 else R(0)
        for j in range(2):
            if k < len(s[j]):
                v = v + sys_.L[i][j] * s[j][k]
        for (j, l, q) in sys_.nz[i]:
            lim = min(k, len(s[j]) - 1)
            acc = R(0)
            for m in range(max(0, k - len(s[l]) + 1), lim + 1):
                acc = acc + s[j][m] * s[l][k - m]
            v = v + q * acc
        out.append(v)
    return out


def taylor_q(sys_, y0, p):
    """Coefficients q_k (exact dyadic zero-radius balls, k=0..p-1): recursion in balls, then midpoints."""
    s = [[y0[0]], [y0[1]]]
    for k in range(p - 1):
        F = Fk(sys_, s, k)
        for i in range(2):
            s[i].append(F[i] / (k + 1))
    return [[R(c.mid()) for c in s[i]] for i in range(2)]


def horner(coefs, t):
    v = R(0)
    for c in reversed(coefs):
        v = v * t + c
    return v


def inv2(P):
    """Rigorous ball inverse of 2x2 (adjugate/det); None if det contains 0."""
    det = P[0][0] * P[1][1] - P[0][1] * P[1][0]
    if det.contains_zero():
        return None
    return [[P[1][1] / det, -P[0][1] / det], [-P[1][0] / det, P[0][0] / det]]


def mv(M, v):
    return [M[0][0] * v[0] + M[0][1] * v[1], M[1][0] * v[0] + M[1][1] * v[1]]


def nrm2(v):
    return rsqrt(sq(v[0]) + sq(v[1]))


def choose_basis(sys_, qm, h):
    """Float eigen-basis of J at q(h/2); exact ball P, rigorous P^-1. Fallback identity."""
    yh = [float(horner(qm[i], B(h / 2.0 if isinstance(h, float) else float(h) / 2.0)).mid().n(53)) for i in range(2)]
    J = sys_.jac_float(yh)
    cand = []
    try:
        w, V = np.linalg.eig(J)
        if np.all(np.isfinite(V)):
            if abs(w[0].imag) > 0 or np.iscomplexobj(V) and np.any(V.imag != 0):
                v = V[:, 0]
                cand.append(np.column_stack([v.real, v.imag]))
            else:
                cand.append(V.real)
    except Exception:
        pass
    cand.append(np.eye(2))
    for Pf in cand:
        Pf = np.array(Pf, dtype=float)
        n = np.linalg.norm(Pf, axis=0)
        if np.any(n == 0) or not np.all(np.isfinite(n)):
            continue
        Pf = Pf / n
        Pb = [[B(float(Pf[i][j])) for j in range(2)] for i in range(2)]
        Pi = inv2(Pb)
        if Pi is not None:
            return Pb, Pi
    raise RuntimeError("no basis")


def matmul(A, Bm):
    return [[A[i][0] * Bm[0][j] + A[i][1] * Bm[1][j] for j in range(2)] for i in range(2)]


class State:
    def __init__(self, t, m, eps_end, jump, P, Pi):
        self.t, self.m, self.eps_end, self.jump, self.P, self.Pi = t, m, eps_end, jump, P, Pi


def attempt(sys_, st, h, p, tau, drop_defect=False):
    """One validated step of exact length h (QQ). Returns (ok, info, newstate-ish, output)."""
    Hb = B(h)
    hp = [R(1)]
    for k in range(1, 2 * p):
        hp.append(hp[-1] * Hb)
    qm = taylor_q(sys_, st.m, p)
    # basis and norm change
    P, Pi = choose_basis(sys_, qm, float(h))
    if st.P is None:
        eps0 = R(0)
        jn = R(0)
    else:
        C = matmul(Pi, st.P)
        f2 = sq(C[0][0]) + sq(C[0][1]) + sq(C[1][0]) + sq(C[1][1])
        dt = C[0][0] * C[1][1] - C[0][1] * C[1][0]
        # spectral norm of a 2x2: sigma_max^2 = (F^2 + sqrt(F^4 - 4 det^2)) / 2
        fro = rsqrt((f2 + rsqrt(sq(f2) - 4 * sq(dt))) / 2)
        eps0 = up(fro * st.eps_end)
        jn = nrm2(mv(Pi, st.jump))
        eps0 = up(eps0 + jn)
    # defect coefficients D_k, k=0..2p-2
    D = []
    for k in range(0, 2 * p - 1):
        F = Fk(sys_, qm, k)
        if k <= p - 2:
            F = [F[i] - (k + 1) * qm[i][k + 1] for i in range(2)]
        D.append(F)
    dbar = R(0)
    for k in range(len(D)):
        dbar = dbar + nrm2(mv(Pi, D[k])) * hp[k]
    dbar = up(dbar)
    dh = up(dbar * Hb)
    if dh.upper() > tau:  # step-size control (also in the deliberately broken control)
        return False, "defect_too_big", None, None
    if drop_defect:  # CONTROL ONLY: deliberately unsound, the defect is thrown away
        dbar = R(0)
        dh = R(0)
    rho = up(8 * (eps0 + dh))
    if rho == 0:
        rho = R(QQ(1) / 10 ** 60)
    # region U = range of q over [0,h] + P-ellipse bound
    T = R(0).union(Hb)
    rows = [nrm2(P[i]) for i in range(2)]
    U = []
    for i in range(2):
        rg = horner(qm[i], T)
        U.append(rg + (rows[i] * rho) * R(-1).union(R(1)))
    J = sys_.jac_ball(U)
    M = matmul(matmul(Pi, J), P)
    a, c, b = M[0][0], M[1][1], (M[0][1] + M[1][0]) / 2
    nu = (a + c) / 2 + rsqrt(sq((a - c) / 2) + sq(b))
    nup = nu.upper()
    nu_plus = R(max(nup, 0 * nup))
    emax = (eps0 + dh) * (nu_plus * Hb).exp()
    if not emax.upper() < rho.lower():
        return False, "bootstrap eps0=%g dh=%g rho=%g nu=%s emax=%g" % (float(eps0.upper()), float(dh.upper()), float(rho.upper()), nu, float(emax.upper())), None, None
    if nu.upper() < 0 or nu.lower() > 0:
        g = ((nu * Hb).exp() - 1) / nu
    else:
        g = Hb * (nu_plus * Hb).exp()
    eps_end = up(eps0 * (nu * Hb).exp() + dbar * g)
    Zend = [horner(qm[i], Hb) for i in range(2)]
    mnew = [R(z.mid()) for z in Zend]
    jump = [Zend[i] - mnew[i] for i in range(2)]
    out = []
    for i in range(2):
        r = rows[i] * eps_end
        out.append(Zend[i] + r * R(-1).union(R(1)))
    info = dict(h=float(h), eps0=float(eps0.upper()), dbar_h=float(dh.upper()), nu=float(nup), eps_end=float(eps_end.upper()))
    return True, info, State(st.t + h, mnew, eps_end, jump, P, Pi), out


def ball_to_str(b):
    return [str(b.mid().exact_rational()), str(QQ(b.rad().exact_rational()))]


def ball_from_str(s):
    return B(QQ(s[0])).add_error(B(QQ(s[1])).upper() if False else R(QQ(s[1])))


def run(sys_, y0, outputs, p=28, tau=1e-17, ckpt=None, drop_defect=False, log=None, h0=1e-9, growth=1.6,
        max_attempts=10 ** 9, cpu_cap_s=None, ckpt_every=300, tmax_wall=None):
    """Integrate through the sorted exact-rational output times. Returns dict with outputs, step history."""
    outputs = [QQ(x) for x in outputs]
    state = None
    res = dict(outputs=[], steps=0, attempts=0, cpu_prev=0.0, history=[])
    if ckpt and os.path.exists(ckpt):
        d = json.load(open(ckpt))
        state = State(QQ(d["t"]), [B(QQ(x)) for x in d["m"]], R(QQ(d["eps_end"])),
                      [ball_from_str(s) for s in d["jump"]],
                      None if d["P"] is None else [[B(QQ(x)) for x in r] for r in d["P"]],
                      None if d["P"] is None else inv2([[B(QQ(x)) for x in r] for r in d["P"]]))
        res = d["res"]
        res["cpu_prev"] = res.get("cpu_s", 0.0)
        h = QQ(d["h"])
    else:
        state = State(QQ(0), [B(QQ(x)) for x in y0], R(0), [R(0), R(0)], None, None)
        h = dq(h0)
    t0 = time.time()
    cpu0 = resource.getrusage(resource.RUSAGE_SELF)
    cpu_start = cpu0.ru_utime + cpu0.ru_stime
    done_idx = len(res["outputs"])
    since = 0

    def save():
        if not ckpt:
            return
        cpu = resource.getrusage(resource.RUSAGE_SELF)
        res["cpu_s"] = res.get("cpu_prev", 0.0) + (cpu.ru_utime + cpu.ru_stime - cpu_start)
        d = dict(t=str(state.t), m=[str(x.exact_rational()) if False else str(x.mid().exact_rational()) for x in state.m],
                 eps_end=str(state.eps_end.upper().exact_rational()),
                 jump=[ball_to_str(x) for x in state.jump],
                 P=None if state.P is None else [[str(x.mid().exact_rational()) for x in r] for r in state.P],
                 h=str(h), res=res)
        json.dump(d, open(ckpt + ".tmp", "w"))
        os.replace(ckpt + ".tmp", ckpt)

    while done_idx < len(outputs):
        tout = outputs[done_idx]
        while state.t < tout:
            res["attempts"] += 1
            if res["attempts"] > max_attempts:
                save()
                return res
            hh = h
            last = False
            if state.t + hh >= tout or (tout - state.t) < 2 * hh and False:
                hh = tout - state.t
                last = True
            ok, info, ns, out = attempt(sys_, state, hh, p, tau, drop_defect)
            if not ok:
                h = hh / 2
                if h < QQ(1) / 10 ** 40:
                    res["failed"] = str(info)
                    save()
                    return res
                continue
            state = ns
            res["steps"] += 1
            if os.environ.get("PH2_VERBOSE") and log:
                print(res["steps"], float(state.t), info, file=log, flush=True)
            if res["steps"] % 20 == 0 or last:
                res["history"].append([float(state.t), info["h"], info["nu"], info["eps_end"]])
            if (info["nu"] * info["h"] < 0.4) and info["dbar_h"] < tau / 100 and not last:
                h = dq(float(hh * QQ(growth)))
            elif not last:
                h = hh
            since += 1
            if since >= ckpt_every:
                since = 0
                save()
            if cpu_cap_s is not None:
                cpu = resource.getrusage(resource.RUSAGE_SELF)
                if res.get("cpu_prev", 0.0) + (cpu.ru_utime + cpu.ru_stime - cpu_start) > cpu_cap_s:
                    save()
                    res["stopped"] = "cpu_cap"
                    return res
        # output reached at t == tout
        res["outputs"].append(dict(t=str(tout), tf=float(tout), box=[ball_to_str(x) for x in out], eps=info["eps_end"], step=res["steps"]))
        done_idx += 1
        if log:
            print(f"t={float(tout):g} steps={res['steps']} attempts={res['attempts']} eps={info['eps_end']:.3e}", file=log, flush=True)
        save()
        # after output, keep h
    res["finished"] = True
    cpu = resource.getrusage(resource.RUSAGE_SELF)
    res["cpu_s"] = res.get("cpu_prev", 0.0) + (cpu.ru_utime + cpu.ru_stime - cpu_start)
    save()
    return res


def box_ball(box_entry):
    """Output entry [mid_str, rad_str] -> ball."""
    return R(QQ(box_entry[0])).add_error(R(QQ(box_entry[1])))


def robertson() -> Quad:
    c = [QQ(1) / 25, 0]
    L = [[-QQ(1) / 25, -QQ(1) / 25], [0, 0]]
    Q = [[[-30000000, -5000], [-5000, 0]], [[30000000, 0], [0, 0]]]
    # f2 = 1/25(1-a-b) - 1e4 a b - 3e7 a^2 ; f3 = 3e7 a^2   with (a,b)=(y2,y3)
    return Quad(c, L, Q)
