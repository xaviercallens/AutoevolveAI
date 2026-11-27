#!/usr/bin/env python3
"""set_compare.py -- control P2b: set-level equality of our canonical configurations with nauty genbg output.
genbg graphs (first class = vertices 0..v-1) are relabelled with nauty-labelg -f<a^v b^v>, the same colouring as
canon_count.py uses, and the sorted canonical sets are compared.
usage: set_compare.py OUTJSON V:OURS.g6:GENBG.g6 [...]
"""
from __future__ import annotations

import json
import subprocess
import sys


def canon(path: str, v: int) -> set[str]:
    with open(path) as fh:
        data = "".join(l for l in fh if not l.startswith(">"))
    cp = subprocess.run(["nauty-labelg", "-q", "-f" + "a" * v + "b" * v], input=data, capture_output=True, text=True,
                        check=True)
    return set(cp.stdout.split())


def main() -> int:
    out = {}
    ok = True
    for spec in sys.argv[2:]:
        v_s, ours, theirs = spec.split(":")
        v = int(v_s)
        a = canon(ours, v)
        b = canon(theirs, v)
        out[v_s] = {"ours": len(a), "genbg": len(b), "equal_sets": a == b}
        ok = ok and a == b
    out["all_equal"] = ok
    with open(sys.argv[1], "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(out))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
