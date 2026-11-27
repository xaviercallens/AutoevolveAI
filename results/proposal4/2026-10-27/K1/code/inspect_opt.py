"""Print the key structure of one optimized-cycle JSON (for orientation; not a result)."""
from __future__ import annotations

import json
import sys


def show(d, pre: str = "", depth: int = 0) -> None:
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, (dict, list)):
                print(pre + k, type(v).__name__, (len(v) if hasattr(v, "__len__") else ""))
                if depth < 3:
                    show(v if isinstance(v, dict) else (v[0] if v and isinstance(v, list) else {}), pre + "  ",
                         depth + 1)
            else:
                print(pre + k, "=", str(v)[:80])
    elif isinstance(d, list) and d:
        print(pre + "[0]:", str(d[0])[:120], "len", len(d))


def main() -> int:
    show(json.load(open(sys.argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
