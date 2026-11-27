"""Check the jet mirror against dump2: core_test cells (all, or a sample with --sample N)."""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dump2io import Dump2
from jetmirror import Ctx


def main() -> int:
    sample = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    d = Dump2(want={"ct", "ct_seg", "ct_run"})
    ctx = Ctx(d.sc)
    bad = 0
    n_checked = 0
    t0 = time.time()
    for seg in range(6):
        n = d.ct_n[seg]
        js = range(n) if not sample else sorted(set([0, n - 1] + list(range(0, n, max(1, n // sample)))))
        for j in js:
            got = list(ctx.core_cell(seg, j, n))
            if got != d.ct[(seg, j)]:
                bad += 1
                print("MISMATCH", seg, j, [g == e for g, e in zip(got, d.ct[(seg, j)])])
            n_checked += 1
    print(f"checked {n_checked} cells, mismatches {bad}, {time.time()-t0:.1f}s")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
