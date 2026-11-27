"""Check the table-stage mirror (propagation step and fh) against dump2 on a sample of nodes (or all with 'all')."""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dump2io import Dump2  # noqa: E402
from jetmirror import KEYS, Ctx, fh, prop_step  # noqa: E402
from l1common import ONE, ZERO  # noqa: E402


def st(s: tuple) -> tuple:
    s1, s2, ps = s
    return (s1, s2, [ps[k] for k in KEYS])


def main() -> int:
    d = Dump2(want={"node", "cell", "pS", "cS"})
    ctx = Ctx(d.sc)
    n = len(d.node)
    stride = 1 if (len(sys.argv) > 1 and sys.argv[1] == "all") else int(sys.argv[1]) if len(sys.argv) > 1 else 97
    bad = 0
    t0 = time.time()
    idx = sorted(set(range(1, n, stride)) | {1562, 1563, 2000, 3003, 4999, 5000, 5005, 5006, 6825})
    for i in idx:
        orig, x, pts = d.node[i]
        old = d.node[i - 1][1]
        sgprev = d.node[i - 1][0]
        if sgprev >= 1:
            ns, bs = prop_step(ctx, old, x, st(d.pS[i - 1]), sgprev)
            if ns != st(d.pS[i]):
                bad += 1
                print("pS mismatch", i)
            if bs != st(d.cS[i - 1]):
                bad += 1
                print("cS mismatch", i - 1)
        tt = (x, ONE, ZERO, ZERO)
        got = fh(ctx, tt, orig, None if orig == 0 else st(d.pS[i]))
        if got != pts:
            bad += 1
            print("pts mismatch", i, [a == b for a, b in zip(got, pts)])
        tc = ((old[0], x[1]), ONE, ZERO, ZERO)
        gc = fh(ctx, tc, sgprev, None if sgprev < 1 else st(d.cS[i - 1]))
        if gc != d.cell[i - 1]:
            bad += 1
            print("cel mismatch", i - 1, [a == b for a, b in zip(gc, d.cell[i - 1])])
    print(f"checked {len(idx)} nodes, mismatches {bad}, {time.time()-t0:.1f}s")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
