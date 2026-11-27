"""Auditor's independent validated integrator for Robertson (reduced to a=y2, b=y3; y1 = 1-a-b exactly).

Method (deliberately different from the producer's log-norm/defect method): Lohner's interval Taylor method
with QR-reorthogonalised parallelepiped, MPFI intervals (Sage RealIntervalField, not Arb), 128 bits.
Per step [t, t+h] with initial set X = m + A r (m point, A point matrix, r interval vector):
  1. a-priori enclosure Y: X + [0,h] f(Y) subset Y  (Moore's lemma => every solution from X stays in Y on [0,h]);
  2. x(h; x0) in T(x0) + R, T = sum_{k<p} T_k(x0) h^k, R = h^p T_p(Y)  (Lagrange remainder, autonomous ODE);
  3. T(x0) in T(m) + S (x0 - m), S = sum_{k<p} dT_k/dx0(hull X) h^k (mean-value form, forward-mode duals);
  4. new set: m' = mid(T(m)+R), A' = Q of QR(mid(S A)), r' = (A'^-1 S A) r + A'^-1 (T(m)+R-m').
usage: sage --python3 aud_lohner.py OUT.json T1 T2 ...
"""
import sys, json, time
import numpy as np
from sage.all import RealIntervalField, QQ

RI = RealIntervalField(128)
K1, K2, K3 = RI(1) / 25, RI(10 ** 4), RI(3 * 10 ** 7)
P_ORD = 18


def series(a0, b0, p):
    """Taylor coefficients 0..p of (a,b) from start (a0,b0) (intervals)."""
    A, B = [a0], [b0]
    for k in range(p):
        aa = sum((A[m] * A[k - m] for m in range(k + 1)), RI(0))
        ab = sum((A[m] * B[k - m] for m in range(k + 1)), RI(0))
        lin = K1 * ((1 if k == 0 else 0) - A[k] - B[k])
        A.append((lin - K2 * ab - K3 * aa) / (k + 1))
        B.append(K3 * aa / (k + 1))
    return A, B


def dseries(a0, b0, p):
    """Forward-mode: coefficients (v, d/da0, d/db0) for k<p, start interval box."""
    A = [(a0, RI(1), RI(0))]
    B = [(b0, RI(0), RI(1))]
    for k in range(p - 1):
        aa = [RI(0)] * 3
        ab = [RI(0)] * 3
        for m in range(k + 1):
            x, y, z = A[m], A[k - m], B[k - m]
            aa[0] += x[0] * y[0]; aa[1] += x[1] * y[0] + x[0] * y[1]; aa[2] += x[2] * y[0] + x[0] * y[2]
            ab[0] += x[0] * z[0]; ab[1] += x[1] * z[0] + x[0] * z[1]; ab[2] += x[2] * z[0] + x[0] * z[2]
        na, nb = [], []
        for j in range(3):
            lin = K1 * (((1 if k == 0 else 0) if j == 0 else 0) - A[k][j] - B[k][j])
            na.append((lin - K2 * ab[j] - K3 * aa[j]) / (k + 1))
            nb.append(K3 * aa[j] / (k + 1))
        A.append(tuple(na)); B.append(tuple(nb))
    return A, B


def f(a, b):
    return K1 * (1 - a - b) - K2 * a * b - K3 * a * a, K3 * a * a


def subset(X, Y):
    return all(X[i].lower() >= Y[i].lower() and X[i].upper() <= Y[i].upper() for i in range(2))


def apriori(X, H):
    fa, fb = f(*X)
    Y = [X[0] + H * fa, X[1] + H * fb]
    for it in range(12):
        Y = [y + (y - y.center()) * RI(QQ(1) / 5) + RI(-1, 1) * RI(2) ** (-200) for y in Y]  # inflate
        fa, fb = f(*Y)
        Yn = [X[0] + H * fa, X[1] + H * fb]
        if subset(Yn, Y):
            return Yn  # X + [0,h] f(Y) subset Y; Yn subset Y also encloses (Yn = X+[0,h]f(Y) contains the solution set)
        Y = [Y[i].union(Yn[i]) for i in range(2)]
    return None


def poly(c, h):
    v = RI(0)
    for x in reversed(c):
        v = v * h + x
    return v


def ex(F):  # exact interval from float
    return RI(QQ(float(F)))


def matvec(M, v):
    return [M[0][0] * v[0] + M[0][1] * v[1], M[1][0] * v[0] + M[1][1] * v[1]]


def matmul(M, N):
    return [[M[i][0] * N[0][j] + M[i][1] * N[1][j] for j in range(2)] for i in range(2)]


def inv2(M):
    d = M[0][0] * M[1][1] - M[0][1] * M[1][0]
    assert not d.contains_zero()
    return [[M[1][1] / d, -M[0][1] / d], [-M[1][0] / d, M[0][0] / d]]


def step(m, A, r, h):
    H = RI(h)
    X = [m[i] + (A[i][0] * r[0] + A[i][1] * r[1]) for i in range(2)]
    Y = apriori(X, RI(0, h))
    if Y is None:
        return None
    Am, Bm = series(m[0], m[1], P_ORD - 1)
    Tm = [poly(Am[:P_ORD], H), poly(Bm[:P_ORD], H)]
    Ay, By = series(Y[0], Y[1], P_ORD)
    Hp = H ** P_ORD
    Rm = [Ay[P_ORD] * Hp, By[P_ORD] * Hp]
    dA, dB = dseries(X[0], X[1], P_ORD)
    S = [[poly([c[1] for c in dA], H), poly([c[2] for c in dA], H)],
         [poly([c[1] for c in dB], H), poly([c[2] for c in dB], H)]]
    c = [Tm[i] + Rm[i] for i in range(2)]
    mn = [RI(ci.center()) for ci in c]
    SA = matmul(S, A)
    M = np.array([[float(SA[i][j].center()) for j in range(2)] for i in range(2)])
    cols = sorted(range(2), key=lambda j: -np.linalg.norm(M[:, j]))
    Qf, _ = np.linalg.qr(M[:, cols])
    An = [[ex(Qf[i][j]) for j in range(2)] for i in range(2)]
    Ai = inv2(An)
    rn = [x + y for x, y in zip(matvec(matmul(Ai, SA), r), matvec(Ai, [c[i] - mn[i] for i in range(2)]))]
    rem = max(float(abs(Rm[i]).upper()) for i in range(2))
    return mn, An, rn, rem


def main():
    out, times = sys.argv[1], [QQ(x) for x in sys.argv[2:]]
    m = [RI(0), RI(0)]
    A = [[RI(1), RI(0)], [RI(0), RI(1)]]
    r = [RI(0), RI(0)]
    t, h, res, nst, t0 = QQ(0), QQ(1) / 10 ** 7, [], 0, time.time()
    for T in times:
        while t < T:
            hh = min(h, T - t)
            s = step(m, A, r, hh)
            if s is None or s[3] > 1e-24:
                h = hh / 2
                continue
            m, A, r, _ = s
            t += hh
            nst += 1
            h = QQ(float(hh) * 1.15) if hh == h else h
        X = [m[i] + (A[i][0] * r[0] + A[i][1] * r[1]) for i in range(2)]
        y1 = 1 - X[0] - X[1]
        row = dict(t=str(T), steps=nst, wall=time.time() - t0,
                   box=[[str(z.lower().exact_rational()), str(z.upper().exact_rational())] for z in (y1, X[0], X[1])],
                   dec=[[float(z.lower()), float(z.upper())] for z in (y1, X[0], X[1])])
        res.append(row)
        print(json.dumps(row), flush=True)
        json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
