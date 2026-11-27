"""Export the data for the rusty-SUNDIALS CVODE cross-check of the table propagation (Tier X).

Writes a plain-text file with
  * the basis coefficients (co[1..38], Tp0..Tp2, edge values, VR, alp, beta, -log R + pi/2 R^2, constants) as f64
    nearest to the midpoints of the C++ intervals (these only define the ODE right-hand side in f64);
  * the C++ propagation-state enclosures pointS (s1, s2, ps_k for k = 6..228) at a subsample of table nodes, each
    endpoint rounded OUTWARD to f64 (exact rational u/Q, then nextafter), so "f64 value inside the f64 box" implies
    "inside the exact C++ enclosure" is NOT claimed; the box is a superset by at most one ulp per side;
  * the C++ initial state ss0(small) (midpoints).
Usage: export_cvode_data.py OUTFILE [STRIDE]
"""
from __future__ import annotations

import math
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dump2io import Dump2  # noqa: E402
from jetmirror import Ctx  # noqa: E402
from l1common import Q, sha256, DUMP2  # noqa: E402


def mid(a: tuple[int, int]) -> float:
    return float(Fraction(a[0] + a[1], 2 * Q))


def down(a: int) -> float:
    x = Fraction(a, Q)
    f = float(x)
    return math.nextafter(f, -math.inf) if Fraction(f) > x else f


def up(a: int) -> float:
    x = Fraction(a, Q)
    f = float(x)
    return math.nextafter(f, math.inf) if Fraction(f) < x else f


def r(x: float) -> str:
    return repr(float(x))


def main() -> int:
    out = Path(sys.argv[1])
    stride = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    d = Dump2(want={"node", "pS", "init_ps"})
    ctx = Ctx(d.sc)
    L = [f"# sandier-serfaty table CVODE cross-check data; source dump2.txt sha256 {sha256(DUMP2)}"]
    for name in ("pi", "p", "R", "small", "cut", "v"):
        val = {"pi": ctx.pi, "p": ctx.p, "R": ctx.R, "small": ctx.small, "cut": ctx.cut, "v": ctx.v}[name]
        L.append(f"const {name} {r(mid(val))}")
    L.append(f"const b0c {r(mid(ctx.b0c))}")
    L.append(f"const cR1 {r(mid(ctx.cR1))}")
    L.append(f"const cR2 {r(mid(ctx.cR2))}")
    for i in range(38):
        L.append(f"mode {i+1} {r(mid(ctx.co[i+1]))} {r(mid(ctx.Tp0[i]))} {r(mid(ctx.Tp1[i]))} {r(mid(ctx.Tp2[i]))} "
                 f"{r(mid(ctx.VR[i]))} {r(mid(ctx.alp[i]))} {r(mid(ctx.beta[i]))}")
        L.append(f"edge {i+1} " + " ".join(r(mid(x)) for x in ctx.edge[i]))
    L.append(f"init {r(mid(d.sc['init_s1']))} {r(mid(d.sc['init_s2']))} " + " ".join(r(mid(d.init_ps[k])) for k in sorted(d.init_ps)))
    n = len(d.node)
    first = min(i for i in range(1, n) if d.node[i - 1][0] >= 1)
    keep = set(range(first - 1, n, stride)) | {n - 1}
    # segment-boundary nodes and their predecessors (for the node-to-node check)
    for i in range(1, n):
        if d.node[i][0] != d.node[i - 1][0]:
            keep |= {i - 1, i}
    keep |= {i - 1 for i in list(keep) if i - 1 >= first - 1}
    for i in sorted(keep):
        if i < first - 1:
            continue
        orig, t, _ = d.node[i]
        s1, s2, ps = d.pS[i]
        vals = [s1, s2] + [ps[k] for k in sorted(ps)]
        L.append(f"node {i} {orig} {r(mid(t))} " + " ".join(f"{r(down(a[0]))} {r(up(a[1]))}" for a in vals))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n")
    print(f"wrote {out} ({out.stat().st_size} bytes, {len(keep)} nodes, first propagating node {first})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
