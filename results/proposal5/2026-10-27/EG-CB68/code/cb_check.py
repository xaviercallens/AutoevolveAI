#!/usr/bin/env python3
"""cb_check.py -- streaming witness-certificate checker for EG-CB68 (separate program from cb_search.c).

It does NOT search for cycles. It re-derives the restricted-growth proposal schedule from the definition
(Tranquilli 2608.02675 v1, Section 3.1), and for every proposal reads one record:
  S q r          structural rejection: q and r are introduced and already share a block      (checked directly)
  6|8|G q r path rejection by a new Levi C6 / C8 / C16: `path` is a simple path of length 4 / 6 / 14
                 in the current (pre-insertion) Levi graph between two distinct members of {p,q,r}  (checked)
  E q r          expansion: the block {p,q,r} is inserted, the child state's records follow, closed by U
  C              completion (only legal when the state really is complete; counted; fails unless --allow-completions)
The stream starts with `R cap orbit [flags]` and ends with `END states attempted structural c6 c8 c16 completions`;
the checker recomputes every counter and requires equality, rejects trailing data and truncation.
Levi vertex encoding: point x -> x, block b -> 64 + b.

usage: cb_check.py STREAM|-  [--allow-completions] [--json OUT]
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from typing import Iterator


class CertError(Exception):
    pass


def records(path: str) -> Iterator[list[str]]:
    if path == "-":
        fh = sys.stdin
    elif path.endswith(".gz"):
        fh = gzip.open(path, "rt")
    else:
        fh = open(path, "r")
    for line in fh:
        yield line.split()


class Checker:
    def __init__(self, cap: int, orbit: int, flags: set[str], allow_completions: bool) -> None:
        self.cap = cap
        self.orbit = orbit
        self.f6 = "c6" in flags
        self.f8 = "no8" not in flags
        self.f16 = "no16" not in flags
        self.allow = allow_completions
        self.blocks: list[tuple[int, int, int]] = []
        self.inc: list[list[int]] = [[] for _ in range(64)]  # point -> block indices
        self.n = 0
        self.cnt = {"states": 0, "attempted": 0, "structural": 0, "c6": 0, "c8": 0, "c16": 0, "completions": 0}
        self.completion_blocks: list[list[tuple[int, int, int]]] = []
        if orbit == 0:
            root = [(0, 1, 2)]
        elif orbit == 1:
            root = [(0, 1, 3), (1, 2, 4), (0, 2, 5), (0, 4, 6)]
        elif orbit == 2:
            root = [(0, 1, 3), (1, 2, 4), (0, 2, 5), (0, 6, 7)]
        else:
            raise CertError("bad orbit")
        for b in root:
            self.insert(b)

    # ----- state -----
    def insert(self, b: tuple[int, int, int]) -> None:
        k = len(self.blocks)
        self.blocks.append(b)
        for x in b:
            self.inc[x].append(k)
        self.n = max(self.n, max(b) + 1)

    def remove(self, b: tuple[int, int, int], old_n: int) -> None:
        k = len(self.blocks) - 1
        if self.blocks[k] != b:
            raise CertError("internal: remove mismatch")
        self.blocks.pop()
        for x in b:
            if self.inc[x][-1] != k:
                raise CertError("internal: incidence order")
            self.inc[x].pop()
        self.n = old_n

    def share(self, x: int, y: int) -> bool:
        return any(y in self.blocks[k] for k in self.inc[x])

    def schedule(self) -> tuple[int, list[tuple[int, int]]]:
        """Return (p, ordered proposal list) or (-1, []) if every introduced point is cubic."""
        p = -1
        for x in range(self.n):
            if len(self.inc[x]) < 3:
                p = x
                break
        if p < 0:
            return -1, []
        bound = (-1, -1)
        for k in self.inc[p]:
            b = self.blocks[k]
            if b[0] == p and (b[1], b[2]) > bound:
                bound = (b[1], b[2])
        elig = [x for x in range(p + 1, self.n) if len(self.inc[x]) < 3 and not self.share(p, x)]
        f = self.n
        cands: list[tuple[int, int]] = []
        for i, q in enumerate(elig):
            for r in elig[i + 1:]:
                cands.append((q, r))
            cands.append((q, f))
        cands.append((f, f + 1))
        out = sorted(c for c in cands if c > bound and c[1] + 1 <= self.cap)
        return p, out

    def adjacent(self, u: int, v: int) -> bool:
        if (u < 64) == (v < 64):
            return False
        x, b = (u, v - 64) if u < 64 else (v, u - 64)
        return 0 <= b < len(self.blocks) and x in self.blocks[b]

    def check_path(self, path: list[int], length: int, ends: tuple[int, int, int]) -> None:
        if len(path) != length + 1:
            raise CertError("witness length")
        if len(set(path)) != len(path):
            raise CertError("witness not simple")
        a, z = path[0], path[-1]
        if a == z or a not in ends or z not in ends:
            raise CertError("witness endpoints")
        if a >= self.n or z >= self.n:
            raise CertError("witness endpoint not introduced")
        for i in range(length):
            if not self.adjacent(path[i], path[i + 1]):
                raise CertError("witness edge missing")

    # ----- stream -----
    def run_state(self, it: Iterator[list[str]]) -> None:
        self.cnt["states"] += 1
        p, props = self.schedule()
        if p < 0:
            rec = next(it, None)
            if rec != ["C"]:
                raise CertError("complete state not reported as C")
            self.cnt["completions"] += 1
            self.completion_blocks.append(list(self.blocks))
            if not self.allow:
                raise CertError("completion found: certificate does not close the tree")
            return
        for (q, r) in props:
            rec = next(it, None)
            if rec is None:
                raise CertError("truncated stream")
            self.cnt["attempted"] += 1
            tag = rec[0]
            if len(rec) < 3 or int(rec[1]) != q or int(rec[2]) != r:
                raise CertError(f"schedule mismatch at p={p}: expected {(q, r)} got {rec[:3]}")
            if tag == "S":
                if not (q < self.n and r < self.n and self.share(q, r)):
                    raise CertError("bad structural rejection")
                self.cnt["structural"] += 1
            elif tag in ("6", "8", "G"):
                length = {"6": 4, "8": 6, "G": 14}[tag]
                enabled = {"6": self.f6, "8": self.f8, "G": self.f16}[tag]
                if not enabled:
                    raise CertError("rejection by a disabled filter")
                self.check_path([int(t) for t in rec[3:]], length, (p, q, r))
                self.cnt[{"6": "c6", "8": "c8", "G": "c16"}[tag]] += 1
            elif tag == "E":
                b = (p, q, r)
                old_n = self.n
                self.insert(b)
                self.run_state(it)
                self.remove(b, old_n)
                if next(it, None) != ["U"]:
                    raise CertError("missing U after child")
            else:
                raise CertError(f"unexpected record {rec[:3]}")


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    path = args[0]
    allow = "--allow-completions" in args
    out = args[args.index("--json") + 1] if "--json" in args else None
    it = records(path)
    result: dict[str, object] = {"stream": path}
    try:
        head = next(it, None)
        if not head or head[0] != "R":
            raise CertError("missing header")
        cap, orbit = int(head[1]), int(head[2])
        chk = Checker(cap, orbit, set(head[3:]), allow)
        result.update({"cap": cap, "orbit": orbit, "flags": head[3:]})
        chk.run_state(it)
        tail = next(it, None)
        if not tail or tail[0] != "END":
            raise CertError("missing END")
        claimed = [int(t) for t in tail[1:]]
        mine = [chk.cnt[k] for k in ("states", "attempted", "structural", "c6", "c8", "c16", "completions")]
        if claimed != mine:
            raise CertError(f"counter mismatch claimed={claimed} recomputed={mine}")
        if next(it, None) is not None:
            raise CertError("trailing data")
        result.update({"accepted": True, "counters": chk.cnt})
        if allow:
            h = hashlib.sha256()
            for bl in chk.completion_blocks:
                h.update(repr(sorted(bl)).encode())
            result["completion_list_sha256"] = h.hexdigest()
    except CertError as e:
        result.update({"accepted": False, "error": str(e)})
    except (ValueError, IndexError) as e:
        result.update({"accepted": False, "error": f"malformed: {e}"})
    txt = json.dumps(result)
    print(txt)
    if out:
        with open(out, "w") as fh:
            fh.write(txt + "\n")
    return 0 if result.get("accepted") else 1


if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    sys.exit(main())
