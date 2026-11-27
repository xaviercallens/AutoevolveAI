"""GE-2 library: enumeration, exclusion rules, witness search, exact certification.
Own code (no third-party census code). Generic in the number of species n (2 or 3)."""
from __future__ import annotations
import itertools
from fractions import Fraction as Fr
from typing import Optional
import numpy as np
import sympy as sp

Exp = tuple[int, ...]
Edge = tuple[Exp, Exp]


def complexes(n: int) -> list[Exp]:
    out: list[Exp] = []
    for i in range(n):
        e = [0] * n
        e[i] = 1
        out.append(tuple(e))
    for i in range(n):
        e = [0] * n
        e[i] = 2
        out.append(tuple(e))
    for i in range(n):
        for j in range(i + 1, n):
            e = [0] * n
            e[i] = e[j] = 1
            out.append(tuple(e))
    return out


def cname(c: Exp) -> str:
    nm = "XYZ"
    parts = []
    for i, e in enumerate(c):
        if e == 2:
            parts.append("2" + nm[i])
        elif e == 1:
            parts.append(nm[i])
    return "+".join(parts)


def edge_list(n: int) -> list[Edge]:
    C = complexes(n)
    return [(a, b) for a in C for b in C if a != b]


def perm_edge_map(n: int) -> list[list[int]]:
    """for each species permutation: index map on edges"""
    E = edge_list(n)
    idx = {e: i for i, e in enumerate(E)}
    maps = []
    for perm in itertools.permutations(range(n)):
        def pc(c: Exp) -> Exp:
            r = [0] * n
            for i in range(n):
                r[perm[i]] = c[i]
            return tuple(r)
        maps.append([idx[(pc(a), pc(b))] for a, b in E])
    return maps


def enumerate_orbits(n: int, mmax: int = 3) -> tuple[int, dict[tuple[int, ...], int], int]:
    """returns (labelled count, {canonical rep: orbit size}, burnside orbit count)"""
    E = edge_list(n)
    maps = perm_edge_map(n)
    labelled = 0
    orbits: dict[tuple[int, ...], int] = {}
    for m in range(mmax + 1):
        for s in itertools.combinations(range(len(E)), m):
            labelled += 1
            can = min(tuple(sorted(mp[e] for e in s)) for mp in maps)
            orbits[can] = orbits.get(can, 0) + 1
    # Burnside: number of m-subsets fixed by a permutation = sum over ... computed by direct count of fixed sets
    fixed_total = 0
    for mp in maps:
        # cycles of the induced permutation on edges
        seen = [False] * len(E)
        cyc: list[int] = []
        for i in range(len(E)):
            if not seen[i]:
                L, j = 0, i
                while not seen[j]:
                    seen[j] = True
                    j = mp[j]
                    L += 1
                cyc.append(L)
        # number of fixed subsets of size <= mmax = coefficient extraction of prod(1+x^L) up to x^mmax
        poly = [1] + [0] * mmax
        for L in cyc:
            new = poly[:]
            for d in range(mmax + 1 - L):
                new[d + L] += poly[d]
            poly = new
        fixed_total += sum(poly)
    assert fixed_total % len(maps) == 0
    return labelled, orbits, fixed_total // len(maps)


def bucket(edges: list[Edge], n: int) -> str:
    if n < 3:
        return "n2"
    supp: set[int] = set()
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for a, b in edges:
        sp_ = [i for i in range(n) if a[i] or b[i]]
        supp.update(sp_)
        for i in sp_[1:]:
            parent[find(i)] = find(sp_[0])
    if len(supp) <= 2:
        return "A"
    comps = {find(i) for i in supp}
    return "C" if len(comps) == 1 else "B"


def mono(a: Exp, x) -> object:
    r = 1
    for i, e in enumerate(a):
        if e:
            r = r * x[i] ** e
    return r


# ---------------- exclusion rules ----------------
def jac_rule(edges: list[Edge], n: int) -> bool:
    xs = sp.symbols(f"x0:{n}", positive=True)
    rh = sp.symbols(f"r0:{n}", positive=True)
    ks = sp.symbols(f"k0:{max(len(edges), 1)}", positive=True)
    f = [-rh[i] * xs[i] for i in range(n)]
    for e, (a, b) in enumerate(edges):
        m = mono(a, xs)
        for i in range(n):
            f[i] = f[i] + ks[e] * (b[i] - a[i]) * m
    J = sp.Matrix(f).jacobian(xs)
    d = sp.expand((-J).det(method="berkowitz"))
    P = sp.Poly(d, *xs, *rh, *ks[: len(edges)])
    return bool(all(c >= 0 for c in P.coeffs()) and not P.is_zero)


def sign_rule(edges: list[Edge], n: int) -> bool:
    """True iff every sign pattern of p-q is contradicted (=> at most one positive equilibrium)."""
    def dsign(a: Exp, s: tuple[int, ...]) -> Optional[int]:
        V = [s[i] for i in range(n) if a[i]]
        if all(v == 0 for v in V):
            return 0
        if all(v >= 0 for v in V):
            return 1
        if all(v <= 0 for v in V):
            return -1
        return None  # free
    for s in itertools.product((1, 0, -1), repeat=n):
        first = next((v for v in s if v), 0)
        if first != 1:
            continue
        contradicted = False
        for i in range(n):
            terms: list[Optional[int]] = []
            for a, b in edges:
                c = b[i] - a[i]
                if c == 0:
                    continue
                d = dsign(a, s)
                if d == 0:
                    continue
                terms.append(None if d is None else (1 if c * d > 0 else -1))
            if any(t is None for t in terms):
                continue
            if s[i] == 1 and 1 not in terms:
                contradicted = True
            elif s[i] == -1 and -1 not in terms:
                contradicted = True
            elif s[i] == 0 and terms and (all(t == 1 for t in terms) or all(t == -1 for t in terms)):
                contradicted = True
            if contradicted:
                break
        if not contradicted:
            return False
    return True


# ---------------- exact certification ----------------
def exact_field(edges: list[Edge], n: int, a, rho, k, x) -> list[Fr]:
    f = [a[i] - rho[i] * x[i] for i in range(n)]
    for e, (al, be) in enumerate(edges):
        m = Fr(1)
        for i in range(n):
            m *= x[i] ** al[i]
        for i in range(n):
            f[i] += k[e] * (be[i] - al[i]) * m
    return f


def exact_jac(edges: list[Edge], n: int, rho, k, x) -> list[list[Fr]]:
    J = [[Fr(0)] * n for _ in range(n)]
    for i in range(n):
        J[i][i] -= rho[i]
    for e, (al, be) in enumerate(edges):
        for j in range(n):
            if al[j] == 0:
                continue
            m = Fr(al[j])
            for i2 in range(n):
                m *= x[i2] ** (al[i2] - (1 if i2 == j else 0))
            for i in range(n):
                J[i][j] += k[e] * (be[i] - al[i]) * m
    return J


def hurwitz(J: list[list[Fr]]) -> dict:
    n = len(J)
    A = [[-J[i][j] for j in range(n)] for i in range(n)]
    if n == 2:
        a1 = A[0][0] + A[1][1]
        a2 = A[0][0] * A[1][1] - A[0][1] * A[1][0]
        return dict(a1=a1, a2=a2, stable=bool(a1 > 0 and a2 > 0))
    a1 = sum(A[i][i] for i in range(3))
    a2 = sum(A[i][i] * A[j][j] - A[i][j] * A[j][i] for i, j in ((0, 1), (0, 2), (1, 2)))
    a3 = (A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1]) - A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0])
          + A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0]))
    return dict(a1=a1, a2=a2, a3=a3, h=a1 * a2 - a3, stable=bool(a1 > 0 and a3 > 0 and a1 * a2 > a3))


def certify(edges: list[Edge], n: int, a, rho, k, p, q) -> dict:
    """Independent exact check. Returns dict with ok_multi, ok_bistable and data."""
    pos = all(v > 0 for v in list(a) + list(rho) + list(k) + list(p) + list(q))
    fp = exact_field(edges, n, a, rho, k, p)
    fq = exact_field(edges, n, a, rho, k, q)
    eq = all(v == 0 for v in fp) and all(v == 0 for v in fq)
    distinct = tuple(p) != tuple(q)
    hp = hurwitz(exact_jac(edges, n, rho, k, p))
    hq = hurwitz(exact_jac(edges, n, rho, k, q))
    multi = bool(pos and eq and distinct)
    return dict(ok_multi=multi, ok_bistable=bool(multi and hp["stable"] and hq["stable"]), hurwitz_p=hp, hurwitz_q=hq)


def rationalize_candidate(edges: list[Edge], n: int, p, q, v_float, den: int = 10 ** 5) -> Optional[tuple]:
    m = len(edges)
    P = [Fr(float(x)).limit_denominator(den) for x in p]
    Q = [Fr(float(x)).limit_denominator(den) for x in q]
    rows = []
    for i in range(n):
        row = [Fr(0)] * (n + m)
        row[i] = P[i] - Q[i]
        for e, (al, be) in enumerate(edges):
            dm = Fr(1)
            dq = Fr(1)
            for t in range(n):
                dm *= P[t] ** al[t]
                dq *= Q[t] ** al[t]
            row[n + e] = -(be[i] - al[i]) * (dm - dq)
        rows.append(row)
    M = sp.Matrix(rows)
    N = M.nullspace()
    if not N:
        return None
    Nm = np.array([[float(x) for x in vec] for vec in N]).T  # (n+m, d)
    c, *_ = np.linalg.lstsq(Nm, np.array(v_float, float), rcond=None)
    cr = [sp.Rational(Fr(float(x)).limit_denominator(10 ** 6)) for x in c]
    v = sum((cr[j] * N[j] for j in range(len(N))), sp.zeros(n + m, 1))
    v = [Fr(int(sp.numer(x)), int(sp.denom(x))) for x in v]
    rho, k = v[:n], v[n:]
    a = []
    for i in range(n):
        h = Fr(0)
        for e, (al, be) in enumerate(edges):
            mm = Fr(1)
            for t in range(n):
                mm *= P[t] ** al[t]
            h += k[e] * (be[i] - al[i]) * mm
        a.append(rho[i] * P[i] - h)
    return a, rho, k, P, Q


# ---------------- numerical search ----------------
def search(edges: list[Edge], n: int, rng: np.random.Generator, npairs: int, ncomb: int = 4,
           batch: int = 20000, need_stable: bool = True, stop_on_stable: bool = True) -> dict:
    """Returns dict(stable=list of candidates (p,q,v), multi=list of candidates). Candidate = float arrays."""
    m = len(edges)
    S = np.array([[b[i] - a[i] for i in range(n)] for a, b in edges], float)  # (m,n)
    A = np.array([a for a, _ in edges], float)  # (m,n)
    stable: list = []
    multi: list = []
    done = 0
    zr = [i for i in range(n) if not np.any(S[:, i])] if m else []  # species never changed by internal reactions: p_i=q_i forced
    nz = len(zr)
    while done < npairs:
        B = min(batch, npairs - done)
        done += B
        P = np.exp(rng.uniform(np.log(1e-2), np.log(1e2), (B, n)))
        Q = np.exp(rng.uniform(np.log(1e-2), np.log(1e2), (B, n)))
        h = B // 2
        Q[:h] = P[:h] * np.exp(rng.normal(0, 0.5, (h, n)))
        for i in zr:
            Q[:, i] = P[:, i]
        PA = np.prod(P[:, None, :] ** A[None], axis=2)  # (B,m)
        QA = np.prod(Q[:, None, :] ** A[None], axis=2)
        D = PA - QA
        M = np.zeros((B, n, n + m))
        for i in range(n):
            M[:, i, i] = P[:, i] - Q[:, i]
        M[:, :, n:] = -S.T[None] * D[:, None, :]
        _, _, Vh = np.linalg.svd(M)
        Nb = Vh[:, n - nz:, :]  # kernel basis (rank n-nz)
        C = rng.normal(size=(B, ncomb, m + nz))
        V = np.einsum("bcm,bmk->bck", C, Nb)
        sgn = np.sign(V[:, :, :1])
        V = V * sgn
        okpos = np.all(V > 1e-12 * np.abs(V).max(axis=2, keepdims=True), axis=2)
        rho = V[:, :, :n]
        k = V[:, :, n:]
        Hp = np.einsum("bcm,mi,bm->bci", k, S, PA)
        a = rho * P[:, None, :] - Hp
        ok = okpos & np.all(a > 1e-9 * np.abs(V).max(axis=2, keepdims=True), axis=2)
        bi, ci = np.nonzero(ok)
        for b, c in zip(bi, ci):
            v = V[b, c]
            cand = (P[b].copy(), Q[b].copy(), v.copy())
            if len(multi) < 20:
                multi.append(cand)
            r = v[:n]
            kk = v[n:]
            sc = v.max()
            st = True
            marg = 0.0
            for X in (P[b], Q[b]):
                J = -np.diag(r)
                for e in range(m):
                    dm = np.array([A[e, j] * np.prod(X ** A[e]) / X[j] if A[e, j] else 0.0 for j in range(n)])
                    J = J + kk[e] * np.outer(S[e], dm)
                mx = np.linalg.eigvals(J).real.max()
                marg = max(marg, mx / sc)
                if mx >= -1e-6 * sc:
                    st = False
                    break
            if st:
                stable.append((P[b].copy(), Q[b].copy(), v.copy(), marg))
        if stop_on_stable and len(stable) >= 3:
            break
        if not need_stable and multi:
            break
    return dict(stable=stable, multi=multi, pairs=done)


def find_witness(edges: list[Edge], n: int, cands: list, kind: str) -> Optional[dict]:
    """try to rationalise candidates; kind 'stable' or 'multi'"""
    cs = sorted(cands, key=(lambda c: c[3]) if kind == "stable" else (lambda c: 0))[:12]
    for cand in cs:
        p, q, v = cand[0], cand[1], cand[2]
        for den in (10 ** 3, 10 ** 5):
            res = rationalize_candidate(edges, n, p, q, v, den)
            if res is None:
                continue
            a, rho, k, P, Q = res
            cert = certify(edges, n, a, rho, k, P, Q)
            if (kind == "stable" and cert["ok_bistable"]) or (kind == "multi" and cert["ok_multi"]):
                return dict(a=a, rho=rho, k=k, p=P, q=Q, cert=cert)
    return None
