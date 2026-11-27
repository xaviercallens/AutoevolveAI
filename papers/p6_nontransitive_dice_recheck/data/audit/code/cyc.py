"""Auditor: cycle enumeration (own DFS) + exact Fraction checks of paper's printed cycles."""
import re
import sys
import struct
import random
from fractions import Fraction
from collections import Counter

PAPER = "/home/callensxavier_gmail_com/dice6_thirdparty/paper_fulltext_alphaxiv.txt"


def load(path: str):
    b = open(path, "rb").read()
    N, n = struct.unpack_from("<ii", b, 0)
    p = 8
    tup = [tuple(b[p + i * n:p + (i + 1) * n]) for i in range(N)]
    p += N * n
    comp = list(struct.unpack_from("<%di" % N, b, p)); p += 4 * N
    off = list(struct.unpack_from("<%dq" % (N + 1), b, p)); p += 8 * (N + 1)
    E = off[N]
    adj = list(struct.unpack_from("<%di" % E, b, p))
    return n, tup, comp, off, adj


def beats(x, y) -> Fraction:
    n = len(x)
    return Fraction(sum(1 for a in x for b in y if a > b), n * n)


def target(n: int) -> Fraction:
    return Fraction(n * n // 2 + 1, n * n)


def is_uniform_min_cycle(cyc) -> tuple:
    n = len(cyc[0])
    ps = [beats(cyc[i], cyc[(i + 1) % len(cyc)]) for i in range(len(cyc))]
    ok = all(p == target(n) for p in ps) and len(set(cyc)) == len(cyc) and all(len(c) == n and min(c) >= 1 and max(c) <= n for c in cyc)
    return ok, ps


def all_simple_cycles(vs, succ):
    """Enumerate simple cycles within vertex set vs: each cycle rooted at its minimum vertex."""
    vs = sorted(vs)
    out = []
    for s in vs:
        allowed = {v for v in vs if v >= s}
        stack = [(s, iter([w for w in succ[s] if w in allowed]))]
        path = [s]; onp = {s}
        while stack:
            v, it = stack[-1]
            w = next(it, None)
            if w is None:
                stack.pop(); onp.discard(path.pop()); continue
            if w == s:
                out.append(list(path)); continue
            if w in onp:
                continue
            path.append(w); onp.add(w)
            stack.append((w, iter([u for u in succ[w] if u in allowed])))
    return out


def parse_tuples(segment: str, n: int):
    nums = [int(t) for t in re.findall(r"\d+", segment)]
    assert len(nums) % n == 0, (len(nums), n)
    return [tuple(nums[i:i + n]) for i in range(0, len(nums), n)]


def main() -> None:
    txt = open(PAPER, encoding="utf-8").read()
    flat = re.sub(r"\s+", " ", txt)
    # n=6 enumeration
    n, tup, comp, off, adj = load("/tmp/diceaudit/g6.bin")
    succ = [adj[off[i]:off[i + 1]] for i in range(len(tup))]
    cc = Counter(comp)
    nontriv = [c for c, k in cc.items() if k > 1]
    total = Counter()
    sixes = []
    for c in nontriv:
        vs = [v for v in range(len(tup)) if comp[v] == c]
        print("SCC", c, "labels(1-based lex)", [v + 1 for v in vs], [tup[v] for v in vs])
        cyc = all_simple_cycles(vs, succ)
        lens = Counter(len(x) for x in cyc)
        print("  cycles by length", dict(lens))
        total.update(lens)
        for x in cyc:
            if len(x) == 6:
                sixes.append([tup[v] for v in x])
    print("n=6 total cycles by length", dict(total))
    for s in sixes:
        print("six-cycle", s, is_uniform_min_cycle(s))
    # f maps cycle 1 to reversed cycle 2
    f = lambda x: tuple(7 - a for a in reversed(x))
    fs = [f(d) for d in sixes[0]][::-1]
    rots = [fs[i:] + fs[:i] for i in range(6)]
    print("f(cycle A) reversed is a rotation of cycle B:", sixes[1] in rots)
    # paper's n=6 cycles from Appendix E
    pc1 = [(1,1,2,5,5,5),(1,3,4,4,4,4),(2,2,2,3,6,6),(1,1,2,5,5,6),(1,3,3,4,4,4),(2,2,3,3,3,6)]
    pc2 = [(1,1,4,5,5,5),(3,3,3,3,4,6),(2,2,2,5,6,6),(1,4,4,4,5,5),(3,3,3,4,4,6),(1,2,2,5,6,6)]
    print("paper n=6 cycle1", is_uniform_min_cycle(pc1)); print("paper n=6 cycle2", is_uniform_min_cycle(pc2))
    # Brute-force n=6 global check: no 7-cycle anywhere / all cycles inside SCCs (DFS limited length 7 from every vertex)
    # printed cycles n=7,8,9,10
    segs = {
        7: (r"non-transitive cycle of length 14 ", r" Case for n = 8"),
        8: (r"directed cycle of length 29\. ", r" Case for n = 9"),
        9: (r"non-transitive cycle of length 10 ", r" 10 TERRY EASLICK"),
        10: (r"directed cycle of length 110 found in that SCC\. ", r" Continuing onto"),
    }
    for m, (a, b) in segs.items():
        i = flat.index(re.sub(r"\\", "", a)) + len(re.sub(r"\\", "", a))
        j = flat.index(b, i)
        seg = flat[i:j]
        seg = re.sub(r"COMPUTER-ASSISTED RESULTS FOR n-SIDED NON-TRANSITIVE DICE TAKING FACE VALUES IN \[n\] \d+", " ", seg)
        seg = re.sub(r"\d+ TERRY EASLICK", " ", seg)
        cyc = parse_tuples(seg, m)
        ok, ps = is_uniform_min_cycle(cyc)
        bad = [k for k, p in enumerate(ps) if p != target(m)]
        print(f"paper n={m}: printed {len(cyc)} dice, distinct {len(set(cyc))}, valid-in-printed-order={ok}, bad edges at {bad[:10]}, target={target(m)}")
    # own n=7 search
    n, tup, comp, off, adj = load("/tmp/diceaudit/g7.bin")
    succ = [adj[off[i]:off[i + 1]] for i in range(len(tup))]
    big = Counter(comp).most_common(1)[0][0]
    insc = [comp[v] == big for v in range(len(tup))]
    rng = random.Random(2026)
    found = {}
    # random-walk cycle closing: walk inside big SCC, record first repeated vertex loops
    for trial in range(200000):
        v = rng.choice([u for u in range(len(tup)) if insc[u]]) if trial == 0 or rng.random() < 0.01 else v
        path = [v]; pos = {v: 0}
        for _ in range(60):
            nb = [w for w in succ[path[-1]] if insc[w]]
            w = rng.choice(nb)
            if w in pos:
                cyc = path[pos[w]:]
                L = len(cyc)
                if L not in found:
                    c = [tup[u] for u in cyc]
                    if is_uniform_min_cycle(c)[0]:
                        found[L] = c
                break
            pos[w] = len(path); path.append(w)
        v = path[-1]
        if all(k in found for k in (7, 8, 14)) and len(found) > 25:
            break
    print("n=7 own random-walk cycle lengths found:", sorted(found))
    for L in (3, 7, 8, 14):
        if L in found:
            print("  len", L, found[L])


if __name__ == "__main__":
    main()
