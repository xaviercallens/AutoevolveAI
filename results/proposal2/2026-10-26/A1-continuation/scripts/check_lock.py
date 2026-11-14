"""Check that the 52 locked A1 Lean files are unchanged (sha256 against A1's STATEMENT_LOCK.json)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from l1common import REPO, sha256  # noqa: E402


def walk(o, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str) and len(v) == 64 and k.endswith(".lean"):
                out[k] = v
            else:
                walk(v, out)
    elif isinstance(o, list):
        for x in o:
            walk(x, out)


def main() -> int:
    lock = json.loads((REPO / "results/proposal2/2026-10-26/A1/STATEMENT_LOCK.json").read_text())
    files: dict[str, str] = {}
    walk(lock, files)
    bad = []
    for name, h in files.items():
        cands = [REPO / "formal_cert/Programmes/SandierSerfaty" / Path(name).name, REPO / name]
        p = next((c for c in cands if c.exists()), None)
        if p is None or sha256(p) != h:
            bad.append(name)
    print(json.dumps({"locked_files_checked": len(files), "changed_or_missing": bad}))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
