"""Delete evidence blobs that no claim in ledger.json references (superseded content-addressed blobs)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    refs = {c["evidence"].split(":", 1)[1] for c in json.loads((HERE / "ledger.json").read_text())["claims"]}
    removed = [p.name for p in sorted((HERE / "evidence").glob("*.json")) if p.stem not in refs]
    for name in removed:
        (HERE / "evidence" / name).unlink()
    left = len(list((HERE / "evidence").glob("*.json")))
    print(json.dumps({"removed": removed, "remaining": left, "referenced": len(refs)}))
    return 0 if left == len(refs) else 1


if __name__ == "__main__":
    sys.exit(main())
