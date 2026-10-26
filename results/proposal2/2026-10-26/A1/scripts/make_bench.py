"""Write kernel-throughput benchmark files that use the real IV.mul / IV.div of Programmes.SandierSerfaty.IV.

Each file holds ONE `decide +kernel` theorem over `calls` independent evaluations, each doing 4 IV.mul and 1 IV.div
(= 1 inv + 1 mul), so 6 C++-counted operations (mul or inv) per call. Usage: make_bench.py OUTDIR CALLS...
"""
from __future__ import annotations

import sys
from pathlib import Path

TEMPLATE = """import Programmes.SandierSerfaty.IV
open ProgSandierSerfaty.Cert ProgSandierSerfaty.Cert.IV

def bx0 : IV := ⟨Q / 2, Q / 2 + 7⟩
def by0 : IV := ⟨Q - Q / 1000 - 1, Q - Q / 1000 + 1⟩
def bz0 : IV := ⟨3 * Q + 11, 3 * Q + 13⟩

def bone (i : Nat) : Bool :=
  let x : IV := ⟨bx0.u + (i : Int) * 12345678901234567, bx0.v + (i : Int) * 12345678901234567⟩
  let r := div (mul (mul (mul (mul x by0) by0) by0) by0) bz0
  decide (r.u ≤ r.v)

def ball : Nat → Bool
  | 0 => true
  | n + 1 => bone n && ball n

set_option maxRecDepth 1000000 in
theorem bench_{calls} : ball {calls} = true := by decide +kernel
"""


def main(argv: list[str]) -> None:
    out = Path(argv[0])
    out.mkdir(parents=True, exist_ok=True)
    for c in argv[1:]:
        n = int(c)
        (out / f"BenchIV{n}.lean").write_text(TEMPLATE.replace("{calls}", str(n)))


if __name__ == "__main__":
    main(sys.argv[1:])
