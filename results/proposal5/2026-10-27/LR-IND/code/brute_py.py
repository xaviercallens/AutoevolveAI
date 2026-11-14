#!/usr/bin/env python3
"""LR-IND third check: a naive Python implementation (no hitting-set search, no pruning) of the same sieve,
written separately from lr_sieve.c, compared on small (k, p) at every level by class count and class hash.

Phase 1 here enumerates EVERY sorted tuple 1 = v1 <= v2 <= ... <= vk <= (p-1)/2 and tests all times directly.
"""
from __future__ import annotations

import itertools
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MASK = (1 << 64) - 1


def good(k: int, d: int, n: int) -> bool:
    return (k + 1) * d >= n


def has_witness(k: int, u: tuple[int, ...], n: int) -> bool:
    for a in range(1, n // 2 + 1):
        ok = True
        for x in u:
            r = a * x % n
            if not good(k, min(r, n - r), n):
                ok = False
                break
        if ok:
            return True
    return False


def gcd_proper(u: tuple[int, ...], level: int) -> bool:
    qs = [q for q in range(2, level + 1) if level % q == 0 and all(q % s for s in range(2, q))]
    return any(sum(1 for x in u if x % q) <= 1 for q in qs)


def canonical(t: tuple[int, ...], p: int) -> tuple[int, ...]:
    best = None
    for x in set(v % p for v in t):
        iv = pow(x, -1, p)
        cur = tuple(sorted(min(iv * v % p, p - iv * v % p) for v in t))
        if best is None or cur < best:
            best = cur
    assert best is not None
    return best


def class_hash(classes: set[tuple[int, ...]]) -> tuple[int, str]:
    h = 1469598103934665603
    for t in sorted(classes):
        for v in t:
            h ^= v
            h = (h * 1099511628211) & MASK
    return len(classes), f"{h:016x}"


def run(k: int, p: int, plan: list[str]) -> list[tuple[int, str]]:
    hh = (p - 1) // 2
    s1 = []
    for rest in itertools.combinations_with_replacement(range(1, hh + 1), k - 1):
        t = (1,) + rest
        if not has_witness(k, t, p):
            s1.append(t)
    sig = [class_hash({canonical(t, p) for t in s1})]
    cur, level = s1, 1
    for op in plan:
        if op == "/":
            cur = sorted({canonical(t, p) for t in cur})
            level = 1
        else:
            c = int(op)
            n0 = level * p
            level *= c
            n1 = level * p
            nxt = []
            for t in cur:
                for js in itertools.product(range(c), repeat=k):
                    u = tuple(t[i] + js[i] * n0 for i in range(k))
                    if not has_witness(k, u, n1) and not gcd_proper(u, level):
                        nxt.append(u)
            cur = nxt
        sig.append(class_hash({canonical(t, p) for t in cur}))
    return sig


def c_sig(k: int, p: int, plan: str) -> list[tuple[int, str]]:
    out = subprocess.run([str(HERE / "lr_sieve"), str(k), str(p), plan, "0", "1", "1"], capture_output=True,
                         text=True, check=True).stdout
    d = json.loads(out)
    return [(d["S1"]["classes"], d["S1"]["class_hash"])] + [(s["classes_mod_p"], s["class_hash"]) for s in d["steps"]]


CASES = [(4, p, "2,2,/,5") for p in (7, 11, 13, 17, 19, 23)] + \
        [(5, p, "2,3") for p in (7, 11, 13, 17, 19, 23, 29, 31)] + \
        [(6, p, "7") for p in (11, 13)] + \
        [(7, p, "2,2,2") for p in (11, 13, 17, 19, 23, 29, 31, 41)]


def main() -> int:
    bad = 0
    rows = []
    for k, p, plan in CASES:
        py = run(k, p, plan.split(","))
        cc = c_sig(k, p, plan)
        ok = [tuple(x) for x in py] == [tuple(x) for x in cc]
        bad += not ok
        rows.append({"k": k, "p": p, "plan": plan, "python": py, "c": cc, "agree": ok})
        print(k, p, plan, "AGREE" if ok else "DISAGREE", py, flush=True)
    (HERE.parent / "logs" / "brute_py.json").write_text(json.dumps(rows, indent=1) + "\n")
    print("disagreements", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
