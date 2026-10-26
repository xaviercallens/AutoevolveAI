"""Split the two large list literals `bndNodes`, `bndCells` of a generated CalcLam*.lean into blocks of BLOCK
elements (`def bndNodes_k`), joined with `++`, so that elaboration stays within Lean's recursion / heartbeat limits.
The element text is moved verbatim. Usage: split_lists.py FILE [BLOCK]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def split(src: str, name: str, ty: str, block: int) -> str:
    m = re.search(rf"def {name} : List {ty} := \[\n(.*?)\]\n", src, re.S)
    if not m:
        raise SystemExit(f"{name} not found")
    items = [x.strip().rstrip(",") for x in m.group(1).split(",\n")]
    defs = []
    for k in range(0, len(items), block):
        part = ",\n  ".join(items[k:k + block])
        defs.append(f"def {name}_{k // block} : List {ty} := [\n  {part}]")
    joined = " ++ ".join(f"{name}_{k}" for k in range(len(defs)))
    new = "\n".join(defs) + f"\ndef {name} : List {ty} := {joined}\n"
    return src[:m.start()] + new + src[m.end():]


def main(path: Path, block: int) -> None:
    s = path.read_text()
    s = split(s, "bndNodes", "IV", block)
    s = split(s, "bndCells", "CellD", block)
    path.write_text(s)
    print("split", path)


if __name__ == "__main__":
    main(Path(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else 100)
