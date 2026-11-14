#!/usr/bin/env python3
"""canon_count.py -- count completions of cb_search (-comp file) up to colour-preserving isomorphism.

Each completion line is `v b0,b1,b2 b0,b1,b2 ...`. We build the Levi graph (points 0..v-1, blocks v..2v-1),
write graph6, and canonically label with nauty-labelg -f<a^v b^v> (points and blocks kept in their classes).
Also checks every completion is a linear, 3-regular, connected configuration with v blocks.
usage: canon_count.py COMPFILE OUTJSON [--g6dir DIR]
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict


def graph6(n: int, edges: list[tuple[int, int]]) -> str:
    adj = set()
    for a, b in edges:
        adj.add((min(a, b), max(a, b)))
    bits: list[int] = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (i, j) in adj else 0)
    while len(bits) % 6:
        bits.append(0)
    if n > 62:
        raise ValueError("n too large for short graph6 header")
    out = [chr(63 + n)]
    for k in range(0, len(bits), 6):
        val = 0
        for t in bits[k:k + 6]:
            val = (val << 1) | t
        out.append(chr(63 + val))
    return "".join(out)


def check_config(v: int, blocks: list[tuple[int, int, int]]) -> None:
    if len(blocks) != v:
        raise ValueError("block count != v")
    deg = [0] * v
    pairs = set()
    for b in blocks:
        if len(set(b)) != 3:
            raise ValueError("degenerate block")
        for x in b:
            deg[x] += 1
        for i in range(3):
            for j in range(i + 1, 3):
                pr = (min(b[i], b[j]), max(b[i], b[j]))
                if pr in pairs:
                    raise ValueError("not linear")
                pairs.add(pr)
    if any(d != 3 for d in deg):
        raise ValueError("not 3-regular")
    seen = {0}
    stack = [0]
    while stack:
        x = stack.pop()
        for b in blocks:
            if x in b:
                for y in b:
                    if y not in seen:
                        seen.add(y)
                        stack.append(y)
    if len(seen) != v:
        raise ValueError("not connected")


def main() -> int:
    comp, outj = sys.argv[1], sys.argv[2]
    g6dir = sys.argv[sys.argv.index("--g6dir") + 1] if "--g6dir" in sys.argv else None
    byv: dict[int, list[str]] = defaultdict(list)
    with open(comp) as fh:
        for line in fh:
            t = line.split()
            v = int(t[0])
            blocks = [tuple(int(a) for a in s.split(",")) for s in t[1:]]
            check_config(v, blocks)
            edges = [(x, v + k) for k, b in enumerate(blocks) for x in b]
            byv[v].append(graph6(2 * v, edges))
    res: dict[str, dict[str, int]] = {}
    for v in sorted(byv):
        inp = "\n".join(byv[v]) + "\n"
        part = "a" * v + "b" * v
        cp = subprocess.run(["nauty-labelg", "-q", "-f" + part], input=inp, capture_output=True, text=True, check=True)
        canon = sorted(set(cp.stdout.split()))
        res[str(v)] = {"labelled_leaves": len(byv[v]), "canonical_classes": len(canon)}
        if g6dir:
            with open(f"{g6dir}/canon_v{v}.g6", "w") as fh:
                fh.write("\n".join(canon) + "\n")
    with open(outj, "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
