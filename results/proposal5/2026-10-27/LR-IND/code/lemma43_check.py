#!/usr/bin/env python3
"""Exact check of the inclusion used in S-T Lemma 4.3: r_k((1/(k+1))Z) is a subset of r_k((1/p)Z), where
r_k(t) = (floor((k+1){t}), ..., floor((k+1){k t})), for k = 10 and every p in P_10 (and footnote-4 primes).
Integer form: floor((k+1) * {i r / q}) = ((k+1) * (i r mod q)) // q."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def rk(k: int, r: int, q: int) -> tuple[int, ...]:
    return tuple(((k + 1) * (i * r % q)) // q for i in range(1, k + 1))


def main() -> int:
    k = 10
    ps = [p for p in range(100, 468) if all(p % d for d in range(2, int(p ** 0.5) + 1))]
    base = {rk(k, r, k + 1) for r in range(k + 1)}
    rows = []
    for p in ps:
        img = {rk(k, r, p) for r in range(p)}
        rows.append({"p": p, "inclusion_holds": base <= img, "p_gt_k2k": p > k * k + k})
    out = {"k": k, "base_size": len(base), "rows": rows,
           "all_P10_hold": all(r["inclusion_holds"] for r in rows if 127 <= r["p"] <= 467),
           "fails": [r["p"] for r in rows if not r["inclusion_holds"]]}
    Path(__file__).resolve().parent.parent.joinpath("logs", "lemma43_check.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k2: v for k2, v in out.items() if k2 != "rows"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
