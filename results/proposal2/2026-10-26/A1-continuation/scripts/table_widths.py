"""Enclosure widths of the table propagation states (pointS) along t, from dump2.txt (for choosing CVODE tolerances)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dump2io import Dump2  # noqa: E402
from l1common import Q  # noqa: E402


def main() -> int:
    d = Dump2(want={"node", "pS"})
    idx = sorted(d.pS)
    for i in idx[:: max(1, len(idx) // 25)] + [idx[-1]]:
        orig, t, _ = d.node[i]
        s1, s2, ps = d.pS[i]
        tm = (t[0] + t[1]) / 2 / Q
        def w(a: tuple[int, int]) -> str:
            mid = (a[0] + a[1]) / 2 / Q
            wd = (a[1] - a[0]) / Q
            return f"{mid:+.6e}±{wd/2:.1e}({wd/2/max(abs(mid),1e-300):.1e})"
        k6, k228 = ps.get(6), ps.get(228)
        print(f"i={i:5d} seg={orig} t={tm:.6f} s1={w(s1)} s2={w(s2)} ps6={w(k6) if k6 else '-'} ps228={w(k228) if k228 else '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
