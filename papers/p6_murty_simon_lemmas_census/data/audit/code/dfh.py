"""Check Dailly-Foucaud-Hansberg (arXiv 1812.08420) computer-search facts against a D2C list.

Usage: python3 -I dfh.py <canonical d2c g6 file> <canonical C5+ g6 file> ; or `gen` to emit C5+ graphs (g6) for n=5..11.
Facts tested: (a) exactly 13 non-bipartite D2C graphs, n<=11, with floor((n-1)^2/4)+1 edges not in C5+, orders 7,8,9
only, 3 without a dominating edge; (b) the only non-bipartite D2C graph above that bound is H5 (n=6, 8 edges);
(c) max degree n-1 only for stars; (d) 10 non-bipartite D2C with a dominating edge at the bound, all n<=9.
"""
import sys
from collections import Counter


def parse_g6(s: str) -> tuple[int, list[int]]:
    b = s.strip().encode()
    n = b[0] - 63
    adj = [0] * n
    k = 0
    for j in range(1, n):
        for i in range(j):
            if ((b[1 + k // 6] - 63) >> (5 - k % 6)) & 1:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            k += 1
    return n, adj


def to_g6(n: int, edges: set[tuple[int, int]]) -> str:
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (i, j) in edges or (j, i) in edges else 0)
    while len(bits) % 6:
        bits.append(0)
    out = chr(n + 63)
    for t in range(0, len(bits), 6):
        v = 0
        for x in bits[t:t + 6]:
            v = 2 * v + x
        out += chr(v + 63)
    return out


def gen_c5plus() -> None:
    for n in range(5, 12):
        for b in sorted({(n - 3) // 2, (n - 2) // 2}):
            if b < 1:
                continue
            for a in range(1, n - 2 - b):
                c = n - 2 - b - a
                if c < 1:
                    continue
                parts = [a, b, c, 1, 1]
                idx = []
                s = 0
                for p in parts:
                    idx.append(list(range(s, s + p)))
                    s += p
                edges = {(u, v) for t in range(5) for u in idx[t] for v in idx[(t + 1) % 5]}
                print(to_g6(n, edges))


def bipartite(n: int, adj: list[int]) -> bool:
    col = [-1] * n
    for s in range(n):
        if col[s] >= 0:
            continue
        col[s] = 0
        st = [s]
        while st:
            x = st.pop()
            for y in range(n):
                if adj[x] >> y & 1:
                    if col[y] < 0:
                        col[y] = 1 - col[x]
                        st.append(y)
                    elif col[y] == col[x]:
                        return False
    return True


def dominating_edge(n: int, adj: list[int]) -> bool:
    full = (1 << n) - 1
    return any(adj[u] >> v & 1 and (adj[u] | adj[v]) == full for u in range(n) for v in range(u + 1, n))


def main() -> None:
    d2c = [l.strip() for l in open(sys.argv[1]) if l.strip()]
    c5p = {l.strip() for l in open(sys.argv[2]) if l.strip()}
    at_bound_notc5 = Counter()
    at_bound_notc5_nodom = 0
    at_bound_dom = Counter()
    above = []
    c5p_found = 0
    star_viol = 0
    for g in d2c:
        n, adj = parse_g6(g)
        e = sum(bin(x).count("1") for x in adj) // 2
        if g in c5p:
            c5p_found += 1
        if max(bin(x).count("1") for x in adj) == n - 1 and e != n - 1:
            star_viol += 1
        if bipartite(n, adj):
            continue
        bound = (n - 1) ** 2 // 4 + 1
        dom = dominating_edge(n, adj)
        if e > bound:
            above.append((n, e, g))
        if e == bound:
            if dom:
                at_bound_dom[n] += 1
            if g not in c5p:
                at_bound_notc5[n] += 1
                at_bound_notc5_nodom += not dom
    print("C5+ graphs generated:", len(c5p), "of which in D2C list:", c5p_found)
    print("non-bipartite at bound, not in C5+, per n:", dict(sorted(at_bound_notc5.items())), "total", sum(at_bound_notc5.values()))
    print("  of these without dominating edge:", at_bound_notc5_nodom)
    print("non-bipartite at bound with dominating edge, per n:", dict(sorted(at_bound_dom.items())), "total", sum(at_bound_dom.values()))
    print("non-bipartite above bound:", above)
    print("max-degree n-1 non-star D2C graphs:", star_viol)


if __name__ == "__main__":
    if sys.argv[1] == "gen":
        gen_c5plus()
    else:
        main()
