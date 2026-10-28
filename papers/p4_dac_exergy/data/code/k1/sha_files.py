"""Write {name: {sha256, bytes}} for the given files into a JSON file (for large logs kept outside the paper bundle).

Usage: python -I sha_files.py <out.json> <file> [<file> ...]
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def main() -> int:
    out = {}
    for f in sys.argv[2:]:
        p = Path(f)
        out[p.name] = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size,
                       "location": "results/proposal4/2026-10-27/K1/logs/rev/ (not in the paper bundle)"}
    Path(sys.argv[1]).write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
