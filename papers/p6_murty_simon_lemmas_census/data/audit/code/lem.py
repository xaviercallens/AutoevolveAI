"""Auditor's own maximal-matching enumerator and Lemma 1.2 / 1.3 test (independent of producer code).

Usage: python3 -I lem.py <g6 file>...   prints a JSON summary per n.
Enumeration: branch on the lowest undecided vertex (leave unmatched, or match to an undecided
neighbour); every matching is produced exactly once; keep those with no edge between two
unmatched vertices (maximal w.r.t. inclusion).
"""
import json
import sys
from collections import defaultdict
from itertools import combinations


def parse_g6(s: str) -> tuple[int, list[int]]:
    b = s.strip().encode()
    n = b[0] - 63
    adj = [0] * n
    k = 0
    for j in range(1, n):
        for i in range(j):
            byte = b[1 + k // 6] - 63
            if (byte >> (5 - k % 6)) & 1:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            k += 1
    return n, adj


def matchings(n: int, adj: list[int]) -> list[int]:
    """Return sizes of all maximal matchings."""
    out: list[int] = []

    def rec(undecided: int, unmatched: int, size: int) -> None:
        if undecided == 0:
            # maximal iff no edge inside unmatched set
            u = unmatched
            while u:
                v = (u & -u).bit_length() - 1
                if adj[v] & unmatched:
                    return
                u &= u - 1
            out.append(size)
            return
        v = (undecided & -undecided).bit_length() - 1
        rest = undecided & ~(1 << v)
        rec(rest, unmatched | (1 << v), size)
        nb = adj[v] & rest
        while nb:
            w = (nb & -nb).bit_length() - 1
            rec(rest & ~(1 << w), unmatched, size + 1)
            nb &= nb - 1

    rec((1 << n) - 1, 0, 0)
    return out


def has_triangle(n: int, adj: list[int]) -> bool:
    return any(adj[i] >> j & 1 and adj[i] & adj[j] for i in range(n) for j in range(i + 1, n))


def is_balanced_complete_bipartite(n: int, adj: list[int]) -> bool:
    # complement must be disjoint union of two cliques of sizes ceil(n/2), floor(n/2)
    full = (1 << n) - 1
    comp = [(~adj[i]) & full & ~(1 << i) for i in range(n)]
    a = comp[0] | 1
    sizes = sorted([bin(a).count("1"), n - bin(a).count("1")])
    if sizes != [n // 2, n - n // 2]:
        return False
    return all(adj[i] == (full & ~a if a >> i & 1 else a) for i in range(n))


def critical_nonedges(n: int, adj: list[int]) -> int:
    return sum(1 for i, j in combinations(range(n), 2) if not adj[i] >> j & 1 and bin(adj[i] & adj[j]).count("1") == 1)


def main() -> None:
    stats: dict[int, dict] = defaultdict(lambda: defaultdict(int))
    for path in sys.argv[1:]:
        for line in open(path):
            if not line.strip():
                continue
            n, adj = parse_g6(line)
            st = stats[n]
            e = sum(bin(x).count("1") for x in adj) // 2
            f = n * (n - 1) // 2 - e
            sizes = matchings(n, adj)
            st["graphs"] += 1
            st["max_matchings"] += len(sizes)
            st["max_edges"] = max(st["max_edges"], e)
            viol = sum(1 for m in sizes if e - m > f)
            st["L12_violations"] += viol
            eq_all = all(e - m == f for m in sizes)
            tri = has_triangle(n, adj)
            st["with_triangle"] += tri
            if eq_all:
                st["eq_all_M"] += 1
                st["eq_all_M_with_triangle"] += tri
                st["eq_all_M_is_Kab"] += is_balanced_complete_bipartite(n, adj)
                st["eq_all_M_critical_nonedges"] += critical_nonedges(n, adj)
            if any(e - m == f for m in sizes):
                st["eq_some_M"] += 1
            if e == n * n // 4:
                st["extremal"] += 1
                st["extremal_Kab"] += is_balanced_complete_bipartite(n, adj)
            # perturbed: strict inequality must fail somewhere
            st["strict_fail"] += any(e - m >= f for m in sizes)
            slack = f - (e - min(sizes))
            st["min_slack"] = slack if st["graphs"] == 1 else min(st["min_slack"], slack)
            st["tri_min_slack"] = (
                min(st.get("tri_min_slack", 10**9), slack) if tri else st.get("tri_min_slack", 10**9)
            )
    print(json.dumps({n: dict(v) for n, v in sorted(stats.items())}, indent=1))


if __name__ == "__main__":
    main()
