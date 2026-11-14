"""Exact death-Birth (dB) weak-selection and fixation tools for unweighted graphs (C1, Proposal 4).

Criterion source: Allen et al., arXiv 1906.01036v1 (PLoS Comput Biol 16(1): e1007529, 2020):
  eq. (5)  tau_ij = 0 (i = j);  tau_ij = 1 + 1/2 sum_k (p_ik tau_jk + p_jk tau_ik)  (i != j)
  eq. (6)  tau_i = 1 + sum_j p_ij tau_ij
  eq. (9)  N_eff = sum_i pi_i tau_i,  pi_i = k_i / sum_j k_j,  p_ij = w_ij / w_i
  eq. (8)/(45)  rho_G(1+delta) = 1/N + delta (N_eff - 2)/(2N) + O(delta^2)
  Definition p. 8: amplifier of weak selection iff N_eff > N.
Hypotheses: connected undirected graph, no self-loops, dB updating, uniform initialisation, mutant fitness 1+delta.

Everything here uses Python Fractions (exact rationals). Nothing is sampled.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from typing import Callable

Adj = list[list[int]]


def parse_graph6(line: str) -> Adj:
    """Decode a graph6 string (N <= 62) into an adjacency list."""
    s = line.strip()
    data = [ord(c) - 63 for c in s]
    n = data[0]
    bits: list[int] = []
    for d in data[1:]:
        for b in range(5, -1, -1):
            bits.append((d >> b) & 1)
    adj: Adj = [[] for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i].append(j)
                adj[j].append(i)
            idx += 1
    return adj


def to_graph6(adj: Adj) -> str:
    """Encode an adjacency list as graph6 (N <= 62)."""
    n = len(adj)
    sets = [set(a) for a in adj]
    bits: list[int] = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if j in sets[i] else 0)
    while len(bits) % 6:
        bits.append(0)
    out = [chr(n + 63)]
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = (v << 1) | b
        out.append(chr(v + 63))
    return "".join(out)


def edges_of(adj: Adj) -> list[tuple[int, int]]:
    return [(i, j) for i in range(len(adj)) for j in adj[i] if i < j]


def is_connected(adj: Adj) -> bool:
    n = len(adj)
    seen = {0}
    stack = [0]
    while stack:
        v = stack.pop()
        for u in adj[v]:
            if u not in seen:
                seen.add(u)
                stack.append(u)
    return len(seen) == n


def solve_fraction(rows: list[dict[int, Fraction]], rhs: list[Fraction]) -> list[Fraction]:
    """Exact Gauss-Jordan elimination on a sparse square system (dict rows). Raises on singular."""
    n = len(rows)
    a = [dict(r) for r in rows]
    b = list(rhs)
    for col in range(n):
        piv = None
        for r in range(col, n):
            if a[r].get(col, 0) != 0:
                piv = r
                break
        if piv is None:
            raise ZeroDivisionError("singular system")
        if piv != col:
            a[col], a[piv] = a[piv], a[col]
            b[col], b[piv] = b[piv], b[col]
        pr = a[col]
        pv = pr[col]
        if pv != 1:
            inv = 1 / pv
            for k in list(pr):
                pr[k] = pr[k] * inv
            b[col] = b[col] * inv
        for r in range(n):
            if r == col:
                continue
            f = a[r].get(col, 0)
            if f == 0:
                continue
            ar = a[r]
            for k, v in pr.items():
                nv = ar.get(k, 0) - f * v
                if nv == 0:
                    ar.pop(k, None)
                else:
                    ar[k] = nv
            b[r] = b[r] - f * b[col]
    return b


def coalescence_times(adj: Adj, step: str = "allen") -> dict[tuple[int, int], Fraction]:
    """Solve Allen eq. (5) exactly. step='allen' uses p_ij = 1/k_i; step='transposed' (NEGATIVE CONTROL) uses 1/k_j."""
    n = len(adj)
    deg = [len(a) for a in adj]
    pairs = list(combinations(range(n), 2))
    index = {p: t for t, p in enumerate(pairs)}

    def pid(i: int, j: int) -> int | None:
        if i == j:
            return None
        return index[(i, j) if i < j else (j, i)]

    def p(i: int, k: int) -> Fraction:
        return Fraction(1, deg[i]) if step == "allen" else Fraction(1, deg[k])

    rows: list[dict[int, Fraction]] = []
    rhs: list[Fraction] = []
    for (i, j) in pairs:
        row: dict[int, Fraction] = {index[(i, j)]: Fraction(1)}
        for k in adj[i]:  # (1/2) p_ik tau_jk
            q = pid(j, k)
            if q is not None:
                row[q] = row.get(q, 0) - p(i, k) / 2
        for k in adj[j]:  # (1/2) p_jk tau_ik
            q = pid(i, k)
            if q is not None:
                row[q] = row.get(q, 0) - p(j, k) / 2
        rows.append({k: v for k, v in row.items() if v != 0})
        rhs.append(Fraction(1))
    sol = solve_fraction(rows, rhs)
    return {pairs[t]: sol[t] for t in range(len(pairs))}


def tau_pair(tau: dict[tuple[int, int], Fraction], i: int, j: int) -> Fraction:
    if i == j:
        return Fraction(0)
    return tau[(i, j) if i < j else (j, i)]


def remeeting_times(adj: Adj, tau: dict[tuple[int, int], Fraction]) -> list[Fraction]:
    """Allen eq. (6)."""
    return [1 + sum((Fraction(1, len(adj[i])) * tau_pair(tau, i, j) for j in adj[i]), Fraction(0)) for i in range(len(adj))]


def neff_exact(adj: Adj, step: str = "allen") -> tuple[Fraction, list[Fraction], dict[tuple[int, int], Fraction]]:
    """Allen eq. (9): N_eff = sum_i pi_i tau_i, pi_i = k_i / sum k. Returns (N_eff, tau_i list, tau_ij)."""
    tau = coalescence_times(adj, step)
    ti = remeeting_times(adj, tau)
    two_m = sum(len(a) for a in adj)
    neff = sum((Fraction(len(adj[i]), two_m) * ti[i] for i in range(len(adj))), Fraction(0))
    return neff, ti, tau


def neff_edge_identity(adj: Adj, tau: dict[tuple[int, int], Fraction]) -> Fraction:
    """Identity derived here: pi_i p_ij = 1/(2m), so N_eff = 1 + (1/m) sum_{ij in E} tau_ij."""
    e = edges_of(adj)
    return 1 + sum((tau[x] for x in e), Fraction(0)) / len(e)


def antal_neff(adj: Adj) -> Fraction:
    """NEGATIVE CONTROL: Antal et al. approximation N mu1^2/mu2 (Allen eq. 23), always <= N."""
    n = len(adj)
    mu1 = Fraction(sum(len(a) for a in adj), n)
    mu2 = Fraction(sum(len(a) ** 2 for a in adj), n)
    return n * mu1 * mu1 / mu2


# ---------------------------------------------------------------- exact 2^N - 2 state fixation chains

def _transitions_db(adj: Adj, state: int, r: Fraction) -> list[tuple[int, Fraction]]:
    """dB: uniform death of v, neighbour reproduces with prob prop. to fitness (mutant r, resident 1)."""
    n = len(adj)
    out: list[tuple[int, Fraction]] = []
    for v in range(n):
        m = sum(1 for u in adj[v] if (state >> u) & 1)
        k = len(adj[v])
        pm = (r * m) / (r * m + (k - m))
        if pm != 0:
            out.append((state | (1 << v), pm / n))
        if pm != 1:
            out.append((state & ~(1 << v), (1 - pm) / n))
    return out


def _transitions_bd(adj: Adj, state: int, r: Fraction) -> list[tuple[int, Fraction]]:
    """Bd: u reproduces with prob prop. to fitness, offspring replaces a uniform neighbour."""
    n = len(adj)
    mcount = bin(state).count("1")
    tot = r * mcount + (n - mcount)
    out: list[tuple[int, Fraction]] = []
    for u in range(n):
        mu = (state >> u) & 1
        fu = r if mu else Fraction(1)
        for v in adj[u]:
            w = fu / tot / len(adj[u])
            ns = state | (1 << v) if mu else state & ~(1 << v)
            out.append((ns, w))
    return out


def fixation_exact(adj: Adj, r: Fraction, rule: str = "dB") -> Fraction:
    """Exact rho_G(r), uniform initialisation, by solving (I - Q) x = R over the 2^N - 2 transient states."""
    n = len(adj)
    full = (1 << n) - 1
    states = list(range(1, full))
    idx = {s: t for t, s in enumerate(states)}
    trans: Callable[[Adj, int, Fraction], list[tuple[int, Fraction]]] = _transitions_db if rule == "dB" else _transitions_bd
    rows: list[dict[int, Fraction]] = []
    rhs: list[Fraction] = []
    for s in states:
        row: dict[int, Fraction] = {idx[s]: Fraction(1)}
        b = Fraction(0)
        for ns, w in trans(adj, s, r):
            if ns == full:
                b += w
            elif ns == 0:
                continue
            else:
                row[idx[ns]] = row.get(idx[ns], 0) - w
        rows.append({k: v for k, v in row.items() if v != 0})
        rhs.append(b)
    x = solve_fraction(rows, rhs)
    return sum((x[idx[1 << v]] for v in range(n)), Fraction(0)) / n


def fixation_slope_at_neutral(adj: Adj) -> Fraction:
    """Independent check of Allen eq. (8): d rho_G / dr at r = 1 from the exact dB chain.
    x(r) solves (I - Q(r)) x = R(r); differentiate: (I - Q0) x' = R' + Q' x0."""
    n = len(adj)
    full = (1 << n) - 1
    states = list(range(1, full))
    idx = {s: t for t, s in enumerate(states)}
    one = Fraction(1)
    # neutral solution
    rows0: list[dict[int, Fraction]] = []
    rhs0: list[Fraction] = []
    dq: list[list[tuple[int, Fraction]]] = []
    dr: list[Fraction] = []
    for s in states:
        row: dict[int, Fraction] = {idx[s]: one}
        b = Fraction(0)
        dqs: list[tuple[int, Fraction]] = []
        drs = Fraction(0)
        for v in range(n):
            m = sum(1 for u in adj[v] if (s >> u) & 1)
            k = len(adj[v])
            pm0 = Fraction(m, k)
            dpm = Fraction(m * (k - m), k * k)  # d/dr [r m/(r m + k - m)] at r = 1
            up = s | (1 << v)
            dn = s & ~(1 << v)
            for ns, w0, dw in ((up, pm0 / n, dpm / n), (dn, (1 - pm0) / n, -dpm / n)):
                if ns == full:
                    b += w0
                    drs += dw
                elif ns == 0:
                    continue
                else:
                    row[idx[ns]] = row.get(idx[ns], 0) - w0
                    if dw != 0:
                        dqs.append((idx[ns], dw))
        rows0.append({k2: v2 for k2, v2 in row.items() if v2 != 0})
        rhs0.append(b)
        dq.append(dqs)
        dr.append(drs)
    x0 = solve_fraction(rows0, rhs0)
    rhs1 = [dr[t] + sum((w * x0[c] for c, w in dq[t]), Fraction(0)) for t in range(len(states))]
    x1 = solve_fraction(rows0, rhs1)
    return sum((x1[idx[1 << v]] for v in range(n)), Fraction(0)) / n


# ---------------------------------------------------------------- closed forms (positive controls)

def rho_complete_db(n: int, r: Fraction) -> Fraction:
    """Allen eq. (1) / Hindersin eq. (5): (N-1)/N (1 - 1/r)/(1 - r^{-(N-1)})."""
    if r == 1:
        return Fraction(1, n)
    return Fraction(n - 1, n) * (1 - 1 / r) / (1 - r ** (-(n - 1)))


def rho_complete_bd(n: int, r: Fraction) -> Fraction:
    if r == 1:
        return Fraction(1, n)
    return (1 - 1 / r) / (1 - r ** (-n))


def rho_cycle_db_kaveh(n: int, r: Fraction) -> Fraction:
    """Kaveh et al. eq. (20) at d=1 / Hindersin SI eq. (18) / Richter eq. (12): 2(r-1)/(3r-1+(r-3) r^{2-N})."""
    return 2 * (r - 1) / (3 * r - 1 + (r - 3) * r ** (2 - n))


def rho_cycle_db_allen_eq3_as_printed(n: int, r: Fraction) -> Fraction:
    """Allen eq. (3) as printed in arXiv v1: 2(r-1)/(3r-1+r^{-(N-1)}-3r^{-(N-2)}) (suspected misprint)."""
    return 2 * (r - 1) / (3 * r - 1 + r ** (-(n - 1)) - 3 * r ** (-(n - 2)))


def rho_star_db(n_leaves: int, r: Fraction) -> Fraction:
    """Allen eq. (2): ((N-1) r + 1)/(N (r+1)) (1/N + r/(N + 2r - 2)), N = n + 1."""
    big = n_leaves + 1
    return ((big - 1) * r + 1) / (big * (r + 1)) * (Fraction(1, big) + r / (big + 2 * r - 2))


def graph_cycle(n: int) -> Adj:
    return [[(i - 1) % n, (i + 1) % n] for i in range(n)]


def graph_complete(n: int) -> Adj:
    return [[j for j in range(n) if j != i] for i in range(n)]


def graph_star(n_leaves: int) -> Adj:
    adj: Adj = [list(range(1, n_leaves + 1))]
    adj += [[0] for _ in range(n_leaves)]
    return adj


def remove_edge(adj: Adj, a: int, b: int) -> Adj:
    out = [list(x) for x in adj]
    out[a].remove(b)
    out[b].remove(a)
    return out
