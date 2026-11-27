"""Shared helpers for the A1 continuation (L1 port of the remaining certificate stages).

Exact Python mirror of the certificate's IV arithmetic (core.hpp). It is UNTRUSTED: it only produces literals and
chunk boundaries for the Lean files. Every literal is recomputed by the Lean kernel, and every stage output is
compared with the C++ dump (dump2.txt).
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path

Q = 2**144
IV = tuple[int, int]

REPO = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
L1DIR = REPO / "formal_cert" / "Programmes" / "SandierSerfatyL1"
CONT = REPO / "results" / "proposal2" / "2026-10-26" / "A1-continuation"
DUMP2 = Path("/home/callensxavier_gmail_com/proposal2-2026-10-26/A1c/dump2/dump2.txt")
OLD_DUMP = Path("/home/callensxavier_gmail_com/proposal2-2026-10-26/A1/dump/dump.txt")


def fq(a: int) -> int:
    return a // Q


def cq(a: int) -> int:
    return -((-a) // Q)


def ofint(n: int) -> IV:
    return (n * Q, n * Q)


ZERO = ofint(0)
ONE = ofint(1)


def neg(a: IV) -> IV:
    return (-a[1], -a[0])


def add(a: IV, b: IV) -> IV:
    return (a[0] + b[0], a[1] + b[1])


def sub(a: IV, b: IV) -> IV:
    return add(a, neg(b))


def mul(a: IV, b: IV) -> IV:
    ps = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return (fq(min(ps)), cq(max(ps)))


def inv(a: IV) -> IV:
    if a[0] > 0:
        return ((Q * Q) // a[1], -((-(Q * Q)) // a[0]))
    if a[1] < 0:
        return neg(inv(neg(a)))
    raise ZeroDivisionError("interval div0")


def div(a: IV, b: IV) -> IV:
    return mul(a, inv(b))


def rat(n: int, d: int = 1) -> IV:
    assert d > 0
    return ((n * Q) // d, -((-(n * Q)) // d))


def pow_(x: IV, k: int) -> IV:
    if k < 0:
        return inv(pow_(x, -k))
    z = ONE
    while k:
        if k & 1:
            z = mul(z, x)
        k >>= 1
        if k:
            x = mul(x, x)
    return z


def lit(a: IV) -> str:
    return f"⟨{a[0]}, {a[1]}⟩"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_scalars(dump: Path) -> dict[str, IV]:
    out: dict[str, IV] = {}
    with dump.open() as fh:
        for line in fh:
            p = line.split()
            if len(p) == 3 and p[0][0].isalpha():
                try:
                    out[p[0]] = (int(p[1]), int(p[2]))
                except ValueError:
                    pass
    return out


def isqrt(n: int) -> int:
    return math.isqrt(n)
